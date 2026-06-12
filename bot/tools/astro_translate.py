"""
8zenith Astro Translate Engine — The Orbital Reader
=====================================================
แปลข้อมูลทางดาราศาสตร์จาก AstroCalculate เป็นภาษามนุษย์
พร้อมระบบ Human-in-the-Loop สำหรับตรวจสอบและปรับปรุง

หลักการ: เราไม่ทำนายอนาคต — เราวิเคราะห์เหตุปัจจัย (Idappaccayatā)
"""

from typing import Dict, List, Optional, Tuple
from datetime import datetime
from tools.astro_calculate import AstroCalculate, PLANET_NAMES, HOUSE_NAMES_TH

# ═══════════════════════════════════════════════════════════════
# ฐานความรู้สำหรับการแปล
# ═══════════════════════════════════════════════════════════════

# แรงขับเคลื่อนจากดาวเด่น
DRIVE_MAP = {
    "moon": {
        "drive": "อารมณ์และสัญชาตญาณ",
        "description": "ถูกขับเคลื่อนด้วยความรู้สึกลึกๆ และสัญชาตญาณ ตัดสินใจด้วยหัวใจมากกว่าเหตุผล",
        "element": "น้ำ",
        "emoji": "🌙"
    },
    "sun": {
        "drive": "เจตจำนงและตัวตน",
        "description": "ถูกขับเคลื่อนด้วยความต้องการแสดงออกและสร้างผลงานที่สะท้อนตัวตน",
        "element": "ไฟ",
        "emoji": "☀️"
    },
    "mars": {
        "drive": "การลงมือและพลัง",
        "description": "ถูกขับเคลื่อนด้วยแรงปรารถนาที่จะพุ่งชนและลงมือทำทันที",
        "element": "ไฟ",
        "emoji": "🔥"
    },
    "jupiter": {
        "drive": "การเติบโตและความหมาย",
        "description": "ถูกขับเคลื่อนด้วยการแสวงหาความรู้และขยายขอบเขตชีวิต",
        "element": "อากาศ",
        "emoji": "🍀"
    },
    "saturn": {
        "drive": "วินัยและความรับผิดชอบ",
        "description": "ถูกขับเคลื่อนด้วยการสร้างโครงสร้างและรักษากฎเกณฑ์",
        "element": "ดิน",
        "emoji": "⛰️"
    },
    "mercury": {
        "drive": "การสื่อสารและการเรียนรู้",
        "description": "ถูกขับเคลื่อนด้วยการแลกเปลี่ยนข้อมูลและการวิเคราะห์",
        "element": "อากาศ",
        "emoji": "🧠"
    },
    "venus": {
        "drive": "ความรักและความงาม",
        "description": "ถูกขับเคลื่อนด้วยการสร้างความสัมพันธ์และแสวงหาความสุขทางสุนทรียะ",
        "element": "ดิน",
        "emoji": "💖"
    },
}

# ภารกิจชีวิตจากมุมอาทิตย์-จันทร์
MISSION_MAP = [
    (0, "🌑 New Moon — ผู้ริเริ่ม (Initiator)",
     "เกิดมาเพื่อเริ่มต้นสิ่งใหม่ๆ เป็นผู้จุดประกาย",
     "Type 7 (Enthusiast) หรือ Type 8 (Challenger)"),
    (45, "🌒 Crescent — ผู้ใฝ่รู้ (Learner)",
     "เกิดมาเพื่อเรียนรู้และสะสมประสบการณ์",
     "Type 4 (Individualist) หรือ Type 5 (Investigator)"),
    (90, "🌓 First Quarter — นักสร้างและนักแก้ไข (Builder/Solver)",
     "เกิดมาเพื่อลงมือทำและเผชิญหน้ากับอุปสรรค",
     "Type 1 (Reformer) หรือ Type 5 (Investigator)"),
    (135, "🌔 Gibbous — นักปรับปรุง (Refiner)",
     "เกิดมาเพื่อวิเคราะห์และทำให้ดีขึ้น",
     "Type 1 (Reformer) หรือ Type 8 (Protector)"),
    (180, "🌕 Full Moon — ผู้เปิดเผย (Revealer)",
     "เกิดมาเพื่อแสดงออกและแบ่งปันอย่างเต็มที่",
     "Type 2 (Helper) หรือ Type 9 (Peacemaker)"),
]

# เลนส์มองโลกจากลัคนา
LENS_MAP = [
    (0, "นักวิเคราะห์และผู้นำ",
     "มองโลกด้วยสายตาที่ต้องการเข้าใจระบบและโครงสร้าง",
     "NT (Intuitive-Thinking) หรือ NF (Intuitive-Feeling)", "ไฟ"),
    (90, "นักสำรวจและผู้สร้างสรรค์",
     "มองโลกด้วยสายตาที่มองเห็นความเป็นไปได้และความงาม",
     "SP (Sensing-Perceiving) หรือ NF (Intuitive-Feeling)", "น้ำ"),
    (180, "นักสืบสวนและผู้ปรับสมดุล",
     "มองโลกด้วยสายตาที่เจาะลึกและตั้งคำถามกับทุกสิ่ง",
     "NT (Intuitive-Thinking) หรือ NF (Intuitive-Feeling)", "อากาศ"),
    (270, "ผู้พิทักษ์และผู้รักษากฎ",
     "มองโลกด้วยสายตาที่ให้ค่ากับความมั่นคงและความถูกต้อง",
     "SJ (Sensing-Judging) หรือ NF (Intuitive-Feeling)", "ดิน"),
]

# ความหมายของดาวเคราะห์ในแต่ละภพ
PLANET_IN_HOUSE_MEANING = {
    "sun": {
        1: "ตัวตนที่แข็งแกร่ง — เกิดมาเพื่อเป็นผู้นำ",
        4: "ตัวตนที่แท้จริงผูกพันกับครอบครัว — รากฐานคือพลัง",
        7: "ค้นพบตัวเองผ่านความสัมพันธ์ — คู่ครองคือกระจกสะท้อน",
        10: "เกิดมาเพื่อสร้างชื่อเสียง — การงานคือเวทีแห่งชีวิต",
    },
    "moon": {
        1: "อารมณ์เป็นตัวนำ — ใช้ความรู้สึกในการตัดสินใจ",
        4: "ความสุขมาจากครอบครัว — บ้านคือที่ชาร์จพลัง",
        8: "อารมณ์ลึกซึ้ง — เกิดมาเพื่อเข้าใจการเกิด-ดับของทุกสิ่ง",
        12: "จิตใต้สำนึกทรงพลัง — ต้องมีเวลาอยู่กับตัวเอง",
    },
    "mars": {
        1: "พลังนักรบติดตัว — เกิดมาเพื่อปกป้องและลงมือทำ",
        3: "สื่อสารด้วยพลัง — คำพูดคืออาวุธ",
        5: "พลังสร้างสรรค์ล้นเหลือ — ทุ่มเทให้กับงานที่รัก",
        10: "นักสู้ในสนามอาชีพ — การงานต้องท้าทาย",
    },
    "jupiter": {
        5: "ความคิดสร้างสรรค์ยิ่งใหญ่ — เกิดมาเพื่อสร้างอะไรบางอย่าง",
        9: "แสวงหาความจริง — ปรัชญาคือเข็มทิศชีวิต",
        10: "ความสำเร็จมาจากความรู้ — ครูหรือที่ปรึกษา",
    },
    "saturn": {
        1: "วินัยคือตัวตน — จริงจังกับชีวิตตั้งแต่เกิด",
        10: "การงานมั่นคง — สร้างเนื้อสร้างตัวด้วยความอดทน",
    },
    "uranus": {
        9: "ปฏิวัติทางความคิด — แหกกฎเพื่อค้นพบความจริงใหม่",
    },
    "neptune": {
        9: "จิตวิญญาณลึกซึ้ง — เชื่อมต่อกับสิ่งที่มองไม่เห็น",
    },
    "pluto": {
        7: "ความสัมพันธ์เปลี่ยนแปลงชีวิต — คู่ครองนำพาการเกิดใหม่",
    },
}

# ความหมายของมุมสัมพันธ์
ASPECT_MEANING = {
    "Conjunction": "สองแรงหลอมรวมเป็นหนึ่ง — พลังงานที่ทรงพลังที่สุด",
    "Sextile": "โอกาสที่เปิดกว้าง — ประตูที่รอให้คุณเดินเข้าไป",
    "Square": "แรงเสียดทานที่ผลักดันให้เติบโต — ความท้าทายที่สร้างความแข็งแกร่ง",
    "Trine": "พลังงานไหลลื่นอย่างเป็นธรรมชาติ — พรสวรรค์ที่ติดตัวมา",
    "Opposition": "การเผชิญหน้าที่นำไปสู่สมดุล — ต้องเรียนรู้ที่จะประนีประนอม",
}


class AstroTranslate:
    """ตัวแปลแรงโน้มถ่วงเป็นภาษามนุษย์"""

    def __init__(self, calc: AstroCalculate):
        self.calc = calc
        self.summary = calc.get_summary()

    # ═══════════════════════════════════════════════════════════
    # 1. แกนหลัก — The Core Reading
    # ═══════════════════════════════════════════════════════════
    def core_motivation(self) -> dict:
        """แปลดาวเด่น → แรงขับเคลื่อนหลัก"""
        dom_name, dom_force = self.calc.dominant_planet()
        info = DRIVE_MAP.get(dom_name, {
            "drive": f"พลังงานของ{PLANET_NAMES.get(dom_name, dom_name)}",
            "description": f"ถูกขับเคลื่อนด้วยพลังงานของ{PLANET_NAMES.get(dom_name, dom_name)}",
            "element": "unknown",
            "emoji": "🪐"
        })
        return {
            "planet": dom_name,
            "planet_th": PLANET_NAMES.get(dom_name, dom_name),
            "tidal_force": dom_force,
            **info
        }

    def mission_phase(self) -> dict:
        """แปลมุมอาทิตย์-จันทร์ → ภารกิจชีวิต"""
        angle = self.calc.aspect_angle("sun", "moon")
        if angle is None:
            return {"phase": "unknown", "description": "ไม่สามารถคำนวณได้"}

        result = MISSION_MAP[-1]  # default: Full Moon
        for threshold, phase, desc, ennea in MISSION_MAP:
            if angle < threshold:
                break
            result = (threshold, phase, desc, ennea)

        return {
            "phase": result[1],
            "description": result[2],
            "enneagram_hint": result[3],
            "angle": angle,
            "emoji": result[1].split()[0]
        }

    def cognitive_lens(self) -> dict:
        """แปลลัคนา → เลนส์มองโลก"""
        asc = self.calc.get_ascendant()
        if asc is None:
            return {"lens": "unknown", "description": "ไม่สามารถคำนวณได้"}

        result = LENS_MAP[-1]  # default
        for threshold, lens, desc, mbti, element in LENS_MAP:
            if asc < threshold:
                break
            result = (threshold, lens, desc, mbti, element)

        return {
            "lens": result[1],
            "description": result[2],
            "mbti_hint": result[3],
            "element": result[4],
            "ascendant": asc
        }

    # ═══════════════════════════════════════════════════════════
    # 2. วิเคราะห์ภพ — Where the Energy Lives
    # ═══════════════════════════════════════════════════════════
    def house_readings(self) -> List[dict]:
        """อ่านความหมายของดาวเคราะห์ในแต่ละภพ"""
        readings = []
        for planet_name in self.calc._planet_data:
            house = self.calc.get_planet_house(planet_name)
            if house is None:
                continue
            meaning = PLANET_IN_HOUSE_MEANING.get(planet_name, {}).get(house)
            if meaning:
                readings.append({
                    "planet": planet_name,
                    "planet_th": PLANET_NAMES.get(planet_name, planet_name),
                    "house": house,
                    "house_th": HOUSE_NAMES_TH[house],
                    "meaning": meaning
                })
        return readings

    def visible_vs_hidden(self) -> dict:
        """วิเคราะห์สิ่งที่รู้ตัว vs จิตใต้สำนึก"""
        visible = self.summary.get("visible_planets", [])
        hidden = self.summary.get("hidden_planets", [])
        total = len(visible) + len(hidden)
        conscious_pct = round(len(visible) / total * 100) if total > 0 else 0

        return {
            "visible": [PLANET_NAMES.get(p, p) for p in visible],
            "hidden": [PLANET_NAMES.get(p, p) for p in hidden],
            "conscious_percentage": conscious_pct,
            "insight": (
                f"คุณรู้ตัวเพียง {conscious_pct}% ของพลังทั้งหมดที่มี — "
                f"อีก {100-conscious_pct}% ทำงานในจิตใต้สำนึก (Shadow)"
            )
        }

    # ═══════════════════════════════════════════════════════════
    # 3. มุมสัมพันธ์ — The Cosmic Conversations
    # ═══════════════════════════════════════════════════════════
    def aspect_readings(self, orb: float = 8.0) -> List[dict]:
        """แปลมุมสัมพันธ์เป็นภาษามนุษย์"""
        aspects = self.calc.get_all_aspects(orb)
        readings = []
        for a in aspects:
            readings.append({
                **a,
                "interpretation": ASPECT_MEANING.get(a["aspect"], ""),
                "narrative": (
                    f"{a['planet1_th']} กับ {a['planet2_th']} "
                    f"ทำมุม {a['aspect']} ({a['symbol']}) ที่ {a['angle']}° — "
                    f"{ASPECT_MEANING.get(a['aspect'], '')}"
                )
            })
        return readings

    # ═══════════════════════════════════════════════════════════
    # 4. Cosmic Signature (4 Emoji)
    # ═══════════════════════════════════════════════════════════
    def cosmic_signature(self) -> dict:
        """สร้าง Cosmic Signature 4 Emoji จากข้อมูลทั้งหมด"""
        core = self.core_motivation()
        mission = self.mission_phase()
        lens = self.cognitive_lens()

        human_map = {
            "moon": "😊", "sun": "😎", "mars": "😤",
            "jupiter": "🤓", "saturn": "😐", "mercury": "😏", "venus": "😍"
        }
        mission_map = {
            "🌑": "🌱", "🌒": "🔍", "🌓": "🚀", "🌔": "🔧", "🌕": "🌟"
        }
        power_map = {"ไฟ": "🐉", "น้ำ": "🐋", "อากาศ": "🦅", "ดิน": "🐂"}

        emoji_1 = human_map.get(core["planet"], "😶")
        emoji_2 = mission_map.get(mission["emoji"], "🛤️")
        emoji_3 = power_map.get(lens["element"], "💎")

        angle = mission.get("angle", 0)
        if 90 <= angle < 135:
            emoji_4 = "✨"
        elif 135 <= angle < 180:
            emoji_4 = "💡"
        else:
            emoji_4 = "🌟"

        signature = f"{emoji_1}{emoji_2}{emoji_3}{emoji_4}"

        return {
            "signature": signature,
            "breakdown": {
                "1_human": emoji_1,
                "2_mission": emoji_2,
                "3_power": emoji_3,
                "4_awakening": emoji_4
            },
            "meaning": {
                emoji_1: "ตัวตนและแรงขับเคลื่อน",
                emoji_2: "ภารกิจและเส้นทางชีวิต",
                emoji_3: "พลังภายในและสัญชาตญาณ",
                emoji_4: "การตื่นรู้และศักยภาพสูงสุด"
            }
        }

    # ═══════════════════════════════════════════════════════════
    # 5. Full Reading
    # ═══════════════════════════════════════════════════════════
    def full_reading(self, events: List[Tuple[str, str]] = None) -> dict:
        """อ่านดวงแบบสมบูรณ์"""
        result = {
            "birth_info": self.summary["birth"],
            "core_motivation": self.core_motivation(),
            "mission_phase": self.mission_phase(),
            "cognitive_lens": self.cognitive_lens(),
            "cosmic_signature": self.cosmic_signature(),
            "house_readings": self.house_readings(),
            "visible_vs_hidden": self.visible_vs_hidden(),
            "aspect_readings": self.aspect_readings(),
            "dominant_planet": self.summary["dominant"],
        }
        return result

    def print_reading(self):
        """พิมพ์ผลอ่านดวง"""
        reading = self.full_reading()
        core = reading["core_motivation"]
        mission = reading["mission_phase"]
        lens = reading["cognitive_lens"]
        sig = reading["cosmic_signature"]
        vh = reading["visible_vs_hidden"]

        print("=" * 70)
        print("🔮 8zenith — The Orbital Reading")
        print("=" * 70)

        # 1. Core Motivation
        print(f"\n🌕 แรงขับเคลื่อนหลัก: {core['drive']} {core['emoji']}")
        print(f"   ดาวเด่น: {core['planet_th']} (Tidal Force: {core['tidal_force']:.2e})")
        print(f"   {core['description']}")

        # 2. Mission Phase
        print(f"\n🌓 ภารกิจชีวิต: {mission['phase']}")
        print(f"   {mission['description']}")
        print(f"   🧩 แนวโน้ม Enneagram: {mission['enneagram_hint']}")

        # 3. Cognitive Lens
        print(f"\n🌅 เลนส์มองโลก: {lens['lens']}")
        print(f"   {lens['description']}")
        print(f"   🧩 แนวโน้ม MBTI: {lens['mbti_hint']}")

        # 4. Cosmic Signature
        print(f"\n✨ Cosmic Signature: {sig['signature']}")
        bd = sig["breakdown"]
        meaning = sig["meaning"]
        print(f"   {bd['1_human']} = {meaning[bd['1_human']]}")
        print(f"   {bd['2_mission']} = {meaning[bd['2_mission']]}")
        print(f"   {bd['3_power']} = {meaning[bd['3_power']]}")
        print(f"   {bd['4_awakening']} = {meaning[bd['4_awakening']]}")

        # 5. Visible vs Hidden
        print(f"\n👁️ {'='*50}")
        print(f"👁️ Visible (เหนือขอบฟ้า — คุณรู้ตัว): {', '.join(vh['visible'])}")
        print(f"🌑 Hidden  (ใต้ขอบฟ้า — จิตใต้สำนึก): {', '.join(vh['hidden'])}")
        print(f"💡 {vh['insight']}")

        # 6. House Readings
        print(f"\n🏠 {'='*50}")
        print(f"🏠 ดาวเคราะห์ในภพที่สำคัญ:")
        for hr in reading["house_readings"]:
            print(f"🏠 {hr['planet_th']} ใน{hr['house_th']} — {hr['meaning']}")

        # 7. Key Aspects
        aspects = reading["aspect_readings"]
        if aspects:
            print(f"\n💫 {'='*50}")
            print(f"💫 มุมสัมพันธ์สำคัญ (Key Aspects):")
            for a in aspects[:5]:
                print(f"💫 {a['symbol']} {a['planet1_th']} — {a['planet2_th']}: {a['interpretation']}")

        print(f"\n{'='*70}")
        print("✅ การวิเคราะห์เสร็จสมบูรณ์")
        print(f"⚠️ นี่ไม่ใช่ 'คำทำนาย' — แต่มันคือ 'การวิเคราะห์เหตุปัจจัย' (Idappaccayatā)")
        print(f"🤔 Human-in-the-Loop: คุณรู้สึกว่ามัน 'ตรง' กับชีวิตคุณไหม?")
        print(f"{'='*70}")

    # ═══════════════════════════════════════════════════════════
    # 6. Human-in-the-Loop
    # ═══════════════════════════════════════════════════════════
    def ask_human(self, question: str, expected: str = "") -> dict:
        """ถามมนุษย์เพื่อตรวจสอบ"""
        print(f"\n🤔 Human-in-the-Loop:")
        print(f"   {question}")
        if expected:
            print(f"   (คาดการณ์: {expected})")
        answer = input("   ✅ Yes / ❌ No / 📝 Comment: ").strip()
        return {"question": question, "expected": expected, "answer": answer}


# ═══════════════════════════════════════════════════════════════
# Quick Test
# ═══════════════════════════════════════════════════════════════
if __name__ == "__main__":
    from datetime import datetime
    from tools.astro_calculate import AstroCalculate

    calc = AstroCalculate(datetime(1992, 8, 8, 16, 49), 6.5417, 101.282)
    reader = AstroTranslate(calc)
    reader.print_reading()