<script lang="ts">
	interface Props { birthDate: string; birthTime: string; birthPlace: string; lat: number; lon: number }
	let { birthDate, birthTime, birthPlace, lat, lon }: Props = $props();
	let data = $state<any>(null); let loading = $state(true); let error = $state('');

	$effect(() => { if (!data) loading = true; else error = '';
		fetch('/api/astrology', { method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({type:'western',birthDate,birthTime,birthPlace,lat,lon}) })
		.then(r=>r.json()).then(j=>{if(j.success)data=j.data;else error=j.error||'Error'}).catch(()=>error='Connection error').finally(()=>loading=false);
	});

	const planetMeanings: Record<string, string> = {
		'อาทิตย์':'ตัวตนหลัก · แก่นของชีวิต · ความมุ่งหมาย', 'จันทร์':'จิตใต้สำนึก · อารมณ์ · ความรู้สึก',
		'พุธ':'การสื่อสาร · ความคิด · การเรียนรู้', 'ศุกร์':'ความรัก · ความงาม · มิตรภาพ · คุณค่า',
		'อังคาร':'พลัง · การกระทำ · ความกล้า · แรงขับ', 'พฤหัสบดี':'โชคลาภ · การขยาย · ปัญญา · การศึกษา',
		'เสาร์':'วินัย · ความรับผิดชอบ · บทเรียน · ข้อจำกัด', 'ยูเรนัส':'การเปลี่ยนแปลง · อิสระ · นวัตกรรม',
		'เนปจูน':'จินตนาการ · จิตวิญญาณ · ความฝัน', 'พลูโต':'อำนาจ · การเปลี่ยนแปลงลึก · การเกิดใหม่',
	};

	const signPros: Record<string, string> = {
		'♈':'กล้าบุกเบิก', '♉':'มั่นคง', '♊':'สื่อสารเก่ง', '♋':'อ่อนไหว',
		'♌':'มีบารมี', '♍':'ละเอียด', '♎':'สมดุล', '♏':'ลึกซึ้ง',
		'♐':'รักอิสระ', '♑':'ทะเยอทะยาน', '♒':'สร้างสรรค์', '♓':'มีจินตนาการ',
	};

	function analyzeWestern(r: any): string[] {
		if (!r?.planets) return [];
		const lines: string[] = [];
		// Element distribution
		const elemCnt: Record<string,number> = {};
		r.planets.forEach((p:any) => { elemCnt[p.elementTH] = (elemCnt[p.elementTH]||0)+1; });
		const sorted = Object.entries(elemCnt).sort((a,b) => b[1]-a[1]);
		lines.push(`🔥 สมดุลธาตุ: ${sorted.map(([e,c]) => `${e}×${c}`).join(' · ')}`);

		// Find dominant planet aspect
		const sunSign = r.sunSign?.slice(0,2);
		const moonSign = r.moonSign?.slice(0,2);
		const risingSign = r.risingSign?.slice(0,2);
		if (sunSign) lines.push(`☀️ ดวงอาทิตย์${r.sunSign} = ${signPros[sunSign]||''} · ${planetMeanings['อาทิตย์']}`);
		if (moonSign) lines.push(`🌙 ดวงจันทร์${r.moonSign} = ${signPros[moonSign]||''} · ${planetMeanings['จันทร์']}`);
		if (risingSign) lines.push(`⬆️ ลัคนา${r.risingSign} = ${signPros[risingSign]||''} · ภาพลักษณ์ที่คนอื่นเห็น`);

		// Each planet quick meaning
		r.planets.forEach((p:any) => {
			const signEmoji = p.sign?.slice(0,2);
			lines.push(`🔹 ${p.nameTH} ใน${signEmoji||''} ${p.degree}° = ${planetMeanings[p.nameTH]||''}`);
		});

		// If we have ayanamsa, mention it
		if (r.ayanamsa) lines.push(`📐 Ayanamsa: ${r.ayanamsa.toFixed(3)}° (ความต่างของ Tropical/Sidereal)`);

		return lines;
	}
</script>

{#if loading && !data}{:else if error}{:else if data}
	{@const r = data}
	{@const analysis = analyzeWestern(r)}
	<div class="card">
		<h3 class="head">🌍 Western Astrology</h3>
		<div class="grid-3 mb-3">
			<div class="mini"><span class="lab">☀️ Sun</span><span class="val">{r.sunSign}</span><span class="sub">{r.sunSignTH}</span></div>
			<div class="mini"><span class="lab">🌙 Moon</span><span class="val">{r.moonSign}</span><span class="sub">{r.moonSignTH}</span></div>
			<div class="mini"><span class="lab">⬆️ Rising</span><span class="val">{r.risingSign}</span><span class="sub">{r.risingSignTH}</span></div>
		</div>
		{#if r.planets}
			<h4 class="text-xs text-text-muted uppercase mb-2">ตำแหน่งดาว</h4>
			<div class="planet-list">
				{#each r.planets as pl}
					<div class="pl-row"><span class="pl-name">{pl.nameTH}</span><span>{pl.sign} {pl.degree}°</span><span class="pl-elem">{pl.elementTH}</span></div>
				{/each}
			</div>
		{/if}
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
	.grid-3{display:grid;grid-template-columns:repeat(3,1fr);gap:.5rem}
	.mini{background:var(--color-surface-2);border:1px solid var(--color-border);border-radius:10px;padding:.65rem;display:flex;flex-direction:column;gap:.15rem}
	.lab{font-size:.6rem;color:var(--color-text-muted);text-transform:uppercase}
	.val{font-size:.9rem;font-weight:700;color:var(--color-text-base)}
	.sub{font-size:.65rem;color:var(--color-text-muted)}
	.planet-list{display:flex;flex-direction:column;gap:.2rem;margin-bottom:.75rem}
	.pl-row{display:flex;align-items:center;gap:.5rem;padding:.25rem .5rem;background:var(--color-surface-2);border-radius:6px;font-size:.7rem}
	.pl-name{font-weight:600;color:var(--color-text-base);min-width:48px}
	.pl-elem{color:var(--color-accent);font-size:.6rem;margin-left:auto}
	.analysis-box{background:rgba(168,85,247,.04);border:1px solid var(--color-border);border-radius:10px;padding:.6rem .75rem;margin-top:.5rem}
	.an-line{font-size:.68rem;color:var(--color-text-muted);line-height:1.6;margin:.15rem 0}
</style>
