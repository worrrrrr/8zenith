import type { RequestHandler } from './$types';
import { GROQ_API_KEY } from '$env/static/private';

// =========================================================================
// 🧠 Universal Chat Endpoint + Meta-Prompt Control
// =========================================================================
const API_URL = 'https://api.groq.com/openai/v1/chat/completions';
const API_KEY = GROQ_API_KEY;
const DEFAULT_MODEL = 'llama-3.3-70b-versatile';

interface ChatMessage {
	role: 'system' | 'user' | 'assistant';
	content: string;
}

interface ChatRequestBody {
	messages: ChatMessage[];
	model?: string;
	temperature?: number;
	max_tokens?: number;
	stream?: boolean;
	// สำหรับ legacy โหราศาสตร์ ถ้ายังอยากเก็บไว้
	astrologyData?: any;
	message?: string;
}

export const POST: RequestHandler = async ({ request }) => {
	try {
		const body: ChatRequestBody = await request.json();
		let messages: ChatMessage[] = [];
		let model = body.model || DEFAULT_MODEL;
		let temperature = body.temperature ?? 0.8;

		// 1. กรณี Chat ปกติ: ใช้ messages ที่ส่งมาตรงๆ
		if (body.messages && Array.isArray(body.messages)) {
			messages = body.messages;
		}

		// 2. Legacy: รองรับ astrologyData เดิม เพื่อไม่พัง
		else if (body.astrologyData) {
			const d = body.astrologyData;
			const bazi =
				d.bazi?.pillars
					?.map(
						(p: any) =>
							`${p.label} ${p.stem}${p.branch} (${p.stemTH}${p.branchTH}) ธาตุ${p.element}${p.yin} 十神:${p.shiShen}`
					)
					.join('\n') || '';

			const astrologyMetaPrompt = `คุณคือผู้เชี่ยวชาญด้านโหราศาสตร์

กฎการตอบ:
1. ตอบยาว 15-20 ย่อหน้า มีหัวข้อชัดเจน ใช้ภาษาไทยสละสลวย
2. ห้ามใช้คำว่าขออภัย/ขอโทษ/ไม่สามารถ
3. ปิดท้ายด้วย <question>คำถามชวนคุยต่อ 1 ข้อ</question> เสมอ ห้ามปนกับเนื้อหา`;
			messages = [{ role: 'system', content: astrologyMetaPrompt }];
		}

		// 3. Legacy: message เดียว
		else if (body.message) {
			messages = [
				{
					role: 'system',
					content:
						'คุณคือผู้ช่วย AI ที่เป็นมิตร ตอบเป็นภาษาไทย ปิดท้ายด้วย <question>คำถามชวนคุยต่อ</question> เสมอ'
				},
				{ role: 'user', content: body.message }
			];
		} else {
			throw new Error('ต้องส่ง messages[] หรือ message หรือ astrologyData มา');
		}

		// กัน user ส่ง messages เปล่า
		if (messages.length === 0 || !messages.some((m) => m.role === 'user')) {
			throw new Error('ต้องมี user message อย่างน้อย 1 ข้อความ');
		}

		const response = await fetch(API_URL, {
			method: 'POST',
			headers: {
				'Content-Type': 'application/json',
				Authorization: `Bearer ${API_KEY}`
			},
			body: JSON.stringify({
				model,
				messages,
				stream: body.stream ?? true,
				temperature,
				max_tokens: body.max_tokens
			})
		});

		if (!response.ok) {
			const errorText = await response.text();
			throw new Error(`AI Provider Error [${response.status}]: ${errorText}`);
		}

		// ถ้าไม่ stream ให้ return JSON ปกติ
		if (body.stream === false) {
			const data = await response.json();
			return new Response(
				JSON.stringify({
					success: true,
					content: data.choices?.[0]?.message?.content || ''
				}),
				{
					headers: { 'Content-Type': 'application/json' }
				}
			);
		}

		// Stream mode
		const transformStream = new ReadableStream({
			async start(controller) {
				const reader = response.body?.getReader();
				const decoder = new TextDecoder();
				if (!reader) return controller.close();

				let buffer = '';
				while (true) {
					const { value, done } = await reader.read();
					if (done) break;

					buffer += decoder.decode(value, { stream: true });
					const lines = buffer.split('\n');
					buffer = lines.pop() || '';

					for (const line of lines) {
						if (!line.startsWith('data:')) continue;
						const dataValue = line.slice(5).trim();
						if (dataValue === '[DONE]') continue;
						try {
							const parsed = JSON.parse(dataValue);
							const tokenChunk = parsed.choices?.[0]?.delta?.content;
							if (tokenChunk) controller.enqueue(new TextEncoder().encode(tokenChunk));
						} catch {
							/* skip partial json */
						}
					}
				}
				controller.close();
			}
		});

		return new Response(transformStream, {
			headers: {
				'Content-Type': 'text/event-stream',
				'Cache-Control': 'no-cache',
				Connection: 'keep-alive'
			}
		});
	} catch (e) {
		const message = e instanceof Error ? e.message : 'Unknown error';
		return new Response(JSON.stringify({ success: false, error: message }), {
			status: 500,
			headers: { 'Content-Type': 'application/json' }
		});
	}
};
