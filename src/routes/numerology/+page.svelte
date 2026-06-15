<script lang="ts">
	let firstName = $state('');
	let lastName = $state('');
	let result = $state<any>(null);
	let loading = $state(false);
	let history = $state<{ name: string; surname: string; total: number; meaning: string }[]>([]);

	async function calculate() {
		if (!firstName) return;
		loading = true;
		result = null;
		try {
			const res = await fetch('/api/astrology', {
				method: 'POST',
				headers: { 'Content-Type': 'application/json' },
				body: JSON.stringify({ type: 'name', firstName, lastName })
			});
			const json = await res.json();
			if (json.success) {
				result = json.data;
				const entry = { name: firstName, surname: lastName, total: json.data.total, meaning: json.data.meaning };
				const saved = JSON.parse(localStorage.getItem('num_history') || '[]');
				const updated = [entry, ...saved.filter((s: any) => !(s.name === entry.name && s.surname === entry.surname))].slice(0, 20);
				localStorage.setItem('num_history', JSON.stringify(updated));
				history = updated;
			}
		} catch (e) {
			console.error(e);
		} finally {
			loading = false;
		}
	}

	function loadFromHistory(entry: any) {
		firstName = entry.name;
		lastName = entry.surname;
		result = entry;
	}

	function clearHistory() {
		localStorage.removeItem('num_history');
		history = [];
	}

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

	// Load history on mount
	$effect(() => {
		const saved = localStorage.getItem('num_history');
		if (saved) history = JSON.parse(saved);
	});

	function calcCompatibility(a: number, b: number): string {
		const diff = Math.abs(a - b);
		if (diff === 0) return 'สูง — สมดุลอย่างสมบูรณ์';
		if (diff <= 2) return 'ดี — เข้ากันได้ดี';
		if (diff <= 4) return 'ปานกลาง — ต้องปรับตัวบ้าง';
		return 'ต่ำ — อาจมีความขัดแย้ง';
	}
</script>

<div class="cosmic-card p-6 max-w-xl mx-auto">
	<h2 class="text-gradient-primary text-2xl font-bold mb-1">🔤 เลขศาสตร์ชื่อ-นามสกุล</h2>
	<p class="text-text-muted text-sm mb-6">คำนวณตามตำราเลขศาสตร์ไทยแท้ — วิเคราะห์ชื่อ+นามสกุล ความหมาย และความเข้ากันได้</p>

	<div class="form">
		<div class="flex gap-2">
			<input type="text" bind:value={firstName} placeholder="ชื่อ" class="form-input flex-1" />
			<input type="text" bind:value={lastName} placeholder="นามสกุล" class="form-input flex-1" />
		</div>
		<button class="quantum-btn mt-3 w-full" onclick={calculate} disabled={loading || !firstName}>
			{loading ? '🌀 กำลังคำนวณ...' : '✨ คำนวณ'}
		</button>
	</div>

	{#if result}
		<div class="result mt-6">
			<div class="summary-card">
				<p class="sum-type">เลข {result.total}</p>
				<p class="sum-sub">{meanings[result.total as keyof typeof meanings]}</p>
			</div>

			<div class="grid-2col mt-4">
				<div class="mini-card">
					<span class="mini-lab">ชื่อ</span>
					<span class="mini-val">{result.firstName}</span>
					<span class="mini-sub">{firstName}</span>
				</div>
				<div class="mini-card">
					<span class="mini-lab">นามสกุล</span>
					<span class="mini-val">{result.lastName}</span>
					<span class="mini-sub">{lastName}</span>
				</div>
			</div>

			{#if lastName}
				<div class="compat-card mt-3">
					<span class="mini-lab">💞 ความเข้ากันได้ของชื่อ-นามสกุล</span>
					<p class="compat-val">{calcCompatibility(result.firstName, result.lastName)}</p>
					<div class="compat-bar">
						<div class="compat-fill" style="width: {Math.max(0, 100 - Math.abs(result.firstName - result.lastName) * 20)}%"></div>
					</div>
				</div>
			{/if}
		</div>
	{/if}

	{#if history.length > 0}
		<div class="mt-6">
			<div class="flex justify-between items-center mb-2">
				<h3 class="text-text-muted text-xs uppercase">📋 ประวัติ</h3>
				<button class="text-xs text-danger opacity-60 hover:opacity-100" onclick={clearHistory}>🗑️ ล้าง</button>
			</div>
			<div class="history-list">
				{#each history as h}
					<button class="h-item" onclick={() => loadFromHistory(h)}>
						<span class="h-name">{h.name} {h.surname}</span>
						<span class="h-tag">เลข {h.total}</span>
					</button>
				{/each}
			</div>
		</div>
	{/if}
</div>

<style>
	.form-input {
		background: var(--color-surface-1);
		border: 1px solid var(--color-border);
		border-radius: 8px;
		padding: 0.55rem 0.75rem;
		color: var(--color-text-base);
		font-size: 0.9rem;
		outline: none;
	}
	.form-input:focus { border-color: var(--color-primary); }

	.summary-card {
		background: linear-gradient(135deg, rgba(168,85,247,0.12), rgba(6,182,212,0.12));
		border: 1px solid var(--color-border-active);
		border-radius: 14px;
		padding: 1.25rem;
		text-align: center;
	}
	.sum-type { font-size: 2rem; font-weight: 700; color: var(--color-text-base); }
	.sum-sub { font-size: 0.85rem; color: var(--color-text-muted); margin-top: 0.3rem; line-height: 1.5; }

	.grid-2col { display: grid; grid-template-columns: 1fr 1fr; gap: 0.5rem; }
	.mini-card {
		background: var(--color-surface-1);
		border: 1px solid var(--color-border);
		border-radius: 10px;
		padding: 0.75rem;
		display: flex;
		flex-direction: column;
		gap: 0.2rem;
	}
	.mini-lab { font-size: 0.65rem; color: var(--color-text-muted); text-transform: uppercase; }
	.mini-val { font-size: 1.2rem; font-weight: 700; color: var(--color-primary); }
	.mini-sub { font-size: 0.72rem; color: var(--color-text-muted); }

	.compat-card {
		background: var(--color-surface-1);
		border: 1px solid var(--color-border);
		border-radius: 10px;
		padding: 0.75rem;
	}
	.compat-val { font-size: 0.85rem; color: var(--color-text-base); margin-top: 0.2rem; }
	.compat-bar { height: 4px; background: var(--color-surface-2); border-radius: 2px; margin-top: 0.4rem; overflow: hidden; }
	.compat-fill { height: 100%; background: linear-gradient(90deg, var(--color-primary), var(--color-secondary)); border-radius: 2px; transition: width 0.5s; }

	.history-list { display: flex; flex-direction: column; gap: 0.25rem; }
	.h-item {
		display: flex; justify-content: space-between; align-items: center;
		padding: 0.45rem 0.65rem;
		background: var(--color-surface-1);
		border: 1px solid var(--color-border);
		border-radius: 8px;
		cursor: pointer;
		transition: all 0.15s;
		width: 100%;
		text-align: left;
		font-size: 0.8rem;
		color: var(--color-text-muted);
	}
	.h-item:hover { background: var(--color-surface-2); border-color: var(--color-border-active); }
	.h-name { font-weight: 600; color: var(--color-text-base); }
	.h-tag { font-size: 0.65rem; color: var(--color-primary); font-weight: 600; }
</style>
