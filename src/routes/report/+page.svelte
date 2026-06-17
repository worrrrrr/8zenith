<script lang="ts">
	import { calculateChineseReports } from '$lib/astrology/chinese';
	import { calcAyanamsa, findNakshatra, getVedicSign, GRAHA_NAMES } from '$lib/astrology/vedic';
	import { getThaiDay, getThaiZodiac, THAI_PLANETS } from '$lib/astrology/thai';
	import { calcHumanDesign } from '$lib/astrology/human-design';
	import { onMount } from 'svelte';
	import { browser } from '$app/environment';

	let birthYear = $state(1992);
	let birthMonth = $state(8);
	let birthDay = $state(8);
	let birthHour = $state(16);
	let birthMinute = $state(49);
	let lat = $state(6.54);
	let lng = $state(101.28);
	let loading = $state(false);
	let error = $state('');
	let report = $state<any>(null);
	let reading = $state<string>('');
	let sweReady = $state(false);

	onMount(async () => {
		if (browser) {
			try { await import('@swisseph/browser'); sweReady = true; } catch {}
		}
	});

	async function run() {
		loading = true; error = ''; report = null; reading = '';
		const hd = birthHour + birthMinute / 60;
		try {
			const chinese = calculateChineseReports(birthYear, birthMonth, birthDay, hd);
			let western, vedic, thai, hdReport;
			if (browser && sweReady) {
				const mod = await import('@swisseph/browser');
				const { SwissEphemeris, HouseSystem, CalculationFlag } = mod;
				const swe = new SwissEphemeris(); await swe.init();
				const jd = swe.julianDay(birthYear, birthMonth, birthDay, hd);
				const Z = ['Aries','Taurus','Gemini','Cancer','Leo','Virgo','Libra','Scorpio','Sagittarius','Capricorn','Aquarius','Pisces'];
				const PN: Record<number,string> = {0:'Sun',1:'Moon',2:'Mercury',3:'Venus',4:'Mars',5:'Jupiter',6:'Saturn',7:'Uranus',8:'Neptune',9:'Pluto'};
				const tp = [0,1,2,3,4,5,6,7,8,9].map(id => {
					const pos = swe.calculatePosition(jd, id, CalculationFlag.MoshierEphemeris|CalculationFlag.Speed);
					const si = Math.floor(pos.longitude/30)%12;
					return { ...pos, id, name: PN[id], sign: Z[si], degree: pos.longitude%30, rx: pos.longitudeSpeed<0 };
				});
				const h = swe.calculateHouses(jd, lat, lng, HouseSystem.Placidus);
				const hs = []; for (let i=1;i<=12;i++){const si=Math.floor(h.cusps[i]/30)%12;hs.push({n:i,s:Z[si],d:h.cusps[i]%30});}
				const as=Math.floor(h.ascendant/30)%12, ms=Math.floor(h.mc/30)%12;
				western = { sunSign: tp[0].sign, moonSign: tp[1].sign, ascSign: Z[as], ascDeg: h.ascendant%30,
					planets: tp.map(p=>({name:p.name,sign:p.sign,degree:p.degree,retrograde:p.rx})),
					houses: hs, ascendant: h.ascendant, mc: h.mc };

				const ay = calcAyanamsa(jd);
				const sp = tp.map(p => {
					const sl = ((p.longitude-ay)%360+360)%360;
					const nak = findNakshatra(sl);
					return { name: p.name, vedicName: GRAHA_NAMES[p.id]||p.name, tropical:{sign:p.sign,degree:p.degree}, sidereal:{sign:getVedicSign(sl),degree:sl%30}, nakshatra:nak, retrograde:p.rx };
				});
				const va = ((h.ascendant-ay)%360+360)%360;
				vedic = { nakshatra: sp[1]?.nakshatra?.name, nakPada: sp[1]?.nakshatra?.pada, nakLord: sp[1]?.nakshatra?.lord, moonSign: sp[1]?.sidereal?.sign, ascSign: getVedicSign(va),
					planets: sp };

				const thp = tp.map(p => {const sl=((p.longitude-ay)%360+360)%360; return {name:p.name,thaiName:THAI_PLANETS[p.id]||p.name,sign:getThaiZodiac(sl),degree:sl%30,retrograde:p.rx};});
				const jsDay = new Date(Date.UTC(birthYear, birthMonth-1, birthDay)).getUTCDay();
				thai = { planets: thp, ascSign: getThaiZodiac(va), dayInfo: getThaiDay(jsDay) };

				try {
  const gl = (n:string) => tp.find(p => p.name === n)?.longitude ?? 0;
  hdReport = calcHumanDesign(jd, {
    sun: gl('Sun'),
    earth: (gl('Sun') + 180) % 360,
    moon: gl('Moon'),
    mercury: gl('Mercury'),
    venus: gl('Venus'),
    mars: gl('Mars'),
    jupiter: gl('Jupiter'),
    saturn: gl('Saturn'),
    uranus: gl('Uranus'),
    neptune: gl('Neptune'),
    pluto: gl('Pluto'),
    northNode: 0,
    southNode: 180
  });
} catch(e) {
  console.error(e);
}

		}
		report = { chinese, western, vedic, thai, hd: hdReport };
		const res = await fetch('/api/deepseek', { method:'POST', body: JSON.stringify({ birth:{year:birthYear,month:birthMonth,day:birthDay,hour:birthHour,minute:birthMinute,lat,lng}, western:western?.planets, vedic, thai, baZi:chinese.eightChar, lunar:chinese.lunar, nineStar:chinese.nineStar, taoist:chinese.taoist, humanDesign:hdReport }) });
		const json = await res.json(); reading = json.reading;
		loading = false;
	}
</script>

<div class="mx-auto max-w-6xl px-4 py-8">
	<h1 class="mb-8 text-4xl font-bold">8Zenith Sinsae</h1>
	<section class="mb-10 rounded-xl border p-6 shadow-sm">
		<div class="grid grid-cols-2 gap-4 md:grid-cols-4 mb-4">
			<input type="number" bind:value={birthYear} placeholder="Year" class="border p-2 rounded" />
			<input type="number" bind:value={birthMonth} placeholder="Month" class="border p-2 rounded" />
			<input type="number" bind:value={birthDay} placeholder="Day" class="border p-2 rounded" />
			<input type="number" bind:value={birthHour} placeholder="Hour" class="border p-2 rounded" />
		</div>
		<button onclick={run} class="bg-indigo-600 text-white px-6 py-2 rounded">วิเคราะห์ดวงชะตา</button>
	</section>

	{#if reading}
		<section class="prose max-w-none p-6 bg-white rounded-xl shadow mb-10">{@html reading.replace(/\n/g, '<br>')}</section>
	{/if}
</div>
