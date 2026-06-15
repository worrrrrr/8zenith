<script lang="ts">
	import Icon from '$lib/components/AnimatedIcons.svelte';
	let note = $state('');
	let saved = $state<string[]>([]);

	function saveNote() {
		if (!note.trim()) return;
		saved = [note, ...saved];
		note = '';
	}
</script>

<div class="cosmic-card p-6">
	<div class="flex items-center gap-2 mb-4">
		<Icon name="pencil" size={24} />
		<h2 class="text-primary text-xl font-bold">📓 Cosmic Notebook</h2>
	</div>
	<hr class="neon-divider" />
	<p class="text-text-muted mb-6">บันทึกความคิดและข้อมูลเชิงลึกแบบโฮโลแกรมส่วนตัว</p>

	<div class="flex gap-2 mb-4">
		<input
			type="text"
			bind:value={note}
			placeholder="พิมพ์บันทึกของคุณ..."
			class="flex-1 bg-surface-1 border border-surface-2 rounded-lg px-4 py-2 text-sm text-text-base outline-none focus:border-primary/50"
			onkeydown={(e) => e.key === 'Enter' && saveNote()}
		/>
		<button class="quantum-btn" onclick={saveNote}>บันทึก</button>
	</div>

	{#if saved.length > 0}
		<div class="space-y-2">
			{#each saved as entry, i}
				<div class="bg-surface-1 border border-surface-2 rounded-lg p-3 text-sm text-text-muted">
					{entry}
				</div>
			{/each}
		</div>
	{/if}
</div>
