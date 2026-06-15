<script lang="ts">
	interface Props {
		name: 'pencil' | 'search' | 'sparkle' | 'toggle';
		size?: number;
		dir?: 'left' | 'right';
		class?: string;
	}

	let { name, size = 20, dir = 'right', class: className = '' }: Props = $props();
</script>

{#if name === 'pencil'}
	<svg
		class="icon-pencil {className}"
		width={size}
		height={size}
		viewBox="0 0 24 24"
		fill="none"
		stroke="currentColor"
		stroke-width="1.8"
		stroke-linecap="round"
		stroke-linejoin="round"
	>
		<path d="M17 3a2.85 2.85 0 1 1 4 4L7.5 20.5 2 22l1.5-5.5Z"/>
		<path class="icon-motion" d="m15 5 4 4"/>
	</svg>
{:else if name === 'search'}
	<svg
		class="icon-search {className}"
		width={size}
		height={size}
		viewBox="0 0 24 24"
		fill="none"
		stroke="currentColor"
		stroke-width="1.8"
		stroke-linecap="round"
		stroke-linejoin="round"
	>
		<circle cx="11" cy="11" r="8"/>
		<path class="icon-motion" d="m21 21-4.3-4.3"/>
	</svg>
{:else if name === 'sparkle'}
	<svg
		class="icon-sparkle {className}"
		width={size}
		height={size}
		viewBox="0 0 24 24"
		fill="none"
		stroke="currentColor"
		stroke-width="1.8"
		stroke-linecap="round"
		stroke-linejoin="round"
	>
		<path class="sparkle-main" d="M12 2l1.5 6.5L20 10l-6.5 1.5L12 18l-1.5-6.5L4 10l6.5-1.5z"/>
	</svg>
{:else if name === 'toggle'}
	<svg
		class="icon-toggle {className}"
		class:dir-left={dir === 'left'}
		width={size}
		height={size}
		viewBox="0 0 24 24"
		fill="none"
		stroke="currentColor"
		stroke-width="1.8"
		stroke-linecap="round"
		stroke-linejoin="round"
	>
		<rect x="3" y="3" width="18" height="18" rx="2"/>
		<path class="toggle-arrow" d="m14 9 4 3-4 3"/>
	</svg>
{/if}

<style>
	/* --- Pencil --- */
	.icon-pencil { transition: transform 0.25s ease; }
	.icon-pencil:hover { transform: rotate(-15deg); }
	.icon-pencil:hover .icon-motion { stroke-dasharray: 8; stroke-dashoffset: 8; animation: draw-line 0.4s ease forwards; }

	/* --- Search --- */
	.icon-search { transition: transform 0.25s ease; }
	.icon-search:hover { transform: scale(1.1); }
	.icon-search:hover .icon-motion { stroke-dasharray: 10; stroke-dashoffset: 10; animation: draw-line 0.4s ease forwards; }

	/* --- Sparkle --- */
	.icon-sparkle {
		transition: transform 0.3s ease;
	}
	.icon-sparkle:hover {
		transform: scale(1.15) rotate(20deg);
	}
	.sparkle-main {
		transform-origin: center;
		animation: sparkle-pulse 2s ease-in-out infinite;
	}
	.icon-sparkle:hover .sparkle-main {
		animation: sparkle-glow 0.6s ease forwards;
	}

	/* --- Toggle --- */
	.icon-toggle { transition: transform 0.3s ease; }
	.icon-toggle:hover { transform: scale(1.1); }
	.icon-toggle.dir-left { transform: scaleX(-1); }
	.icon-toggle.dir-left:hover { transform: scaleX(-1) scale(1.1); }
	.icon-toggle:hover .toggle-arrow {
		animation: arrow-peek 0.5s ease forwards;
	}

	/* --- Shared Keyframes --- */
	@keyframes draw-line {
		to { stroke-dashoffset: 0; }
	}

	@keyframes sparkle-pulse {
		0%, 100% { transform: scale(1); opacity: 0.6; }
		50% { transform: scale(1.08); opacity: 1; }
	}

	@keyframes sparkle-glow {
		0% { transform: scale(1); opacity: 0.8; filter: drop-shadow(0 0 2px currentColor); }
		50% { transform: scale(1.25); opacity: 1; filter: drop-shadow(0 0 8px currentColor); }
		100% { transform: scale(1); opacity: 0.8; filter: drop-shadow(0 0 2px currentColor); }
	}

	@keyframes arrow-peek {
		0%, 100% { transform: translateX(0); opacity: 1; }
		50% { transform: translateX(3px); opacity: 0.6; }
	}

	@keyframes divider-pulse {
		0%, 100% { opacity: 0.5; }
		50% { opacity: 1; }
	}

	@keyframes toggle-slide {
		0% { transform: translateX(0); }
		50% { transform: translateX(10px); }
		100% { transform: translateX(0); }
	}
</style>
