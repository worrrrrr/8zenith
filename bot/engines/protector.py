"""
8zenith Protector Engine — ผู้ตรวจสอบความถูกต้อง (The Validator)
================================================================
รับผลลัพธ์จาก Seeker → ตรวจสอบความสมเหตุสมผลและความปลอดภัย → อนุญาตหรือปฏิเสธ
หลักการ: ป้องกันข้อมูลขยะหรือ Error จากระบบส่งต่อไปยังผู้ใช้

Dependency: engines.seeker
"""

from dataclasses import dataclass
from typing import Dict, Any, Optional
from engines.seeker import SeekerResult


# ═══════════════════════════════════════════════════════════════
# Data Structures
# ═══════════════════════════════════════════════════════════════

@dataclass
class ProtectionResult:
    """ผลลัพธ์จากการตรวจสอบ"""
    is_valid: bool
    validated_data: Dict[str, Any]
    warning: Optional[str] = None


# ═══════════════════════════════════════════════════════════════
# Protector Engine
# ═══════════════════════════════════════════════════════════════

class ProtectorEngine:
    """ผู้พิทักษ์: ตรวจสอบความถูกต้องของข้อมูลจาก Seeker"""

    def validate(self, seeker_result: SeekerResult) -> ProtectionResult:
        if not seeker_result.success:
            return ProtectionResult(False, {}, seeker_result.error_detail or seeker_result.message)

        data = seeker_result.raw_data
        
        # กฎการตรวจสอบ (Validation Rules)
        if "dominant_planet" in data:
            if data["dominant_planet"].get("planet") == "unknown":
                return ProtectionResult(False, {}, "ระบบไม่สามารถคำนวณดาวเด่นได้ ข้อมูลอาจไม่ถูกต้อง")
        
        if "birth_info" in data:
            dt_str = data["birth_info"].get("datetime", "")
            if not dt_str or len(dt_str) < 4:
                return ProtectionResult(False, {}, "ข้อมูลวันเวลาเกิดไม่ถูกต้องหรือเสียหาย")

        if "response" in data:
            bad_words = ["หยาบ", "แย่", "โง่"]
            if any(word in str(data["response"]) for word in bad_words):
                return ProtectionResult(False, {}, "เนื้อหาไม่เหมาะสม")

        return ProtectionResult(True, data, None)


# ═══════════════════════════════════════════════════════════════
# Quick Test
# ═══════════════════════════════════════════════════════════════
if __name__ == "__main__":
    from engines.seeker import SeekerResult
    valid_res = SeekerResult(True, {"dominant_planet": {"planet": "moon"}, "birth_info": {"datetime": "1992-08-08 16:49:00"}}, "OK")
    invalid_res = SeekerResult(False, {}, "Fail", "Error detail")
    
    protector = ProtectorEngine()
    print("Valid Test:", protector.validate(valid_res).is_valid)
    print("Invalid Test:", protector.validate(invalid_res).is_valid, "-", protector.validate(invalid_res).warning)