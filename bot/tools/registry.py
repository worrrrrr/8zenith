"""
8zenith Tool Registry — BaseTool Auto-Discovery
=================================================
- Scan tools/ directory → หาทุก subclass ของ BaseTool
- ลงทะเบียน intent → tool_instance โดยอัตโนมัติ
- ไม่ต้องแก้ REGISTRY_MAP เมื่อเพิ่ม tool ใหม่

ใช้โดย:
    Seeker → registry.get_tool(intent) → tool.execute(context)
    CLI → python -m tools.registry → ดูสถานะ
"""

import sys
import importlib
import inspect
from pathlib import Path
from typing import Dict, Optional

from tools.base import BaseTool

# ═══════════════════════════════════════════════════════════════
# Tool Instance Registry (intent → BaseTool instance)
# ═══════════════════════════════════════════════════════════════

_registry: Dict[str, BaseTool] = {}
_initialized = False


def discover() -> Dict[str, BaseTool]:
    """
    Scan tools/ directory → หาทุก subclass ของ BaseTool
    → ลงทะเบียน intent → instance โดยอัตโนมัติ
    """
    global _registry, _initialized
    if _initialized:
        return _registry

    tools_dir = Path(__file__).resolve().parent
    bot_root = tools_dir.parent
    if str(bot_root) not in sys.path:
        sys.path.insert(0, str(bot_root))

    for py_file in tools_dir.glob("*.py"):
        module_name = py_file.stem
        if module_name.startswith("_") or module_name in ("base", "registry"):
            continue

        try:
            module = importlib.import_module(f"tools.{module_name}")

            for name, obj in inspect.getmembers(module, inspect.isclass):
                if (
                    issubclass(obj, BaseTool)
                    and obj is not BaseTool
                    and obj.__module__ == f"tools.{module_name}"
                ):
                    instance = obj()
                    for intent in instance.intents:
                        _registry[intent] = instance
                        print(f"🔍 Registered: {intent} → {instance.name}")

        except Exception as e:
            print(f"⚠️  Skipped {module_name}: {e}")

    _initialized = True
    return _registry


def get_tool(intent: str) -> Optional[BaseTool]:
    """คืนค่า tool instance สำหรับ intent ที่กำหนด"""
    discover()
    return _registry.get(intent)


def list_tools() -> Dict[str, str]:
    """คืนค่า {intent: tool_name}"""
    discover()
    return {intent: tool.name for intent, tool in _registry.items()}


def status():
    """พิมพ์รายงานสถานะ"""
    discover()
    print(f"\n{'='*60}")
    print(f"🛠️  8zenith Tool Registry — Auto-Discovery Status")
    print(f"{'='*60}")
    print(f"{'Intent':<20} {'Tool':<25} {'Status'}")
    print(f"{'-'*20} {'-'*25} {'-'*10}")

    for intent, tool in sorted(_registry.items()):
        print(f"{intent:<20} {tool.name:<25} ✅ Ready")

    print(f"{'='*60}")
    print(f"📊 Total: {len(_registry)} tools registered for {len(set(_registry.values()))} intents")
    print(f"{'='*60}\n")


# ═══════════════════════════════════════════════════════════════
# CLI
# ═══════════════════════════════════════════════════════════════
if __name__ == "__main__":
    status()