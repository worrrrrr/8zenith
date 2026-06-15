// ─────────────────────────────────────────────
// Astrology Engines — Bazi, Indian, Western, Thai, Human Design, Name Numerology
// ─────────────────────────────────────────────

export interface BirthData {
	year: number;
	month: number;   // 1-12
	day: number;
	hour: number;    // 0-23
	minute: number;
	place: string;
}

// ─── BAZI (สี่เสาหลัก) ───────────────────────
const STEMS = ['甲','乙','丙','丁','戊','己','庚','辛','壬','癸'];
const BRANCHES = ['子','寅','卯','辰','巳','午','未','申','酉','戌','亥','丑'];
const STEMS_TH = ['เจีย','อี่','ปิ่ง','ติง','อู้','จี่','เกิง','ซิน','เหริน','กุ่ย'];
const BRANCH_TH = ['ชวด','ขาล','เถาะ','มะโรง','มะเส็ง','มะเมีย','มะแม','วอก','ระกา','จอ','กุน','ฉลู'];
const ELEMENTS = ['ไม้','ไฟ','ดิน','ทอง','น้ำ'];
const ELEMENTS_STEM = [0,0,1,1,2,2,3,3,4,4]; // ไม้ ไม้ ไฟ ไฟ ดิน ดิน ทอง ทอง น้ำ น้ำ
const YIN_STEM = [1,0,1,0,1,0,1,0,1,0]; // 1=yin, 0=yang

export function calcBazi(d: BirthData) {
	const solarTerm = getSolarTermIndex(d.year, d.month, d.day);
	
	// Year pillar
	const yearStem = (d.year - 4) % 10;
	const yearBranch = (d.year - 4) % 12;
	
	// Month pillar (based on solar terms)
	const monthStem = (yearStem * 2 + solarTerm) % 10;
	const monthBranch = solarTerm % 12;
	
	// Day pillar (approximate)
	const daysFromBase = daysFromEpoch(d.year, d.month, d.day);
	const dayStem = (daysFromBase + 9) % 10;
	const dayBranch = (daysFromBase + 5) % 12;
	
	// Hour pillar
	const hourBranch = Math.floor((d.hour + 1) / 2) % 12;
	const hourStem = (dayStem * 2 + hourBranch) % 10;
	
	// Day Master element
	const dayElement = ELEMENTS[ELEMENTS_STEM[dayStem]];
	const dayYin = YIN_STEM[dayStem] ? 'หยิน' : 'หยาง';
	
	return {
		pillars: [
			{ stem: STEMS[yearStem], branch: BRANCHES[yearBranch], stemTH: STEMS_TH[yearStem], branchTH: BRANCH_TH[yearBranch], label: 'ปี' },
			{ stem: STEMS[monthStem], branch: BRANCHES[monthBranch], stemTH: STEMS_TH[monthStem], branchTH: BRANCH_TH[monthBranch], label: 'เดือน' },
			{ stem: STEMS[dayStem], branch: BRANCHES[dayBranch], stemTH: STEMS_TH[dayStem], branchTH: BRANCH_TH[dayBranch], label: 'วัน' },
			{ stem: STEMS[hourStem], branch: BRANCHES[hourBranch], stemTH: STEMS_TH[hourStem], branchTH: BRANCH_TH[hourBranch], label: 'ชั่วโมง' },
		],
		dayMaster: `${STEMS[dayStem]} (${STEMS_TH[dayStem]})`,
		dayMasterElement: `${dayElement} ${dayYin}`,
	};
}

function getSolarTermIndex(year: number, month: number, day: number): number {
	// Approximate solar term boundaries
	const terms = [5,19,4,19,6,21,6,21,7,23,8,23,8,23,8,23,8,23,8,23,7,22,7,22];
	const idx = (month - 1) * 2;
	if (day < terms[idx]) return month - 1;
	if (day >= terms[idx + 1] && idx + 1 < 24) return month;
	return month - 1;
}

function daysFromEpoch(year: number, month: number, day: number): number {
	const y = year - 1900;
	let d = y * 365 + Math.floor((y + 3) / 4);
	const md = [0,31,59,90,120,151,181,212,243,273,304,334];
	d += md[month - 1] + day;
	if (month > 2 && (year % 4 === 0 && (year % 100 !== 0 || year % 400 === 0))) d += 1;
	return d;
}

// ─── INDIAN / VEDIC ────────────────────────
const RASHI = ['เมษ','พฤษภ','มิถุน','กรกฎ','สิงห์','กันย์','ตุล','พิจิก','ธนู','มังกร','กุมภ์','มีน'];
const RASHI_EN = ['Aries','Taurus','Gemini','Cancer','Leo','Virgo','Libra','Scorpio','Sagittarius','Capricorn','Aquarius','Pisces'];
const RASHI_LORD = ['Mars','Venus','Mercury','Moon','Sun','Mercury','Venus','Mars','Jupiter','Saturn','Saturn','Jupiter'];
const NAKSHATRA = ['อัศวินี','ภรณี','กฤติกา','โรหิณี','มฤคศิระ','อารทรา','ปุนัพสุ','ปุษยะ','อัศเลษา','มาฆะ','ปูรพผลคุนี','อุตรผลคุนี','หัสตะ','จิตรา','สวาตี','วิสาขา','อนุราธะ','เชษฐะ','มูละ','ปูรพาษาฒ','อุตราษาฒ','ศรวณะ','ธนิษฐา','ศตภิษัช','ปูรพภัทรบท','อุตรภัทรบท','เรวดี'];
const NAK_LORD = ['Ketu','Venus','Sun','Moon','Mars','Rahu','Jupiter','Saturn','Mercury','Ketu','Venus','Sun','Moon','Mars','Rahu','Jupiter','Saturn','Mercury','Ketu','Venus','Sun','Moon','Mars','Rahu','Jupiter','Saturn','Mercury'];

export function calcIndian(d: BirthData) {
	const dayOfYear = monthDayToDayOfYear(d.month, d.day);
	const sunLong = (dayOfYear / 365.25) * 360;
	const moonLong = (sunLong + (d.hour * 15) + (d.minute * 0.25) + 180) % 360;
	
	const sunSign = Math.floor(sunLong / 30) % 12;
	const moonSign = Math.floor(moonLong / 30) % 12;
	const lagna = Math.floor(((d.hour * 60 + d.minute) / 1440) * 360 / 30) % 12;
	
	const nakshatraIndex = Math.floor((moonLong % 360) / (360 / 27));
	const pada = Math.floor(((moonLong % 360) % (360 / 27)) / (360 / 27 / 4)) + 1;
	
	return {
		sunSign: { name: RASHI[sunSign], en: RASHI_EN[sunSign], lord: RASHI_LORD[sunSign] },
		moonSign: { name: RASHI[moonSign], en: RASHI_EN[moonSign], lord: RASHI_LORD[moonSign] },
		lagna: { name: RASHI[lagna], en: RASHI_EN[lagna], lord: RASHI_LORD[lagna] },
		nakshatra: { name: NAKSHATRA[nakshatraIndex], lord: NAK_LORD[nakshatraIndex], pada },
	};
}

// ─── WESTERN ────────────────────────────────
const ZODIAC = ['♈ Aries','♉ Taurus','♊ Gemini','♋ Cancer','♌ Leo','♍ Virgo','♎ Libra','♏ Scorpio','♐ Sagittarius','♑ Capricorn','♒ Aquarius','♓ Pisces'];
const ZODIAC_TH = ['ราศีเมษ','ราศีพฤษภ','ราศีเมถุน','ราศีกรกฎ','ราศีสิงห์','ราศีกันย์','ราศีตุล','ราศีพิจิก','ราศีธนู','ราศีมังกร','ราศีกุมภ์','ราศีมีน'];
const PLANETS = ['Sun','Moon','Mercury','Venus','Mars','Jupiter','Saturn','Uranus','Neptune','Pluto'];
const PLANET_TH = ['อาทิตย์','จันทร์','พุธ','ศุกร์','อังคาร','พฤหัส','เสาร์','ยูเรนัส','เนปจูน','พลูโต'];
const ELEMENTS_ZODIAC = ['Fire','Earth','Air','Water','Fire','Earth','Air','Water','Fire','Earth','Air','Water'];
const ELEMENTS_TH = ['ไฟ','ดิน','ลม','น้ำ'];

export function calcWestern(d: BirthData) {
	const dayOfYear = monthDayToDayOfYear(d.month, d.day);
	const baseLong = (dayOfYear / 365.25) * 360;
	
	// Approximate planetary positions at birth
	const planets = PLANETS.map((name, i) => {
		const offset = [0, 150, 45, 72, 220, 315, 180, 260, 340, 90][i];
		const long = (baseLong + offset + (d.year - 2000) * [0, 13, 4.1, 1.6, 0.53, 0.08, 0.03, 0.01, 0.006, 0.004][i]) % 360;
		const sign = Math.floor(long / 30) % 12;
		return { name, nameTH: PLANET_TH[i], sign: ZODIAC[sign], signTH: ZODIAC_TH[sign], element: ELEMENTS_ZODIAC[sign], elementTH: ELEMENTS_TH[ELEMENTS_ZODIAC.indexOf(ELEMENTS_ZODIAC[sign])], degree: Math.round(long % 30) };
	});
	
	const sunSign = Math.floor(baseLong / 30) % 12;
	const moonSign = Math.floor(((baseLong + 150) % 360) / 30) % 12;
	const risingSign = Math.floor(((d.hour * 60 + d.minute) / 1440) * 360 / 30) % 12;
	
	return { sunSign: ZODIAC[sunSign], moonSign: ZODIAC[moonSign], risingSign: ZODIAC[risingSign], sunSignTH: ZODIAC_TH[sunSign], moonSignTH: ZODIAC_TH[moonSign], risingSignTH: ZODIAC_TH[risingSign], planets };
}

// ─── THAI ASTROLOGY ────────────────────────
const THAI_YEARS = ['ชวด','ฉลู','ขาล','เถาะ','มะโรง','มะเส็ง','มะเมีย','มะแม','วอก','ระกา','จอ','กุน'];
const THAI_PLANETS = ['อาทิตย์','จันทร์','อังคาร','พุธ','พฤหัสบดี','ศุกร์','เสาร์','ราหู','เกตุ','มฤตยู'];
const THAI_DAYS = ['อาทิตย์','จันทร์','อังคาร','พุธ','พฤหัสบดี','ศุกร์','เสาร์'];
const THAI_COLORS = ['แดง','เหลือง','ชมพู','เขียว','ส้ม','ฟ้า','ม่วง'];

export function calcThai(d: BirthData) {
	const thaiYear = d.year + 543;
	const thaiZodiac = THAI_YEARS[(d.year - 4) % 12];
	
	const dateObj = new Date(d.year, d.month - 1, d.day);
	const weekday = dateObj.getDay();
	
	const dayNum = d.day;
	const thaiPlanet = THAI_PLANETS[weekday];
	const thaiColor = THAI_COLORS[weekday];
	
	// Thai numerology: sum digits of birth date
	const dateStr = `${d.day}${d.month}${d.year}`;
	let sum = 0;
	for (const ch of dateStr) sum += parseInt(ch);
	while (sum > 9) { let s = 0; for (const ch of String(sum)) s += parseInt(ch); sum = s; }
	
	// Lucky/unlucky based on day of week
	const luckyDays: Record<number, string> = { 0:'พฤหัส,ศุกร์', 1:'พุธ,เสาร์', 2:'อาทิตย์,พฤหัส', 3:'จันทร์,ศุกร์', 4:'อังคาร,อาทิตย์', 5:'พุธ,จันทร์', 6:'อังคาร,พฤหัส' };
	
	return {
		thaiYear, thaiZodiac,
		birthDay: THAI_DAYS[weekday],
		planet: thaiPlanet,
		color: thaiColor,
		destinyNumber: sum,
		luckyDays: luckyDays[weekday] || '',
	};
}

// ─── HUMAN DESIGN (Ra Uru Hu) ─────────────

// 64 Gates of the Rave I-Ching
const GATE_NAMES: Record<number, string> = {
	1: 'Self-Expression · The Creative', 2: 'Receptivity · Direction of Self', 3: 'Ordering · Difficulty at Beginning',
	4: 'Formulization · Youthful Folly', 5: 'Fixed Rhythms · Waiting', 6: 'Friction · Conflict',
	7: 'Role of Self · The Army', 8: 'Contribution · Holding Together', 9: 'Focus · Taming Power of Small',
	10: 'Self Behavior · Treading', 11: 'Ideas · Peace', 12: 'Caution · Standstill',
	13: 'Listener · Fellowship', 14: 'Power Skills · Possession in Great Measure', 15: 'Extremes · Modesty',
	16: 'Skills · Enthusiasm', 17: 'Opinions · Following', 18: 'Correction · Work on Decay',
	19: 'Wanting · Approach', 20: 'Now · Contemplation', 21: 'Hunter · Biting Through',
	22: 'Grace · Openness', 23: 'Assimilation · Splitting Apart', 24: 'Rationalizing · Return',
	25: 'Spirit of Self · Innocence', 26: 'Egoist · Taming Power of Great', 27: 'Caring · Nourishment',
	28: 'Game Player · Preponderance of Great', 29: 'Saying Yes · Abysmal', 30: 'Feelings · Clinging Fire',
	31: 'Leading · Influence', 32: 'Continuity · Duration', 33: 'Privacy · Retreat',
	34: 'Power · Great Power', 35: 'Progress · Change', 36: 'Crisis · Darkening of Light',
	37: 'Friendship · Family', 38: 'Fighter · Opposition', 39: 'Provocation · Obstruction',
	40: 'Aloneness · Deliverance', 41: 'Fantasy · Decrease', 42: 'Growth · Increase',
	43: 'Insight · Breakthrough', 44: 'Alertness · Coming to Meet', 45: 'Gatherer · Gathering Together',
	46: 'Body Love · Pushing Upward', 47: 'Realizing · Oppression', 48: 'Depth · The Well',
	49: 'Principles · Revolution', 50: 'Values · The Cauldron', 51: 'Shock · Arousing',
	52: 'Inaction · Keeping Still', 53: 'Beginnings · Development', 54: 'Ambition · Marrying Maiden',
	55: 'Spirit · Abundance', 56: 'Stimulation · The Wanderer', 57: 'Intuitive Clarity · Gentle Penetration',
	58: 'Joy · The Joyous', 59: 'Sexuality · Dispersion', 60: 'Limitation · Acceptance',
	61: 'Mystery · Inner Truth', 62: 'Detail · Preponderance of Small', 63: 'Doubt · After Completion',
	64: 'Confusion · Before Completion',
};

// Centers and their gates
const SACRAL = new Set([3,5,9,14,27,29,34,42,59]);
const ROOT = new Set([19,38,39,41,52,53,54,58,60]);
const SPLEEN = new Set([16,18,28,32,44,48,50,57]);
const SOLAR_PLEXUS = new Set([6,22,30,36,37,49,55]);
const HEART_EGO = new Set([21,26,40,51]);
const G_CENTER = new Set([1,2,7,10,13,15,25,46]);
const THROAT = new Set([8,12,16,20,23,31,33,35,45,56,62]);
const AJNA = new Set([4,11,17,24,43,47]);
const HEAD = new Set([61,63,64]);

// Channels connecting gates
const CHANNELS: [number, number, string, string][] = [
	[1,8,'Inspiration','G → Throat | Individual Creative'], [2,14,'The Beat','G → Sacral | Individual Direction'],
	[3,60,'Mutation','Sacral → Root | Individual Pulse'], [4,63,'Logic','Head → Ajna | Collective Logic'],
	[5,15,'Rhythm','Sacral → G | Collective Flow'], [6,59,'Mating','Solar Plexus → Sacral | Tribal Intimacy'],
	[7,31,'Alpha','G → Throat | Collective Leadership'], [9,52,'Concentration','Sacral → Root | Collective Logic'],
	[10,20,'Awakening','G → Throat | Individual Awareness'], [11,56,'Curiosity','Ajna → Throat | Collective Logic'],
	[12,22,'Openness','Solar Plexus → Throat | Individual Expression'], [13,33,'Prodigal','G → Throat | Collective History'],
	[16,48,'Talent','Spleen → Throat | Collective Skill'], [17,62,'Acceptance','Ajna → Throat | Collective Logic'],
	[18,58,'Judgment','Spleen → Root | Collective Correction'], [19,49,'Synthesis','Root → Solar Plexus | Tribal Sensitivity'],
	[20,34,'Charisma','Sacral → Throat | Individual Manifestation'], [20,57,'Brainwave','Spleen → Throat | Individual Awareness'],
	[21,45,'Money','Heart → Throat | Tribal Material'], [23,43,'Structuring','Ajna → Throat | Individual Insight'],
	[24,61,'Awareness','Head → Ajna | Individual Knowing'], [25,51,'Initiation','G → Heart | Individual Will'],
	[26,44,'Surrender','Spleen → Heart | Tribal Instincts'], [27,50,'Preservation','Sacral → Spleen | Tribal Protection'],
	[28,38,'Struggle','Spleen → Root | Individual Survival'], [29,46,'Discovery','Sacral → G | Collective Experience'],
	[30,41,'Recognition','Root → Solar Plexus | Collective Desire'], [32,54,'Transformation','Spleen → Root | Tribal Ambition'],
	[34,57,'Power','Sacral → Spleen | Individual Sustenance'], [35,36,'Transitoriness','Solar Plexus → Throat | Collective Crisis'],
	[37,40,'Community','Solar Plexus → Heart | Tribal Bonding'], [39,55,'Emoting','Root → Solar Plexus | Individual Mood'],
	[42,53,'Maturation','Root → Sacral | Collective Development'], [47,64,'Abstraction','Head → Ajna | Collective Logic'],
];

export function calcHumanDesign(d: BirthData) {
	const dayOfYear = monthDayToDayOfYear(d.month, d.day);
	const sunLong = (dayOfYear / 365.25) * 360;

	// Personality (conscious) - birth date
	const pSunGate = Math.floor(sunLong / (360 / 64));
	const pSunLine = Math.floor((sunLong % (360 / 64)) / (360 / 64 / 6)) + 1;

	// Design (unconscious) - 88° solar arc before birth (~88 days)
	const designDayOfYear = ((dayOfYear - 88) + 365) % 365;
	const designLong = (designDayOfYear / 365.25) * 360;
	const dSunGate = Math.floor(designLong / (360 / 64));
	const dSunLine = Math.floor((designLong % (360 / 64)) / (360 / 64 / 6)) + 1;

	// Find active channels between personality and design gates
	const activeChannels = CHANNELS.filter(([g1, g2]) =>
		(g1 === pSunGate || g2 === pSunGate || g1 === dSunGate || g2 === dSunGate)
	);

	// Determine defined centers
	const definedCenters = new Set<string>();
	const allGates = [pSunGate, dSunGate];
	activeChannels.forEach(([g1, g2]) => {
		allGates.push(g1, g2);
	});

	// Check which centers are defined by active gates
	const centerCheck: [Set<number>, string][] = [
		[HEAD, 'Head'], [AJNA, 'Ajna'], [THROAT, 'Throat'],
		[G_CENTER, 'G'], [HEART_EGO, 'Heart-Ego'], [SOLAR_PLEXUS, 'Solar Plexus'],
		[SACRAL, 'Sacral'], [SPLEEN, 'Spleen'], [ROOT, 'Root'],
	];
	centerCheck.forEach(([gates, name]) => {
		if (gates.size > 0 && Array.from(gates).some(g => allGates.includes(g))) {
			definedCenters.add(name);
		}
	});

	// Type determination (Ra Uru Hu's criteria)
	const hasSacral = definedCenters.has('Sacral');
	const hasMotorToThroat = activeChannels.some(([g1, g2, , desc]) =>
		desc.includes('Throat') && (desc.includes('Sacral') || desc.includes('Heart') || desc.includes('Root') || desc.includes('Plexus'))
	);
	const hasAnyMotor = definedCenters.has('Sacral') || definedCenters.has('Heart-Ego') || definedCenters.has('Root') || definedCenters.has('Solar Plexus');
	const totalDefined = definedCenters.size;

	let type = 'Reflector';
	let strategy = 'Wait a full lunar cycle (28 days) before major decisions';
	let authority = 'Lunar (Reflector)';
	let aura = 'Resistant / Sampling';

	if (totalDefined === 0) {
		type = 'Reflector'; strategy = 'Wait 28 days (lunar cycle)';
		authority = 'Lunar'; aura = 'Resistant / Sampling';
	} else if (hasSacral && !hasMotorToThroat) {
		type = 'Generator'; strategy = 'Wait to Respond';
		authority = 'Sacral'; aura = 'Open & Enveloping';
	} else if (hasSacral && hasMotorToThroat) {
		type = 'Manifesting Generator'; strategy = 'Wait to Respond, then Inform';
		authority = definedCenters.has('Solar Plexus') ? 'Emotional (wait for clarity)' : 'Sacral';
		aura = 'Open & Enveloping';
	} else if (!hasSacral && hasMotorToThroat) {
		type = 'Manifestor'; strategy = 'Inform before acting';
		authority = definedCenters.has('Solar Plexus') ? 'Emotional' : definedCenters.has('Spleen') ? 'Splenic (spontaneous)' : 'Heart-Ego';
		aura = 'Closed & Repelling';
	} else if (!hasSacral && !hasMotorToThroat && hasAnyMotor) {
		type = 'Projector'; strategy = 'Wait for the Invitation (recognition)';
		authority = definedCenters.has('Solar Plexus') ? 'Emotional (wait for clarity)' : definedCenters.has('Spleen') ? 'Splenic' : definedCenters.has('G') ? 'Self (G-directed)' : 'Mental (environmental)';
		aura = 'Focused & Absorbing';
	}

	const typeInfo: Record<string, { desc: string; pop: string; signature: string; notSelf: string }> = {
		'Generator': { desc: 'ผู้สร้างพลัง — Sacral ตอบสนองต่อชีวิต', pop: '~37%', signature: 'Satisfaction (ความพึงพอใจ)', notSelf: 'Frustration (หงุดหงิด)' },
		'Manifesting Generator': { desc: 'Generator ที่ Manifest ได้ — เร็ว หลายเลน', pop: '~33%', signature: 'Satisfaction & Peace', notSelf: 'Frustration & Anger' },
		'Projector': { desc: 'ผู้ชี้นำ — มองเห็นผู้อื่นและชี้นำทาง', pop: '~20%', signature: 'Success (ความสำเร็จ)', notSelf: 'Bitterness (ขมขื่น)' },
		'Manifestor': { desc: 'ผู้ริเริ่ม — ลงมือทำกระทันหัน ทรงพลัง', pop: '~9%', signature: 'Peace (สันติ)', notSelf: 'Anger (โกรธ)' },
		'Reflector': { desc: 'กระจกส่องสังคม — สะท้อนสิ่งแวดล้อม', pop: '~1%', signature: 'Surprise (ประหลาดใจ)', notSelf: 'Disappointment (ผิดหวัง)' },
	};

	return {
		type, typeInfo: typeInfo[type],
		strategy, authority, aura,
		definedCenters: Array.from(definedCenters),
		undefinedCenters: ['Head','Ajna','Throat','G','Heart-Ego','Solar Plexus','Sacral','Spleen','Root'].filter(c => !definedCenters.has(c)),
		personalityGate: { num: pSunGate, line: pSunLine, name: GATE_NAMES[pSunGate] || `Gate ${pSunGate}` },
		designGate: { num: dSunGate, line: dSunLine, name: GATE_NAMES[dSunGate] || `Gate ${dSunGate}` },
		activeChannels: activeChannels.map(([g1, g2, name, desc]) => ({ gate1: g1, gate2: g2, name, desc })),
		incarnationCross: getIncarnationCross(pSunGate, dSunGate),
	};
}

function getIncarnationCross(pGate: number, dGate: number): string {
	const crosses: Record<string, string> = {
		'1_2': 'RAX of Maya 1', '7_13': 'RAX of Maya 2', '10_25': 'RAX of Maya 3', '15_46': 'RAX of Maya 4',
		'3_20': 'RAX of Penetration 1', '42_53': 'RAX of Penetration 2', '34_57': 'RAX of Penetration 3',
		'4_49': 'RAX of Explanation 1', '8_14': 'RAX of Explanation 2', '43_23': 'RAX of Explanation 3',
		'5_35': 'RAX of Consciousness 1', '9_16': 'RAX of Consciousness 2', '11_26': 'RAX of Consciousness 3',
	};
	const key = `${Math.min(pGate, dGate)}_${Math.max(pGate, dGate)}`;
	return crosses[key] || 'Individual Cross';
}

// ─── NAME NUMEROLOGY (เลขศาสตร์) ────────────
// ตารางเทียบค่าหลักเลขศาสตร์ไทย-อังกฤษ
const THAI_NUMBERS: Record<string, number> = {
	// ๑
	'ก':1,'ด':1,'ท':1,'ถ':1,'ภ':1,'ฤ':1,
	// สระ อา อุ อำ / วรรณยุกต์ ไม้เอก
	'า':1,'ุ':1,'ำ':1,'่':1,
	
	// ๒
	'ข':2,'ช':2,'บ':2,'ป':2,'ง':2,
	// สระ เอ แอ อู / วรรณยุกต์ ไม้โท
	'เ':2,'แ':2,'ู':2,'้':2,
	
	// ๓
	'ฆ':3,'ฑ':3,'ฒ':3,'ต':3,'ฃ':3,'๊':3,
	
	// ๔
	'ค':4,'ธ':4,'ร':4,'ญ':4,'ษ':4,
	// สระ โอ อะ อิ ไม้หันอากาศ
	'โ':4,'ะ':4,'ิ':4,'ั':4,
	
	// ๕
	'ฉ':5,'ณ':5,'ฌ':5,'น':5,'ม':5,'ห':5,'ฮ':5,'ฎ':5,'ฬ':5,'ึ':5,
	
	// ๖
	'จ':6,'ล':6,'ว':6,'อ':6,'ใ':6,
	
	// ๗
	'ศ':7,'ส':7,'ซ':7,'ี':7,'ือ':7,'ื':7,'๋':7,
	
	// ๘
	'ย':8,'พ':8,'ฟ':8,'ผ':8,'ฝ':8,
	
	// ๙
	'ฏ':9,'ฐ':9,'ไ':9,'์':9,
};

const ENG_NUMBERS: Record<string, number> = {
	// 1
	'a':1,'i':1,'j':1,'q':1,'y':1,
	// 2
	'b':2,'k':2,'r':2,
	// 3
	'c':3,'g':3,'l':3,'s':3,
	// 4
	'd':4,'m':4,'t':4,
	// 5
	'e':5,'h':5,'n':5,'x':5,
	// 6
	'u':6,'v':6,'w':6,
	// 7
	'o':7,'z':7,
	// 8
	'f':8,'p':8,
};

export function calcNameNumerology(firstName: string, lastName: string) {
	const firstVal = sumNameFull(firstName);
	const lastVal = sumNameFull(lastName);
	const total = ((firstVal + lastVal - 1) % 9) + 1;

	const meanings: Record<number, string> = {
		1: 'ผู้นำ — กล้าหาญ มีความเป็นตัวของตัวเอง กล้าตัดสินใจ',
		2: 'นุ่มนวล — อ่อนโยน มีเสน่ห์ รักสวยรักงาม เข้ากับคนง่าย',
		3: 'นักพูด — เจรจาเก่ง สื่อสารดี มีชีวิตชีวา สร้างสรรค์',
		4: 'นักวางแผน — เจ้าระเบียบ ซื่อสัตย์ มุ่งมั่น หนักแน่น',
		5: 'นักปราชญ์ — ฉลาด รอบรู้ ช่างคิดวิเคราะห์ เรียนรู้เร็ว',
		6: 'นักสร้าง — รักศิลปะ สุนทรีย์ มีน้ำใจ ครอบครัวอบอุ่น',
		7: 'นักสู้ — อดทน หนักแน่น ผ่านทุกอุปสรรค มีความลับ',
		8: 'นักธุรกิจ — มั่งคั่ง ร่ำรวย ทำงานเก่ง บริหารเป็น',
		9: 'นักบุญ — เมตตา เสียสละ คิดถึงส่วนรวม มีญาณหยั่งรู้',
	};

	return {
		firstName: firstVal,
		lastName: lastVal,
		total,
		meaning: meanings[total] || '',
		name: firstName,
		surname: lastName,
	};
}

function sumNameFull(name: string): number {
	let sum = 0;
	for (const ch of name.toLowerCase()) {
		sum += THAI_NUMBERS[ch] || ENG_NUMBERS[ch] || 0;
	}
	while (sum > 9) {
		let s = 0;
		for (const c of String(sum)) s += parseInt(c);
		sum = s;
	}
	return sum;
}

function sumName(name: string): number {
	return sumNameFull(name);
}

// ─── Helpers ────────────────────────────────
function monthDayToDayOfYear(month: number, day: number): number {
	const md = [0,31,59,90,120,151,181,212,243,273,304,334];
	return md[month - 1] + day;
}
