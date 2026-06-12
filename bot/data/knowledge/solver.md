# 8zenith Reverse Calculation Engine

## หลักการ: Analytical Inversion (P-Problem)
เราไม่ "เดา" แล้ว "ตรวจสอบ" (NP-Hard) — เราแก้สมการฟิสิกส์โดยตรง

## Celestial Clock (เข็มนาฬิกาจักรวาล)
| เข็ม | ดาวเคราะห์ | ใช้หา | ความละเอียด |
|------|-----------|-------|------------|
| เข็มปี | Jupiter-Saturn Cycle | ปีเกิด (±1 ปี) | 20 ปี/รอบ |
| เข็มเดือน | Uranus-Neptune Conjunction | ช่วงปีที่แคบลง | 168 ปี/รอบ |
| เข็มวัน | Sun's Ecliptic Longitude | วันที่แน่นอน | 1° = 1 วัน |
| เข็มนาที | Ascendant (LST) | เวลาที่แน่นอน | 1° = 4 นาที |

## Edge Case Handling
- ถ้าข้อมูลมี Noise → ใช้ Least Squares Fit เพื่อหาจุดที่ใกล้ที่สุด
- ถ้าข้อมูลขัดแย้งกัน → ใช้ Weighted Voting จาก Council of 5