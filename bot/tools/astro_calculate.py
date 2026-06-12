"""
8zenith Astro Calculate Engine — Full Universal System
========================================================
ใช้ swisseph (pyswisseph) ในการคำนวณตำแหน่งดาวเคราะห์ ระยะห่าง แรงโน้มถ่วง
ระบบบ้าน และ Local Horizon โดยไม่พึ่งพาระบบราศีหรือการตีความใด ๆ

Dependency: pip install pyswisseph
"""

import swisseph as swe
from datetime import datetime
from typing import Dict, List, Optional, Tuple

# ═══════════════════════════════════════════════════════════════
# ค่าคงที่ทางฟิสิกส์
# ═══════════════════════════════════════════════════════════════
G = 6.67430e-11
AU = 1.495978707e11
SOLAR_MASS = 1.98847e30

# ═══════════════════════════════════════════════════════════════
# รายชื่อดาวเคราะห์และรหัส Swiss Ephemeris
# ═══════════════════════════════════════════════════════════════
PLANETS = {
    "sun": swe.SUN, "moon": swe.MOON, "mercury": swe.MERCURY,
    "venus": swe.VENUS, "mars": swe.MARS, "jupiter": swe.JUPITER,
    "saturn": swe.SATURN, "uranus": swe.URANUS, "neptune": swe.NEPTUNE,
    "pluto": swe.PLUTO, "mean_node": swe.MEAN_NODE, "true_node": swe.TRUE_NODE,
}

MASSES = {
    "sun": 1.989e30, "moon": 7.342e22, "mercury": 3.301e23,
    "venus": 4.867e24, "mars": 6.417e23, "jupiter": 1.898e27,
    "saturn": 5.683e26, "uranus": 8.681e25, "neptune": 1.024e26,
    "pluto": 1.303e22,
}

PLANET_NAMES = {
    "sun": "ดวงอาทิตย์", "moon": "ดวงจันทร์", "mercury": "ดาวพุธ",
    "venus": "ดาวศุกร์", "mars": "ดาวอังคาร", "jupiter": "ดาวพฤหัสบดี",
    "saturn": "ดาวเสาร์", "uranus": "ดาวยูเรนัส", "neptune": "ดาวเนปจูน",
    "pluto": "ดาวพลูโต", "mean_node": "ราหู (เฉลี่ย)", "true_node": "ราหู (จริง)",
}

HOUSE_SYSTEMS = {
    'P': 'Placidus', 'W': 'Whole Sign', 'E': 'Equal (Asc)',
    'K': 'Koch', 'C': 'Campanus', 'R': 'Regiomontanus',
}

HOUSE_NAMES_TH = {
    1: "ตนุ (ตัวตน)", 2: "กดุมภะ (ทรัพย์สิน)", 3: "สหัชชะ (พี่น้อง)",
    4: "พันธุ (ครอบครัว)", 5: "ปุตตะ (ความคิดสร้างสรรค์)", 6: "อริ (อุปสรรค)",
    7: "ปัตนิ (คู่ครอง)", 8: "มรณะ (การเปลี่ยนแปลง)", 9: "ศุภะ (โชคลาภ)",
    10: "กรรมะ (การงาน)", 11: "ลาภะ (มิตรสหาย)", 12: "วินาศ (การปลีกวิเวก)"
}

ASPECT_SYMBOLS = {
    "Conjunction": "☌", "Sextile": "⚹", "Square": "□",
    "Trine": "△", "Opposition": "☍"
}

ASPECT_MEANINGS = {
    "Conjunction": "รวมพลัง", "Sextile": "ส่งเสริม",
    "Square": "ขัดแย้ง", "Trine": "กลมกลืน", "Opposition": "ตรงข้าม"
}


class AstroCalculate:
    """จักรกลคำนวณตำแหน่งและแรงโน้มถ่วงของดาวเคราะห์ (Universal Edition)"""

    def __init__(self, birth_dt: datetime, lat: float, lon: float,
                 house_system: str = 'P', ephemeris_path: Optional[str] = None):
        self.birth_dt = birth_dt
        self.lat = lat
        self.lon = lon
        self.house_system = house_system

        if ephemeris_path:
            swe.set_ephe_path(ephemeris_path)

        self.jd = swe.julday(birth_dt.year, birth_dt.month, birth_dt.day,
                             birth_dt.hour + birth_dt.minute / 60.0 + birth_dt.second / 3600.0)

        self._planet_data: Dict[str, dict] = {}
        self._horizon_data: Dict[str, dict] = {}
        self._houses: Dict = {}

        self._calc_all_planets()
        self._calc_houses()
        self._calc_local_horizon()

    # ═══════════════════════════════════════════════════════════
    # 1. ตำแหน่งดาวเคราะห์
    # ═══════════════════════════════════════════════════════════
    def _calc_all_planets(self):
        for name, pid in PLANETS.items():
            try:
                res = swe.calc_ut(self.jd, pid)
                if res[0]:
                    lon, lat, dist, sp_lon, sp_lat, sp_dist = res[0]
                    self._planet_data[name] = {
                        "longitude": lon, "latitude": lat, "distance_au": dist,
                        "speed_lon": sp_lon, "speed_lat": sp_lat, "speed_dist": sp_dist
                    }
            except Exception as e:
                print(f"Warning: cannot calculate {name}: {e}")

    # ═══════════════════════════════════════════════════════════
    # 2. ระบบบ้าน
    # ═══════════════════════════════════════════════════════════
    def _calc_houses(self):
        try:
            hsys = self.house_system.encode() if isinstance(self.house_system, str) else self.house_system
            houses, ascmc = swe.houses(self.jd, self.lat, self.lon, hsys)
            if houses and len(houses) >= 12:
                self._houses = {
                    "ascendant": ascmc[0], "mc": ascmc[1],
                    "houses": [houses[i] for i in range(12)],
                    "house_system": HOUSE_SYSTEMS.get(self.house_system, 'Unknown')
                }
        except Exception as e:
            print(f"House calculation failed: {e}")
            self._houses = {}

    # ═══════════════════════════════════════════════════════════
    # 3. Local Horizon
    # ═══════════════════════════════════════════════════════════
    def _calc_local_horizon(self):
        asc = self._houses.get("ascendant", 0.0)
        for name, data in self._planet_data.items():
            lon = data["longitude"]
            try:
                geopos = (self.lon, self.lat, 0.0)
                res = swe.azalt(self.jd, swe.HOR2ECL, geopos, lon, data["latitude"])
                if res:
                    azimuth, altitude = res[0], res[1]
                    self._horizon_data[name] = {
                        "azimuth": azimuth, "altitude": altitude, "visible": altitude > 0
                    }
                    continue
            except Exception:
                pass

            desc = (asc + 180) % 360
            if asc < desc:
                visible = asc <= lon <= desc
            else:
                visible = lon >= asc or lon <= desc

            self._horizon_data[name] = {
                "azimuth": 0.0, "altitude": 90 if visible else -90, "visible": visible
            }

    # ═══════════════════════════════════════════════════════════
    # 4. ดาวเคราะห์ในภพ
    # ═══════════════════════════════════════════════════════════
    def get_planet_house(self, planet_name: str) -> Optional[int]:
        p = self.get_planet(planet_name)
        if not p or not self._houses: return None
        lon = p["longitude"]
        boundaries = self._houses["houses"]
        for i in range(12):
            start = boundaries[i]
            end = boundaries[(i + 1) % 12]
            if i == 11:
                if lon >= start or lon < end: return 12
            else:
                if start <= lon < end: return i + 1
        return None

    def get_all_planets_in_houses(self) -> Dict[int, List[str]]:
        result = {i: [] for i in range(1, 13)}
        for planet_name in self._planet_data:
            house = self.get_planet_house(planet_name)
            if house: result[house].append(planet_name)
        return result

    def find_dusthana_planet(self, planet_name: str) -> Optional[dict]:
        house = self.get_planet_house(planet_name)
        if house is None: return None
        dusthana = {6: "ภพอริ/อุปสรรค", 8: "ภพมรณะ/การเกิดใหม่", 12: "ภพวินาศ/การปลีกวิเวก"}
        return {
            "planet": planet_name,
            "planet_th": PLANET_NAMES.get(planet_name, planet_name),
            "house": house,
            "is_dusthana": house in dusthana,
            "meaning": dusthana.get(house, "ปกติ — พลังงานแสดงออกได้อย่างอิสระ")
        }

    # ═══════════════════════════════════════════════════════════
    # 5. มุมสัมพันธ์ (Aspects)
    # ═══════════════════════════════════════════════════════════
    def get_all_aspects(self, orb: float = 8.0) -> List[dict]:
        aspects = []
        planet_names = list(self._planet_data.keys())
        for i in range(len(planet_names)):
            for j in range(i + 1, len(planet_names)):
                p1, p2 = planet_names[i], planet_names[j]
                angle = self.aspect_angle(p1, p2)
                if angle is None: continue
                aspect_type = None
                if angle <= orb: aspect_type = "Conjunction"
                elif abs(angle - 60) <= orb: aspect_type = "Sextile"
                elif abs(angle - 90) <= orb: aspect_type = "Square"
                elif abs(angle - 120) <= orb: aspect_type = "Trine"
                elif abs(angle - 180) <= orb: aspect_type = "Opposition"
                if aspect_type:
                    aspects.append({
                        "planet1": p1, "planet1_th": PLANET_NAMES.get(p1, p1),
                        "planet2": p2, "planet2_th": PLANET_NAMES.get(p2, p2),
                        "angle": round(angle, 2), "aspect": aspect_type,
                        "symbol": ASPECT_SYMBOLS.get(aspect_type, ""),
                        "meaning": ASPECT_MEANINGS.get(aspect_type, ""),
                        "force_type": "แรงดึงดูด" if angle < 90 else "แรงเหวี่ยง" if angle > 120 else "แรงตึงเครียด"
                    })
        return sorted(aspects, key=lambda x: x["angle"])

    # ═══════════════════════════════════════════════════════════
    # 6. Public API
    # ═══════════════════════════════════════════════════════════
    def get_planet(self, name: str) -> Optional[dict]:
        return self._planet_data.get(name.lower())

    def is_visible(self, name: str) -> Optional[bool]:
        return self._horizon_data.get(name.lower(), {}).get("visible")

    def get_houses(self) -> Dict:
        return self._houses

    def get_ascendant(self) -> Optional[float]:
        return self._houses.get("ascendant")

    def get_mc(self) -> Optional[float]:
        return self._houses.get("mc")

    def tidal_force(self, name: str) -> float:
        p = self.get_planet(name)
        if not p: return 0.0
        mass = MASSES.get(name, 0.0)
        dist_m = p["distance_au"] * AU
        return G * mass / (dist_m ** 3) if dist_m != 0 else float("inf")

    def dominant_planet(self) -> Tuple[str, float]:
        forces = {name: self.tidal_force(name) for name in self._planet_data}
        if not forces: return ("unknown", 0.0)
        return max(forces.items(), key=lambda x: x[1])

    def aspect_angle(self, name1: str, name2: str) -> Optional[float]:
        p1 = self.get_planet(name1)
        p2 = self.get_planet(name2)
        if not p1 or not p2: return None
        diff = abs(p1["longitude"] - p2["longitude"]) % 360.0
        return diff if diff <= 180 else 360 - diff

    # ═══════════════════════════════════════════════════════════
    # 7. Summary & Print (RAW DATA — no interpretation)
    # ═══════════════════════════════════════════════════════════
    def get_summary(self) -> dict:
        dom_name, dom_force = self.dominant_planet()
        sun_moon = self.aspect_angle("sun", "moon")
        asc = self._houses.get("ascendant", 0.0)
        visible_planets = [p for p in PLANETS if self.is_visible(p) is True]
        hidden_planets = [p for p in PLANETS if self.is_visible(p) is False]

        return {
            "birth": {
                "datetime": self.birth_dt.strftime("%Y-%m-%d %H:%M:%S"),
                "lat": self.lat, "lon": self.lon,
            },
            "dominant": {
                "planet": dom_name, "tidal_force": dom_force,
                "name_th": PLANET_NAMES.get(dom_name, dom_name),
            },
            "sun_moon_angle": sun_moon,
            "ascendant": asc,
            "visible_planets": visible_planets,
            "hidden_planets": hidden_planets,
            "house_system": self._houses.get("house_system", "Unknown"),
            "planet_count": len(self._planet_data),
        }

    def print_summary(self):
        """พิมพ์ข้อมูลดิบทั้งหมด — ไม่มีการตีความ (หน้าที่ของ AstroTranslate)"""
        s = self.get_summary()
        dom = s["dominant"]
        print(f"🌟 แรงดึงดูดหลัก: {dom['name_th']} ({dom['planet']}) — {dom['tidal_force']:.2e}")
        print(f"🌓 มุมอาทิตย์-จันทร์: {s['sun_moon_angle']:.2f}°")
        print(f"🌅 ลัคนา (Ascendant): {s['ascendant']:.2f}°")
        self.print_detailed_planets()
        self.print_houses()
        self.print_visible_hidden()
        self.print_aspects()

    def print_detailed_planets(self):
        """พิมพ์รายละเอียดของดาวเคราะห์ทุกดวง"""
        print(f"\n🪐 {'='*70}")
        print(f"🪐 รายละเอียดดาวเคราะห์ ณ วันที่เกิด (RAW DATA)")
        print(f"🪐 {'='*70}")
        print(f"{'ดาวเคราะห์':15s} | {'ลองจิจูด (°)':12s} | {'ระยะ (AU)':10s} | {'แรงไทดัล':12s} | {'ภพ':4s} | {'ขอบฟ้า':10s}")
        print(f"{'-'*15} | {'-'*12} | {'-'*10} | {'-'*12} | {'-'*4} | {'-'*10}")
        
        for name in self._planet_data:
            p = self._planet_data[name]
            name_th = PLANET_NAMES.get(name, name)
            lon = p["longitude"]
            dist = p["distance_au"]
            force = self.tidal_force(name)
            house = self.get_planet_house(name) or "-"
            visible = "เหนือ" if self.is_visible(name) else "ใต้" if self.is_visible(name) is False else "N/A"
            
            print(f"{name_th:15s} | {lon:11.2f}° | {dist:9.4f}  | {force:12.2e} | {str(house):4s} | {visible:10s}")
        
        print(f"🪐 {'='*70}")

    def print_houses(self):
        houses = self.get_all_planets_in_houses()
        print(f"\n🏠 {'='*50}")
        print(f"🏠 12 ภพ (House System: {self._houses.get('house_system', 'Unknown')})")
        print(f"🏠 {'='*50}")
        for house_num in range(1, 13):
            planets = houses[house_num]
            planet_names_th = [PLANET_NAMES.get(p, p) for p in planets]
            planet_list = ', '.join(planet_names_th) if planet_names_th else '(ว่าง)'
            print(f"🏠 ภพที่ {house_num:2d} | {HOUSE_NAMES_TH[house_num]:30s} | {planet_list}")
        print(f"🏠 {'='*50}")

    def print_visible_hidden(self):
        visible = [PLANET_NAMES.get(p, p) for p in self.get_summary()["visible_planets"]]
        hidden = [PLANET_NAMES.get(p, p) for p in self.get_summary()["hidden_planets"]]
        print(f"\n👁️ {'='*50}")
        print(f"👁️ Visible (เหนือขอบฟ้า — คุณรู้ตัว): {', '.join(visible) if visible else '(ไม่มี)'}")
        print(f"🌑 Hidden  (ใต้ขอบฟ้า — จิตใต้สำนึก): {', '.join(hidden) if hidden else '(ไม่มี)'}")
        print(f"👁️ {'='*50}")

    def print_aspects(self, orb: float = 8.0):
        """พิมพ์มุมสัมพันธ์ทั้งหมด"""
        aspects = self.get_all_aspects(orb)
        print(f"\n💫 {'='*50}")
        print(f"💫 มุมสัมพันธ์ระหว่างดาว (Aspects — orb {orb}°)")
        print(f"💫 {'='*50}")
        if not aspects:
            print("💫 ไม่พบมุมสำคัญ")
            return
        for a in aspects:
            print(f"💫 {a['symbol']} {a['planet1_th']:12s} — {a['planet2_th']:12s} | "
                  f"{a['aspect']:12s} | {a['angle']:6.2f}° | {a['force_type']}")
        print(f"💫 {'='*50}")


# ═══════════════════════════════════════════════════════════════
# Quick Test
# ═══════════════════════════════════════════════════════════════
if __name__ == "__main__":
    print("8/8/1992 16.49 ยะลา")
    calc = AstroCalculate(datetime(1992, 8, 8, 16, 49), 6.5417, 101.282)
    calc.print_summary()