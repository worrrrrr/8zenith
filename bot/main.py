"""
8zenith Main Entry Point — Interactive Mode
================================================================
ประตูหน้าของระบบ: รับ Input จากผู้ใช้ → ส่งให้ Orchestrator → แสดงผล
หลักการ: เป็นจุดเริ่มต้นเดียว (Single Entry Point) ที่สะอาดและใช้งานง่าย
         รองรับ Interactive Mode (คุยต่อเนื่องได้)

Dependency: core.orchestrator, sys
"""

import sys
from core.orchestrator import Orchestrator


# ═══════════════════════════════════════════════════════════════
# Main Execution
# ═══════════════════════════════════════════════════════════════

def main():
    """ฟังก์ชันหลักในการเริ่มทำงานของระบบ (Interactive Loop)"""
    orch = Orchestrator()
    
    print("=" * 60)
    print("🔮 8zenith — ระบบวิเคราะห์เหตุปัจจัยแห่งฟ้าดิน")
    print("   พิมพ์ 'exit' หรือ 'quit' เพื่อออก")
    print("=" * 60)
    
    # Interactive Loop — คุยต่อเนื่องได้จนกว่าจะขอออก
    while True:
        print()  # เว้นบรรทัด
        user_input = input("🔮 8zenith > ").strip()
        
        # ตรวจสอบคำสั่งออก
        if user_input.lower() in ["exit", "quit", "ออก", "q"]:
            print("\n👋 ลาก่อนครับท่านวอ แล้วพบกันใหม่")
            break
        
        # ถ้าไม่ป้อนอะไรเลย → ข้ามไป
        if not user_input:
            continue
        
        # ประมวลผลและแสดงผลลัพธ์
        try:
            response = orch.process(user_input)
            print("\n" + "-" * 60)
            print(response)
            print("-" * 60)
        except Exception as e:
            print(f"\n⚠️ เกิดข้อผิดพลาดที่ไม่คาดคิด: {e}")
            print("   กรุณาลองใหม่อีกครั้ง")


if __name__ == "__main__":
    main()