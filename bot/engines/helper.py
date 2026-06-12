"""
8zenith Helper Engine — ผู้ประสานภารกิจ (Full-Scale Dispatcher)
รับข้อมูลจาก Observer (20+ intents) → วิเคราะห์ → ตั้งสมมติฐาน → สั่งการ Seeker

หลักการ:
1. Pure Rule-Based Routing: จัดเส้นทางเฉพาะ Tools ที่ทำงานแบบ Deterministic 100%
2. No LLM in Pipeline: ตัดการเรียก LLM ออกทั้งหมด เพื่อรับประกัน Zero Hallucination
3. Graceful Fallback: Intent ที่ยังไม่มี Tool จริง จะถูกส่งไปหา rule_based_fallback 
   เพื่อตอบกลับด้วยข้อความที่กำหนดไว้ล่วงหน้า (ไม่ทำให้ Pipeline หัก)
Dependency: engines.observer
"""

from dataclasses import dataclass
from typing import Dict, Any, Optional
from engines.observer import ObservationResult


# ═══════════════════════════════════════════════════════════════
# Data Structures
# ═══════════════════════════════════════════════════════════════

@dataclass
class HelperTask:
    """โครงสร้างคำสั่งงานที่จะส่งต่อไปให้ Seeker"""
    intent: str                          # Intent ต้นทางจาก Observer
    target_tool: Optional[str]           # เครื่องมือที่ Seeker ต้องเรียกใช้
    payload: Dict[str, Any]              # ข้อมูลดิบที่สกัดมาแล้ว
    hypothesis: str                      # สมมติฐานที่อธิบายเจตนาของคำขอ


# ═══════════════════════════════════════════════════════════════
# Helper Engine
# ═══════════════════════════════════════════════════════════════

class HelperEngine:
    """
    สมองผู้สั่งการ: แปลง ObservationResult เป็น HelperTask สำหรับ 20 Intents
    แยกเส้นทางชัดเจนระหว่าง Rule-Based Tool จริง และ Deterministic Fallback
    """
    
    def dispatch(self, obs: ObservationResult) -> HelperTask:
        intent = obs.intent
        data = obs.cleaned_data

        # ─── กลุ่มที่ 1: Rule-Based Tools ที่ทำงานเต็มรูปแบบแล้ว ───
        if intent in ["birth", "astrology"]:
            return HelperTask(
                intent=intent,
                target_tool="astro_calculate",
                payload=data,
                hypothesis="ผู้ใช้ต้องการผูกดวงและวิเคราะห์ชะตาจากวันเวลาและสถานที่เกิด (ใช้ Swiss Ephemeris)"
            )
        elif intent == "math":
            return HelperTask(
                intent=intent,
                target_tool="math_solver",
                payload=data,
                hypothesis="ผู้ใช้ต้องการให้ระบบแก้สมการหรือคำนวณทางคณิตศาสตร์ (ใช้ Z3/SymPy)"
            )
        elif intent == "chat":
            return HelperTask(
                intent=intent,
                target_tool="chat_response",
                payload=data,
                hypothesis="ผู้ใช้ต้องการสนทนาทักทายหรือปิดบทสนทนาทั่วไป"
            )
        elif intent == "name":
            return HelperTask(
                intent=intent,
                target_tool="name_analyzer",
                payload=data,
                hypothesis="ผู้ใช้ต้องการวิเคราะห์ความหมายหรือพลังงานของชื่อ-นามสกุล"
            )

        # ─── กลุ่มที่ 2: System & Command (Deterministic Logic) ───
        elif intent in ["command", "settings"]:
            return HelperTask(
                intent=intent,
                target_tool="system_action",
                payload=data,
                hypothesis="ผู้ใช้ต้องการสั่งการระบบหรือเปลี่ยนการตั้งค่า"
            )

        # ─── กลุ่มที่ 3: Text/Logic Processing (เตรียมรองรับ Rule-based Engine) ───
        elif intent in ["text_analysis", "summarization", "translation", "comparison"]:
            return HelperTask(
                intent=intent,
                target_tool="text_rule_engine",
                payload=data,
                hypothesis="ผู้ใช้ต้องการประมวลผลข้อความด้วยกฎที่กำหนดไว้ (ไม่ใช่ LLM)"
            )
        elif intent == "coding":
            return HelperTask(
                intent=intent,
                target_tool="code_handler",
                payload=data,
                hypothesis="ผู้ใช้ต้องการให้จัดการหรือตรวจสอบโค้ด"
            )
        elif intent in ["creative", "planning", "recommendation", "opinion"]:
            return HelperTask(
                intent=intent,
                target_tool="rule_based_generator",
                payload=data,
                hypothesis="ผู้ใช้ต้องการคำแนะนำหรือการวางแผนจากฐานความรู้ตายตัว"
            )

        # ─── กลุ่มที่ 4: Info & General Query (Fallback ไปยัง Static/Rule QA) ───
        elif intent in ["info_query", "help", "system_query", "general"]:
            return HelperTask(
                intent=intent,
                target_tool="static_qa",
                payload=data,
                hypothesis="ผู้ใช้ต้องการถามข้อมูลทั่วไปหรือขอความช่วยเหลือ"
            )

        # ─── Fallback: Intent ไม่รู้จัก หรือ คะแนนไม่ถึง Threshold ───
        else:
            return HelperTask(
                intent="unknown",
                target_tool="system_fallback",
                payload=data,
                hypothesis="ระบบไม่สามารถระบุเครื่องมือที่เหมาะสมได้ (Unknown/Low Confidence)"
            )


# ═══════════════════════════════════════════════════════════════
# Quick Test
# ═══════════════════════════════════════════════════════════════

if __name__ == "__main__":
    # จำลอง ObservationResult จาก Observer
    test_cases = [
        ObservationResult("birth", 0.95, {"year": 1992, "month": 8, "day": 8, "hour": 16, "lat": 6.54, "lon": 101.28}),
        ObservationResult("math", 0.90, {"equation": "x^2 + 19x - 92 = 0", "variables": ["x"]}),
        ObservationResult("chat", 0.85, {"chat_type": "greeting", "message": "สวัสดีครับ"}),
        ObservationResult("coding", 0.80, {"code": "def hello(): pass", "language": "python"}),
        ObservationResult("summarization", 0.75, {"content_to_summarize": "บทความยาวๆ..."}),
        ObservationResult("info_query", 0.70, {"query": "อะไรคือ machine learning", "topic": "machine learning"}),
        ObservationResult("unknown", 0.0, {"raw": "blabla", "reason": "low score"})
    ]
    
    helper = HelperEngine()
    
    print("🧪 TESTING HELPER ENGINE (Full 20-Intent Routing)")
    print("=" * 70)
    for obs in test_cases:
        task = helper.dispatch(obs)
        print(f"\n🎯 Intent: {obs.intent} (Conf: {obs.confidence})")
        print(f"   🔧 Target Tool: {task.target_tool}")
        print(f"   💡 Hypothesis: {task.hypothesis}")
        print(f"   📦 Payload Keys: {list(task.payload.keys())}")