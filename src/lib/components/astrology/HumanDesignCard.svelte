<script lang="ts">
	interface Props { birthDate: string; birthTime: string; birthPlace: string; lat: number; lon: number }
	let { birthDate, birthTime, birthPlace, lat, lon }: Props = $props();
	let data = $state<any>(null); let loading = $state(true); let refresh = $state(false);
	let error = $state('');

	$effect(() => {
		if (!data) { loading = true; } else {  error = ''; }
		fetch('/api/astrology', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ type: 'humandesign', birthDate, birthTime, birthPlace, lat, lon }) })
			.then(r => r.json()).then(j => { if (j.success) data = j.data; else error = j.error || 'Error'; }).catch(() => error = 'Connection error').finally(() => { loading = false;   });
	});

	const typeInfo: Record<string, { pop: string; sig: string; ns: string; desc: string }> = {
		Generator: { pop:'~37%', sig:'Satisfaction', ns:'Frustration', desc:'ผู้สร้างพลัง — Sacral ตอบสนอง' },
		'Manifesting Generator': { pop:'~33%', sig:'Satisfaction & Peace', ns:'Frustration & Anger', desc:'เร็ว หลายเลน' },
		Projector: { pop:'~20%', sig:'Success', ns:'Bitterness', desc:'ผู้ชี้นำ — มองเห็นระบบ' },
		Manifestor: { pop:'~9%', sig:'Peace', ns:'Anger', desc:'ผู้ริเริ่ม' },
		Reflector: { pop:'~1%', sig:'Surprise', ns:'Disappointment', desc:'กระจกสะท้อน' },
	};
</script>

{#if loading && !data}{:else if error}{:else if data}
	{@const r = data}
	{@const info = typeInfo[r.type] || typeInfo['Generator']}
	<div class="card">
		<h3 class="head">🔷 Human Design</h3>
		<div class="sum-card mb-3"><p class="sum-type">{r.type}</p><p class="sum-sub">{info.desc} · {info.pop}</p></div>
		<div class="grid mb-3">
			<div class="mini"><span class="lab">🎯 Strategy</span><span class="val">{r.strategy}</span></div>
			<div class="mini"><span class="lab">🧭 Authority</span><span class="val">{r.authority}</span></div>
			<div class="mini"><span class="lab">🌀 Aura</span><span class="val">{r.aura}</span></div>
			<div class="mini"><span class="lab">✅ Signature</span><span class="val">{info.sig}</span></div>
			<div class="mini"><span class="lab">❌ Not-Self</span><span class="val">{info.ns}</span></div>
		</div>
		{#if r.personalityGate}
			<div class="gates">
				<div class="gate"><span class="lab">☀️ Personality</span><span class="gate-val">Gate {r.personalityGate.num}.{r.personalityGate.line}</span><span class="sub">{r.personalityGate.name}</span></div>
				<div class="gate"><span class="lab">🌑 Design</span><span class="gate-val">Gate {r.designGate.num}.{r.designGate.line}</span><span class="sub">{r.designGate.name}</span></div>
			</div>
		{/if}
	</div>
{/if}
	

<style>
	.refreshing{text-align:center;padding:.25rem;font-size:.65rem;color:var(--color-text-muted);opacity:.7}
	.loading { padding: 2rem; text-align: center; color: var(--color-text-muted); font-size: 0.85rem; }
	.error { background: rgba(239,68,68,0.1); border: 1px solid rgba(239,68,68,0.3); border-radius: 10px; padding: 0.75rem; color: #ef4444; text-align: center; font-size: 0.82rem; }
	.card { background: var(--color-surface-1); border: 1px solid var(--color-border); border-radius: 14px; padding: 1.25rem; }
	.head { font-size: 1rem; font-weight: 700; color: var(--color-text-base); margin-bottom: 0.75rem; }
	.sum-card { background: linear-gradient(135deg, rgba(168,85,247,0.12), rgba(6,182,212,0.12)); border: 1px solid var(--color-border-active); border-radius: 14px; padding: 1rem; text-align: center; }
	.sum-type { font-size: 1.3rem; font-weight: 700; color: var(--color-text-base); }
	.sum-sub { font-size: 0.78rem; color: var(--color-text-muted); margin-top: 0.15rem; }
	.grid { display: grid; grid-template-columns: 1fr 1fr; gap: 0.4rem; }
	.mini { background: var(--color-surface-2); border: 1px solid var(--color-border); border-radius: 10px; padding: 0.55rem; display: flex; flex-direction: column; gap: 0.1rem; }
	.lab { font-size: 0.58rem; color: var(--color-text-muted); text-transform: uppercase; }
	.val { font-size: 0.75rem; font-weight: 600; color: var(--color-text-base); }
	.gates { display: flex; flex-direction: column; gap: 0.3rem; }
	.gate { background: var(--color-surface-2); border: 1px solid var(--color-border); border-radius: 8px; padding: 0.5rem 0.65rem; display: flex; flex-wrap: wrap; align-items: baseline; gap: 0.3rem; }
	.gate-val { font-size: 0.78rem; font-weight: 700; color: var(--color-primary); }
	.sub { font-size: 0.65rem; color: var(--color-text-muted); }
</style>
