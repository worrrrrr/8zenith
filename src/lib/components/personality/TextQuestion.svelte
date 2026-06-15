<script lang="ts">
	interface Props {
		number: number;
		title: string;
		placeholder: string;
		value: string;
		oninput: (v: string) => void;
	}

	let { number, title, placeholder, value, oninput }: Props = $props();
</script>

<div class="textq-card">
	<h3 class="q-number">ข้อ {number}</h3>
	<p class="q-title">{title}</p>
	<textarea class="text-input" rows="3" {placeholder} value={value} oninput={(e) => oninput(e.currentTarget.value)}></textarea>
</div>

<style>
	.textq-card { animation: qFadeIn 0.3s ease; }
	.q-number { font-size: 1.1rem; font-weight: 600; color: var(--color-text-base); margin-bottom: 0.25rem; }
	.q-title { color: var(--color-text-muted); font-size: 0.85rem; margin-bottom: 1rem; line-height: 1.6; }
	.text-input {
		width: 100%;
		background: var(--color-surface-1);
		border: 1px solid var(--color-border);
		border-radius: 10px;
		padding: 0.75rem;
		color: var(--color-text-base);
		font-size: 0.85rem;
		font-family: inherit;
		line-height: 1.6;
		resize: vertical;
		outline: none;
		transition: all 0.2s;
	}
	.text-input:focus { border-color: var(--color-primary); box-shadow: 0 0 0 2px rgba(168,85,247,0.12); }
	.text-input::placeholder { color: var(--color-text-muted); opacity: 0.4; }
	@keyframes qFadeIn {
		from { opacity: 0; transform: translateY(6px); }
		to { opacity: 1; transform: translateY(0); }
	}
</style>
