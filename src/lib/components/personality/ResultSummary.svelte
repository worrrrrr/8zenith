<script lang="ts">
	interface Props {
		summary: string;
		enneagramType: string;
		enneagramDesc: string;
		wingLabel: string;
		wingDesc: string;
		mbtiType: string;
		mbtiDesc: string;
		dominant: string;
		auxiliary: string;
		enneagramScores: [string, number][];
		cognitiveScores: [string, number][];
		dichotomies: Record<string, number>;
		onreset: () => void;
	}

	let {
		summary, enneagramType, enneagramDesc, wingLabel, wingDesc,
		mbtiType, mbtiDesc, dominant, auxiliary,
		enneagramScores, cognitiveScores, dichotomies, onreset
	}: Props = $props();

	const dimLabel: Record<string, string> = {
		I: 'Introvert', E: 'Extrovert', S: 'Sensing', N: 'Intuition',
		T: 'Thinking', F: 'Feeling', J: 'Judging', P: 'Perceiving'
	};
</script>

<div class="result-section">
	<h2 class="text-gradient-primary text-2xl font-bold mb-2">🔮 ผลวิเคราะห์</h2>
	<hr class="neon-divider" />

	<div class="summary-card mb-4">
		<p class="text-text-base text-lg font-bold leading-relaxed">{summary}</p>
	</div>

	<div class="card mb-4">
		<h3 class="card-head">🏷️ Enneagram</h3>
		<p class="card-value">
			{enneagramType} — <span class="text-secondary">{wingLabel}</span>
		</p>
		<p class="card-desc whitespace-pre-line">{enneagramDesc}</p>
		{#if wingDesc}
			<p class="wing-note">✦ Wing: {wingDesc}</p>
		{/if}
		<div class="tags">
			{#each enneagramScores as [type, score]}
				<span class="tag">{type}: {score} คะแนน</span>
			{/each}
		</div>
	</div>

	<div class="card mb-4">
		<h3 class="card-head">🧩 MBTI</h3>
		<p class="card-value">{mbtiType} — {mbtiDesc}</p>
		<p class="card-desc">
			<span class="text-accent font-bold">{dominant}</span> (Dominant)
			+
			<span class="text-secondary font-bold">{auxiliary}</span> (Auxiliary)
		</p>
		<div class="tags">
			{#each cognitiveScores as [fn, score]}
				<span class="tag">{fn}: {score} คะแนน</span>
			{/each}
		</div>
	</div>

	<div class="card mb-4">
		<h3 class="card-head">🗂️ Dichotomies</h3>
		<div class="dims-grid">
			{#each Object.entries(dichotomies).sort(([,a], [,b]) => b - a) as [key, val]}
				<span class="dim-item">
					<span>{dimLabel[key] || key}</span>
					<span>{val}</span>
				</span>
			{/each}
		</div>
	</div>

	<div class="card">
		<h3 class="card-head">💡 คำแนะนำ</h3>
		<p class="card-desc text-sm leading-relaxed">
			ผลลัพธ์นี้สะท้อนโค้งแห่งการรับรู้และการตัดสินใจภายในของคุณ ใช้เป็นกระจกสะท้อนตน ฝึกพัฒนาฟังก์ชันที่อ่อนกว่าเพื่อสร้างสมดุล — เส้นทางแห่งการรู้ตนไม่มีวันสิ้นสุด
		</p>
	</div>

	<button class="quantum-btn mt-6" onclick={onreset}>🔄 ทำแบบทดสอบใหม่</button>
</div>

<style>
	.result-section { animation: rFadeIn 0.4s ease; }

	.summary-card {
		background: linear-gradient(135deg, rgba(168,85,247,0.1), rgba(6,182,212,0.1));
		border: 1px solid var(--color-border-active);
		border-radius: 14px;
		padding: 1.25rem;
	}

	.card {
		background: var(--color-surface-1);
		border: 1px solid var(--color-border);
		border-radius: 12px;
		padding: 1rem;
	}

	.card-head { font-size: 1.05rem; font-weight: 700; color: var(--color-primary); margin-bottom: 0.4rem; }

	.card-value {
		font-size: 1.15rem;
		font-weight: 700;
		color: var(--color-text-base);
		margin-top: 0.4rem;
	}

	.card-desc {
		color: var(--color-text-muted);
		font-size: 0.82rem;
		margin-top: 0.25rem;
	}

	.wing-note {
		color: var(--color-text-muted);
		font-size: 0.7rem;
		margin-top: 0.15rem;
		opacity: 0.7;
	}

	.tags {
		display: flex;
		flex-wrap: wrap;
		gap: 0.3rem;
		margin-top: 0.5rem;
	}

	.tag {
		background: var(--color-surface-2);
		border: 1px solid var(--color-border);
		border-radius: 20px;
		padding: 0.15rem 0.55rem;
		font-size: 0.68rem;
		color: var(--color-text-muted);
	}

	.dims-grid {
		display: grid;
		grid-template-columns: 1fr 1fr;
		gap: 0.3rem;
		margin-top: 0.4rem;
	}

	.dim-item {
		display: flex;
		justify-content: space-between;
		background: var(--color-surface-2);
		border-radius: 6px;
		padding: 0.3rem 0.5rem;
		font-size: 0.75rem;
		color: var(--color-text-muted);
	}

	@keyframes rFadeIn {
		from { opacity: 0; transform: translateY(10px); }
		to { opacity: 1; transform: translateY(0); }
	}
</style>
