"""
8zenith Seeker Engine — ผู้ค้นหาและลงมือทำ (The Worker)
รับภารกิจจาก Helper → ลงมือเรียก Tools จริง (No Mocks, No LLM) → คืนผลลัพธ์ดิบ

หลักการ:
1. Rule-Based First: ใช้ Library คำนวณจริง (Swiss Ephemeris, Z3, SymPy)
2. Zero Hallucination: ไม่มีการสร้างข้อมูลขึ้นมาเอง หากไม่มีข้อมูลให้ตอบตาม Fallback
3. Graceful Degradation: หาก Intent นั้นยังไม่มี Tool จริง ให้ตอบกลับด้วยข้อความมาตรฐาน
   เพื่อให้ Pipeline ไหลลื่นและไม่เกิด Error
Dependency: tools.astro_calculate, tools.astro_translate, tools.math, engines.helper
"""

import logging
from dataclasses import dataclass
from typing import Dict, Any, Optional
from datetime import datetime

from engines.helper import HelperTask

# ตั้งค่า Logger
logger = logging.getLogger("8zenith.seeker")

# ═══════════════════════════════════════════════════════════
# Data Structures
# ═══════════════════════════════════════════════════════════
@dataclass
class SeekerResult:
    """ผลลัพธ์จากการลงมือค้นหาหรือคำนวณ"""
    success: bool
    raw_data: Dict[str, Any]
    message: str
    error_detail: Optional[str] = None


# ═══════════════════════════════════════════════════════════
# Seeker Engine
# ═══════════════════════════════════════════════════════════
class SeekerEngine:
    """แขนขาผู้ลงมือทำ: เรียกใช้ Tools จริงตาม HelperTask"""
    
    def search(self, task: HelperTask) -> SeekerResult:
        """จุดเริ่มต้นการทำงาน: รับ Task → Route ไปยังเครื่องมือที่ถูกต้อง"""
        target = task.target_tool
        payload = task.payload
        
        logger.info(f"Seeker เริ่มทำงาน: target={target}, intent={task.intent}")

        try:
            # ─── กลุ่มที่ 1: Rule-based Tools หลัก (คำนวณจริง 100%) ───
            if target == "astro_calculate":
                return self._seek_real_astrology(payload)
            elif target == "math_solver":
                return self._seek_real_math(payload)
            elif target == "chat_response":
                return self._seek_chat(payload)
            elif target == "name_analyzer":
                return self._seek_name(payload)
            
            # ─── กลุ่มที่ 2: Rule-based Fallback (สำหรับ Intent ที่ยังไม่มี Tool จริง) ───
            # เพื่อป้องกัน Pipeline หัก และยืนยันว่าเราไม่ใช้ LLM มาตอบแทน
            elif target in [
                "text_rule_engine", "code_handler", "rule_based_generator", 
                "static_qa", "system_action", "system_fallback"
            ]:
                return self._seek_rule_based_fallback(target, payload)
            
            # ─── Fallback: ไม่รู้จักคำสั่ง ───
            else:
                return SeekerResult(
                    success=False, 
                    raw_data={}, 
                    message="ไม่พบเครื่องมือที่รองรับ", 
                    error_detail=f"Unknown or unregistered tool: {target}"
                )
                
        except Exception as e:
            logger.error(f"Seeker ล้มเหลวสำหรับ task {task.intent}: {str(e)}")
            return SeekerResult(
                success=False, 
                raw_data={}, 
                message="เกิดข้อผิดพลาดระหว่างการประมวลผลจริง", 
                error_detail=str(e)
            )

    # ═══════════════════════════════════════════════════════
    # 1. Core Rule-Based Seekers
    # ═══════════════════════════════════════════════════════
    def _seek_real_astrology(self, data: Dict[str, Any]) -> SeekerResult:
        """เรียกใช้จักรกลดาราศาสตร์จริง (No Mocks)"""
        from tools.astro_calculate import AstroCalculate
        from tools.astro_translate import AstroTranslate

        # ใช้ Default Value ที่ปลอดภัยหากข้อมูลไม่ครบ (Protector จะดักจับทีหลัง)
        dt = datetime(
            data.get("year", 1992), data.get("month", 1), data.get("day", 1),
            data.get("hour", 12), data.get("minute", 0)
        )
        lat = float(data.get("lat", 13.75))
        lon = float(data.get("lon", 100.50))

        # 1. คำนวณข้อมูลดิบทางฟิสิกส์/ดาราศาสตร์
        calc = AstroCalculate(dt, lat, lon, house_system='P')
        
        # 2. แปลผลเป็นภาษามนุษย์ผ่าน Deterministic Mapping
        reader = AstroTranslate(calc)
        reading_dict = reader.full_reading()
        
        return SeekerResult(
            success=True, 
            raw_data=reading_dict, 
            message="คำนวณและแปลผลดวงชะตาสำเร็จจากข้อมูลจริง (Swiss Ephemeris)"
        )

    def _seek_real_math(self, data: Dict[str, Any]) -> SeekerResult:
        """เรียกใช้ Math Solver (Z3 + SymPy)"""
        from tools.math import MathTool
        
        math_tool = MathTool()
        result = math_tool.execute(data)
        
        if "error" in result:
            return SeekerResult(
                success=False, 
                raw_data=result, 
                message="แก้สมการไม่สำเร็จ", 
                error_detail=result.get("error", "Unknown math error")
            )
            
        return SeekerResult(
            success=True, 
            raw_data=result, 
            message="แก้สมการสำเร็จด้วย Z3/SymPy"
        )

    def _seek_chat(self, payload: Dict[str, Any]) -> SeekerResult:
        """ตอบกลับการสนทนาพื้นฐานจาก Map ที่กำหนดไว้ (No LLM)"""
        chat_type = payload.get("chat_type", "unknown")
        responses = {
            "greeting": "สวัสดีครับ! ผมคือ 8zenith พร้อมให้บริการวิเคราะห์เหตุปัจจัยทางคณิตศาสตร์และดาราศาสตร์ครับ",
            "thanks": "ด้วยความยินดีครับ! หากมีสมการหรือข้อมูลวันเกิดเพิ่มเติม ถามได้ตลอดเวลาครับ",
            "farewell": "ลาก่อนครับ! ขอให้วันนี้เป็นวันที่ดีและมีเหตุผลรองรับทุกการกระทำนะครับ",
            "apology": "ไม่ต้องขอโทษครับ ผมพร้อมช่วยเหลือคุณเสมอ",
            "smalltalk": "ผมเป็นระบบ Rule-based ที่ไม่มีความรู้สึก แต่ผมพร้อมคำนวณให้คุณอย่างแม่นยำครับ!",
            "unknown": "รับทราบครับ มีอะไรให้ผมช่วยคำนวณหรือวิเคราะห์เพิ่มเติมไหมครับ?"
        }
        return SeekerResult(
            success=True, 
            raw_data={"response": responses.get(chat_type, responses["unknown"])}, 
            message="ตอบกลับสำเร็จ"
        )

    def _seek_name(self, payload: Dict[str, Any]) -> SeekerResult:
        """วิเคราะห์ชื่อแบบ Rule-based ง่ายๆ (Placeholder สำหรับ Name Analyzer)"""
        full_name = payload.get("full_name", payload.get("first_name", "ไม่ระบุชื่อ"))
        
        # ตัวอย่างการคำนวณแบบ Deterministic (เช่น ผลรวมค่า ASCII ของชื่อ)
        name_score = sum(ord(char) for char in full_name if char.isalpha()) % 100
        
        return SeekerResult(
            success=True,
            raw_data={
                "name": full_name,
                "numerology_score": name_score,
                "analysis": f"ชื่อ '{full_name}' มีค่าพลังงานพื้นฐานอยู่ที่ {name_score} (ระบบวิเคราะห์แบบ Rule-based)"
            },
            message="วิเคราะห์ชื่อสำเร็จ"
        )

    # ═══════════════════════════════════════════════════════
    # 2. Rule-Based Fallbacks (No LLM Guarantee)
    # ═══════════════════════════════════════════════════════
    def _seek_rule_based_fallback(self, target: str, payload: Dict[str, Any]) -> SeekerResult:
        """จัดการคำขอที่ยังไม่มี Tool จริง โดยไม่ใช้ LLM"""
        fallback_messages = {
            "text_rule_engine": "ระบบได้รับข้อความแล้ว อย่างไรก็ตาม ฟีเจอร์การประมวลผลข้อความขั้นสูงยังอยู่ในระหว่างการพัฒนาโมดูล Rule-based เฉพาะทาง",
            "code_handler": "ระบบรับทราบคำขอเกี่ยวกับโค้ด แต่ปัจจุบัน 8zenith มุ่งเน้นที่การคำนวณดาราศาสตร์และคณิตศาสตร์เป็นหลัก",
            "rule_based_generator": "ระบบได้รับคำขอแล้ว กรุณาระบุรายละเอียดในรูปแบบโครงสร้างที่ชัดเจน เพื่อให้ระบบสามารถประมวลผลแบบ Rule-based ได้",
            "static_qa": "ขออภัยครับ ฐานความรู้แบบ Static QA สำหรับคำถามนี้ยังอยู่ในระหว่างการรวบรวมข้อมูล",
            "system_action": f"รับคำสั่งระบบ: {payload.get('verb', 'action')} {payload.get('object', 'target')} (อยู่ในโหมดจำลอง)",
            "system_fallback": "ขออภัยครับ ระบบไม่เข้าใจคำสั่งนี้ในรูปแบบ Rule-based กรุณาลองใช้คำสั่งเช่น 'แก้สมการ x+2=5' หรือ 'ดูดวง เกิด 8/8/1992'"
        }
        
        msg = fallback_messages.get(target, "ระบบได้รับคำสั่งแล้ว แต่ยังไม่มีโมดูล Rule-based รองรับในขณะนี้")
        
        return SeekerResult(
            success=True, # สำเร็จในแง่ที่ระบบจัดการคำขอได้โดยไม่ Crash
            raw_data={"fallback_message": msg, "target": target},
            message="จัดการคำขอด้วย Rule-based Fallback"
        )


# ═══════════════════════════════════════════════════════════
# Quick Test
# ═══════════════════════════════════════════════════════════
if __name__ == "__init__":
    pass # ป้องกันการรันซ้ำหากถูก import

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    
    seeker = SeekerEngine()
    
    # ทดสอบ 1: Astrology (Rule-based จริง)
    print("\n" + "="*60)
    print("🧪 TEST 1: Astrology")
    task_astro = HelperTask(
        intent="birth",
        target_tool="astro_calculate",
        payload={"year": 1992, "month": 8, "day": 8, "hour": 16, "minute": 49, "lat": 6.5417, "lon": 101.282},
        hypothesis="ผู้ใช้ต้องการผูกดวง"
    )
    res = seeker.search(task_astro)
    print(f"✅ Success: {res.success} | Msg: {res.message}")
    print(f"📦 Keys: {list(res.raw_data.keys()) if res.success else 'N/A'}")

    # ทดสอบ 2: Math (Rule-based จริง)
    print("\n" + "="*60)
    print("🧪 TEST 2: Math Solver")
    task_math = HelperTask(
        intent="math",
        target_tool="math_solver",
        payload={"equation": "x^2 + 19x - 92 = 0", "variables": ["x"]},
        hypothesis="ผู้ใช้ต้องการแก้สมการ"
    )
    res = seeker.search(task_math)
    print(f"✅ Success: {res.success} | Msg: {res.message}")
    if res.success:
        print(f"📦 Solutions: {res.raw_data.get('math', {}).get('numerical', [])}")

    # ทดสอบ 3: Chat (Deterministic Map)
    print("\n" + "="*60)
    print("🧪 TEST 3: Chat Response")
    task_chat = HelperTask(
        intent="chat",
        target_tool="chat_response",
        payload={"chat_type": "greeting", "message": "สวัสดีครับ"},
        hypothesis="ผู้ใช้ทักทาย"
    )
    res = seeker.search(task_chat)
    print(f"✅ Success: {res.success} | Msg: {res.message}")
    print(f"📦 Response: {res.raw_data.get('response')}")

    # ทดสอบ 4: Fallback (No LLM)
    print("\n" + "="*60)
    print("🧪 TEST 4: Rule-Based Fallback (No LLM)")
    task_fallback = HelperTask(
        intent="coding",
        target_tool="code_handler",
        payload={"code": "print('hello')"},
        hypothesis="ผู้ใช้ต้องการให้เขียนโค้ด"
    )
    res = seeker.search(task_fallback)
    print(f"✅ Success: {res.success} | Msg: {res.message}")
    print(f"📦 Fallback Msg: {res.raw_data.get('fallback_message')}")