"""
8zenith Observer Engine — Production Ready (Extended Edition)
============================================
ด่านแรกของ Council of 5 Pipeline
รับข้อความดิบ → วิเคราะห์ Intent → สกัดข้อมูล → ส่งต่อ Helper

หลักการ:
- Weighted Scoring: ไม่ใช่ if-else ตายตัว แต่ให้คะแนนทุก intent แล้วเลือกคะแนนสูงสุด
- Second-Pass Validation: ตรวจสอบซ้ำว่า intent ที่เลือกไม่ "กลืน" intent อื่น
- Confidence Threshold: ถ้าคะแนนต่ำกว่า threshold → unknown
- Extended Intents: รองรับการใช้งานจริง 20 ประเภท
"""

import re
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field


# ═══════════════════════════════════════════════════════════════
# Data Structures
# ═══════════════════════════════════════════════════════════════

@dataclass
class ObservationResult:
    """ผลลัพธ์จาก Observer"""
    intent: str                          # Intent ที่ตรวจจับได้
    confidence: float                     # 0.0 - 1.0
    cleaned_data: dict = field(default_factory=dict)
    all_scores: dict = field(default_factory=dict)
    warning: Optional[str] = None


# ═══════════════════════════════════════════════════════════════
# Intent Scoring Rules (Extended Edition)
# ═══════════════════════════════════════════════════════════════

# -- 1. Math Problem -------------------------------------------------
MATH_PATTERNS = [
    (r"=", 15, "สมการ"),
    (r"\^|\*\*", 10, "เลขยกกำลัง"),
    (r"[+\-*/%]", 5, "ตัวดำเนินการ"),
    (r"\b[x-zX-Z]\b", 10, "ตัวแปร"),
]
MATH_STARTS_WITH = ("math,",)
MATH_KEYWORDS = ["แก้สมการ", "สมการ", "คำนวณ", "หาค่า", "แก้โจทย์", "proof", "prove"]

# -- 2. Birth Info ---------------------------------------------------
BIRTH_DATE_PATTERNS = [
    (r"\d{1,2}/\d{1,2}/\d{4}", 25),
    (r"\d{4}-\d{2}-\d{2}", 25),
    (r"\d{1,2}\s*(มกราคม|กุมภาพันธ์|มีนาคม|เมษายน|พฤษภาคม|มิถุนายน|กรกฎาคม|สิงหาคม|กันยายน|ตุลาคม|พฤศจิกายน|ธันวาคม)\s*\d{4}", 25),
]
BIRTH_TIME_PATTERNS = [
    (r"\d{1,2}[:.]\d{2}", 15),
]
BIRTH_KEYWORDS = ["เกิด", "วันเกิด", "เวลาเกิด", "สถานที่เกิด", "birth"]

# -- 3. Astrology Question -------------------------------------------
ASTROLOGY_KEYWORDS = [
    "ดูดวง", "พยากรณ์", "ดวงชะตา", "โหราศาสตร์", "หมอดู",
    "bazi", "ba zi", "numerology", "mbti", "enneagram",
    "human design", "สี่เสา", "เลขศาสตร์",
]

# -- 4. Name Analysis ------------------------------------------------
NAME_PREFIXES = ["นาย", "นางสาว", "นาง", "เด็กชาย", "เด็กหญิง"]
NAME_KEYWORDS = ["ชื่อ", "นามสกุล", "ตั้งชื่อ", "เปลี่ยนชื่อ", "ความหมายชื่อ", "วิเคราะห์ชื่อ"]

# -- 5. Chat/Conversation (NEW) --------------------------------------
CHAT_GREETINGS = ["สวัสดี", "หวัดดี", "ดีครับ", "ดีค่ะ", "hello", "hi", "hey", "sa-wat-dee"]
CHAT_THANKS = ["ขอบคุณ", "ขอบใจ", "thanks", "thank you", "thx", "ขอบคุณมาก"]
CHAT_APOLOGY = ["ขอโทษ", "โทษที", "sorry", "apologize", "เสียใจ"]
CHAT_FAREWELL = ["บอกลา", "ลาก่อน", "bye", "goodbye", "see you", "ไว้เจอกัน"]
CHAT_SMALLTALK = ["สบายดีไหม", "เป็นอย่างไร", "how are you", "what's up", "ทำอะไรอยู่"]

# -- 6. Information Query (NEW) --------------------------------------
INFO_QUERY_STARTS = ["อะไรคือ", "คืออะไร", "ใครคือ", "ที่ไหน", "เมื่อไหร่", "ทำไม", "อย่างไร"]
INFO_QUERY_PATTERNS = [
    (r"^(อะไร|ใคร|ที่ไหน|เมื่อไหร่|ทำไม|อย่างไร|how|what|where|when|why|who)", 20),
]
INFO_QUERY_KEYWORDS = ["อธิบาย", "บอกเกี่ยวกับ", "ข้อมูลเกี่ยวกับ", "ความรู้เรื่อง", "tell me about"]

# -- 7. Command/Action (NEW) -----------------------------------------
COMMAND_VERBS = [
    "สร้าง", "ลบ", "แก้ไข", "เพิ่ม", "ลบออก", "อัพเดท", "อัปเดต",
    "เปิด", "ปิด", "เริ่ม", "หยุด", "รัน", "execute", "create", "delete", "update"
]
COMMAND_OBJECTS = ["ไฟล์", "โฟลเดอร์", "โปรเจค", "เอกสาร", "ตาราง", "รายการ"]

# -- 8. Text Analysis (NEW) ------------------------------------------
TEXT_ANALYSIS_KEYWORDS = [
    "สรุป", "ย่อ", "วิเคราะห์ข้อความ", "ตรวจคำผิด", "แก้ไจ", "แปลภาษา",
    "summarize", "analyze", "proofread", "translate", "extract keywords"
]

# -- 9. Coding/Programming (NEW) -------------------------------------
CODING_KEYWORDS = [
    "เขียนโค้ด", "เขียนโปรแกรม", "แก้บั๊ก", "debug", "code", "programming",
    "python", "javascript", "java", "function", "class", "api", "database"
]
CODING_PATTERNS = [
    (r"```[\s\S]*?```", 30, "code block"),
    (r"\b(def|class|import|from|return|if|else|for|while)\b", 15, "python keywords"),
    (r"\b(function|const|let|var|=>)\b", 15, "javascript keywords"),
]

# -- 10. Creative Writing (NEW) --------------------------------------
CREATIVE_KEYWORDS = [
    "แต่งเรื่อง", "แต่งกลอน", "เขียนนิยาย", "ไอเดีย", "ความคิดสร้างสรรค์",
    "story", "poem", "novel", "creative", "imagine", "write a story"
]

# -- 11. Planning/Organization (NEW) ---------------------------------
PLANNING_KEYWORDS = [
    "วางแผน", "ตารางเวลา", "รายการ", "to-do", "todo", "schedule", "plan",
    "organize", "จัดลำดับ", "prioritize"
]

# -- 12. Recommendation (NEW) ----------------------------------------
RECOMMENDATION_KEYWORDS = [
    "แนะนำ", "แนะนำหนัง", "แนะนำเพลง", "แนะนำร้านอาหาร", "ควรดู", "ควรฟัง",
    "recommend", "suggestion", "best", "top", "good"
]

# -- 13. Comparison (NEW) --------------------------------------------
COMPARISON_PATTERNS = [
    (r"\b(vs|versus|เทียบกับ|ดีกว่า|แย่กว่า|เหมือน|แตกต่าง)\b", 20),
]
COMPARISON_KEYWORDS = ["เปรียบเทียบ", "ข้อดี", "ข้อเสีย", "ต่าง", "เหมือนกัน", "compare"]

# -- 14. Translation (NEW) -------------------------------------------
TRANSLATION_KEYWORDS = [
    "แปลว่า", "แปลเป็น", "แปลภาษา", "translate", "meaning in", "how to say"
]
TRANSLATION_PATTERNS = [
    (r"(แปล|translate)\s+\S+\s+(เป็น|to)\s+\S+", 25),
]

# -- 15. Summarization (NEW) -----------------------------------------
SUMMARIZATION_KEYWORDS = [
    "สรุปให้", "สรุปสั้นๆ", "tl;dr", "summary", "brief", "key points"
]

# -- 16. Opinion/Feedback (NEW) --------------------------------------
OPINION_KEYWORDS = [
    "คิดว่า", "เห็นด้วยไหม", "ความคิดเห็น", "รู้สึกอย่างไร", "what do you think",
    "opinion", "agree", "disagree", "feedback"
]

# -- 17. Help Request (NEW) ------------------------------------------
HELP_KEYWORDS = [
    "ช่วยด้วย", "ทำไม่ได้", "ติดปัญหา", "error", "help", "stuck", "problem"
]

# -- 18. Settings/Preferences (NEW) ----------------------------------
SETTINGS_KEYWORDS = [
    "ตั้งค่า", "เปลี่ยนภาษา", "theme", "setting", "preference", "config"
]

# -- 19. System Query (NEW) ------------------------------------------
SYSTEM_QUERY_KEYWORDS = [
    "ทำอะไรได้บ้าง", "ความสามารถ", "features", "what can you do", "help me"
]

# -- 20. General Question (Fallback) ---------------------------------
GENERAL_ACTION_WORDS = [
    "ช่วย", "อยาก", "ขอ", "สร้าง", "ทำ", "ออกแบบ", "แนะนำ",
    "บอก", "สอน", "คิด", "หา", "แก้", "แสดง", "อธิบาย",
]
GENERAL_WH_WORDS = ["อะไร", "เมื่อไหร่", "ทำไม", "อย่างไร", "ที่ไหน", "ใคร"]


# ═══════════════════════════════════════════════════════════════
# Observer Engine (Extended)
# ═══════════════════════════════════════════════════════════════

class ObserverEngine:
    """
    Observer Engine — ด่านแรกของ Council of 5 (Extended Edition)
    รองรับ 20 intents สำหรับการใช้งานจริง
    """

    def __init__(self, confidence_threshold: float = 10.0):
        self.threshold = confidence_threshold

    # ─── Public API ──────────────────────────────────────────
    def observe(self, text: str) -> ObservationResult:
        """Main entry point: รับข้อความ → คืน ObservationResult"""
        text = text.strip()
        if not text:
            return self._unknown(text, "empty input")

        # 1) ให้คะแนนทุก intent
        scores = {
            "math": self._score_math(text),
            "birth": self._score_birth(text),
            "astrology": self._score_astrology(text),
            "name": self._score_name(text),
            "chat": self._score_chat(text),
            "info_query": self._score_info_query(text),
            "command": self._score_command(text),
            "text_analysis": self._score_text_analysis(text),
            "coding": self._score_coding(text),
            "creative": self._score_creative(text),
            "planning": self._score_planning(text),
            "recommendation": self._score_recommendation(text),
            "comparison": self._score_comparison(text),
            "translation": self._score_translation(text),
            "summarization": self._score_summarization(text),
            "opinion": self._score_opinion(text),
            "help": self._score_help(text),
            "settings": self._score_settings(text),
            "system_query": self._score_system_query(text),
            "general": self._score_general(text),
        }

        # 2) เลือก intent ที่คะแนนสูงสุด
        best = max(scores, key=scores.get)
        best_score = scores[best]

        # 3) ถ้าคะแนนต่ำกว่า threshold → unknown
        if best_score < self.threshold:
            return self._unknown(text, f"all scores below threshold ({best_score:.1f})", scores)

        # 4) Second-Pass Validation
        best = self._second_pass(text, best, scores)

        # 5) สกัดข้อมูลตาม intent
        cleaned = self._extract_data(text, best)

        # 6) Confidence (0-100 → 0.0-1.0)
        confidence = min(best_score / 100.0, 1.0)

        return ObservationResult(
            intent=best,
            confidence=round(confidence, 2),
            cleaned_data=cleaned,
            all_scores=scores
        )

    # ─── Scoring Methods ────────────────────────────────────

    def _score_math(self, text: str) -> float:
        score = 0.0
        if text.lower().startswith(MATH_STARTS_WITH):
            score += 30
        for pattern, pts, _ in MATH_PATTERNS:
            if re.search(pattern, text):
                score += pts
        for kw in MATH_KEYWORDS:
            if kw in text.lower():
                score += 10
                break
        if re.search(r"\d+", text) and re.search(r"[a-zA-Z]", text):
            score += 5
        return score

    def _score_birth(self, text: str) -> float:
        score = 0.0
        for pattern, pts in BIRTH_DATE_PATTERNS:
            if re.search(pattern, text):
                score += pts
        for pattern, pts in BIRTH_TIME_PATTERNS:
            if re.search(pattern, text):
                score += pts
        for kw in BIRTH_KEYWORDS:
            if kw in text.lower():
                score += 10
                break
        has_date = any(re.search(p, text) for p, _ in BIRTH_DATE_PATTERNS)
        has_time = any(re.search(p, text) for p, _ in BIRTH_TIME_PATTERNS)
        if has_date and has_time:
            score += 20
        return score

    def _score_astrology(self, text: str) -> float:
        score = 0.0
        for kw in ASTROLOGY_KEYWORDS:
            if kw in text.lower():
                score += 20
                break
        return score

    def _score_name(self, text: str) -> float:
        score = 0.0
        if not re.search(r"[ก-ฮ]", text):
            return 0.0
        score += 5
        if "?" in text or "=" in text:
            return 0.0
        for prefix in NAME_PREFIXES:
            if text.startswith(prefix):
                score += 20
                break
        parts = text.split()
        if len(parts) >= 2 and all(re.search(r"[ก-ฮ]", p) for p in parts):
            score += 15
        if not re.search(r"\d", text):
            score += 5
        for kw in NAME_KEYWORDS:
            if kw in text:
                score += 15
                break
        return score

    def _score_chat(self, text: str) -> float:
        """คะแนนสำหรับการสนทนาทั่วไป"""
        score = 0.0
        text_lower = text.lower()
        
        # ทักทาย
        for greeting in CHAT_GREETINGS:
            if greeting in text_lower:
                score += 25
                break
        
        # ขอบคุณ
        for thanks in CHAT_THANKS:
            if thanks in text_lower:
                score += 25
                break
        
        # ขอโทษ
        for apology in CHAT_APOLOGY:
            if apology in text_lower:
                score += 20
                break
        
        # บอกลา
        for farewell in CHAT_FAREWELL:
            if farewell in text_lower:
                score += 20
                break
        
        # Small talk
        for smalltalk in CHAT_SMALLTALK:
            if smalltalk in text_lower:
                score += 15
                break
        
        # ถ้าข้อความสั้นมาก (1-3 คำ) → น่าจะเป็น chat
        if len(text.split()) <= 3 and score == 0:
            score += 10
        
        return score

    def _score_info_query(self, text: str) -> float:
        """คะแนนสำหรับการถามข้อมูล"""
        score = 0.0
        text_lower = text.lower()
        
        # ขึ้นต้นด้วยคำถาม
        for start in INFO_QUERY_STARTS:
            if text_lower.startswith(start):
                score += 25
                break
        
        # Pattern matching
        for pattern, pts in INFO_QUERY_PATTERNS:
            if re.search(pattern, text_lower):
                score += pts
                break
        
        # Keywords
        for kw in INFO_QUERY_KEYWORDS:
            if kw in text_lower:
                score += 15
                break
        
        # มีเครื่องหมายคำถาม
        if "?" in text or "؟" in text:
            score += 10
        
        return score

    def _score_command(self, text: str) -> float:
        """คะแนนสำหรับการสั่งงาน"""
        score = 0.0
        text_lower = text.lower()
        
        # มีคำกริยาสั่งการ
        for verb in COMMAND_VERBS:
            if verb in text_lower:
                score += 20
                break
        
        # มีวัตถุที่ถูกกระทำ
        for obj in COMMAND_OBJECTS:
            if obj in text_lower:
                score += 15
                break
        
        # ถ้ามีทั้งกริยาและวัตถุ → คะแนนสูง
        has_verb = any(v in text_lower for v in COMMAND_VERBS)
        has_obj = any(o in text_lower for o in COMMAND_OBJECTS)
        if has_verb and has_obj:
            score += 20
        
        return score

    def _score_text_analysis(self, text: str) -> float:
        """คะแนนสำหรับการวิเคราะห์ข้อความ"""
        score = 0.0
        text_lower = text.lower()
        
        for kw in TEXT_ANALYSIS_KEYWORDS:
            if kw in text_lower:
                score += 25
                break
        
        return score

    def _score_coding(self, text: str) -> float:
        """คะแนนสำหรับการเขียนโปรแกรม"""
        score = 0.0
        text_lower = text.lower()
        
        # Keywords
        for kw in CODING_KEYWORDS:
            if kw in text_lower:
                score += 20
                break
        
        # Patterns (code blocks, programming keywords)
        for pattern, pts, _ in CODING_PATTERNS:
            if re.search(pattern, text):
                score += pts
        
        return score

    def _score_creative(self, text: str) -> float:
        """คะแนนสำหรับการสร้างสรรค์"""
        score = 0.0
        text_lower = text.lower()
        
        for kw in CREATIVE_KEYWORDS:
            if kw in text_lower:
                score += 25
                break
        
        return score

    def _score_planning(self, text: str) -> float:
        """คะแนนสำหรับการวางแผน"""
        score = 0.0
        text_lower = text.lower()
        
        for kw in PLANNING_KEYWORDS:
            if kw in text_lower:
                score += 25
                break
        
        return score

    def _score_recommendation(self, text: str) -> float:
        """คะแนนสำหรับการแนะนำ"""
        score = 0.0
        text_lower = text.lower()
        
        for kw in RECOMMENDATION_KEYWORDS:
            if kw in text_lower:
                score += 25
                break
        
        return score

    def _score_comparison(self, text: str) -> float:
        """คะแนนสำหรับการเปรียบเทียบ"""
        score = 0.0
        text_lower = text.lower()
        
        # Patterns
        for pattern, pts in COMPARISON_PATTERNS:
            if re.search(pattern, text_lower):
                score += pts
                break
        
        # Keywords
        for kw in COMPARISON_KEYWORDS:
            if kw in text_lower:
                score += 20
                break
        
        return score

    def _score_translation(self, text: str) -> float:
        """คะแนนสำหรับการแปลภาษา"""
        score = 0.0
        text_lower = text.lower()
        
        # Keywords
        for kw in TRANSLATION_KEYWORDS:
            if kw in text_lower:
                score += 25
                break
        
        # Patterns
        for pattern, pts in TRANSLATION_PATTERNS:
            if re.search(pattern, text_lower):
                score += pts
                break
        
        return score

    def _score_summarization(self, text: str) -> float:
        """คะแนนสำหรับการสรุป"""
        score = 0.0
        text_lower = text.lower()
        
        for kw in SUMMARIZATION_KEYWORDS:
            if kw in text_lower:
                score += 25
                break
        
        return score

    def _score_opinion(self, text: str) -> float:
        """คะแนนสำหรับการถามความคิดเห็น"""
        score = 0.0
        text_lower = text.lower()
        
        for kw in OPINION_KEYWORDS:
            if kw in text_lower:
                score += 25
                break
        
        return score

    def _score_help(self, text: str) -> float:
        """คะแนนสำหรับการขอความช่วยเหลือ"""
        score = 0.0
        text_lower = text.lower()
        
        for kw in HELP_KEYWORDS:
            if kw in text_lower:
                score += 25
                break
        
        return score

    def _score_settings(self, text: str) -> float:
        """คะแนนสำหรับการตั้งค่า"""
        score = 0.0
        text_lower = text.lower()
        
        for kw in SETTINGS_KEYWORDS:
            if kw in text_lower:
                score += 25
                break
        
        return score

    def _score_system_query(self, text: str) -> float:
        """คะแนนสำหรับการถามเกี่ยวกับระบบ"""
        score = 0.0
        text_lower = text.lower()
        
        for kw in SYSTEM_QUERY_KEYWORDS:
            if kw in text_lower:
                score += 25
                break
        
        return score

    def _score_general(self, text: str) -> float:
        """คะแนนสำหรับคำถามทั่วไป (fallback)"""
        score = 0.0
        if "?" in text or "？" in text:
            score += 15
        for w in GENERAL_ACTION_WORDS:
            if w in text:
                score += 10
                break
        for w in GENERAL_WH_WORDS:
            if w in text:
                score += 10
                break
        return score

    # ─── Second-Pass Validation ─────────────────────────────

    def _second_pass(self, text: str, best: str, scores: dict) -> str:
        """
        ป้องกัน intent ถูก "กลืน"
        - ถ้า general ชนะ แต่มีสัญญาณ math → เปลี่ยนเป็น math
        - ถ้า name ชนะ แต่มีสัญญาณ astrology → เปลี่ยนเป็น astrology
        - ถ้า chat ชนะ แต่มีสัญญาณ info_query → เปลี่ยนเป็น info_query
        """
        # Math overrides
        if best in ["general", "chat"] and scores.get("math", 0) >= 25:
            return "math"
        
        # Birth info overrides
        if best in ["general", "chat"] and scores.get("birth", 0) >= 25:
            return "birth"
        
        # Astrology overrides name
        if best == "name" and scores.get("astrology", 0) >= 20:
            return "astrology"
        
        # Coding overrides general
        if best == "general" and scores.get("coding", 0) >= 30:
            return "coding"
        
        # Translation overrides text_analysis
        if best == "text_analysis" and scores.get("translation", 0) >= 25:
            return "translation"
        
        # Info query overrides chat
        if best == "chat" and scores.get("info_query", 0) >= 25:
            return "info_query"
        
        # Command overrides general
        if best == "general" and scores.get("command", 0) >= 30:
            return "command"
        
        return best

    # ─── Data Extraction ────────────────────────────────────

    def _extract_data(self, text: str, intent: str) -> dict:
        """สกัดข้อมูลตาม intent"""
        extractors = {
            "birth": self._extract_birth_data,
            "name": self._extract_name_data,
            "math": self._extract_math_data,
            "chat": self._extract_chat_data,
            "info_query": self._extract_info_query_data,
            "command": self._extract_command_data,
            "text_analysis": self._extract_text_analysis_data,
            "coding": self._extract_coding_data,
            "creative": self._extract_creative_data,
            "planning": self._extract_planning_data,
            "recommendation": self._extract_recommendation_data,
            "comparison": self._extract_comparison_data,
            "translation": self._extract_translation_data,
            "summarization": self._extract_summarization_data,
            "opinion": self._extract_opinion_data,
            "help": self._extract_help_data,
            "settings": self._extract_settings_data,
            "system_query": self._extract_system_query_data,
            "astrology": lambda t: {"query": t},
            "general": lambda t: {"query": t},
        }
        
        extractor = extractors.get(intent, lambda t: {"raw": t})
        return extractor(text)

    def _extract_birth_data(self, text: str) -> dict:
        """สกัด วัน/เดือน/ปี/เวลา/สถานที่"""
        result = {}

        # วันที่: 8/8/1992
        date_match = re.search(r"(\d{1,2})[/\-](\d{1,2})[/\-](\d{4})", text)
        if date_match:
            result["day"] = int(date_match.group(1))
            result["month"] = int(date_match.group(2))
            result["year"] = int(date_match.group(3))
        else:
            # yyyy-mm-dd
            date_match = re.search(r"(\d{4})[/\-](\d{1,2})[/\-](\d{1,2})", text)
            if date_match:
                result["year"] = int(date_match.group(1))
                result["month"] = int(date_match.group(2))
                result["day"] = int(date_match.group(3))

        # เวลา: 16:49
        time_match = re.search(r"(\d{1,2})[:.](\d{2})", text)
        if time_match:
            result["hour"] = int(time_match.group(1))
            result["minute"] = int(time_match.group(2))

        # สถานที่
        locations = [
            ("ยะลา", (6.5417, 101.282)),
            ("กรุงเทพ", (13.75, 100.50)),
            ("เชียงใหม่", (18.79, 98.98)),
            ("นครราชสีมา", (14.97, 102.10)),
            ("สงขลา", (7.20, 100.60)),
            ("ขอนแก่น", (16.44, 102.83)),
            ("ภูเก็ต", (7.88, 98.40)),
            ("บุรีรัมย์", (14.99, 103.10)),
            ("นครศรีธรรมราช", (8.43, 99.96)),
        ]
        for loc_name, (lat, lon) in locations:
            if loc_name in text:
                result["location"] = loc_name
                result["lat"] = lat
                result["lon"] = lon
                break

        return result

    def _extract_name_data(self, text: str) -> dict:
        """สกัด ชื่อ-นามสกุล"""
        t = text.strip()
        for prefix in NAME_PREFIXES:
            if t.startswith(prefix):
                t = t[len(prefix):].strip()
                break

        for kw in NAME_KEYWORDS:
            t = t.replace(kw, "").strip()

        parts = t.split()
        if len(parts) >= 2:
            return {
                "first_name": parts[0],
                "last_name": " ".join(parts[1:]),
                "full_name": t
            }
        return {
            "first_name": t,
            "last_name": "",
            "full_name": t
        }

    def _extract_math_data(self, text: str) -> dict:
        """สกัดข้อมูลสมการ"""
        clean = text
        if clean.lower().startswith("math,"):
            clean = clean[5:].strip()

        eq_match = re.search(r"([^=]+=[^=]+)", clean)
        equation = eq_match.group(1).strip() if eq_match else clean

        variables = list(set(re.findall(r"[a-zA-Z]+", equation)))
        variables = [v for v in variables if v not in ("e", "pi", "sin", "cos", "tan")]

        return {
            "equation": equation,
            "variables": variables,
            "raw": clean
        }

    def _extract_chat_data(self, text: str) -> dict:
        """สกัดข้อมูลการสนทนา"""
        text_lower = text.lower()
        chat_type = "unknown"
        
        if any(g in text_lower for g in CHAT_GREETINGS):
            chat_type = "greeting"
        elif any(t in text_lower for t in CHAT_THANKS):
            chat_type = "thanks"
        elif any(a in text_lower for a in CHAT_APOLOGY):
            chat_type = "apology"
        elif any(f in text_lower for f in CHAT_FAREWELL):
            chat_type = "farewell"
        elif any(s in text_lower for s in CHAT_SMALLTALK):
            chat_type = "smalltalk"
        
        return {
            "chat_type": chat_type,
            "message": text
        }

    def _extract_info_query_data(self, text: str) -> dict:
        """สกัดข้อมูลคำถาม"""
        # หาหัวข้อที่ถาม
        topic = text
        for start in INFO_QUERY_STARTS:
            if text.lower().startswith(start):
                topic = text[len(start):].strip()
                break
        
        return {
            "query": text,
            "topic": topic,
            "question_type": "factual"
        }

    def _extract_command_data(self, text: str) -> dict:
        """สกัดข้อมูลคำสั่ง"""
        text_lower = text.lower()
        
        # หา verb และ object
        verb = None
        obj = None
        
        for v in COMMAND_VERBS:
            if v in text_lower:
                verb = v
                break
        
        for o in COMMAND_OBJECTS:
            if o in text_lower:
                obj = o
                break
        
        return {
            "command": text,
            "verb": verb,
            "object": obj,
            "action_type": "execute"
        }

    def _extract_text_analysis_data(self, text: str) -> dict:
        """สกัดข้อมูลการวิเคราะห์ข้อความ"""
        return {
            "text": text,
            "analysis_type": "general"
        }

    def _extract_coding_data(self, text: str) -> dict:
        """สกัดข้อมูลโค้ด"""
        # หา code block
        code_blocks = re.findall(r"```[\s\S]*?```", text)
        
        # หา programming language
        lang = None
        if "python" in text.lower():
            lang = "python"
        elif "javascript" in text.lower() or "js" in text.lower():
            lang = "javascript"
        elif "java" in text.lower():
            lang = "java"
        
        return {
            "code": text,
            "code_blocks": code_blocks,
            "language": lang,
            "task": "coding"
        }

    def _extract_creative_data(self, text: str) -> dict:
        """สกัดข้อมูลการสร้างสรรค์"""
        return {
            "prompt": text,
            "creative_type": "writing"
        }

    def _extract_planning_data(self, text: str) -> dict:
        """สกัดข้อมูลการวางแผน"""
        return {
            "plan_request": text,
            "planning_type": "general"
        }

    def _extract_recommendation_data(self, text: str) -> dict:
        """สกัดข้อมูลการแนะนำ"""
        # หาหมวดหมู่
        category = "general"
        if "หนัง" in text or "movie" in text.lower():
            category = "movie"
        elif "เพลง" in text or "music" in text.lower():
            category = "music"
        elif "ร้านอาหาร" in text or "restaurant" in text.lower():
            category = "restaurant"
        
        return {
            "recommendation_request": text,
            "category": category
        }

    def _extract_comparison_data(self, text: str) -> dict:
        """สกัดข้อมูลการเปรียบเทียบ"""
        # หา items ที่เปรียบเทียบ
        items = []
        if " vs " in text.lower():
            items = text.lower().split(" vs ")
        elif "เทียบกับ" in text:
            items = text.split("เทียบกับ")
        
        return {
            "comparison_request": text,
            "items": [item.strip() for item in items] if items else []
        }

    def _extract_translation_data(self, text: str) -> dict:
        """สกัดข้อมูลการแปล"""
        # หา source และ target language
        source_lang = None
        target_lang = None
        
        if "แปลเป็นอังกฤษ" in text or "translate to english" in text.lower():
            target_lang = "english"
        elif "แปลเป็นไทย" in text or "translate to thai" in text.lower():
            target_lang = "thai"
        
        return {
            "text_to_translate": text,
            "source_language": source_lang,
            "target_language": target_lang
        }

    def _extract_summarization_data(self, text: str) -> dict:
        """สกัดข้อมูลการสรุป"""
        return {
            "content_to_summarize": text,
            "summary_type": "brief"
        }

    def _extract_opinion_data(self, text: str) -> dict:
        """สกัดข้อมูลการถามความคิดเห็น"""
        return {
            "question": text,
            "opinion_type": "general"
        }

    def _extract_help_data(self, text: str) -> dict:
        """สกัดข้อมูลการขอความช่วยเหลือ"""
        return {
            "help_request": text,
            "issue_type": "general"
        }

    def _extract_settings_data(self, text: str) -> dict:
        """สกัดข้อมูลการตั้งค่า"""
        return {
            "settings_request": text,
            "setting_type": "general"
        }

    def _extract_system_query_data(self, text: str) -> dict:
        """สกัดข้อมูลการถามเกี่ยวกับระบบ"""
        return {
            "query": text,
            "query_type": "system_capabilities"
        }

    def _unknown(self, text: str, reason: str, scores: dict = None) -> ObservationResult:
        """สร้างผลลัพธ์ unknown"""
        return ObservationResult(
            intent="unknown",
            confidence=0.0,
            cleaned_data={"raw": text, "reason": reason},
            all_scores=scores or {},
            warning=reason
        )


# ═══════════════════════════════════════════════════════════════
# Quick Test (Extended)
# ═══════════════════════════════════════════════════════════════

if __name__ == "__main__":
    obs = ObserverEngine()

    tests = [
        # Original tests
        "ดูดวง",
        "8/8/1992 16:49 ยะลา",
        "วรกฤช สุนทรธรรมนิติ",
        "แก้สมการ 3^x = x^9",
        "ช่วยออกแบบเว็บให้หน่อย",
        "ทำไมท้องฟ้าถึงเป็นสีฟ้า",
        "x^2 + 19x - 92 = 0",
        "นายสมชาย ใจดี",
        "ฉันเกิดวันที่ 15 เมษายน 1990",
        "อยากทำเว็บคลังความรู้",
        "math,3**x=x**9 x=?,verbose=true",
        
        # New tests - Chat
        "สวัสดีครับ",
        "ขอบคุณมากครับ",
        "ขอโทษที",
        "ลาก่อน",
        "สบายดีไหม",
        
        # New tests - Info Query
        "อะไรคือ machine learning",
        "ใครเป็นผู้ประดิษฐ์โทรศัพท์",
        "ทำไมน้ำถึงเดือดที่ 100 องศา",
        
        # New tests - Command
        "สร้างไฟล์ใหม่",
        "ลบโฟลเดอร์ temp",
        "อัพเดทโปรเจค",
        
        # New tests - Text Analysis
        "สรุปบทความนี้ให้หน่อย",
        "ตรวจคำผิดให้หน่อย",
        
        # New tests - Coding
        "เขียนฟังก์ชัน python สำหรับหาค่าเฉลี่ย",
        "แก้บั๊กโค้ดนี้ให้หน่อย",
        "```python\ndef hello():\n    print('hi')\n```",
        
        # New tests - Creative
        "แต่งเรื่องสั้นเกี่ยวกับ AI",
        "ช่วยคิดไอเดียสำหรับ startup",
        
        # New tests - Planning
        "วางแผนการทำงานสัปดาห์นี้",
        "สร้าง to-do list",
        
        # New tests - Recommendation
        "แนะนำหนังน่าดูหน่อย",
        "ร้านอาหารอร่อยๆ ในกรุงเทพ",
        
        # New tests - Comparison
        "Python vs JavaScript อันไหนดีกว่า",
        "เปรียบเทียบ iPhone กับ Samsung",
        
        # New tests - Translation
        "แปลว่า 'สวัสดี' เป็นภาษาอังกฤษ",
        "translate 'hello' to thai",
        
        # New tests - Summarization
        "สรุปสั้นๆ ให้หน่อย",
        "tl;dr",
        
        # New tests - Opinion
        "คิดว่า AI จะแทนที่มนุษย์ไหม",
        "เห็นด้วยกับเรื่องนี้ไหม",
        
        # New tests - Help
        "ช่วยด้วย ทำไม่ได้",
        "ติดปัญหา error",
        
        # New tests - Settings
        "เปลี่ยนภาษาเป็นอังกฤษ",
        "ตั้งค่า theme",
        
        # New tests - System Query
        "คุณทำอะไรได้บ้าง",
        "ความสามารถของระบบ",
    ]

    for t in tests:
        result = obs.observe(t)
        print(f"\n{'─'*50}")
        print(f"Input: {t}")
        print(f"Intent: {result.intent} (confidence: {result.confidence})")
        print(f"Data: {result.cleaned_data}")
        if result.all_scores:
            top_3 = sorted(result.all_scores.items(), key=lambda x: -x[1])[:3]
            print(f"Top 3 Scores: {dict(top_3)}")