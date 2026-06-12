"""
LLM Client for 8zenith
ใช้ Groq SDK ในการสื่อสารกับโมเดล
"""

import os
from groq import Groq

class LLMClient:
    def __init__(self, model="llama-3.3-70b-versatile"):
        self.client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        self.model = model

    def generate(self, messages, response_format=None):
        """
        ส่งข้อความไปยัง LLM และรับผลลัพธ์กลับ
        - messages: list of dict (role, content)
        - response_format: {"type": "json_object"} เพื่อบังคับให้ตอบ JSON
        """
        kwargs = dict(
            model=self.model,
            messages=messages,
            temperature=0.2,
            max_tokens=4096
        )
        if response_format:
            kwargs["response_format"] = response_format

        response = self.client.chat.completions.create(**kwargs)
        return response.choices[0].message.content