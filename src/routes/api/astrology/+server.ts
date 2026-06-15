import type { RequestHandler } from './$types';
import { json } from '@sveltejs/kit';
import { createRequire } from 'node:module';

const req = createRequire(import.meta.url);

// ─── sweph (Swiss Ephemeris) ──────────────
const sweph = req('sweph');

// ─── lunar-javascript ─────────────────────
const Lunar = req('lunar-javascript');

const STEMS_TH = ['เจีย','อี่','ปิ่ง','ติง','อู้','จี่','เกิง','ซิน','เหริน','กุ่ย'];
const BRANCH_TH = ['🐀ชวด','🐂ฉลู','🐯ขาล','🐰เถาะ','🐲มะโรง','🐍มะเส็ง','🐴มะเมีย','🐐มะแม','🐵วอก','🐔ระกา','🐕จอ','🐷กุน'];
const ELEMENTS = ['ไม้','ไฟ','ดิน','ทอง','น้ำ'];
const ELEMENTS_MAP = [0,0,1,1,2,2,3,3,4,4];
const YIN = [1,0,1,0,1,0,1,0,1,0];
const ZHI_HIDDEN: number[][] = [[9],[5,9,7],[0,2,4],[1],[4,1,9],[2,6,4],[3,5],[5,3,1],[6,8,4],[7],[4,7,3],[8,0]];
const GAN = ['甲','乙','丙','丁','戊','己','庚','辛','壬','癸'];
const ZHI = ['子','丑','寅','卯','辰','巳','午','未','申','酉','戌','亥'];
const SHI_SHEN_NAMES = ['比肩','劫财','食神','伤官','偏财','正财','偏官','正官','偏印','正印'];

// ─── BAZI (lunar-javascript) ───────────────
function calcBazi(birthDate: string, birthTime: string) {
	const [y, m, d] = birthDate.split('-').map(Number);
	const [h] = birthTime.split(':').map(Number);
	const Solar = Lunar.Solar;
	const solar = Solar.fromYmd(y, m, d);
	const lunar = solar.getLunar();
	const time = Lunar.LunarTime.fromYmdHms(y, m, d, h, 0, 0);

	const yearG = lunar.getYearGanIndex(), yearZ = lunar.getYearZhiIndex();
	const monthG = lunar.getMonthGanIndex(), monthZ = lunar.getMonthZhiIndex();
	const dayG = lunar.getDayGanIndexExact2(), dayZ = lunar.getDayZhiIndexExact2();
	const hourG = time.getGanIndex(), hourZ = time.getZhiIndex();

	// Ten Gods
	const stemSS = lunar.getBaZiShiShenGan(); // [year, month, day, hour]
	const branchSS = lunar.getBaZiShiShenZhi(); // [[], [], [], []] for year, month, day, time

	const pillars = [
		{ stem: GAN[yearG], branch: ZHI[yearZ], stemTH: STEMS_TH[yearG], branchTH: BRANCH_TH[yearZ], element: ELEMENTS[ELEMENTS_MAP[yearG]], yin: YIN[yearG] ? 'หยิน' : 'หยาง', shiShen: stemSS[0], hidden: ZHI_HIDDEN[yearZ].map(i => GAN[i]+STEMS_TH[i]).join(' '), label: '年' },
		{ stem: GAN[monthG], branch: ZHI[monthZ], stemTH: STEMS_TH[monthG], branchTH: BRANCH_TH[monthZ], element: ELEMENTS[ELEMENTS_MAP[monthG]], yin: YIN[monthG] ? 'หยิน' : 'หยาง', shiShen: stemSS[1], hidden: ZHI_HIDDEN[monthZ].map(i => GAN[i]+STEMS_TH[i]).join(' '), label: '月' },
		{ stem: GAN[dayG], branch: ZHI[dayZ], stemTH: STEMS_TH[dayG], branchTH: BRANCH_TH[dayZ], element: ELEMENTS[ELEMENTS_MAP[dayG]], yin: YIN[dayG] ? 'หยิน' : 'หยาง', shiShen: '日主', hidden: ZHI_HIDDEN[dayZ].map(i => GAN[i]+STEMS_TH[i]).join(' '), label: '日' },
		{ stem: GAN[hourG], branch: ZHI[hourZ], stemTH: STEMS_TH[hourG], branchTH: BRANCH_TH[hourZ], element: ELEMENTS[ELEMENTS_MAP[hourG]], yin: YIN[hourG] ? 'หยิน' : 'หยาง', shiShen: stemSS[3], hidden: ZHI_HIDDEN[hourZ].map(i => GAN[i]+STEMS_TH[i]).join(' '), label: '时' },
	];

	// Special structures
	const dayElement = ELEMENTS[ELEMENTS_MAP[dayG]];
	const specialStructure = detectSpecial(yearG, monthG, dayG, yearZ, monthZ);

	return {
		dayMaster: `${GAN[dayG]} (${STEMS_TH[dayG]})`,
		dayMasterElement: `${dayElement} ${YIN[dayG] ? 'หยิน' : 'หยาง'}`,
		pillars,
		wuXing: [lunar.getBaZiWuXing()],
		naYin: lunar.getBaZiNaYin(),
		shiShenZhi: {
			year: lunar.getBaZiShiShenYearZhi(),
			month: lunar.getBaZiShiShenMonthZhi(),
			day: lunar.getBaZiShiShenDayZhi(),
			time: lunar.getBaZiShiShenTimeZhi(),
		},
		empty: (lunar.getDayXunKong() || '').split(''),
		chong: lunar.getChong(),
		sha: lunar.getSha(),
		specialStructure,
	};
}

function detectSpecial(yearG: number, monthG: number, dayG: number, yearZ: number, monthZ: number): string[] {
	// Simplified special pattern detection
	const patterns: string[] = [];
	const dayE = ELEMENTS_MAP[dayG % 10];
	const monthE = ELEMENTS_MAP[monthG % 10];
	const yearE = ELEMENTS_MAP[yearG % 10];
	
	// Same element in year, month, day stems → special pattern
	if (yearE === monthE && monthE === dayE) patterns.push('三合干');
	if (yearZ === monthZ) patterns.push('伏吟');
	
	return patterns;
}

// ─── WESTERN (sweph) ────────────────────────
function julianDay(y: number, m: number, d: number, h: number): number {
	if (m <= 2) { y--; m += 12; }
	const a = Math.floor(y / 100);
	const b = 2 - a + Math.floor(a / 4);
	return Math.floor(365.25 * (y + 4716)) + Math.floor(30.6001 * (m + 1)) + d + h / 24 + b - 1524.5;
}

const PLANET_NAMES = ['Sun','Moon','Mercury','Venus','Mars','Jupiter','Saturn','Uranus','Neptune','Pluto'];
const PLANET_TH = ['อาทิตย์','จันทร์','พุธ','ศุกร์','อังคาร','พฤหัสบดี','เสาร์','ยูเรนัส','เนปจูน','พลูโต'];
const ZODIAC = ['♈ Aries','♉ Taurus','♊ Gemini','♋ Cancer','♌ Leo','♍ Virgo','♎ Libra','♏ Scorpio','♐ Sagittarius','♑ Capricorn','♒ Aquarius','♓ Pisces'];
const ZODIAC_TH = ['เมษ','พฤษภ','เมถุน','กรกฎ','สิงห์','กันย์','ตุล','พิจิก','ธนู','มังกร','กุมภ์','มีน'];
const ELEM = ['Fire','Earth','Air','Water','Fire','Earth','Air','Water','Fire','Earth','Air','Water'];

function calcWestern(birthDate: string, birthTime: string) {
	const [y, m, d] = birthDate.split('-').map(Number);
	const [h] = birthTime.split(':').map(Number);
	const jd = julianDay(y, m, d, h);
	const planets = PLANET_NAMES.map((name, i) => {
		const res = sweph.calc_ut(jd, i, 0x000002); // 0x000002 = Swiss Ephemeris mode
		const lon = res.data[0];
		const sign = Math.floor(lon / 30) % 12;
		return { nameTH: PLANET_TH[i], name, sign: ZODIAC[sign], signTH: ZODIAC_TH[sign], degree: Math.floor(lon % 30), element: ELEM[sign], elementTH: ['ไฟ','ดิน','ลม','น้ำ'][sign % 4] };
	});
	const sunSign = Math.floor(planets[0].degree > 0 ? planets[0].degree : 0);
	const moonSign = Math.floor(planets[1].degree > 0 ? planets[1].degree : 0);
	return {
		sunSign: planets[0].sign, sunSignTH: planets[0].signTH,
		moonSign: planets[1].sign, moonSignTH: planets[1].signTH,
		risingSign: ZODIAC[Math.floor((jd - Math.floor(jd)) * 24 / 2)], risingSignTH: ZODIAC_TH[Math.floor((jd - Math.floor(jd)) * 24 / 2)],
		planets,
		ayanamsa: sweph.get_ayanamsa_ex_ut(jd, 0).data[0],
	};
}

// ─── INDIAN (sweph + ayanamsa) ─────────────
function calcIndian(birthDate: string, birthTime: string) {
	const [y, m, d] = birthDate.split('-').map(Number);
	const [h] = birthTime.split(':').map(Number);
	const jd = julianDay(y, m, d, h);
	const ayanamsa = sweph.get_ayanamsa_ex_ut(jd, 0).data[0];
	const RASHI = ['เมษ','พฤษภ','เมถุน','กรกฎ','สิงห์','กันย์','ตุล','พิจิก','ธนู','มังกร','กุมภ์','มีน'];
	const RASHI_EN = ['Aries','Taurus','Gemini','Cancer','Leo','Virgo','Libra','Scorpio','Sagittarius','Capricorn','Aquarius','Pisces'];
	const RASHI_LORD = ['Mars','Venus','Mercury','Moon','Sun','Mercury','Venus','Mars','Jupiter','Saturn','Saturn','Jupiter'];

	// Sun in sidereal zodiac
	const sunRes = sweph.calc_ut(jd, 0, 0);
	const sunSidereal = (sunRes.data[0] - ayanamsa + 360) % 360;
	const sunSign = Math.floor(sunSidereal / 30);

	// Moon
	const moonRes = sweph.calc_ut(jd, 1, 0);
	const moonSidereal = (moonRes.data[0] - ayanamsa + 360) % 360;
	const moonSign = Math.floor(moonSidereal / 30);

	// Lagna (Rising)
	const lagna = Math.floor((((sunRes.data[0] / 30) + (h / 24) * 12) % 12));

	// Nakshatra
	const nIdx = Math.floor((moonSidereal % 360) / 13.3333);
	const NAK = ['อัศวินี','ภรณี','กฤติกา','โรหิณี','มฤคศิระ','อารทรา','ปุนัพสุ','ปุษยะ','อัศเลษา','มาฆะ','ปูรพผลคุนี','อุตรผลคุนี','หัสตะ','จิตรา','สวาตี','วิสาขา','อนุราธะ','เชษฐะ','มูละ','ปูรพาษาฒ','อุตราษาฒ','ศรวณะ','ธนิษฐา','ศตภิษัช','ปูรพภัทรบท','อุตรภัทรบท','เรวดี'];
	const NAK_LORD = ['Ketu','Venus','Sun','Moon','Mars','Rahu','Jupiter','Saturn','Mercury','Ketu','Venus','Sun','Moon','Mars','Rahu','Jupiter','Saturn','Mercury','Ketu','Venus','Sun','Moon','Mars','Rahu','Jupiter','Saturn','Mercury'];

	return {
		sunSign: { name: RASHI[sunSign], en: RASHI_EN[sunSign], lord: RASHI_LORD[sunSign] },
		moonSign: { name: RASHI[moonSign], en: RASHI_EN[moonSign], lord: RASHI_LORD[moonSign] },
		lagna: { name: RASHI[lagna], en: RASHI_EN[lagna], lord: RASHI_LORD[lagna] },
		nakshatra: { name: NAK[nIdx], lord: NAK_LORD[nIdx], pada: Math.floor((moonSidereal % 13.3333) / 3.3333) + 1 },
	};
}

// ─── THAI ──────────────────────────────────
function calcThai(birthDate: string) {
	const [y, m, d] = birthDate.split('-').map(Number);
	const dt = new Date(y, m - 1, d);
	const thaiYear = y + 543;
	const zodiax = (y - 4) % 12;
	const thaiZodiac = ['ชวด','ฉลู','ขาล','เถาะ','มะโรง','มะเส็ง','มะเมีย','มะแม','วอก','ระกา','จอ','กุน'][zodiax];
	const days = ['อาทิตย์','จันทร์','อังคาร','พุธ','พฤหัสบดี','ศุกร์','เสาร์'];
	const colors = ['แดง','เหลือง','ชมพู','เขียว','ส้ม','ฟ้า','ม่วง'];
	const wd = dt.getDay();
	let sum = 0; for (const c of `${d}${m}${y}`) sum += parseInt(c);
	while (sum > 9) { let s = 0; for (const c of String(sum)) s += parseInt(c); sum = s; }
	return { thaiYear, thaiZodiac, birthDay: days[wd], planet: ['อาทิตย์','จันทร์','อังคาร','พุธ','พฤหัสบดี','ศุกร์','เสาร์'][wd], color: colors[wd], destinyNumber: sum, luckyDays: ['พฤหัส,ศุกร์','พุธ,เสาร์','อาทิตย์,พฤหัส','จันทร์,ศุกร์','อังคาร,อาทิตย์','พุธ,จันทร์','อังคาร,พฤหัส'][wd] };
}

// ─── HUMAN DESIGN (sweph) ──────────────────
function calcHumanDesign(birthDate: string, birthTime: string) {
	const [y, m, d] = birthDate.split('-').map(Number);
	const [h] = birthTime.split(':').map(Number);
	const jd = julianDay(y, m, d, h);

	// Personality Sun gate (1-64)
	const sunRes = sweph.calc_ut(jd, 0, 0);
	const sunLong = sunRes.data[0] % 360;
	const pGate = Math.floor(sunLong / (360 / 64)) + 1; // FIXED: +1
	const pLine = Math.floor((sunLong % (360 / 64)) / (360 / 64 / 6)) + 1;

	// Design Sun (88 days before birth)
	const designJd = jd - 88;
	const designSunRes = sweph.calc_ut(designJd, 0, 0);
	const designLong = designSunRes.data[0] % 360;
	const dGate = Math.floor(designLong / (360 / 64)) + 1; // FIXED: +1
	const dLine = Math.floor((designLong % (360 / 64)) / (360 / 64 / 6)) + 1;

	// All active gates (personality + design)
	const activeGates = new Set([pGate, dGate]);

	// Check which centers are defined (have at least one active gate)
	const hasHead = [61,63,64].some(g => activeGates.has(g));
	const hasAjna = [4,11,17,24,43,47].some(g => activeGates.has(g));
	const hasThroat = [8,12,16,20,23,31,33,35,45,56,62].some(g => activeGates.has(g));
	const hasG = [1,2,7,10,13,15,25,46].some(g => activeGates.has(g));
	const hasSacral = [3,5,9,14,27,29,34,42,59].some(g => activeGates.has(g));
	const hasEgo = [21,26,40,51].some(g => activeGates.has(g));
	const hasSP = [6,22,30,36,37,39,49,55].some(g => activeGates.has(g)); // Solar Plexus
	const hasSpleen = [16,18,28,32,44,48,50,57].some(g => activeGates.has(g));
	const hasRoot = [19,38,39,41,52,53,54,58,60].some(g => activeGates.has(g));

	// Motor centers that can connect to throat
	const throatGates = [8,12,16,20,23,31,33,35,45,56,62];
	const motorChannels: [number, number, string][] = [
		[34,20,'Sacral→Throat'],[14,8,'Sacral→Throat'],[5,48,'Sacral→Spleen'],[29,46,'Sacral→G'],
		[21,45,'Ego→Throat'],[26,44,'Ego→Spleen'],[40,37,'Ego→SP'],[51,25,'Ego→G'],
		[6,59,'SP→Sacral'],[22,12,'SP→Throat'],[30,41,'Root→SP'],[36,35,'SP→Throat'],
		[38,28,'Root→Spleen'],[39,55,'Root→SP'],[41,30,'Root→SP'],[19,49,'Root→SP'],
		[52,9,'Root→Sacral'],[53,42,'Root→Sacral'],[54,32,'Root→Spleen'],[58,18,'Root→Spleen'],
		[60,3,'Root→Sacral'],[50,27,'Spleen→Sacral'],[57,34,'Spleen→Sacral'],
	];
	const hasMotorToThroat = motorChannels.some(([g1, g2]) => {
		const bothActive = activeGates.has(g1) && activeGates.has(g2);
		return bothActive && (throatGates.includes(g1) || throatGates.includes(g2));
	});

	const defined: string[] = [];
	const undefined_: string[] = [];
	const checkCenters: [boolean, string][] = [[hasHead,'Head'],[hasAjna,'Ajna'],[hasThroat,'Throat'],[hasG,'G'],[hasEgo,'Ego'],[hasSP,'Solar Plexus'],[hasSacral,'Sacral'],[hasSpleen,'Spleen'],[hasRoot,'Root']];
	for (const [has, name] of checkCenters) {
		if (has) defined.push(name); else undefined_.push(name);
	}

	let type = 'Reflector', strategy = 'Wait 28 days', authority = 'Lunar', aura = 'Sampling';
	const numDefined = defined.length;

	const GATE_NAMES: Record<number, string> = { 1:'Self-Expression',2:'Direction',3:'Ordering',4:'Formulization',5:'Fixed Rhythms',6:'Friction',7:'Role of Self',8:'Contribution',9:'Focus',10:'Self Behavior',11:'Ideas',12:'Caution',13:'Listener',14:'Power Skills',15:'Extremes',16:'Skills',17:'Opinions',18:'Correction',19:'Wanting',20:'Now',21:'Hunter',22:'Grace/Openness',23:'Assimilation',24:'Rationalizing',25:'Spirit of Self',26:'Egoist',27:'Caring',28:'Game Player',29:'Saying Yes',30:'Feelings',31:'Leading',32:'Continuity',33:'Privacy',34:'Power',35:'Progress',36:'Crisis',37:'Friendship',38:'Fighter',39:'Provocation',40:'Aloneness',41:'Fantasy',42:'Growth',43:'Insight',44:'Alertness',45:'Gatherer',46:'Body Love',47:'Realizing',48:'Depth',49:'Principles',50:'Values',51:'Shock',52:'Inaction',53:'Beginnings',54:'Ambition',55:'Spirit',56:'Stimulation',57:'Intuitive Clarity',58:'Joy',59:'Sexuality',60:'Limitation',61:'Mystery',62:'Detail',63:'Doubt',64:'Confusion' };

	return {
		type, strategy, authority, aura,
		definedCenters: defined, undefinedCenters: undefined_,
		personalityGate: { num: pGate, line: pLine, name: GATE_NAMES[pGate] || `Gate ${pGate}` },
		designGate: { num: dGate, line: dLine, name: GATE_NAMES[dGate] || `Gate ${dGate}` },
	};
}

// ─── NAME NUMEROLOGY ──────────────────────
const THAI_N: Record<string, number> = {
	'ก':1,'ด':1,'ท':1,'ถ':1,'ภ':1,'ฤ':1,'า':1,'ุ':1,'ำ':1,'่':1,
	'ข':2,'ช':2,'บ':2,'ป':2,'ง':2,'เ':2,'แ':2,'ู':2,'้':2,
	'ฆ':3,'ฑ':3,'ฒ':3,'ต':3,'ฃ':3,'๊':3,
	'ค':4,'ธ':4,'ร':4,'ญ':4,'ษ':4,'โ':4,'ะ':4,'ิ':4,'ั':4,
	'ฉ':5,'ณ':5,'ฌ':5,'น':5,'ม':5,'ห':5,'ฮ':5,'ฎ':5,'ฬ':5,'ึ':5,
	'จ':6,'ล':6,'ว':6,'อ':6,'ใ':6,
	'ศ':7,'ส':7,'ซ':7,'ี':7,'ื':7,'๋':7,
	'ย':8,'พ':8,'ฟ':8,'ผ':8,'ฝ':8,
	'ฏ':9,'ฐ':9,'ไ':9,'์':9,
};
const ENG: Record<string, number> = { 'a':1,'i':1,'j':1,'q':1,'y':1,'b':2,'k':2,'r':2,'c':3,'g':3,'l':3,'s':3,'d':4,'m':4,'t':4,'e':5,'h':5,'n':5,'x':5,'u':6,'v':6,'w':6,'o':7,'z':7,'f':8,'p':8, };
function red(n: number): number { while (n > 9) { let s = 0; for (const c of String(n)) s += parseInt(c); n = s; } return n; }
function calcName(fn: string, ln: string) {
	const sm = (n: string) => { let s = 0; for (const c of n.toLowerCase()) s += THAI_N[c] || ENG[c] || 0; return red(s); };
	const f = sm(fn), l = sm(ln), t = red(f + l);
	const m: Record<number, string> = { 1:'ผู้นำ — กล้าหาญ',2:'นุ่มนวล — มีเสน่ห์',3:'นักพูด — สื่อสารดี',4:'นักวางแผน — ซื่อสัตย์',5:'นักปราชญ์ — รอบรู้',6:'นักสร้าง — รักศิลปะ',7:'นักสู้ — อดทน',8:'นักธุรกิจ — มั่งคั่ง',9:'นักบุญ — เมตตา' };
	return { firstName: f, lastName: l, total: t, meaning: m[t] || '', name: fn, surname: ln };
}

// ─── API Handler ──────────────────────────
export const POST: RequestHandler = async ({ request }) => {
	try {
		const body = await request.json();
		const { type, birthDate, birthTime, birthPlace, lat, lon, firstName, lastName } = body;

		// Set topographic position for sweph
		if (lat !== undefined && lon !== undefined) {
			try { sweph.set_topo(lon, lat, 0); } catch {}
		}

		if (type === 'bazi') return json({ success: true, data: calcBazi(birthDate, birthTime) });
		if (type === 'western') return json({ success: true, data: calcWestern(birthDate, birthTime) });
		if (type === 'indian') return json({ success: true, data: calcIndian(birthDate, birthTime) });
		if (type === 'thai') return json({ success: true, data: calcThai(birthDate) });
		if (type === 'humandesign') return json({ success: true, data: calcHumanDesign(birthDate, birthTime) });
		if (type === 'name') return json({ success: true, data: calcName(firstName, lastName) });

		// Synthesize: call all engines then send to AI for interpretation
		if (type === 'synthesize') {
			const all = {
				bazi: calcBazi(birthDate, birthTime),
				western: calcWestern(birthDate, birthTime),
				indian: calcIndian(birthDate, birthTime),
				thai: calcThai(birthDate),
				humandesign: calcHumanDesign(birthDate, birthTime),
				birthDate, birthTime, birthPlace, lat, lon,
			};

			const prompt = `คุณคือโหราจารย์ในตำนานที่เชี่ยวชาญทุกศาสตร์ ใช้ข้อมูลดวงชะตาที่คำนวณจาก Swiss Ephemeris และ lunar-javascript ด้านล่างนี้เพื่อพยากรณ์แบบองค์รวม:

## วันเกิด
${birthDate} เวลา ${birthTime} สถานที่ ${birthPlace}

## 🀄 Bazi (สี่เสาหลัก)
- Day Master: ${all.bazi.dayMaster} (${all.bazi.dayMasterElement})
- Pillars: ${all.bazi.pillars.map((p: any) => `[${p.label}] ${p.stem}${p.branch} (${p.element} ${p.shiShen})`).join(', ')}
- 十神: ${JSON.stringify(all.bazi.shiShenZhi)}
- 空亡: ${all.bazi.empty?.join(',') || '—'} · 冲: ${all.bazi.chong || '—'} · 煞: ${all.bazi.sha || '—'}

## 🌍 Western
- Sun: ${all.western.sunSign} · Moon: ${all.western.moonSign} · Rising: ${all.western.risingSign}
- Planets: ${all.western.planets.map((p: any) => `${p.nameTH}@${p.sign}${p.degree}°`).join(', ')}

## 🕉️ Vedic
- Sun: ${all.indian.sunSign.name} · Moon: ${all.indian.moonSign.name} · Lagna: ${all.indian.lagna.name}
- Nakshatra: ${all.indian.nakshatra.name} pada ${all.indian.nakshatra.pada}

## 🇹🇭 Thai
- พ.ศ.${all.thai.thaiYear} ปี${all.thai.thaiZodiac} · วัน${all.thai.birthDay} · ดาว${all.thai.planet}
- เลขดวง ${all.thai.destinyNumber}

## 🔷 Human Design
- Type: ${all.humandesign.type} · Strategy: ${all.humandesign.strategy} · Authority: ${all.humandesign.authority}

---
วิเคราะห์แบบองค์รวม:
1. แก่นแท้ของดวงชะตานี้คืออะไร
2. จุดแข็งและจุดที่ต้องระวังในชีวิต
3. การงาน การเงิน ความรัก (ภาพรวม)
4. ช่วงเวลา/ปีที่ควรระวังและที่ควรลงมือ
5. คำแนะนำเสริมดวง (สี, หิน, ทิศ, วันที่ดี)
6. ข้อความให้กำลังใจปิดท้าย

ตอบเป็นภาษาไทยให้สละสลวย มีพลัง mystic แต่แฝงด้วยแง่คิดลึกซึ้ง`;
			const text = await callJinx(prompt);
			return json({ success: true, data: text });
		}

		return json({ success: false, error: 'Unknown type' }, { status: 400 });
	} catch (e) {
		return json({ success: false, error: e instanceof Error ? e.message : 'Unknown' }, { status: 500 });
	}
};

async function callJinx(prompt: string): Promise<string> {
	const HF_SPACE = 'https://worrrrrr-jinx.hf.space';
	const res = await fetch(`${HF_SPACE}/gradio_api/call/chat_interface`, {
		method: 'POST', headers: { 'Content-Type': 'application/json' },
		body: JSON.stringify({ data: [prompt, []] })
	});
	if (!res.ok) throw new Error('Jinx request failed');
	const { event_id } = await res.json();
	const sseRes = await fetch(`${HF_SPACE}/gradio_api/call/chat_interface/${event_id}`, {
		headers: { Accept: 'text/event-stream' }
	});
	const text = await sseRes.text();
	const match = text.match(/data:\s*(.+)/);
	if (!match) throw new Error('No SSE data');
	return JSON.parse(match[1])[0] || '';
}
