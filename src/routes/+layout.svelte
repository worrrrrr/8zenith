<script lang="ts">
    import './layout.css';
    import favicon from '$lib/assets/favicon.svg';
    import Sidemenu from '$lib/components/Sidemenu.svelte';
    import RightPane from '$lib/components/RightPane.svelte';

    let { children } = $props();

    let sidebarOpen = $state(true);
    let rightPaneOpen = $state(true);
</script>

<svelte:head>
    <link rel="icon" href={favicon} />
</svelte:head>

<div
    class="holy-grail"
    style="--sidebar-w: {sidebarOpen ? '280px' : '48px'}; --rightpane-w: {rightPaneOpen ? '320px' : '48px'}"
>
    <div class="holy-grail-left">
        <Sidemenu collapsed={!sidebarOpen} ontoggle={() => sidebarOpen = !sidebarOpen} />
    </div>
    
    <main class="holy-grail-main">
        {@render children()}
        
        </main>
    
    <div class="holy-grail-right">
        <RightPane collapsed={!rightPaneOpen} ontoggle={() => rightPaneOpen = !rightPaneOpen} />
    </div>
</div>


<style>
  .holy-grail {
    display: grid;
    grid-template-columns: auto 1fr auto;
    height: 100vh;      /* เปลี่ยนจาก min-height */
    overflow: hidden;   /* เพิ่มตรงนี้ */
  }
  
  .holy-grail-main {
    overflow-y: auto;   /* เพิ่มตรงนี้ */
    min-height: 0;      /* เพิ่มตรงนี้ */
  }
</style>