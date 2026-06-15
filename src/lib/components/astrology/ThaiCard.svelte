<script lang="ts">
	interface Props { birthDate: string; birthTime?: string; birthPlace?: string; lat?: number; lon?: number }
	let { birthDate }: Props = $props();

	const data = $derived(calcThai(birthDate));

	const zodiacMeanings: Record<string, string> = {
		'🐀ชวด':'หนู — ฉลาด ไหวพริบดี เอาตัวรอดเก่ง เข้าสังคม',
		'🐂ฉลู':'วัว — ขยัน อดทน ซื่อสัตย์ มุ่งมั่น',
		'🐯ขาล':'เสือ — กล้าหาญ มีอำนาจ ผู้นำ กล้าเสี่ยง',
		'🐰เถาะ':'กระต่าย — สุภาพ มีเสน่ห์ ระมัดระวัง ศิลปะ',
		'🐲มะโรง':'มังกร — มีบารมี ทะเยอทะยาน ทรงพลัง',
		'🐍มะเส็ง':'งู — ฉลาด ลึกลับ มีไหวพริบ เจรจาเก่ง',
		'🐴มะเมีย':'ม้า — รักอิสระ กระตือรือร้น เปิดโลก',
		'🐐มะแม':'แพะ — สร้างสรรค์ ศิลปะ อ่อนไหว จินตนาการ',
		'🐵วอก':'ลิง — เจ้าเล่ห์ ปรับตัวเก่ง ไหวพริบดี',
		'🐔ระกา':'ไก่ — ตรงไปตรงมา มีเสน่ห์ ภูมิใจ',
		'🐕จอ':'หมา — ซื่อสัตย์ ภักดี ยุติธรรม มีหลักการ',
		'🐷กุน':'หมู — ใจดี โอบอ้อม มีกินมีใช้ สุขสบาย',
	};

	const dayMeanings: Record<string, string> = {
		'อาทิตย์':'☀️ วันอาทิตย์ — มีบารมี ผู้นำ อบอุ่น ใจกว้าง ดวงแข็ง',
		'จันทร์':'🌙 วันจันทร์ — อ่อนโยน มีเสน่ห์ จินตนาการ โรแมนติก',
		'อังคาร':'🔥 วันอังคาร — กล้าหาญ เด็ดขาด ตรงไปตรงมา เจ้าอารมณ์',
		'พุธ':'💬 วันพุธ — ฉลาด เจรจาเก่ง การเงินดี ปรับตัว',
		'พฤหัสบดี':'📚 วันพฤหัส — ปัญญา การศึกษา ครูบาอาจารย์ โชคดี',
		'ศุกร์':'💖 วันศุกร์ — รักสวยรักงาม มีเสน่ห์ ศิลปะ เมตตา',
		'เสาร์':'🏔️ วันเสาร์ — อดทน ขยัน หนักแน่น เรียนสูง',
	};

	const planetDesc: Record<string, string> = {
		'อาทิตย์':'☀️ พระอาทิตย์ — ทางการงาน บารมี อำนาจ ความสำเร็จ',
		'จันทร์':'🌙 พระจันทร์ — จิตใจ ความรู้สึก ครอบครัว เพศแม่',
		'อังคาร':'🔥 พระอังคาร — พลังงาน การต่อสู้ ความกล้า',
		'พุธ':'💎 พระพุธ — การค้า การพูด การเดินทาง',
		'พฤหัสบดี':'📖 พระพฤหัส — ปัญญา โชคลาภ การศึกษา ครู',
		'ศุกร์':'💝 พระศุกร์ — ความรัก ความงาม ศิลปะ ความมั่งคั่ง',
		'เสาร์':'🗿 พระเสาร์ — กรรม วินัย อุปสรรค บทเรียนชีวิต',
	};

	const destinyMeaning: Record<number, string> = {
		1: 'ผู้นำ — เส้นทางของตัวเอง กล้าตัดสินใจ', 2: 'การร่วมมือ — ประสาน ประนีประนอม จับคู่',
		3: 'การสื่อสาร — สร้างสรรค์ เข้าสังคม มีชีวิตชีวา', 4: 'ความมั่นคง — วางแผน ทำงานหนัก สร้างฐาน',
		5: 'อิสระ — เปลี่ยนแปลง ผจญภัย ก้าวหน้า', 6: 'ความรับผิดชอบ — ครอบครัว อบอุ่น ดูแล',
		7: 'ปัญญา — วิเคราะห์ ลึกลับ วิจัย', 8: 'อำนาจ — ธุรกิจ มั่งคั่ง บริหาร',
		9: 'เมตตา — สากล เสียสละ จิตวิญญาณ',
	};

	function calcThai(bd: string) {
		const [y, m, d] = bd.split('-').map(Number);
		const dt = new Date(y, m - 1, d);
		const thaiYear = y + 543;
		const zodiacIdx = (y - 4) % 12;
		const zNames = ['🐀ชวด','🐂ฉลู','🐯ขาล','🐰เถาะ','🐲มะโรง','🐍มะเส็ง','🐴มะเมีย','🐐มะแม','🐵วอก','🐔ระกา','🐕จอ','🐷กุน'];
		const days = ['อาทิตย์','จันทร์','อังคาร','พุธ','พฤหัสบดี','ศุกร์','เสาร์'];
		const colors = ['แดง','เหลือง','ชมพู','เขียว','ส้ม','ฟ้า','ม่วง'];
		const wd = dt.getDay();
		let sum = 0; for (const c of `${d}${m}${y}`) sum += parseInt(c);
		while (sum > 9) { let s = 0; for (const c of String(sum)) s += parseInt(c); sum = s; }
		return { thaiYear, thaiZodiac: zNames[zodiacIdx], birthDay: days[wd], planet: days[wd], color: colors[wd], destinyNumber: sum };
	}
</script>

<div class="card">
	<h3 class="head">🇹🇭 Thai Astrology</h3>
	<div class="grid">
		<div class="mini"><span class="lab">📅 พ.ศ.</span><span class="val">{data.thaiYear}</span></div>
		<div class="mini"><span class="lab">🐉 ปี{data.thaiZodiac}</span><span class="val" style="font-size:.72rem">{zodiacMeanings[data.thaiZodiac]||''}</span></div>
		<div class="mini"><span class="lab">📆 เกิดวัน</span><span class="val">{data.birthDay}</span><span class="sub">{dayMeanings[data.birthDay]||''}</span></div>
		<div class="mini"><span class="lab">🪐 ดาว</span><span class="val">{data.planet}</span><span class="sub">{planetDesc[data.planet]||''}</span></div>
		<div class="mini"><span class="lab">🎨 สี</span><span class="val">{data.color}</span></div>
		<div class="mini"><span class="lab">🔢 เลขดวง</span><span class="val">{data.destinyNumber}</span><span class="sub">{destinyMeaning[data.destinyNumber]||''}</span></div>
	</div>
</div>

<style>
	.card{background:var(--color-surface-1);border:1px solid var(--color-border);border-radius:14px;padding:1.25rem}
	.head{font-size:1rem;font-weight:700;color:var(--color-text-base);margin-bottom:.75rem}
	.grid{display:grid;grid-template-columns:1fr;gap:.4rem}
	.mini{background:var(--color-surface-2);border:1px solid var(--color-border);border-radius:10px;padding:.6rem;display:flex;flex-wrap:wrap;align-items:baseline;gap:.15rem .5rem}
	.lab{font-size:.6rem;color:var(--color-text-muted);text-transform:uppercase;min-width:55px}
	.val{font-size:.9rem;font-weight:700;color:var(--color-text-base)}
	.sub{font-size:.65rem;color:var(--color-text-muted);width:100%}
</style>
