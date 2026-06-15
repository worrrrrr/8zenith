<script lang="ts">
	import { onMount } from 'svelte';
	import { page } from '$app/state';
	import Icon from '$lib/components/AnimatedIcons.svelte';
	import ZenithLogo from '$lib/components/ZenithLogo.svelte';

	interface MenuItem {
		name: string;
		href?: string;
		icon: string;
		children?: MenuItem[];
	}

	interface Props {
		collapsed?: boolean;
		ontoggle?: () => void;
	}

	let { collapsed = false, ontoggle }: Props = $props();

	const pages = import.meta.glob('/src/routes/**/+page.svelte');

	function getIcon(name: string): string {
		const icons: Record<string, string> = {
			root: '🏠',
			chat: '💬',
			tools: '🛠️',
			astrology: '🌟',
			personality: '🌌',
			notebook: '📓',
			settings: '⚙️',
			prompts:'🤖',
			games:'🃏',
			'zenith-tower':'🏯',
			projects:'📋'
		};
		return icons[name.toLowerCase()] || '📁';
	}

	const menuItems = $derived.by(() => {
		const root: MenuItem = { name: 'Root', icon: '🏠', children: [] };

		for (const path in pages) {
			let cleanPath = path.replace('/src/routes/', '').replace('/+page.svelte', '');
			if (cleanPath.includes('(') || cleanPath.includes('[') || cleanPath.startsWith('+')) continue;
			if (cleanPath === '') {
				root.children!.push({ name: 'Home', href: '/', icon: '🏠' });
				continue;
			}
			const segments = cleanPath.split('/');
			let currentLevel = root.children!;
			let currentHref = '';
			segments.forEach((segment, index) => {
				currentHref += `/${segment}`;
				const isLast = index === segments.length - 1;
				const displayName = segment.charAt(0).toUpperCase() + segment.slice(1);
				let existing = currentLevel.find((item) => item.name === displayName);
				if (!existing) {
					existing = {
						name: displayName,
						icon: getIcon(segment),
						href: isLast ? currentHref : undefined,
						children: isLast ? undefined : []
					};
					currentLevel.push(existing);
				} else if (isLast) {
					existing.href = currentHref;
				}
				if (existing.children) currentLevel = existing.children;
			});
		}
		return (
			root.children?.sort((a, b) => {
				if (a.name === 'Home') return -1;
				if (b.name === 'Home') return 1;
				return a.name.localeCompare(b.name);
			}) ?? []
		);
	});

	let expandedFolders = $state<Record<string, boolean>>({});
	let currentPath = $derived(page.url.pathname);

	function isItemActive(item: MenuItem): boolean {
		if (item.href === '/') return currentPath === '/';
		if (item.href && currentPath === item.href) return true;
		if (item.children) return item.children.some((child) => isItemActive(child));
		return false;
	}

	function autoExpandActiveFolders(items: MenuItem[]) {
		for (const item of items) {
			if (item.children) {
				const hasActiveChild = item.children.some(
					(child) => isItemActive(child) || (child.children && isItemActive(child))
				);
				if (hasActiveChild) expandedFolders[item.name] = true;
				autoExpandActiveFolders(item.children);
			}
		}
	}

	$effect(() => {
		autoExpandActiveFolders(menuItems);
	});

	function toggleFolder(name: string) {
		expandedFolders[name] = !expandedFolders[name];
	}

	let currentTheme = $state('dark');

	onMount(() => {
		currentTheme = document.documentElement.getAttribute('data-theme') || 'dark';
	});

	const themes = [
		{ id: 'light', icon: '☀️', label: 'Light' },
		{ id: 'dark', icon: '🌙', label: 'Dark' },
		{ id: 'midnight', icon: '🌌', label: 'Midnight' },
		{ id: 'aurora', icon: '🌷', label: 'Aurora' },
		{ id: 'forest', icon: '🌿', label: 'Forest' },
		{ id: 'ocean', icon: '🌊', label: 'Ocean' },
		{ id: 'sunset', icon: '🔥', label: 'Sunset' },
	];

	function setTheme(theme: string) {
		currentTheme = theme;
		document.documentElement.setAttribute('data-theme', theme);
		localStorage.setItem('theme', theme);
	}

	function cycleTheme() {
		const idx = themes.findIndex(t => t.id === currentTheme);
		const next = themes[(idx + 1) % themes.length];
		setTheme(next.id);
	}
</script>

<nav class="sidebar-nav" class:collapsed>
	{#if collapsed}
		<button class="toggle-btn" onclick={ontoggle} title="ขยายเมนู">
				<ZenithLogo size={28} />
		</button>

		<div class="mini-icons">
			{#each menuItems as item}
				<a href={item.href || '#'} class="mini-icon" title={item.name}>
					<span>{item.icon}</span>
				</a>
			{/each}
		<button class="mini-icon theme-toggle" onclick={cycleTheme} title={themes.find(t => t.id === currentTheme)?.label}>
				<span>{themes.find(t => t.id === currentTheme)?.icon || '🎨'}</span>
			</button>
		</div>
	{:else}
		<div class="sidebar-header">
			<div class="brand">
				<a href="/" class="href">
					<ZenithLogo size={28} />
				</a>
				<span class="logo text-gradient-primary">8zenith</span>
			</div>
			<button class="toggle-btn" onclick={ontoggle} title="ย่อเมนู">
				<Icon name="toggle" size={18} dir="left" />
			</button>
		</div>
		<div class="search-wrap">
			<Icon name="search" size={16} />
			<input type="text" class="search-input" placeholder="ค้นหาเมนู..." />
		</div>
		<div class="menu-container">
			{@render renderMenu(menuItems, 0)}
		</div>
		<div class="theme-footer">
			<div class="theme-label">🎨 {themes.find(t => t.id === currentTheme)?.label || 'Theme'}</div>
			<div class="theme-buttons">
				{#each themes as t}
					<button class="theme-btn" class:active={currentTheme === t.id} onclick={() => setTheme(t.id)} title={t.label}>
						{t.icon}
					</button>
				{/each}
			</div>
		</div>
	{/if}
</nav>

{#snippet renderMenu(items: MenuItem[], depth: number)}
	<ul class="menu-list" style="--depth: {depth}">
		{#each items as item}
			{@const active = isItemActive(item)}
			{@const hasChildren = !!item.children?.length}
			{@const isOpen = expandedFolders[item.name]}
			<li>
				{#if hasChildren}
					<button
						type="button"
						class="sidebar-link folder-trigger"
						class:active-parent={active}
						onclick={() => toggleFolder(item.name)}
					>
						<span class="icon">{item.icon}</span>
						{#if item.href}
							<a href={item.href} class="name-link" class:active={currentPath === item.href}
								>{item.name}</a
							>
						{:else}
							<span class="name">{item.name}</span>
						{/if}
						<span class="arrow-icon" class:rotated={isOpen}>➔</span>
					</button>
					<div class="submenu-wrapper" style="grid-template-rows: {isOpen ? '1fr' : '0fr'}">
						<div class="submenu-content">
							{@render renderMenu(item.children!, depth + 1)}
						</div>
					</div>
				{:else}
					<a href={item.href} class="sidebar-link" class:active={currentPath === item.href}>
						<span class="icon">{item.icon}</span>
						<span class="name">{item.name}</span>
					</a>
				{/if}
			</li>
		{/each}
	</ul>
{/snippet}

<style>
	.sidebar-nav {
		display: flex;
		flex-direction: column;
		height: 100%;
		overflow: hidden;
		will-change: width;
	}

	.toggle-btn {
		display: flex;
		align-items: center;
		justify-content: center;
		width: 36px;
		height: 36px;
		flex-shrink: 0;
		background: var(--color-surface-1);
		border: 1px solid var(--color-border);
		border-radius: 8px;
		color: var(--color-text-muted);
		cursor: pointer;
		transition: all 0.2s;
	}
	.toggle-btn:hover {
		background: var(--color-primary);
		color: white;
		border-color: var(--color-primary);
		box-shadow: 0 0 20px rgba(168, 85, 247, 0.5);
	}
	.sidebar-nav.collapsed .toggle-btn {
		margin: 6px auto;
	}

	.sidebar-header {
		display: flex;
		align-items: center;
		justify-content: space-between;
		padding: 0.5rem 1rem;
		border-bottom: 1px solid var(--color-border);
		margin-bottom: 0.25rem;
	}
	.brand {
		display: flex;
		align-items: center;
		gap: 0.35rem;
	}
	.logo {
		font-size: 1.2rem;
		font-weight: bold;
		white-space: nowrap;
	}

	.search-wrap {
		display: flex;
		align-items: center;
		gap: 0.15rem;
		margin: 0.25rem 0.5rem;
		padding: 0.25rem 0.5rem;
		background: var(--color-surface-1);
		border: 1px solid var(--color-border);
		border-radius: 6px;
		color: var(--color-text-muted);
		transition: all 0.2s;
	}
	.search-wrap:focus-within {
		border-color: var(--color-primary);
		box-shadow: 0 0 8px rgba(168, 85, 247, 0.15);
	}
	.search-input {
		background: none;
		border: none;
		outline: none;
		color: var(--color-text-base);
		font-size: 0.75rem;
		width: 100%;
	}
	.search-input::placeholder {
		color: var(--color-text-muted);
		opacity: 0.5;
	}

	/* --- Collapsed Mini Icons --- */
	.mini-icons {
		display: flex;
		flex-direction: column;
		align-items: center;
		gap: 4px;
		padding: 8px 0;
		flex: 1;
		overflow-y: auto;
	}
	.mini-icon {
		display: flex;
		align-items: center;
		justify-content: center;
		width: 36px;
		height: 36px;
		border-radius: 8px;
		font-size: 1.1rem;
		text-decoration: none;
		transition: all 0.2s;
	}
	.mini-icon:hover {
		background: rgba(168, 85, 247, 0.15);
		transform: scale(1.15);
	}
	.mini-icon:hover span {
		animation: mini-bounce 0.4s ease;
	}

	@keyframes mini-bounce {
		0%,
		100% {
			transform: scale(1);
		}
		50% {
			transform: scale(1.25);
		}
	}
	.theme-toggle {
		margin-top: auto;
		background: none;
		border: none;
		cursor: pointer;
	}

	/* --- Expanded Menu --- */
	.menu-container {
		flex: 1;
		overflow-y: auto;
		padding: 0.25rem 0.5rem;
	}
	.menu-list {
		list-style: none;
		padding: 0;
		margin: 0;
	}
	li {
		margin: 0.1rem 0;
	}
	.icon {
		font-size: 1.1rem;
		width: 1.5rem;
		text-align: center;
		flex-shrink: 0;
	}
	.sidebar-link {
		display: flex;
		align-items: center;
		gap: 0.5rem;
		padding: 0.45rem 0.75rem;
		border-radius: 0.5rem;
		color: var(--color-text-muted);
		text-decoration: none;
		transition: all 0.2s;
		cursor: pointer;
		border: none;
		background: none;
		width: 100%;
		text-align: left;
		font-size: 0.85rem;
	}
	.sidebar-link:hover {
		background: rgba(168, 85, 247, 0.1);
		color: var(--color-text-base);
	}
	.sidebar-link.active {
		background: rgba(168, 85, 247, 0.15);
		color: var(--color-primary);
	}
	.name-link {
		color: inherit;
		text-decoration: none;
		flex: 1;
	}
	.arrow-icon {
		margin-left: auto;
		font-size: 0.65rem;
		transition: transform 0.2s;
	}
	.arrow-icon.rotated {
		transform: rotate(90deg);
	}
	.submenu-wrapper {
		display: grid;
		transition: grid-template-rows 0.25s;
	}
	.submenu-content {
		overflow: hidden;
		padding-left: 0.75rem;
	}

	.theme-footer {
		padding: 0.75rem;
		border-top: 1px solid var(--color-border);
		background: var(--color-surface-4);
	}
	.theme-label {
		font-size: 0.6rem;
		text-transform: uppercase;
		letter-spacing: 1px;
		color: var(--color-text-muted);
		margin-bottom: 0.35rem;
		text-align: center;
	}
	.theme-buttons {
		display: flex;
		gap: 0.25rem;
		justify-content: center;
	}
	.theme-btn {
		background: var(--color-surface-2);
		border: none;
		border-radius: 30px;
		padding: 0.25rem 0.5rem;
		font-size: 0.9rem;
		cursor: pointer;
		transition: all 0.2s;
	}
	.theme-btn.active {
		background: linear-gradient(135deg, var(--color-primary), var(--color-secondary));
		box-shadow: var(--shadow-glow-primary);
	}
</style>
