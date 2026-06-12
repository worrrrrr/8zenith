"""
8zenith Orchestrator — ผู้ประสานงาน Pipeline
================================================================
รับข้อความดิบ → ส่งผ่าน 5 ด่าน → คืนผลลัพธ์สุดท้าย
หลักการ: จัดการ Flow การทำงานทั้งหมดโดยไม่พึ่งพา LLM ในขั้นตอนหลัก

Dependency: engines.observer, engines.helper, engines.seeker, engines.protector, engines.integrator
"""

from engines.observer import ObserverEngine
from engines.helper import HelperEngine
from engines.seeker import SeekerEngine
from engines.protector import ProtectorEngine
from engines.integrator import IntegratorEngine


# ═══════════════════════════════════════════════════════════════
# Orchestrator Engine
# ═══════════════════════════════════════════════════════════════

class Orchestrator:
    """สมองกลาง: ประสานงาน Council of 5 Pipeline"""

    def __init__(self):
        self.observer = ObserverEngine(confidence_threshold=15.0)
        self.helper = HelperEngine()
        self.seeker = SeekerEngine()
        self.protector = ProtectorEngine()
        self.integrator = IntegratorEngine()

    def process(self, user_input: str) -> str:
        """กระบวนการหลัก: รับ String → ส่งผ่าน 5 ด่าน → คืน String"""
        print(f"📥 [1. Observer] รับข้อมูล: {user_input}")
        obs = self.observer.observe(user_input)
        if obs.intent == "unknown":
            return "❌ ขออภัยครับ ระบบไม่เข้าใจคำสั่งของคุณ กรุณาระบุให้ชัดเจนยิ่งขึ้น"
        print(f"   ✅ Intent: {obs.intent} (Confidence: {obs.confidence})")

        print(f"📥 [2. Helper] กำหนดภารกิจ...")
        task = self.helper.dispatch(obs)
        print(f"   ✅ Target: {task.target_tool} | Hypothesis: {task.hypothesis}")

        print(f"📥 [3. Seeker] กำลังคำนวณ/ค้นหาจริง...")
        seeker_res = self.seeker.search(task)
        if not seeker_res.success:
            print(f"   ⚠️ Seeker ล้มเหลว: {seeker_res.error_detail}")

        print(f"📥 [4. Protector] กำลังตรวจสอบความถูกต้อง...")
        prot_res = self.protector.validate(seeker_res)
        if not prot_res.is_valid:
            print(f"   ⚠️ Protector ปฏิเสธ: {prot_res.warning}")

        print(f"📥 [5. Integrator] กำลังรวบรวมคำตอบสุดท้าย...")
        return self.integrator.assemble(obs, prot_res)


# ═══════════════════════════════════════════════════════════════
# Quick Test
# ═══════════════════════════════════════════════════════════════
if __name__ == "__main__":
    orch = Orchestrator()
    result = orch.process("ดูดวงให้หน่อย เกิด 8/8/1992 16:49 ยะลา")
    print("\n" + "="*60)
    print(result)
    print("="*60)