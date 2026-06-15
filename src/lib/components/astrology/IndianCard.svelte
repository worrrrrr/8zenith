<script lang="ts">
	interface Props { birthDate: string; birthTime: string; birthPlace: string; lat: number; lon: number }
	let { birthDate, birthTime, birthPlace, lat, lon }: Props = $props();
	let data = $state<any>(null); let loading = $state(true); let error = $state('');

	$effect(() => { if (!data) loading = true; else error = '';
		fetch('/api/astrology', { method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({type:'indian',birthDate,birthTime,birthPlace,lat,lon}) })
		.then(r=>r.json()).then(j=>{if(j.success)data=j.data;else error=j.error||'Error'}).catch(()=>error='Connection error').finally(()=>loading=false);
	});

	const rashiDesc: Record<string, string> = {
		'เมษ':'🔥 เมษ(Aries) → กล้าหาญ บุกเบิก แข่งขัน (Lord: Mars)', 'พฤษภ':'🌍 พฤษภ(Taurus) → มั่นคง  sensual  อดทน (Lord: Venus)',
		'เมถุน':'💨 เมถุน(Gemini) → สื่อสาร เรียนรู้ ปรับตัว (Lord: Mercury)', 'กรกฎ':'💧 กรกฎ(Cancer) → อ่อนไหว อบอุ่น ครอบครัว (Lord: Moon)',
		'สิงห์':'🔥 สิงห์(Leo) → มีบารมี สร้างสรรค์ ใจกว้าง (Lord: Sun)', 'กันย์':'🌍 กันย์(Virgo) → ละเอียด บริการ วิเคราะห์ (Lord: Mercury)',
		'ตุล':'💨 ตุล(Libra) → สมดุล ยุติธรรม มีเสน่ห์ (Lord: Venus)', 'พิจิก':'💧 พิจิก(Scorpio) → ลึกซึ้ง เปลี่ยนแปลง ทรงพลัง (Lord: Mars)',
		'ธนู':'🔥 ธนู(Sagittarius) → รักอิสระ มองไกล ปรัชญา (Lord: Jupiter)', 'มังกร':'🌍 มังกร(Capricorn) → ทะเยอทะยาน วินัย อดทน (Lord: Saturn)',
		'กุมภ์':'💨 กุมภ์(Aquarius) → สร้างสรรค์ มนุษยธรรม อิสระ (Lord: Saturn)', 'มีน':'💧 มีน(Pisces) → จินตนาการ เมตตา จิตวิญญาณ (Lord: Jupiter)',
	};

	const nakDesc: Record<string, string> = {
		'อัศวินี':'🐴 อัศวินี(Ketu) — รวดเร็ว เยียวยา ผู้บุกเบิก', 'ภรณี':'👶 ภรณี(Venus) — เกิดใหม่ ราคะ ความอดทน',
		'กฤติกา':'🔪 กฤติกา(Sun) — เฉียบคม ชำระล้าง ผ่าตัด', 'โรหิณี':'🚜 โรหิณี(Moon) — เติบโต อุดมสมบูรณ์ ศิลปะ',
		'มฤคศิระ':'🦌 มฤคศิระ(Mars) — ค้นหา  wanderer  อ่อนโยน', 'อารทรา':'💧 อารทรา(Rahu) — เจ็บปวด เปลี่ยนแปลง หยั่งลึก',
		'ปุนัพสุ':'🔄 ปุนัพสุ(Jupiter) — ฟื้นคืน กลับมา เริ่มใหม่', 'ปุษยะ':'🌺 ปุษยะ(Saturn) — เลี้ยงดู ฟูมฟัก ปกป้อง',
		'อัศเลษา':'🐍 อัศเลษา(Mercury) — พันกัน รักษา ลึกลับ', 'มาฆะ':'👑 มาฆะ(Ketu) — อำนาจ บรรพบุรุษ เกียรติยศ',
		'ปูรพผลคุนี':'🛏️ ปูรพผลคุนี(Venus) — สนุก โรแมนติก ศิลปะ', 'อุตรผลคุนี':'🤝 อุตรผลคุนี(Sun) — มิตรภาพ การแต่งงาน',
		'หัสตะ':'✋ หัสตะ(Moon) — ฝีมือ รักษา บริการ', 'จิตรา':'💎 จิตรา(Mars) — เปล่งปลั่ง สร้างสรรค์ อัญมณี',
		'สวาตี':'🌬️ สวาตี(Rahu) — อิสระ ผู้ประกอบการ ลมพัด', 'วิสาขา':'🎯 วิสาขา(Jupiter) — มุ่งมั่น บรรลุเป้า ต่อสู้',
		'อนุราธะ':'🌸 อนุราธะ(Saturn) — มิตร ซื่อสัตย์ ไสยศาสตร์', 'เชษฐะ':'🦅 เชษฐะ(Mercury) — เหนือกว่า ผู้นำ ปกป้อง',
		'มูละ':'🌪️ มูละ(Ketu) — ถอนราก วิจัย ลึกลับ', 'ปูรพาษาฒ':'🌊 ปูรพาษาฒ(Venus) — ชำระ สะอาด กล้าหาญ',
		'อุตราษาฒ':'🐘 อุตราษาฒ(Sun) — ชนะ ผู้นำ พิชิต', 'ศรวณะ':'👂 ศรวณะ(Moon) — ฟัง เรียนรู้ ท่องเที่ยว',
		'ธนิษฐา':'🥁 ธนิษฐา(Mars) — จังหวะ นักดนตรี มั่งคั่ง', 'ศตภิษัช':'💊 ศตภิษัช(Rahu) — รักษา วิทยาศาสตร์ หมอ',
		'ปูรพภัทรบท':'🔥 ปูรพภัทรบท(Jupiter) — เร่าร้อน จิตวิญญาณ', 'อุตรภัทรบท':'💧 อุตรภัทรบท(Saturn) — มั่นคง  ควบคุม  รู้แจ้ง',
		'เรวดี':'🐟 เรวดี(Mercury) — เลี้ยงดู เมตตา มั่งคั่ง',
	};

	function analyzeIndian(r: any): string[] {
		if (!r?.sunSign) return [];
		const lines: string[] = [];
		if (r.sunSign?.name) lines.push(`☀️ ราศีอาทิตย์ ${r.sunSign.name} → ${rashiDesc[r.sunSign.name]||''}`);
		if (r.moonSign?.name) lines.push(`🌙 ราศีจันทร์ ${r.moonSign.name} → ${rashiDesc[r.moonSign.name]||''}`);
		if (r.lagna?.name) lines.push(`⬆️ ลัคนา ${r.lagna.name} → ${rashiDesc[r.lagna.name]||''}`);
		if (r.nakshatra?.name) lines.push(`⭐ นักษัตร ${r.nakshatra.name} (Pada ${r.nakshatra.pada}) → ${nakDesc[r.nakshatra.name]||''}`);
		// Check if Sun and Moon signs match
		if (r.sunSign?.name === r.moonSign?.name) lines.push(`⚠️ อาทิตย์+จันทร์ราศีเดียวกัน → จิต-กายสอดคล้องสูง`);
		return lines;
	}
</script>

{#if loading && !data}{:else if error}{:else if data}
	{@const r = data}
	{@const analysis = analyzeIndian(r)}
	<div class="card">
		<h3 class="head">🕉️ Vedic Astrology</h3>
		<div class="grid">
			<div class="mini"><span class="lab">☀️ Sun Rashi</span><span class="val">{r.sunSign.name}</span><span class="sub">{r.sunSign.en} · Lord: {r.sunSign.lord}</span></div>
			<div class="mini"><span class="lab">🌙 Moon Rashi</span><span class="val">{r.moonSign.name}</span><span class="sub">{r.moonSign.en} · Lord: {r.moonSign.lord}</span></div>
			<div class="mini"><span class="lab">⬆️ Lagna</span><span class="val">{r.lagna.name}</span><span class="sub">{r.lagna.en} · Lord: {r.lagna.lord}</span></div>
			<div class="mini"><span class="lab">⭐ Nakshatra</span><span class="val">{r.nakshatra.name}</span><span class="sub">Pada {r.nakshatra.pada} · Lord: {r.nakshatra.lord}</span></div>
		</div>
		<div class="analysis-box">
			<h4 class="text-xs text-primary font-bold uppercase mb-1">📖 พยากรณ์</h4>
			{#each analysis as line}<p class="an-line">{line}</p>{/each}
		</div>
	</div>
{/if}

<style>
	.loading{text-align:center;padding:2rem;color:var(--color-text-muted);font-size:.85rem}
	.error{background:rgba(239,68,68,.1);border:1px solid rgba(239,68,68,.3);border-radius:10px;padding:.75rem;color:#ef4444;text-align:center;font-size:.82rem}
	.card{background:var(--color-surface-1);border:1px solid var(--color-border);border-radius:14px;padding:1.25rem}
	.head{font-size:1rem;font-weight:700;color:var(--color-text-base);margin-bottom:.75rem}
	.grid{display:grid;grid-template-columns:1fr 1fr;gap:.5rem}
	.mini{background:var(--color-surface-2);border:1px solid var(--color-border);border-radius:10px;padding:.65rem;display:flex;flex-direction:column;gap:.15rem}
	.lab{font-size:.6rem;color:var(--color-text-muted);text-transform:uppercase}
	.val{font-size:.95rem;font-weight:700;color:var(--color-text-base)}
	.sub{font-size:.65rem;color:var(--color-text-muted)}
	.analysis-box{background:rgba(168,85,247,.04);border:1px solid var(--color-border);border-radius:10px;padding:.6rem .75rem;margin-top:.75rem}
	.an-line{font-size:.68rem;color:var(--color-text-muted);line-height:1.6;margin:.15rem 0}
</style>
