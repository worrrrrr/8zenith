<script lang="ts">
	import BaziCard from '$lib/components/astrology/BaziCard.svelte';
	import IndianCard from '$lib/components/astrology/IndianCard.svelte';
	import WesternCard from '$lib/components/astrology/WesternCard.svelte';
	import ThaiCard from '$lib/components/astrology/ThaiCard.svelte';
	import HumanDesignCard from '$lib/components/astrology/HumanDesignCard.svelte';

	let birthDate = $state('2000-01-01');
	let birthTime = $state('12:00');
	let selectedCountry = $state('thailand');
	let selectedCity = $state('Bangkok');
	let activeTab = $state('bazi');
	let reading = $state<string | null>(null);
	let readingLoading = $state(false);
				
	const countries: Record<string, { flag: string; label: string; cities: { name: string; lat: number; lon: number }[] }> = { /* (same data) */
		thailand: { flag: '🇹🇭', label: 'ประเทศไทย', cities: [
			{ name: 'Bangkok', lat: 13.75, lon: 100.5167 }, { name: 'Chiang Mai', lat: 18.7969, lon: 98.9792 },
			{ name: 'Phuket', lat: 7.8804, lon: 98.3923 }, { name: 'Pattaya', lat: 12.9333, lon: 100.8833 },
			{ name: 'Hat Yai', lat: 6.9993, lon: 100.4728 }, { name: 'Nakhon Ratchasima', lat: 14.9739, lon: 102.0843 },
			{ name: 'Khon Kaen', lat: 16.4489, lon: 102.8276 }, { name: 'Chonburi', lat: 13.3667, lon: 100.9833 },
			{ name: 'Surat Thani', lat: 9.1402, lon: 99.3333 }, { name: 'Udon Thani', lat: 17.4167, lon: 102.7833 },
		]},
		laos: { flag: '🇱🇦', label: 'สปป.ลาว', cities: [{ name: 'Vientiane', lat: 17.9667, lon: 102.6 }, { name: 'Luang Prabang', lat: 19.8833, lon: 102.1333 }] },
		vietnam: { flag: '🇻🇳', label: 'เวียดนาม', cities: [{ name: 'Hanoi', lat: 21.0285, lon: 105.8542 }, { name: 'Ho Chi Minh City', lat: 10.8231, lon: 106.6297 }, { name: 'Da Nang', lat: 16.0544, lon: 108.2022 }] },
		cambodia: { flag: '🇰🇭', label: 'กัมพูชา', cities: [{ name: 'Phnom Penh', lat: 11.5695, lon: 104.9211 }, { name: 'Siem Reap', lat: 13.3611, lon: 103.8606 }] },
		myanmar: { flag: '🇲🇲', label: 'เมียนมา', cities: [{ name: 'Yangon', lat: 16.8661, lon: 96.1951 }, { name: 'Mandalay', lat: 22.0029, lon: 96.0833 }] },
		malaysia: { flag: '🇲🇾', label: 'มาเลเซีย', cities: [{ name: 'Kuala Lumpur', lat: 3.139, lon: 101.6869 }, { name: 'George Town', lat: 5.4141, lon: 100.3288 }] },
		singapore: { flag: '🇸🇬', label: 'สิงคโปร์', cities: [{ name: 'Singapore', lat: 1.3521, lon: 103.8198 }] },
		china: { flag: '🇨🇳', label: 'จีน', cities: [{ name: 'Beijing', lat: 39.9042, lon: 116.4074 }, { name: 'Shanghai', lat: 31.2304, lon: 121.4737 }, { name: 'Hong Kong', lat: 22.3193, lon: 114.1694 }] },
		japan: { flag: '🇯🇵', label: 'ญี่ปุ่น', cities: [{ name: 'Tokyo', lat: 35.6762, lon: 139.6503 }, { name: 'Osaka', lat: 34.6937, lon: 135.5023 }, { name: 'Kyoto', lat: 35.0116, lon: 135.768 }] },
		korea: { flag: '🇰🇷', label: 'เกาหลีใต้', cities: [{ name: 'Seoul', lat: 37.5665, lon: 126.978 }, { name: 'Busan', lat: 35.1796, lon: 129.0756 }] },
		india: { flag: '🇮🇳', label: 'อินเดีย', cities: [{ name: 'New Delhi', lat: 28.6139, lon: 77.209 }, { name: 'Mumbai', lat: 19.076, lon: 72.8777 }, { name: 'Bangalore', lat: 12.9716, lon: 77.5946 }] },
		usa: { flag: '🇺🇸', label: 'สหรัฐอเมริกา', cities: [{ name: 'New York', lat: 40.7128, lon: -74.006 }, { name: 'Los Angeles', lat: 34.0522, lon: -118.2437 }, { name: 'San Francisco', lat: 37.7749, lon: -122.4194 }] },
		uk: { flag: '🇬🇧', label: 'สหราชอาณาจักร', cities: [{ name: 'London', lat: 51.5074, lon: -0.1278 }, { name: 'Manchester', lat: 53.4808, lon: -2.2426 }] },
		australia: { flag: '🇦🇺', label: 'ออสเตรเลีย', cities: [{ name: 'Sydney', lat: -33.8688, lon: 151.2093 }, { name: 'Melbourne', lat: -37.8136, lon: 144.9631 }] },
	};

	let birthPlace = $derived(selectedCity);
	let birthLat = $derived(countries[selectedCountry]?.cities.find(c => c.name === selectedCity)?.lat ?? 13.75);
	let birthLon = $derived(countries[selectedCountry]?.cities.find(c => c.name === selectedCity)?.lon ?? 100.5);

	const tabs = [
		{ id: 'bazi', icon: '🀄', label: 'Bazi', comp: BaziCard },
		{ id: 'indian', icon: '🕉️', label: 'Indian', comp: IndianCard },
		{ id: 'western', icon: '🌍', label: 'Western', comp: WesternCard },
		{ id: 'thai', icon: '🇹🇭', label: 'Thai', comp: ThaiCard },
		{ id: 'humandesign', icon: '🔷', label: 'Human Design', comp: HumanDesignCard },
	];

	async function synthesize() {
		reading = null; readingLoading = true;
		try {
			// Fetch all 5 systems first for ground truth
			const [bazi, western, indian, thai, humandesign] = await Promise.all([
				fetch('/api/astrology', { method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({type:'bazi',birthDate,birthTime,birthPlace,lat:birthLat,lon:birthLon}) }).then(r=>r.json()),
				fetch('/api/astrology', { method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({type:'western',birthDate,birthTime,birthPlace,lat:birthLat,lon:birthLon}) }).then(r=>r.json()),
				fetch('/api/astrology', { method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({type:'indian',birthDate,birthTime,birthPlace,lat:birthLat,lon:birthLon}) }).then(r=>r.json()),
				fetch('/api/astrology', { method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({type:'thai',birthDate,birthPlace,lat:birthLat,lon:birthLon}) }).then(r=>r.json()),
				fetch('/api/astrology', { method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({type:'humandesign',birthDate,birthTime,birthPlace,lat:birthLat,lon:birthLon}) }).then(r=>r.json()),
			]);

			// Send ground truth to DeepSeek for interpretation
			const astrologyData = {
				birthDate, birthTime, birthPlace, lat: birthLat, lon: birthLon,
				bazi: bazi.success ? bazi.data : null,
				western: western.success ? western.data : null,
				indian: indian.success ? indian.data : null,
				thai: thai.success ? thai.data : null,
				humandesign: humandesign.success ? humandesign.data : null,
			};

			const res = await fetch('/api/chat', {
				method: 'POST', headers: { 'Content-Type': 'application/json' },
				body: JSON.stringify({ astrologyData })
			});

			if (!res.ok) throw new Error('Chat API error');
			if (!res.body) throw new Error('No response body');

			const reader = res.body.getReader();
			const decoder = new TextDecoder();
			let text = '';
			while (true) {
				const { value, done } = await reader.read();
				if (done) break;
				text += decoder.decode(value, { stream: true });
			}
			reading = text;
			// Save to localStorage so Chat page can use it too
			localStorage.setItem('astrology_chart', JSON.stringify(astrologyData));
		} catch { reading = '⚠️ เกิดข้อผิดพลาด'; }
		finally { readingLoading = false; }
	}

	
</script>

<div class="cosmic-card p-6 max-w-3xl mx-auto">
	<h2 class="text-gradient-primary text-2xl font-bold mb-2">🌌 Astrology Nexus</h2>
	<p class="text-text-muted text-sm mb-6">sweph + lunar-javascript — 5 ระบบ คำนวณเมื่อเปิด tab เท่านั้น</p>

	<div class="form-grid mb-6">
		<div><label>📅 วันเกิด</label><input type="date" bind:value={birthDate} class="fi" /></div>
		<div><label>⏰ เวลา</label><input type="time" bind:value={birthTime} class="fi" /></div>
		<div class="loc-row full">
			<div><label>🌍 ประเทศ</label><select bind:value={selectedCountry} onchange={() => selectedCity = countries[selectedCountry].cities[0].name} class="fi">
				{#each Object.entries(countries) as [id, c]}<option value={id}>{c.flag} {c.label}</option>{/each}
			</select></div>
			<div><label>📍 เมือง</label><select bind:value={selectedCity} class="fi">
				{#each countries[selectedCountry]?.cities || [] as c}<option value={c.name}>{c.name}</option>{/each}
			</select></div>
		</div>
	</div>

	<div class="tab-bar">
		{#each tabs as { id, icon, label }}
			<button class="tab" class:active={activeTab === id} onclick={() => activeTab = id}>{icon} {label}</button>
		{/each}
	</div>

	<div class="tab-content">
		{#each tabs as { id, comp: Comp }}
			<div class="tab-pane" class:active={activeTab === id}>
				<Comp {birthDate} {birthTime} {birthPlace} lat={birthLat} lon={birthLon} />
			</div>
		{/each}
	</div>

	<button class="synth-btn mb-6" onclick={synthesize} disabled={readingLoading}>
		{readingLoading ? '🌀 AI กำลังตีความดวงชะตาของคุณ...' : '🔮 สังเคราะห์ดวง — รวม 5 ศาสตร์ ตีความด้วย AI'}
	</button>

	{#if reading}
		<div class="reading-card">
			<h3 class="reading-head">🔮 คำพยากรณ์องค์รวม</h3>
			<div class="reading-body">
				{#each reading.split('\n') as line}
					{#if line.trim()}
						<p>{line}</p>
					{/if}
				{/each}
			</div>
		</div>
	{/if}

</div>

<style>
	.form-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 0.6rem; }
	.form-grid .full { grid-column: span 2; }
	.loc-row { display: grid; grid-template-columns: 1fr 1fr; gap: 0.6rem; }
	label { font-size: 0.72rem; color: var(--color-text-muted); }
	.fi { background: var(--color-surface-1); border: 1px solid var(--color-border); border-radius: 8px; padding: 0.5rem 0.65rem; color: var(--color-text-base); font-size: 0.85rem; outline: none; width: 100%; }
	.fi:focus { border-color: var(--color-primary); }
	.tab-bar { display: flex; gap: 2px; margin-bottom: 1rem; overflow-x: auto; }
	.tab { padding: 0.4rem 0.65rem; background: var(--color-surface-1); border: 1px solid var(--color-border); border-bottom: none; border-radius: 8px 8px 0 0; color: var(--color-text-muted); font-size: 0.72rem; cursor: pointer; white-space: nowrap; transition: all 0.2s; }
	.tab:hover { background: var(--color-surface-2); }
	.tab.active { background: var(--color-primary); color: white; border-color: var(--color-primary); }
	.tab-content { animation: fade 0.25s ease; }
	.tab-pane { display: none; }
	.tab-pane.active { display: block; }

	.synth-btn {
		display: block; width: 100%; padding: 0.6rem; border: 2px dashed var(--color-primary);
		border-radius: 12px; background: rgba(168,85,247,0.06); color: var(--color-primary);
		font-size: 0.9rem; font-weight: 600; cursor: pointer; transition: all 0.25s;
	}
	.synth-btn:hover:not(:disabled) { background: var(--color-primary); color: white; box-shadow: var(--shadow-glow-primary); }
	.synth-btn:disabled { opacity: 0.5; cursor: wait; }

	.reading-card { background: linear-gradient(135deg, rgba(168,85,247,0.08), rgba(6,182,212,0.08)); border: 1px solid var(--color-border-active); border-radius: 16px; padding: 1.5rem; animation: fade 0.5s ease; }
	.reading-head { font-size: 1.15rem; font-weight: 700; color: var(--color-text-base); margin-bottom: 1rem; }
	.reading-body { line-height: 1.8; }
	.reading-body p { margin: 0.4rem 0; color: var(--color-text-muted); font-size: 0.88rem; }

	@keyframes fade { from { opacity: 0; transform: translateY(6px); } to { opacity: 1; transform: translateY(0); } }
</style>
