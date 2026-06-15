import type { RequestHandler } from './$types';
import { GROQ_API_KEY } from '$env/static/private';
import { error, json } from '@sveltejs/kit';

// =========================================================================
// 🧠 Universal Chat Endpoint
// =========================================================================
const API_URL = 'https://api.groq.com/openai/v1/chat/completions';
const DEFAULT_MODEL = 'llama-3.3-70b-versatile';
const DEFAULT_MAX_TOKENS = 2048;
const REQUEST_TIMEOUT_MS = 60_000;

if (!GROQ_API_KEY) {
	throw new Error('Missing GROQ_API_KEY in environment');
}

interface ChatMessage {
	role: 'system' | 'user' | 'assistant';
	content: string;
}

type ChatRequest =
	| { messages: ChatMessage[]; model?: string; temperature?: number; max_tokens?: number; stream?: boolean }
	| { message: string; model?: string; temperature?: number; max_tokens?: number; stream?: boolean }
	| { astrologyData: any; model?: string; temperature?: number; max_tokens?: number; stream?: boolean };

const ASTROLOGY_SYSTEM_PROMPT = `คุณคือผู้เชี่ยวชาญด้านโหราศาสตร์

กฎการตอบ:
1. ตอบยาว 15-20 ย่อหน้า มีหัวข้อชัดเจน ใช้ภาษาไทยสละสลวย
2. ห้ามใช้คำว่าขออภัย/ขอโทษ/ไม่สามารถ
3. ปิดท้ายด้วย <question>คำถามชวนคุยต่อ 1 ข้อ</question> เสมอ ห้ามปนกับเนื้อหา`;

const DEFAULT_SYSTEM_PROMPT = 'คุณคือผู้ช่วย AI ที่เป็นมิตร ตอบเป็นภาษาไทย ปิดท้ายด้วย <question>คำถามชวนคุยต่อ</question> เสมอ';

function buildMessages(body: ChatRequest): ChatMessage[] {
	if ('messages' in body && body.messages?.length) {
		return body.messages;
	}
	
	if ('astrologyData' in body) {
		// แนะนำ: ย้าย logic format bazi ไป util แยก จะได้ test ง่าย
		return [{ role: 'system', content: ASTROLOGY_SYSTEM_PROMPT }];
	}
	
	if ('message' in body && body.message) {
		return [
			{ role: 'system', content: DEFAULT_SYSTEM_PROMPT },
			{ role: 'user', content: body.message }
		];
	}
	
	throw error(400, 'ต้องส่ง messages[] หรือ message หรือ astrologyData มา');
}

async function fetchWithTimeout(url: string, options: RequestInit, timeout: number) {
	const controller = new AbortController();
	const id = setTimeout(() => controller.abort(), timeout);
	
	try {
		const response = await fetch(url, {...options, signal: controller.signal });
		return response;
	} finally {
		clearTimeout(id);
	}
}

export const POST: RequestHandler = async ({ request }) => {
	try {
		const body: ChatRequest = await request.json();
		const messages = buildMessages(body);
		
		if (!messages.some((m) => m.role === 'user')) {
			throw error(400, 'ต้องมี user message อย่างน้อย 1 ข้อความ');
		}

		const shouldStream = body.stream?? true;
		
		const response = await fetchWithTimeout(
			API_URL,
			{
				method: 'POST',
				headers: {
					'Content-Type': 'application/json',
					Authorization: `Bearer ${GROQ_API_KEY}`
				},
				body: JSON.stringify({
					model: body.model?? DEFAULT_MODEL,
					messages,
					stream: shouldStream,
					temperature: body.temperature?? 0.8,
					max_tokens: body.max_tokens?? DEFAULT_MAX_TOKENS
				})
			},
			REQUEST_TIMEOUT_MS
		);

		if (!response.ok) {
			const errorText = await response.text();
			throw error(response.status, `Groq API Error: ${errorText}`);
		}


		// Stream mode with error propagation
		const stream = new ReadableStream({
			async start(controller) {
				const reader = response.body?.getReader();
				const decoder = new TextDecoder();
				
				if (!reader) {
					controller.error(new Error('No response body'));
					return;
				}

				let buffer = '';
				try {
					while (true) {
						const { value, done } = await reader.read();
						if (done) break;

						buffer += decoder.decode(value, { stream: true });
						const lines = buffer.split('\n');
						buffer = lines.pop()?? '';

						for (const line of lines) {
							if (!line.startsWith('data: ')) continue;
							const dataValue = line.slice(6).trim();
							if (dataValue === '[DONE]') continue;
							
							try {
								const parsed = JSON.parse(dataValue);
								const token = parsed.choices?.[0]?.delta?.content;
								if (token) controller.enqueue(new TextEncoder().encode(token));
								
								// ดัก error ที่ Groq อาจส่งมากลาง stream
								if (parsed.error) {
									throw new Error(parsed.error.message?? 'Stream error');
								}
							} catch {
								// skip partial json
							}
						}
					}
				} catch (err) {
					controller.error(err);
				} finally {
					controller.close();
				}
			}
		});

		return new Response(stream, {
			headers: {
				'Content-Type': 'text/event-stream',
				'Cache-Control': 'no-cache',
				Connection: 'keep-alive'
			}
		});
	} catch (e) {
		if (e instanceof Response) throw e; // จาก sveltekit error()
		
		const message = e instanceof Error? e.message : 'Unknown error';
		console.error('Chat endpoint error:', e);
		return json({ success: false, error: message }, { status: 500 });
	}
};