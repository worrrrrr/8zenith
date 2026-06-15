<script lang="ts">
	// @ts-ignore
import * as Lunar from 'lunar-javascript';

	interface Props { birthDate: string; birthTime: string }
	let { birthDate, birthTime }: Props = $props();

	const result = $derived(calcBazi(birthDate, birthTime));

	const ssMap: Record<string, string> = {
		'正官':'ผู้ปกครอง · วินัย', '七杀':'อำนาจ · บททดสอบ', '正印':'ปัญญา · การศึกษา',
		'偏印':'จินตนาการ · นอกกรอบ', '正财':'ทรัพย์มั่นคง · รายได้', '偏财':'โชคลาภ · การลงทุน',
		'食神':'ความสุข · พรสวรรค์', '伤官':'ปัญญาเฉียบ · อิสระ', '比肩':'เพื่อน · การแข่งขัน',
		'劫财':'มิตร · การแบ่งปัน',
	};
	const emptyTh: Record<string, string> = { '子':'🐀หนู','丑':'🐂วัว','寅':'🐯เสือ','卯':'🐰กระต่าย','辰':'🐲มังกร','巳':'🐍งู','午':'🐴ม้า','未':'🐐แพะ','申':'🐵ลิง','酉':'🐔ไก่','戌':'🐕หมา','亥':'🐷หมู' };
	const elemDesc: Record<string, string> = { 'ไฟ':'🔥 กระตือรือร้น', 'ดิน':'🏔️ มั่นคง', 'ทอง':'⚔️ เด็ดขาด', 'น้ำ':'🌊 ยืดหยุ่น', 'ไม้':'🌱 เติบโต' };

	const ZHI_HIDDEN: number[][] = [[9],[5,9,7],[0,2,4],[1],[4,1,9],[2,6,4],[3,5],[5,3,1],[6,8,4],[7],[4,7,3],[8,0]];
	const STEMS_TH = ['เจีย','อี่','ปิ่ง','ติง','อู้','จี่','เกิง','ซิน','เหริน','กุ่ย'];
	const BRANCH_TH = ['🐀ชวด','🐂ฉลู','🐯ขาล','🐰เถาะ','🐲มะโรง','🐍มะเส็ง','🐴มะเมีย','🐐มะแม','🐵วอก','🐔ระกา','🐕จอ','🐷กุน'];
	const GAN = ['甲','乙','丙','丁','戊','己','庚','辛','壬','癸'];
	const ZHI = ['子','丑','寅','卯','辰','巳','午','未','申','酉','戌','亥'];
	const ELEMENTS_MAP = [0,0,1,1,2,2,3,3,4,4];
	const ELEMENTS = ['ไม้','ไฟ','ดิน','ทอง','น้ำ'];

	function calcBazi(bd: string, bt: string) {
		const [y, m, d] = bd.split('-').map(Number);
		const [h] = bt.split(':').map(Number);
		const Solar = Lunar.Solar;
		const solar = Solar.fromYmd(y, m, d);
		const lunar = solar.getLunar();
		const time = Lunar.LunarTime.fromYmdHms(y, m, d, h, 0, 0);

		const yearG = lunar.getYearGanIndex(), yearZ = lunar.getYearZhiIndex();
		const monthG = lunar.getMonthGanIndex(), monthZ = lunar.getMonthZhiIndex();
		const dayG = lunar.getDayGanIndexExact2(), dayZ = lunar.getDayZhiIndexExact2();
		const hourG = time.getGanIndex(), hourZ = time.getZhiIndex();
		const stemSS = lunar.getBaZiShiShenGan();

		const pillars = [
			{ stem: GAN[yearG], branch: ZHI[yearZ], stemTH: STEMS_TH[yearG], branchTH: BRANCH_TH[yearZ], element: ELEMENTS[ELEMENTS_MAP[yearG]], yin: YIN[yearG] ? 'หยิน' : 'หยาง', shiShen: stemSS[0], hidden: ZHI_HIDDEN[yearZ].map(i => GAN[i]+STEMS_TH[i]).join(' '), label: '年' },
			{ stem: GAN[monthG], branch: ZHI[monthZ], stemTH: STEMS_TH[monthG], branchTH: BRANCH_TH[monthZ], element: ELEMENTS[ELEMENTS_MAP[monthG]], yin: YIN[monthG] ? 'หยิน' : 'หยาง', shiShen: stemSS[1], hidden: ZHI_HIDDEN[monthZ].map(i => GAN[i]+STEMS_TH[i]).join(' '), label: '月' },
			{ stem: GAN[dayG], branch: ZHI[dayZ], stemTH: STEMS_TH[dayG], branchTH: BRANCH_TH[dayZ], element: ELEMENTS[ELEMENTS_MAP[dayG]], yin: YIN[dayG] ? 'หยิน' : 'หยาง', shiShen: '日主', hidden: ZHI_HIDDEN[dayZ].map(i => GAN[i]+STEMS_TH[i]).join(' '), label: '日' },
			{ stem: GAN[hourG], branch: ZHI[hourZ], stemTH: STEMS_TH[hourG], branchTH: BRANCH_TH[hourZ], element: ELEMENTS[ELEMENTS_MAP[hourG]], yin: YIN[hourG] ? 'หยิน' : 'หยาง', shiShen: stemSS[3], hidden: ZHI_HIDDEN[hourZ].map(i => GAN[i]+STEMS_TH[i]).join(' '), label: '时' },
		];

		const patterns: string[] = [];
		if (yearZ === monthZ || monthZ === dayZ || dayZ === hourZ) patterns.push('伏吟');
		const empty = (lunar.getDayXunKong() || '').split('');

		return {
			dayMaster: `${GAN[dayG]} (${STEMS_TH[dayG]})`, dayMasterElement: `${ELEMENTS[ELEMENTS_MAP[dayG]]} ${YIN[dayG] ? 'หยิน' : 'หยาง'}`,
			pillars, specialStructure: patterns, empty, chong: lunar.getChong(), sha: lunar.getSha(),
			shiShenZhi: { year: lunar.getBaZiShiShenYearZhi(), month: lunar.getBaZiShiShenMonthZhi(), day: lunar.getBaZiShiShenDayZhi(), time: lunar.getBaZiShiShenTimeZhi() },
			naYin: lunar.getBaZiNaYin(),
		};
	}

	const YIN = [0,1,0,1,0,1,0,1,0,1];

	// Deep interpretations lookup
	const dmPersonality: Record<string, string> = {
		'甲':'🌳 甲(เจีย) ไม้หยาง — เสาหลักของป่าใหญ่ ผู้นำโดยธรรมชาติ กล้าตัดสินใจ มั่นคง แต่บางครั้งดื้อรั้น',
		'乙':'🌿 乙(อี่) ไม้หยิน — เถาวัลย์ที่เลื้อยพัน ยืดหยุ่น ปรับตัวเก่ง มีเสน่ห์ แต่ลังเล',
		'丙':'☀️ 丙(ปิ่ง) ไฟหยาง — ดวงตะวันส่องสว่าง อบอุ่น มีพลัง สร้างแรงบันดาลใจ แต่ใจร้อน',
		'丁':'🕯️ 丁(ติง) ไฟหยิน — แสงเทียนในความมืด ลึกซึ้ง อ่อนไหว มีสมาธิ เปราะบาง',
		'戊':'⛰️ 戊(อู้) ดินหยาง — ภูเขาใหญ่ หนักแน่น ไว้ใจได้ อดทน แต่หัวแข็ง',
		'己':'🏔️ 己(จี่) ดินหยิน — ดินอุดมสมบูรณ์ มีเมตตา รู้จักปรับ ใจกว้าง แต่ยึดติด',
		'庚':'⚔️ 庚(เกิง) ทองหยาง — ดาบที่คมกริบ ตรงไปตรงมา ยุติธรรม เด็ดขาด แต่บาดคม',
		'辛':'💎 辛(ซิน) ทองหยิน — เพชรล้ำค่า ละเอียดอ่อน มีรสนิยมสูง สมบูรณ์แบบ แต่เปราะ',
		'壬':'🌊 壬(เหริน) น้ำหยาง — มหาสมุทรแปรปรวน กว้างขวาง กล้าได้กล้าเสีย ควบคุมยาก',
		'癸':'💧 癸(กุ่ย) น้ำหยิน — สายฝนโปรยปราย ฉลาด ลึกซึ้ง เข้าใจธรรมชาติ เปลี่ยนตามสภาพ',
	};

	const naYinMeanings: Record<string, string> = {
		'甲子': 'หนูทอง — จินตนาการสูง', '乙丑': 'วัวทอง — มั่นคง', '丙寅': 'เสือไฟ — พลังงานสูง',
		'丁卯': 'กระต่ายไฟ — อ่อนโยน', '戊辰': 'มังกรดิน — หนักแน่น', '己巳': 'งูดิน — ลึกลับ',
		'庚午': 'ม้าทอง — ว่องไว', '辛未': 'แพะทอง — สร้างสรรค์', '壬申': 'ลิงน้ำ — ปรับตัวเก่ง',
		'癸酉': 'ไก่น้ำ — ละเอียด', '甲戌': 'หมาไม้ — ซื่อสัตย์', '乙亥': 'หมูไม้ — ใจดี',
		'丙子': 'หนูไฟ — กระฉับกระเฉง', '丁丑': 'วัวไฟ — มุ่งมั่น', '戊寅': 'เสือดิน — กล้าหาญ',
		'己卯': 'กระต่ายดิน — สงบ', '庚辰': 'มังกรทอง — มีอำนาจ', '辛巳': 'งูทอง — ปราดเปรื่อง',
		'壬午': 'ม้าน้ำ — โลดแล่น', '癸未': 'แพะน้ำ — ศิลปะ', '甲申': 'ลิงไม้ — ไหวพริบ',
		'乙酉': 'ไก่ไม้ — ตรงไปตรงมา', '丙戌': 'หมาไฟ — ภักดี', '丁亥': 'หมูไฟ — มีเมตตา',
		'戊子': 'หนูดิน — ฉลาด', '己丑': 'วัวดิน — ขยัน', '庚寅': 'เสือทอง — กล้า',
		'辛卯': 'กระต่ายทอง — ละเอียดอ่อน', '壬辰': 'มังกรน้ำ — มีพลัง', '癸巳': 'งูน้ำ — เฉียบแหลม',
		'甲午': 'ม้าไม้ — กระตือรือร้น', '乙未': 'แพะไม้ — สร้าง', '丙申': 'ลิงไฟ — ฉลาดหลักแหลม',
		'丁酉': 'ไก่ไฟ — มีเสน่ห์', '戊戌': 'หมาไม้ — มั่นคง', '己亥': 'หมูดิน — ใจกว้าง',
		'庚子': 'หนูทอง — ปราดเปรียว', '辛丑': 'วัวทอง — มานะ', '壬寅': 'เสือน้ำ — มีอำนาจ',
		'癸卯': 'กระต่ายน้ำ — อ่อนโยน', '甲辰': 'มังกรไม้ — ทะเยอทะยาน', '乙巳': 'งูไม้ — เฉียบขาด',
		'丙午': 'ม้าไฟ — เปี่ยมพลัง', '丁未': 'แพะไฟ — สร้างสรรค์', '戊申': 'ลิงดิน — เจรจาเก่ง',
		'己酉': 'ไก่ดิน — มีระเบียบ', '庚戌': 'หมาทอง — ซื่อตรง', '辛亥': 'หมูทอง — ใจบุญ',
		'壬子': 'หนูน้ำ — ฉลาดรอบรู้', '癸丑': 'วัวน้ำ — อดทน', '甲寅': 'เสือไม้ — ผู้นำ',
		'乙卯': 'กระต่ายไม้ — สงบ', '丙辰': 'มังกรไฟ — มีบารมี', '丁巳': 'งูไฟ — เฉียบคม',
		'戊午': 'ม้าดิน — มั่นคง', '己未': 'แพะดิน — ใจดี', '庚申': 'ลิงทอง — ปราดเปรื่อง',
		'辛酉': 'ไก่ทอง — เด็ดขาด', '壬戌': 'หมาหมู — ภักดี', '癸亥': 'หมูน้ำ — เมตตา',
	};

	const elemMeanings: Record<string, string> = {
		'ไม้': '🌱 ไม้ = การเติบโต ขยายตัว มีอุดมการณ์ ใจกว้าง คิดสร้างสรรค์',
		'ไฟ': '🔥 ไฟ = พลังงาน ความหลงใหล มีชีวิตชีวา เปลี่ยนแปลง กระตือรือร้น',
		'ดิน': '🏔️ ดิน = ความมั่นคง ไว้ใจได้ จัดการ อบอุ่น อนุรักษ์',
		'ทอง': '⚔️ ทอง = ความเด็ดขาด ยุติธรรม มีหลักการ ตัดสินใจ ตรงไปตรงมา',
		'น้ำ': '🌊 น้ำ = ความยืดหยุ่น ปรับตัว ฉลาด ลึกลับ สื่อสารเก่ง',
	};

	function getDeepAnalysis(r: typeof result): string[] {
		const dm = r.pillars?.[2];
		if (!dm) return [];
		const parts: string[] = [];
		
		// Day Master personality
		parts.push(`🎯 ${dmPersonality[dm.stem] || dm.stem}${dm.yin}`);
		
		// Element balance
		const elemCount: Record<string, number> = {};
		for (const p of r.pillars) { elemCount[p.element] = (elemCount[p.element]||0)+1; }
		const sorted = Object.entries(elemCount).sort((a,b) => b[1]-a[1]);
		parts.push(`⚖️ สมดุลธาตุ: ${sorted.map(([e,c]) => `${e}×${c}`).join(' · ')}`);
		const strongest = sorted[0];
		if (strongest) parts.push(`   ธาตุเด่น: ${elemMeanings[strongest[0]] || ''}`);
		
		// Na Yin
		if (r.naYin) {
			const nyParts = r.naYin.map((n:string) => naYinMeanings[n] || n);
			parts.push(`🔮 納音: ${nyParts.join(' · ')}`);
		}
		
		return parts;
	}

	function getSummary(r: typeof result) {
		if (!r?.pillars?.[2]) return '';
		const dm = r.pillars[2];
		const lines = [`🔹 Day Master "${dm.stemTH}" (${dm.element}${dm.yin}) → ${elemDesc[dm.element] || ''}`];
		const allSS = r.pillars.map((p:any) => p.shiShen);
		const allZhi = r.shiShenZhi ? [...r.shiShenZhi.year, ...r.shiShenZhi.month, ...r.shiShenZhi.day, ...r.shiShenZhi.time] : [];
		if (allSS.includes('食神') && allZhi.includes('七杀')) lines.push('🔸 สัมพันธ์เด่น: 食神 → ควบคุม ← 七杀 = ปัญญาปราบอุปสรรค');
		if (r.specialStructure?.includes('伏吟')) lines.push('🔸 伏吟 → ซ้ำซ้อน');
		if (r.empty?.length) lines.push(`🔸 空亡 ${r.empty.map((e:string)=>emptyTh[e]||e)} → ระวังจุดอ่อน`);
		return lines.join('\n');
	}
</script>

{#if result}
	{@const r = result}
	<div class="card">
		<h3 class="head">🀄 Bazi — สี่เสาหลัก (Local)</h3>
		<p class="sub">Day Master: <strong>{r.dayMaster}</strong> · {r.dayMasterElement}</p>

		<div class="pillars">
			{#each r.pillars as p}
				<div class="pillar" class:dm={p.shiShen === '日主'}>
					<div class="p-label">{p.label}</div>
					<div class="p-ganzhi">{p.stem}{p.branch}</div>
					<div class="p-thai">{p.stemTH} {p.branchTH}</div>
					<div class="p-elem">{p.element}{p.yin}</div>
					<div class="p-ss">{ssMap[p.shiShen] || p.shiShen}</div>
					{#if p.hidden}<div class="p-hid">藏 {p.hidden}</div>{/if}
				</div>
			{/each}
		</div>

		{#if r.shiShenZhi}
			<div class="mt-3"><div class="m-title">十神ประจำเสา</div>
			<table class="tbl"><tbody>
				{#each [['year','年 สังคม'],['month','月 สภาพแวดล้อม'],['day','日 ตนเอง/คู่'],['time','时 ปลายทาง']] as [k, label]}
					<tr><td class="tl">{label}</td><td>{r.shiShenZhi[k as keyof typeof r.shiShenZhi].map((s:string) => `${s}: ${ssMap[s]||''}`).join(' · ')}</td></tr>
				{/each}
			</tbody></table></div>
		{/if}

		<div class="meta-row">
			{#if r.empty?.length}<div class="mi"><span class="ml">空亡</span><span class="mv">{r.empty.map((e:string)=>emptyTh[e]||e).join(', ')}</span></div>{/if}
			{#if r.chong}<div class="mi"><span class="ml">冲</span><span class="mv">{r.chong}</span></div>{/if}
			{#if r.sha}<div class="mi"><span class="ml">煞</span><span class="mv">{r.sha}</span></div>{/if}
			{#if r.specialStructure?.length}<div class="mi"><span class="ml">格局</span><span class="mv">{r.specialStructure.map((s:string) => s === '伏吟' ? '伏吟(ซ้ำ)' : s).join(', ')}</span></div>{/if}
			{#if r.naYin}<div class="mi"><span class="ml">納音</span><span class="mv">{r.naYin.join(' · ')}</span></div>{/if}
		</div>

		<div class="sum-box"><h4 class="sh">📖 สรุป</h4><p class="st">{getSummary(r)}</p></div>

		{#each getDeepAnalysis(r) as line}
			<p class="deep-line">{line}</p>
		{/each}
	</div>
{/if}

<style>
	.card{background:var(--color-surface-1);border:1px solid var(--color-border);border-radius:14px;padding:1.25rem}
	.head{font-size:1rem;font-weight:700;color:var(--color-text-base);margin-bottom:.25rem}
	.sub{font-size:.78rem;color:var(--color-text-muted);margin-bottom:.75rem}
	.pillars{display:grid;grid-template-columns:repeat(4,1fr);gap:.4rem}
	@media(max-width:450px){.pillars{grid-template-columns:1fr 1fr}}
	.pillar{background:var(--color-surface-2);border:1px solid var(--color-border);border-radius:10px;padding:.5rem .35rem;text-align:center}
	.pillar.dm{border-color:var(--color-primary);box-shadow:0 0 8px rgba(168,85,247,.2)}
	.p-label{font-size:.48rem;color:var(--color-text-muted);text-transform:uppercase}
	.p-ganzhi{font-size:1.2rem;font-weight:700;color:var(--color-primary);margin:.1rem 0}
	.p-thai{font-size:.58rem;color:var(--color-text-muted)}
	.p-elem{font-size:.55rem;color:var(--color-accent)}
	.p-ss{font-size:.58rem;font-weight:600;color:var(--color-text-base);margin-top:.05rem;line-height:1.2}
	.p-hid{font-size:.5rem;color:var(--color-secondary);margin-top:.05rem}
	.mt-3{margin-top:.75rem}
	.m-title{font-size:.6rem;color:var(--color-text-muted);text-transform:uppercase;letter-spacing:.5px;margin-bottom:.2rem}
	.tbl{width:100%;font-size:.65rem;border-collapse:collapse}
	.tbl td{padding:.2rem .4rem;border-bottom:1px solid var(--color-border);color:var(--color-text-muted)}
	.tl{color:var(--color-text-base)!important;font-weight:600;white-space:nowrap;width:30%}
	.meta-row{display:flex;flex-wrap:wrap;gap:.3rem;margin-top:.5rem}
	.mi{background:var(--color-surface-2);border:1px solid var(--color-border);border-radius:8px;padding:.25rem .5rem;flex:1;min-width:80px}
	.ml{font-size:.5rem;color:var(--color-text-muted);text-transform:uppercase;display:block}
	.mv{font-size:.65rem;color:var(--color-text-base);font-weight:600}
	.sum-box{margin-top:.75rem;padding:.75rem;background:rgba(168,85,247,.06);border:1px solid var(--color-border-active);border-radius:10px}
	.sh{font-size:.78rem;font-weight:700;color:var(--color-primary);margin-bottom:.3rem}
	.st{font-size:.7rem;color:var(--color-text-muted);line-height:1.6;white-space:pre-line}
	.deep-line{font-size:.68rem;color:var(--color-text-muted);line-height:1.6;margin-top:.3rem;padding-left:.3rem}
</style>
