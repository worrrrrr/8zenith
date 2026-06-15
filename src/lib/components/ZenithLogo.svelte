<script lang="ts">
	interface Props {
		size?: number;
		animated?: boolean;
	}

	let { size = 40, animated = true }: Props = $props();
</script>

<svg
	class="zenith-logo"
	class:animated
	width={size}
	height={size}
	viewBox="0 0 100 100"
	fill="none"
	xmlns="http://www.w3.org/2000/svg"
>
	<!-- Definitions for gradients -->
	<defs>
		<linearGradient id="logo-grad-{size}" x1="0%" y1="0%" x2="100%" y2="100%">
			<stop offset="0%" stop-color="#a855f7" />
			<stop offset="100%" stop-color="#06b6d4" />
		</linearGradient>
		<linearGradient id="logo-accent-{size}" x1="0%" y1="100%" x2="100%" y2="0%">
			<stop offset="0%" stop-color="#f59e0b" />
			<stop offset="100%" stop-color="#a855f7" />
		</linearGradient>
	</defs>

	<!-- ⏳ วงแหวนนอก — กฎแห่งสังสารวัฏ (Cycle of Samsara) -->
	<circle class="ring-outer" cx="50" cy="50" r="46" stroke="url(#logo-grad-{size})" stroke-width="1.5" />
	<circle class="ring-mid" cx="50" cy="50" r="40" stroke="url(#logo-accent-{size})" stroke-width="1" stroke-dasharray="4 6" />

	<!-- 🔮 กฎแห่งกาลเวลา (Time) — นาฬิกาทราย / Infinity -->
	<!-- เส้นโค้งแทนกาลเวลาที่ไหลเวียน -->
	<path class="time-flow" d="M50 15 C35 30, 30 45, 50 50 C70 55, 65 70, 50 85" stroke="url(#logo-grad-{size})" stroke-width="1.8" stroke-linecap="round" />
	<path class="time-flow delay" d="M50 15 C65 30, 70 45, 50 50 C30 55, 35 70, 50 85" stroke="url(#logo-accent-{size})" stroke-width="1.8" stroke-linecap="round" />

	<!-- 🧊 กฎแห่งมิติ (Dimensions) — รูปทรงเรขาคณิตซ้อนทับ -->
	<!-- สามเหลี่ยมด้านเท่า — มิติที่ 1 -->
	<polygon class="dim-shape d1" points="50,22 72,65 28,65" stroke="url(#logo-grad-{size})" stroke-width="1.2" fill="none" />

	<!-- สี่เหลี่ยม — มิติที่ 2 (ทับซ้อนกลับด้าน) -->
	<polygon class="dim-shape d2" points="30,35 70,35 60,70 40,70" stroke="url(#logo-accent-{size})" stroke-width="1" fill="none" opacity="0.6" />

	<!-- จุดศูนย์กลาง — กฎทั้งสามบรรจบ -->
	<circle class="center-dot" cx="50" cy="50" r="3" fill="url(#logo-grad-{size})" />
	<circle class="center-glow" cx="50" cy="50" r="6" fill="none" stroke="url(#logo-grad-{size})" stroke-width="0.8" />
</svg>

<style>
	.zenith-logo.animated .ring-outer {
		animation: logo-spin 12s linear infinite;
		transform-origin: center;
	}

	.zenith-logo.animated .ring-mid {
		animation: logo-spin-rev 8s linear infinite;
		transform-origin: center;
	}

	.zenith-logo.animated .time-flow {
		stroke-dasharray: 80;
		stroke-dashoffset: 0;
		animation: time-draw 4s ease-in-out infinite alternate;
	}

	.zenith-logo.animated .time-flow.delay {
		animation-delay: 2s;
	}

	.zenith-logo.animated .dim-shape {
		animation: dim-pulse 3s ease-in-out infinite alternate;
	}

	.zenith-logo.animated .dim-shape.d2 {
		animation-delay: 0.5s;
		animation-duration: 4s;
	}

	.zenith-logo.animated .center-glow {
		animation: glow-pulse 2s ease-in-out infinite;
	}

	@keyframes logo-spin {
		from { transform: rotate(0deg); }
		to { transform: rotate(360deg); }
	}

	@keyframes logo-spin-rev {
		from { transform: rotate(360deg); }
		to { transform: rotate(0deg); }
	}

	@keyframes time-draw {
		0% { stroke-dashoffset: 80; opacity: 0.4; }
		100% { stroke-dashoffset: 0; opacity: 1; }
	}

	@keyframes dim-pulse {
		0% { opacity: 0.3; transform: scale(0.95); }
		100% { opacity: 0.8; transform: scale(1.05); }
	}

	@keyframes glow-pulse {
		0%, 100% { r: 6; opacity: 0.5; }
		50% { r: 9; opacity: 1; }
	}
</style>
