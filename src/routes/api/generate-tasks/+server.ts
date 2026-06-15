import type { RequestHandler } from './$types';
import { GROQ_API_KEY } from '$env/static/private';

const API_URL = 'https://api.groq.com/openai/v1/chat/completions';
const MODEL = 'llama-3.3-70b-versatile';

export const POST: RequestHandler = async ({ request }) => {
  try {
    const { name, description } = await request.json();

    if (!name?.trim()) {
      return new Response(JSON.stringify({ success: false, error: 'Missing project name' }), {
        status: 400,
        headers: { 'Content-Type': 'application/json' },
      });
    }

    const systemPrompt = `You are a project management AI assistant. Given a project name and description, generate a practical task list.

Rules:
- Return ONLY valid JSON, no markdown, no code fences
- Each task must have: title (string), description (string), priority ("low" | "medium" | "high")
- Generate 3-8 tasks
- Tasks should be concrete, actionable, and cover the key steps to complete the project
- Write in Thai language

Format:
{ "tasks": [ { "title": "ชื่อ task", "description": "รายละเอียด", "priority": "high" } ] }`;

    const userMessage = `Project name: ${name}\nDescription: ${description || '(no description)'}`;

    const response = await fetch(API_URL, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${GROQ_API_KEY}`,
      },
      body: JSON.stringify({
        model: MODEL,
        messages: [
          { role: 'system', content: systemPrompt },
          { role: 'user', content: userMessage },
        ],
        temperature: 0.7,
        stream: false,
      }),
    });

    if (!response.ok) {
      const err = await response.text();
      throw new Error(`Groq API error [${response.status}]: ${err}`);
    }

    const data = await response.json();
    const content = data.choices?.[0]?.message?.content || '';

    // Try to parse JSON from response
    const jsonMatch = content.match(/\{[\s\S]*\}/);
    if (!jsonMatch) {
      throw new Error('AI response did not contain valid JSON');
    }

    const parsed = JSON.parse(jsonMatch[0]);
    const tasks = Array.isArray(parsed.tasks) ? parsed.tasks : [];

    return new Response(JSON.stringify({ success: true, tasks }), {
      headers: { 'Content-Type': 'application/json' },
    });
  } catch (e) {
    const message = e instanceof Error ? e.message : 'Unknown error';
    return new Response(JSON.stringify({ success: false, error: message }), {
      status: 500,
      headers: { 'Content-Type': 'application/json' },
    });
  }
};
