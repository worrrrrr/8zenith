"""
BaseTool — รากฐานของทุกเครื่องมือใน 8zenith
ทุก tool ต้อง inherit BaseTool และ implement:
    - intents: list[str]  — รายการ intent ที่ tool นี้รับผิดชอบ
    - execute(context: dict) -> dict — ลงมือทำงาน
"""

from abc import ABC, abstractmethod
from typing import List, Dict


class BaseTool(ABC):
    """Abstract Base Class สำหรับทุก tool ใน 8zenith"""

    @property
    @abstractmethod
    def intents(self) -> List[str]:
        """คืนค่ารายการ intent ที่ tool นี้รับผิดชอบ
        เช่น: ["birth", "astrology"] หรือ ["math"]
        """
        pass

    @abstractmethod
    def execute(self, context: dict) -> dict:
        """ลงมือทำงานตาม context ที่ได้รับ
        คืนค่า dict ของผลลัพธ์
        """
        pass

    @property
    def name(self) -> str:
        """ชื่อ tool (default: ชื่อ class)"""
        return self.__class__.__name__

    @property
    def description(self) -> str:
        """คำอธิบาย tool (optional)"""
        return self.__doc__ or ""

    def validate_context(self, context: dict) -> bool:
        """ตรวจสอบว่า context ครบถ้วนสำหรับ tool นี้หรือไม่
        override ได้ใน subclass
        """
        return True