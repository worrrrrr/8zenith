<script lang="ts">
	import Icon from '$lib/components/AnimatedIcons.svelte';

	interface Props {
		collapsed?: boolean;
		ontoggle?: () => void;
	}

	let { collapsed = false, ontoggle }: Props = $props();

	let sections = $state([
		{ id: 'clock', label: '🕐 เวลา', icon: '🕐', open: true },
		{ id: 'mood', label: '🧠 AI Mood', icon: '🧠', open: false },
	]);

	let code = $state('9.8-9.11');
	let result = $derived(evaluate(code));
	let now = $state(new Date());

	function evaluate(expr: string): string {
		try {
			const fn = new Function('return (' + expr + ')');
			return String(fn());
		} catch (e: unknown) {
			return 'error: ' + (e instanceof Error ? e.message : String(e));
		}
	}

	$effect(() => {
		const id = setInterval(() => now = new Date(), 1000);
		return () => clearInterval(id);
	});

	function toggleSection(id: string) {
		const section = sections.find(s => s.id === id);
		if (section) section.open = !section.open;
	}
</script>

<aside class="right-pane" class:collapsed>
	<div class="pane-inner">
		<button class="toggle-btn" onclick={ontoggle} title={collapsed ? 'ขยายแผง' : 'ย่อแผง'}>
			<Icon name="toggle" size={18} dir={collapsed ? 'left' : 'right'} />
		</button>

		{#if collapsed}
			<div class="mini-icons">
				{#each sections as section}
					<button class="mini-icon" onclick={ontoggle} title={section.label}>
						<span>{section.icon}</span>
					</button>
				{/each}
			</div>
		{:else}
			<div class="pane-header">
				<span class="pane-title">📊 Dashboard</span>
			</div>
			<div class="pane-body">
				{#each sections as section}
					<div class="section">
						<button class="section-header" onclick={() => toggleSection(section.id)}>
							<span>{section.label}</span>
							<span class="chevron" class:open={section.open}>
								<svg width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round">
									<polyline points="6 9 12 15 18 9"/>
								</svg>
							</span>
						</button>
						<div class="section-body" style="display: {section.open ? 'block' : 'none'}">
							{#if section.id === 'clock'}
								<div class="clock-card">
									<div class="time-large">{now.toLocaleTimeString('th-TH', { hour: '2-digit', minute: '2-digit' })}</div>
									<div class="date">{now.toLocaleDateString('th-TH', { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' })}</div>
								</div>
							{:else if section.id === 'mood'}
								<div class="mood-card">
									<div class="mood-header">
										<Icon name="sparkle" size={22} />
										<span class="ai-mood">🧘 สงบและมีสมาธิ</span>
									</div>
									<div class="ai-quote">"The stars align to guide your quantum path."</div>
								</div>
							{/if}
						</div>
					</div>
				{/each}
			</div>
		{/if}
	</div>
</aside>

<style>
	.right-pane {
		height: 100%;
		overflow: hidden;
		will-change: width;
	}

	.pane-inner {
		height: 100%;
		display: flex;
		flex-direction: column;
		align-items: center;
	}

	.toggle-btn {
		display: flex;
		align-items: center;
		justify-content: center;
		width: 36px;
		height: 36px;
		margin: 6px;
		flex-shrink: 0;
		background: var(--color-surface-1);
		border: 1px solid var(--color-border);
		border-radius: 8px;
		color: var(--color-text-muted);
		cursor: pointer;
		transition: all 0.2s;
	}
	.toggle-btn:hover {
		background: var(--color-secondary);
		color: white;
		border-color: var(--color-secondary);
		box-shadow: 0 0 20px rgba(6, 182, 212, 0.5);
	}
	.right-pane.collapsed .toggle-btn {
		margin: 6px auto;
	}
	.right-pane:not(.collapsed) .pane-inner {
		align-items: flex-start;
	}
	.right-pane:not(.collapsed) .toggle-btn {
		align-self: flex-start;
		margin-left: -1px;
		border-radius: 0 8px 8px 0;
		border-left: none;
	}

	/* --- Collapsed: mini icons --- */
	.mini-icons {
		display: flex;
		flex-direction: column;
		align-items: center;
		gap: 4px;
		padding: 4px 0;
		flex: 1;
	}
	.mini-icon {
		display: flex;
		align-items: center;
		justify-content: center;
		width: 36px;
		height: 36px;
		border-radius: 8px;
		font-size: 1.1rem;
		background: none;
		border: none;
		color: var(--color-text-muted);
		cursor: pointer;
		transition: all 0.2s;
	}
	.mini-icon:hover {
		background: rgba(6, 182, 212, 0.15);
		color: var(--color-secondary);
		transform: scale(1.15);
	}
	.mini-icon:hover span {
		animation: mini-bounce 0.4s ease;
	}
	@keyframes mini-bounce {
		0%, 100% { transform: scale(1); }
		50% { transform: scale(1.25); }
	}

	/* --- Expanded --- */
	.pane-header {
		width: 100%;
		padding: 0.6rem 0.75rem;
		border-bottom: 1px solid var(--color-border);
		flex-shrink: 0;
	}
	.pane-title {
		font-size: 0.8rem;
		font-weight: 600;
		color: var(--color-text-muted);
	}

	.pane-body {
		width: 100%;
		flex: 1;
		overflow-y: auto;
		padding: 0.5rem;
	}

	.section {
		margin-bottom: 0.4rem;
		border: 1px solid var(--color-border);
		border-radius: 10px;
		overflow: hidden;
	}

	.section-header {
		display: flex;
		align-items: center;
		justify-content: space-between;
		width: 100%;
		padding: 0.5rem 0.65rem;
		background: var(--color-surface-1);
		border: none;
		color: var(--color-text-muted);
		font-size: 0.78rem;
		cursor: pointer;
		transition: all 0.2s;
	}
	.section-header:hover {
		background: var(--color-surface-2);
		color: var(--color-text-base);
	}
	.section-header:hover .chevron svg {
		stroke: var(--color-secondary);
	}

	.chevron {
		display: flex;
		transition: transform 0.2s;
	}
	.chevron.open {
		transform: rotate(180deg);
	}

	.section-body {
		padding: 0.4rem;
	}

	.clock-card { text-align: center; padding: 0.4rem 0; }
	.time-large { font-size: 1.35rem; font-weight: bold; font-family: var(--font-mono); color: var(--color-primary); }
	.date { font-size: 0.7rem; color: var(--color-text-muted); margin-top: 0.2rem; }

	.mood-card { padding: 0.4rem; }
	.ai-mood { font-size: 0.9rem; margin-bottom: 0.2rem; }
	.ai-quote { font-size: 0.7rem; font-style: italic; color: var(--color-text-muted); }

	.calc-card { padding: 0.4rem; }
	.calc-input {
		background: var(--color-surface-1); border: 1px solid var(--color-border);
		border-radius: 6px; padding: 0.35rem 0.5rem; color: var(--color-text-base);
		font-family: var(--font-mono); font-size: 0.8rem; width: 100%; outline: none;
	}
	.calc-input:focus { border-color: var(--color-primary); }
	.calc-result { margin-top: 0.25rem; font-size: 0.8rem; color: var(--color-accent); font-family: var(--font-mono); }
</style>
