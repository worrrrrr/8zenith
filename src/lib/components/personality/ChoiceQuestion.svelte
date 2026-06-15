<script lang="ts">
	interface Option {
		key: string;
		text: string;
	}

	interface Props {
		number: number;
		title: string;
		options: Option[];
		selected: string | undefined;
		onselect: (key: string) => void;
	}

	let { number, title, options, selected, onselect }: Props = $props();
</script>

<div class="question-card">
	<h3 class="q-number">ข้อ {number}</h3>
	<p class="q-title">{title}</p>

	<div class="options-list">
		{#each options as opt}
			<button
				class="option-btn"
				class:selected={selected === opt.key}
				onclick={() => onselect(opt.key)}
			>
				<span class="option-radio" class:checked={selected === opt.key}>
					{#if selected === opt.key}●{/if}
				</span>
				<span class="option-text">{opt.text}</span>
			</button>
		{/each}
	</div>
</div>

<style>
	.question-card { animation: qFadeIn 0.3s ease; }
	.q-number { font-size: 1.1rem; font-weight: 600; color: var(--color-text-base); margin-bottom: 0.25rem; }
	.q-title { color: var(--color-text-muted); font-size: 0.85rem; margin-bottom: 1rem; line-height: 1.6; }
	.options-list { display: flex; flex-direction: column; gap: 0.4rem; }
	.option-btn {
		display: flex; align-items: flex-start; gap: 0.6rem;
		padding: 0.6rem 0.75rem;
		background: var(--color-surface-1);
		border: 1px solid var(--color-border);
		border-radius: 10px;
		color: var(--color-text-muted);
		font-size: 0.82rem;
		cursor: pointer;
		text-align: left;
		line-height: 1.5;
		transition: all 0.2s;
		width: 100%;
	}
	.option-btn:hover { background: var(--color-surface-2); border-color: var(--color-border-active); }
	.option-btn.selected { background: rgba(168, 85, 247, 0.12); border-color: var(--color-primary); color: var(--color-text-base); }
	.option-radio {
		display: flex; align-items: center; justify-content: center;
		width: 18px; height: 18px; border-radius: 50%;
		border: 2px solid var(--color-border); flex-shrink: 0; margin-top: 2px; font-size: 0.65rem; transition: all 0.2s;
	}
	.option-radio.checked { border-color: var(--color-primary); background: var(--color-primary); color: white; }
	.option-text { flex: 1; }
	@keyframes qFadeIn {
		from { opacity: 0; transform: translateY(6px); }
		to { opacity: 1; transform: translateY(0); }
	}
</style>
