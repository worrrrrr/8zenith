"""
benchmark_runner.py — 8zenith Multi-LLM Benchmark Runner (Full Edition)
=========================================================================
โหลด questions + prompts + models → รันทดสอบ → บันทึกผลทันทีทุกข้อ

โครงสร้างการวนลูป:
    for model in models:           # ทดสอบทีละโมเดล
        for prompt in prompts:     # ทดสอบทีละ prompt
            for question in questions:  # ทดสอบทีละคำถาม
                → ถาม LLM → บันทึกผลทันที

คุณสมบัติ:
- Save ทันทีหลังแต่ละ trial เสร็จ — ไม่ต้องรอจนจบ
- แสดงผลชัด: Prompt อะไร → โมเดลอะไร → ตอบว่าอะไร
- ไฟล์ .jsonl (JSON Lines) — append ได้ไม่จำกัด
"""

import os
import json
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

# ═══════════════════════════════════════════════════════════════
# 1. Imports สำหรับแต่ละ Provider
# ═══════════════════════════════════════════════════════════════

from groq import Groq
from anthropic import Anthropic
import requests


# ═══════════════════════════════════════════════════════════════
# 2. Clients (Groq, Ollama, Claude)
# ═══════════════════════════════════════════════════════════════

def ask_groq(system_prompt: str, user_input: str, model: str,
             temperature: float = 0.0, max_tokens: int = 100) -> dict:
    """ถาม Groq Cloud API"""
    client = Groq(api_key=os.getenv("GROQ_API_KEY"))
    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": user_input})

    response = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=temperature,
        max_tokens=max_tokens
    )
    return {
        "answer": response.choices[0].message.content,
        "tokens_in": response.usage.prompt_tokens,
        "tokens_out": response.usage.completion_tokens,
        "tokens_total": response.usage.total_tokens
    }


def ask_ollama(system_prompt: str, user_input: str, model: str,
               temperature: float = 0.0, max_tokens: int = 2024,thinking=False) -> dict:
    """ถาม Ollama (Local)"""
    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": user_input})

    response = requests.post(
        "http://localhost:11434/api/chat",
        json={
            "model": model,
            "messages": messages,
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens
            },
            "stream": False,
            "thinking":False
        },
        timeout=120
    )
    data = response.json()
    return {
        "answer": data.get("message", {}).get("content", ""),
        "tokens_in": data.get("prompt_eval_count", 0),
        "tokens_out": data.get("eval_count", 0),
        "tokens_total": data.get("prompt_eval_count", 0) + data.get("eval_count", 0)
    }


def ask_claude(system_prompt: str, user_input: str, model: str,
               temperature: float = 0.0, max_tokens: int = 100) -> dict:
    """ถาม Claude (Anthropic API)"""
    client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
    response = client.messages.create(
        model=model,
        system=system_prompt if system_prompt else "คุณคือผู้ช่วยทั่วไป",
        messages=[{"role": "user", "content": user_input}],
        temperature=temperature,
        max_tokens=max_tokens
    )
    return {
        "answer": response.content[0].text,
        "tokens_in": response.usage.input_tokens,
        "tokens_out": response.usage.output_tokens,
        "tokens_total": response.usage.input_tokens + response.usage.output_tokens
    }


# ═══════════════════════════════════════════════════════════════
# 3. Verdict Engine
# ═══════════════════════════════════════════════════════════════

def verdict(answer: str, expected: str) -> str:
    """
    ตัดสินคำตอบของ LLM

    Returns:
        "correct"      — ตอบถูก
        "date_error"   — ติด Date Pattern (-0.31)
        "ask_back"     — ถามกลับ (ฉลาด!)
        "silent"       — ไม่ตอบอะไรเลย
        "other"        — ตอบอย่างอื่น
    """
    if not answer or not answer.strip():
        return "silent"

    clean = answer.replace(" ", "").replace("\n", " ")

    # Date Pattern Detection
    if "-0.31" in clean:
        return "date_error"

    # ตรวจสอบว่าตอบถูกหรือไม่
    expected_clean = expected.replace(" ", "")

    if expected_clean in clean:
        return "correct"

    if "0.69" in clean:
        return "correct"

    if "0.300000" in clean or "0.3" in clean:
        return "correct"

    if "?" in answer or "หมายถึง" in answer or "clarify" in answer.lower():
        return "ask_back"

    return "other"


# ═══════════════════════════════════════════════════════════════
# 4. Main Runner
# ═══════════════════════════════════════════════════════════════

def main():
    BASE = Path("data/benchmark")

    # ─── 4.1 โหลด Questions ──────────────────────────────
    questions = []
    for f in sorted((BASE / "questions").glob("*.json")):
        with open(f, "r", encoding="utf-8") as fp:
            data = json.load(fp)
            questions.extend(data["questions"])
            print(f"📥 Loaded {len(data['questions'])} questions from {f.name}")

    print(f"   Total questions: {len(questions)}")

    # ─── 4.2 โหลด Prompts ────────────────────────────────
    prompts = {}
    for f in sorted((BASE / "prompts").glob("*.json")):
        with open(f, "r", encoding="utf-8") as fp:
            data = json.load(fp)
            prompts[f.stem] = {
                "name": data.get("name", f.stem),
                "text": data.get("text", "")
            }
            print(f"📝 Loaded prompt: {f.stem} → \"{data.get('name', f.stem)}\"")

    print(f"   Total prompts: {len(prompts)}")

    # ─── 4.3 โหลด Models ─────────────────────────────────
    with open(BASE / "models" / "registry.json", "r", encoding="utf-8") as f:
        registry = json.load(f)

    models = registry["models"]
    print(f"🤖 Loaded {len(models)} models:")
    for m in models:
        print(f"   - {m['id']} ({m['provider']}) → {m['model']}")

    # ─── 4.4 สร้าง Session ───────────────────────────────
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    runs_dir = BASE / "runs"
    runs_dir.mkdir(parents=True, exist_ok=True)

    run_file = runs_dir / f"{timestamp}.jsonl"
    print(f"\n📁 Session: {run_file}\n")

    # ─── 4.5 Statistics ───────────────────────────────────
    total = 0
    correct = 0
    date_errors = 0
    silent_count = 0
    error_count = 0

    # ─── 4.6 MAIN LOOP: Models → Prompts → Questions ─────
    for model in models:
        print(f"{'='*70}")
        print(f"🧠 MODEL: {model['name']}")
        print(f"   Provider: {model['provider']} | Model: {model['model']}")
        print(f"{'='*70}")

        for prompt_key, prompt_data in prompts.items():
            prompt_name = prompt_data["name"]
            prompt_text = prompt_data["text"]

            print(f"\n   📋 PROMPT: {prompt_key} — \"{prompt_name}\"")
            if prompt_text:
                print(f"      Text: {prompt_text[:80]}...")
            else:
                print(f"      Text: (empty — no system prompt)")
            print(f"      {'─'*60}")

            for q in questions:
                total += 1
                start = time.time()

                try:
                    # ─── เรียก LLM ตาม provider ──────────
                    if model["provider"] == "groq":
                        result = ask_groq(prompt_text, q["text"], model["model"])
                    elif model["provider"] == "ollama":
                        result = ask_ollama(prompt_text, q["text"], model["model"])
                    elif model["provider"] == "claude":
                        result = ask_claude(prompt_text, q["text"], model["model"])
                    else:
                        continue

                    elapsed = time.time() - start
                    v = verdict(result["answer"], q["expected"])

                    # ─── สร้าง trial record ──────────────
                    trial = {
                        "timestamp": datetime.now().isoformat(),
                        "model": model["id"],
                        "model_name": model["name"],
                        "prompt": prompt_key,
                        "prompt_name": prompt_name,
                        "question": q["id"],
                        "question_text": q["text"],
                        "answer": result["answer"],
                        "expected": q["expected"],
                        "verdict": v,
                        "elapsed_sec": round(elapsed, 3)
                    }

                    # ─── SAVE ทันที ──────────────────────
                    with open(run_file, "a", encoding="utf-8") as f:
                        f.write(json.dumps(trial, ensure_ascii=False) + "\n")

                    # ─── นับสถิติ ────────────────────────
                    if v == "correct":
                        correct += 1
                    elif v == "date_error":
                        date_errors += 1
                    elif v == "silent":
                        silent_count += 1

                    # ─── แสดงผล ──────────────────────────
                    emoji = {
                        "correct": "✅",
                        "date_error": "❌",
                        "ask_back": "🤔",
                        "silent": "🔇",
                        "other": "❓",
                        "error": "⚠️"
                    }.get(v, "❓")

                    answer_preview = result["answer"].replace("\n", " ")[:80]
                    print(f"      {emoji} {q['id']:10s} | {v:12s} | {answer_preview}")

                except Exception as e:
                    error_count += 1
                    trial = {
                        "timestamp": datetime.now().isoformat(),
                        "model": model["id"],
                        "model_name": model["name"],
                        "prompt": prompt_key,
                        "prompt_name": prompt_name,
                        "question": q["id"],
                        "question_text": q["text"],
                        "verdict": "error",
                        "error": str(e)
                    }
                    with open(run_file, "a", encoding="utf-8") as f:
                        f.write(json.dumps(trial, ensure_ascii=False) + "\n")
                    print(f"      ⚠️ {q['id']:10s} | error      | {str(e)[:60]}")

    # ─── 4.7 Final Report ─────────────────────────────────
    print(f"\n{'='*70}")
    print(f"📊 FINAL REPORT")
    print(f"{'='*70}")
    print(f"📁 Log File: {run_file}")
    print(f"📊 Total Trials: {total}")
    if total > 0:
        print(f"✅ Correct:         {correct:4d} ({correct/total*100:5.1f}%)")
        print(f"❌ Date Error:      {date_errors:4d} ({date_errors/total*100:5.1f}%)")
        print(f"🔇 Silent:          {silent_count:4d} ({silent_count/total*100:5.1f}%)")
        print(f"⚠️  Error:           {error_count:4d} ({error_count/total*100:5.1f}%)")
        print(f"❓ Other:           {total-correct-date_errors-silent_count-error_count:4d}")
    print(f"{'='*70}")

    # ─── 4.8 Summary per Model ────────────────────────────
    print(f"\n📊 PER-MODEL SUMMARY")
    print(f"{'='*70}")
    for model in models:
        # นับจากไฟล์ log
        model_total = 0
        model_correct = 0
        model_date = 0
        model_silent = 0
        with open(run_file, "r", encoding="utf-8") as f:
            for line in f:
                t = json.loads(line)
                if t["model"] == model["id"]:
                    model_total += 1
                    if t["verdict"] == "correct":
                        model_correct += 1
                    elif t["verdict"] == "date_error":
                        model_date += 1
                    elif t["verdict"] == "silent":
                        model_silent += 1

        if model_total > 0:
            print(f"{model['name']:30s} | {model_correct:2d}/{model_total:2d} correct | {model_date:2d} date_err | {model_silent:2d} silent")
    print(f"{'='*70}")


# ═══════════════════════════════════════════════════════════════
# 5. Entry Point
# ═══════════════════════════════════════════════════════════════

if __name__ == "__main__":
    main()