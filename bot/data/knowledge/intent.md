# 8zenith Intent Detection Rules
> Source of Truth สำหรับ Observer Engine  
> แก้ไขตารางด้านล่างได้โดยตรง Observer จะอ่านผ่าน `tools/md_parser_dict.py`

---

## 1. Math Problem
| Feature | Detail | Score | Example |
|---------|--------|-------|---------|
| Structured prefix | user input starts with `math,` | 30 | `math,3**x=x**9 x=?,verbose=true` |
| Equation presence | contains `=` (assignment or equation) | 15 | `x^2+19x-92=0` |
| Exponent notation | contains `^` or `**` | 10 | `4^x=x^16` |
| Common variable | single letter `x`, `y`, `z`, `t` | 10 | `23x+100=491` |
| System of equations | comma or Thai `และ` between equations | 20 | `x-y=5, xy=24` |
| Math keywords (Thai) | `แก้สมการ`, `สมการ`, `คำนวณ`, `หาค่า` | 10 | `แก้สมการ 3^x = x^9` |
| Math symbols | `+`, `-`, `*`, `/`, `√`, `∫`, `∑` | 5 | – |

## 2. Birth Info
| Feature | Detail | Score | Example |
|---------|--------|-------|---------|
| Date format | `dd/mm/yyyy` or `yyyy-mm-dd` | 25 | `8/8/1992` |
| Time format | `hh:mm` (24h) | 15 | `16:49` |
| Location name | Thai province/city names (extensible) | 10 | `ยะลา`, `กรุงเทพ` |
| Birth keywords | `เกิด`, `วันเกิด`, `เวลาเกิด`, `สถานที่เกิด` | 10 | `ผมเกิดวันที่ 8/8/1992` |
| Combined birth+time | date and time found together | +20 (additive) | `8/8/1992 16:49` |

## 3. Astrology Question
| Feature | Detail | Score | Example |
|---------|--------|-------|---------|
| Thai astrology keywords | `ดูดวง`, `พยากรณ์`, `ดวงชะตา`, `โหราศาสตร์`, `หมอดู` | 20 | `ดูดวง` |
| English system names | `Bazi`, `Ba Zi`, `Four Pillars`, `Numerology`, `MBTI`, `Enneagram`, `Human Design` | 20 | `Human Design` |
| Astrology action words | `คำนวณดวง`, `ผูกดวง`, `ดูดวงฟรี`, `เช็คดวง` | 15 | `เช็คดวง` |
| Name+astrology combo | contains both a Thai name and astrology keyword | +10 (additive) | `ช่วยดูดวงให้ วรกฤช` |

## 4. Name Analysis
| Feature | Detail | Score | Example |
|---------|--------|-------|---------|
| Thai name prefix | `นาย`, `นางสาว`, `นาง`, `เด็กชาย`, `เด็กหญิง` | 20 | `นายวรกฤช` |
| Multiple Thai words | 2+ Thai words (looks like full name) | 15 | `วรกฤช สุนทรธรรมนิติ` |
| Pure Thai characters | only Thai alphabet, no digits, no `?` | 10 | `สมชาย` |
| Name analysis keywords | `ชื่อ`, `นามสกุล`, `ตั้งชื่อ`, `เปลี่ยนชื่อ`, `ความหมายชื่อ` | 15 | `วิเคราะห์ชื่อ วรกฤช` |

## 5. General Question
| Feature | Detail | Score | Example |
|---------|--------|-------|---------|
| Question mark | `?` or `？` | 15 | `ทำไม?` |
| Action request words | `ช่วย`, `อยาก`, `ขอ`, `สร้าง`, `ทำ`, `ออกแบบ`, `แนะนำ`, `บอก`, `สอน`, `คิด`, `หา`, `แก้`, `แสดง` | 10 | `ช่วยออกแบบเว็บ` |
| Wh- words (Thai) | `อะไร`, `เมื่อไหร่`, `ทำไม`, `อย่างไร`, `ที่ไหน`, `ใคร` | 10 | `อะไรคือ Bazi` |
| Explicit intent prefix | starts with `ask,` or `question,` | 30 | `ask,what is love?` |

## 6. Project / Code Generation
| Feature | Detail | Score | Example |
|---------|--------|-------|---------|
| Code keywords | `โค้ด`, `code`, `เขียนโปรแกรม`, `python`, `javascript` | 15 | `เขียนโค้ด python` |
| Git/Project init | `git init`, `สร้างโปรเจค`, `โครงโปรเจค`, `setup` | 15 | `สร้างโครงโปรเจค` |
| File names / extensions | `.py`, `.json`, `.md`, `README`, `main.py` | 10 | `สร้าง main.py` |
| Explicit dev prefix | starts with `dev,` or `code,` | 30 | `dev,สร้าง api endpoint` |

## 7. Knowledge Query
| Feature | Detail | Score | Example |
|---------|--------|-------|---------|
| Factual question starters | `คืออะไร`, `หมายถึง`, `นิยามของ`, `ใครคือ`, `เมื่อใด` | 10 | `Bazi คืออะไร` |
| Encyclopedia keywords | `ข้อมูล`, `สถิติ`, `ประวัติ`, `ข้อเท็จจริง` | 10 | `ประวัติของ Albert Einstein` |
| Explicit knowledge prefix | starts with `kb,` or `wiki,` | 30 | `kb,Einstein` |

## 8. Creative Writing
| Feature | Detail | Score | Example |
|---------|--------|-------|---------|
| Writing request words | `เขียน`, `แต่ง`, `กลอน`, `บทความ`, `เรื่องสั้น`, `นิยาย`, `คำคม` | 15 | `แต่งกลอนให้หน่อย` |
| Tone/Style description | `แนว`, `สไตล์`, `แบบ`, `อารมณ์` | 5 | `เขียนบทความแนวตลก` |
| Explicit creative prefix | starts with `write,` or `creative,` | 30 | `write,poem about stars` |

## 9. Translation
| Feature | Detail | Score | Example |
|---------|--------|-------|---------|
| Translation request words | `แปล`, `translate`, `ภาษา`, `คำว่า` | 15 | `แปลว่า` |
| Language pairs | `ไทย->อังกฤษ`, `en->th`, `จีน` | 5 | `ไทยเป็นอังกฤษ` |
| Explicit translation prefix | starts with `trans,` or `tran,` | 30 | `trans,hello,en->th` |

## 10. Summarization
| Feature | Detail | Score | Example |
|---------|--------|-------|---------|
| Summarize keywords | `สรุป`, `ย่อ`, `จับใจความ`, `shorten` | 15 | `สรุปให้หน่อย` |
| Long text input | message length > 500 characters (detected by engine) | 10 | – |
| Explicit summarize prefix | starts with `sum,` | 30 | `sum,ข้อความยาว...` |

## 11. System Command
| Feature | Detail | Score | Example |
|---------|--------|-------|---------|
| System verbs | `เปิด`, `ปิด`, `ตั้งค่า`, `config`, `reset`, `ล้าง`, `เปลี่ยนโหมด` | 15 | `เปิดโหมดมืด` |
| Target keywords | `ระบบ`, `บอท`, `AI`, `8zenith`, `การแจ้งเตือน` | 5 | `เปลี่ยนชื่อบอท` |
| Explicit system prefix | starts with `sys,` or `cmd,` | 30 | `sys,reset session` |

## 12. Help / Guide
| Feature | Detail | Score | Example |
|---------|--------|-------|---------|
| Help request words | `ช่วยเหลือ`, `คู่มือ`, `guide`, `help`, `วิธีใช้`, `วิธีการ` | 15 | `วิธีใช้ 8zenith` |
| Onboarding request | `เริ่มต้น`, `getting started`, `first time` | 15 | `เริ่มต้นใช้งาน` |
| Explicit help prefix | starts with `help,` or `guide,` | 30 | `help,intent` |