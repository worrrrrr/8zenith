"""
8zenith Integrator Engine — ผู้รวบรวมและจัดรูปแบบ (The Formatter)
================================================================
รับข้อมูลที่ผ่านการตรวจสอบ → จัดรูปแบบสวยงาม (หรือจัดการ Fallback หากล้มเหลว)
หลักการ: จัดกล่องบรรจุภัณฑ์ให้เรียบร้อย หากข้อมูลเสีย ต้องวิเคราะห์รากเหง้าและตอบกลับอย่างสุภาพ

Dependency: engines.observer, engines.protector, tools.astro_translate
"""

from engines.protector import ProtectionResult
from engines.observer import ObservationResult


# ═══════════════════════════════════════════════════════════════
# Integrator Engine
# ═══════════════════════════════════════════════════════════════

class IntegratorEngine:
    """นักจัดรูปแบบและจัดการความล้มเหลว: รวบรวมข้อมูลและสร้างคำตอบสุดท้าย"""

    def assemble(self, obs: ObservationResult, prot: ProtectionResult) -> str:
        if prot.is_valid:
            return self._format_success(obs.intent, prot.validated_data)
        else:
            return self._format_fallback(obs, prot)

    def _format_success(self, intent: str, data: dict) -> str:
        if intent in ["birth", "astrology"]:
            return self._format_astro_reading(data)
        elif intent == "chat":
            return data.get("response", "สวัสดีครับ")
        return "✅ ประมวลผลสำเร็จ"

    def _format_astro_reading(self, data: dict) -> str:
        """จัดรูปแบบ Dictionary จริงจาก full_reading() ให้สวยงาม"""
        core = data.get("core_motivation", {})
        mission = data.get("mission_phase", {})
        lens = data.get("cognitive_lens", {})
        sig = data.get("cosmic_signature", {})
        vh = data.get("visible_vs_hidden", {})
        houses = data.get("house_readings", [])
        aspects = data.get("aspect_readings", [])[:5]

        lines = [
            "=" * 70,
            "📜 คัมภีร์แปดทิศ — การอ่านชะตาฟ้าลิขิต (The Celestial Decree)",
            "=" * 70,
            f"\n🌕 พลังปราณหลัก: {core.get('drive', 'N/A')} {core.get('emoji', '🪐')}",
            f"   ดวงดาวนำโชค: {core.get('planet_th', 'N/A')} (พลังลมปราณ: {core.get('tidal_force', 0):.2e})",
            f"   {core.get('description', 'N/A')}",
            f"\n🌓 วิถีแห่งฟ้าลิขิต: {mission.get('phase', 'N/A')}",
            f"   {mission.get('description', 'N/A')}",
            f"   🧩 แนวโน้ม: {mission.get('enneagram_hint', 'N/A')}",
            f"\n🌅 ธาตุประจำกายและจิต: {lens.get('lens', 'N/A')}",
            f"   {lens.get('description', 'N/A')}",
            f"   🧩 แนวโน้มการคิด: {lens.get('mbti_hint', 'N/A')}",
            f"\n✨ ตราสัญลักษณ์แห่งสวรรค์: {sig.get('signature', 'N/A')}",
        ]

        if houses:
            lines.append("\n🏯 ดวงดาวสถิตในตำหนักสำคัญ:")
            for hr in houses:
                lines.append(f"🏯 {hr['planet_th']} สถิตใน{hr['house_th']} — {hr['meaning']}")

        if aspects:
            lines.append("\n💫 สัมพันธภาพแห่งดวงดาว (Key Aspects):")
            for a in aspects:
                lines.append(f"💫 {a['symbol']} {a['planet1_th']} — {a['planet2_th']}: {a['interpretation']}")

        lines.extend([
            f"\n👁️ พลังหยาง (รู้ตัว): {', '.join(vh.get('visible', []))}",
            f"🌑 พลังหยิน (ซ่อนเร้น): {', '.join(vh.get('hidden', []))}",
            f"💡 {vh.get('insight', '')}",
            "\n" + "=" * 70,
            "✅ การถอดรหัสคัมภีร์เสร็จสมบูรณ์",
            "⚠️ นี่มิใช่ 'คำทำนาย' — หากแต่คือ 'การวิเคราะห์เหตุปัจจัยแห่งฟ้าดิน'",
            "=" * 70
        ])
        return "\n".join(lines)

    def _format_fallback(self, obs: ObservationResult, prot: ProtectionResult) -> str:
        """จัดการเมื่อข้อมูลไม่ครบหรือระบบล้มเหลว (Root Cause Analysis)"""
        raw = obs.cleaned_data
        if obs.intent in ["birth", "astrology"]:
            missing = [k for k in ["year", "month", "day", "hour"] if k not in raw]
            if missing:
                return f"⚠️ ขออภัยครับ ระบบไม่สามารถผูกดวงได้เนื่องจากข้อมูลไม่ครบถ้วน\n👉 กรุณาระบุ: {', '.join(missing)} (เช่น 'เกิด 8/8/1992 16:49 ยะลา')"
        
        return f"❌ เกิดข้อผิดพลาดในการประมวลผล: {prot.warning}\n📊 ข้อมูลดิบ: {raw}"


# ═══════════════════════════════════════════════════════════════
# Quick Test
# ═══════════════════════════════════════════════════════════════
if __name__ == "__main__":
    from engines.observer import ObservationResult
    from engines.protector import ProtectionResult
    
    obs = ObservationResult("birth", 0.9, {"year": 1992, "month": 8, "day": 8, "hour": 16})
    prot = ProtectionResult(False, {}, "ข้อมูลไม่ครบ")
    
    integrator = IntegratorEngine()
    print(integrator.assemble(obs, prot))