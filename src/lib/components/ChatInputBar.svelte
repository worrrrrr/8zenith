<script lang="ts">
  import { tick } from 'svelte';

  interface ChatInputProps {
    onsend?: (text: string) => void | Promise<void>;
    activeQuestion?: string; 
  }

  let { onsend, activeQuestion = '' }: ChatInputProps = $props();

  interface SlashCommand {
    cmd: string;
    desc: string;
    icon: string;
  }

  interface ActionMenu {
    label: string;
    icon: string;
    action: () => void;
  }

  const commands: SlashCommand[] = [
    { cmd: '/clear', desc: 'ล้างประวัติการสนทนาทั้งหมดในห้องนี้', icon: '🧹' },
    { cmd: '/prompt', desc: 'ดึงเทมเพลต Prompt สำเร็จรูปจากระบบ', icon: '📝' },
    { cmd: '/code', desc: 'บังคับให้ AI ตอบเฉพาะซอร์สโค้ดโปรแกรมมิ่ง', icon: '💻' },
    { cmd: '/image', desc: 'เปลี่ยนโหมดเป็นเจนภาพด้วยโมเดล Diffusion', icon: '🎨' }
  ];

  let textInput = $state('');
  let showPlusMenu = $state(false);
  let selectedCommandIndex = $state(0);
  let textareaEl = $state<HTMLTextAreaElement | null>(null);
  let containerEl = $state<HTMLDivElement | null>(null);

  const plusActions: ActionMenu[] = [
    { label: 'อัปโหลดไฟล์เอกสาร', icon: '📁', action: () => handlePlusAction('Upload File') },
    { label: 'อัปโหลดรูปภาพ (Vision)', icon: '🖼️', action: () => handlePlusAction('Upload Image') },
    { label: 'เปิดใช้งานการค้นหาเว็บ Real-time', icon: '🌐', action: () => handlePlusAction('Web Search Toggle') }
  ];

  let isSlashActive = $derived(textInput.startsWith('/'));
  let filteredCommands = $derived(
    isSlashActive 
      ? commands.filter(c => c.cmd.toLowerCase().includes(textInput.toLowerCase())) 
      : []
  );
  let showSlashMenu = $derived(isSlashActive && filteredCommands.length > 0);

  async function adjustHeight() {
    await tick();
    if (textareaEl) {
      textareaEl.style.height = 'auto';
      textareaEl.style.height = Math.min(textareaEl.scrollHeight, 200) + 'px';
    }
  }

  function triggerSubmit() {
    if (textInput.trim()) {
      if (onsend) onsend(textInput.trim());
      textInput = '';
      adjustHeight();
    }
  }

  function executeSlashCommand(command: SlashCommand) {
    if (command.cmd === '/clear') {
      textInput = '';
    } else {
      textInput = command.cmd + ' ';
    }
    showPlusMenu = false;
    selectedCommandIndex = 0;
    adjustHeight();
    textareaEl?.focus();
  }

  function handlePlusAction(actionName: string) {
    console.log(`Action: ${actionName}`);
    showPlusMenu = false;
  }

  function handleKeyDown(event: KeyboardEvent) {
    if (showSlashMenu) {
      if (event.key === 'ArrowDown') {
        event.preventDefault();
        selectedCommandIndex = (selectedCommandIndex + 1) % filteredCommands.length;
        return;
      }
      if (event.key === 'ArrowUp') {
        event.preventDefault();
        selectedCommandIndex = (selectedCommandIndex - 1 + filteredCommands.length) % filteredCommands.length;
        return;
      }
      if (event.key === 'Enter') {
        event.preventDefault();
        executeSlashCommand(filteredCommands[selectedCommandIndex]);
        return;
      }
      if (event.key === 'Escape') {
        event.preventDefault();
        textInput = '';
        return;
      }
    }

    if (event.key === 'Enter' && !event.shiftKey) {
      event.preventDefault();
      triggerSubmit();
    }
  }

  function handleWindowClick(event: MouseEvent) {
    if (containerEl && !containerEl.contains(event.target as Node)) {
      showPlusMenu = false;
    }
  }
</script>

<svelte:window onclick={handleWindowClick} />

<div class="chat-input-bar-sub-anchor">
  <div class="chat-input-container" bind:this={containerEl}>
    
    <!-- ================= ⚪ ชั้นลอยคำถามกระจกแก้วใส โหมดสว่างสไตล์ DeepSeek ================= -->
    {#if activeQuestion}
      <div class="input-attached-question-banner">
        <div class="q-badge-row">
          <span class="q-spark">✨</span>
          <span class="q-label-text">คำถามถึงคุณ (AI กำลังรอคำตอบ)</span>
        </div>
        <p class="q-actual-content">{activeQuestion}</p>
      </div>
    {/if}

    <!-- ================= FLOATING MENUS ================= -->
    {#if showSlashMenu}
      <div class="floating-menu slash-menu" role="listbox" aria-label="Slash Commands">
        {#each filteredCommands as cmd, index}
          <button
            class="menu-item"
            class:active={index === selectedCommandIndex}
            onclick={() => executeSlashCommand(cmd)}
            onmouseenter={() => selectedCommandIndex = index}
            onfocus={() => selectedCommandIndex = index}
            role="option"
            aria-selected={index === selectedCommandIndex}
          >
            <span class="menu-icon">{cmd.icon}</span>
            <div class="menu-text-group">
              <span class="menu-cmd-title">{cmd.cmd}</span>
              <span class="menu-cmd-desc">{cmd.desc}</span>
            </div>
          </button>
        {/each}
      </div>
    {/if}

    {#if showPlusMenu}
      <div class="floating-menu plus-menu" role="menu" aria-label="Additional Actions">
        {#each plusActions as action}
          <button class="menu-item" onclick={action.action} role="menuitem">
            <span class="menu-icon">{action.icon}</span>
            <span class="menu-action-label">{action.label}</span>
          </button>
        {/each}
      </div>
    {/if}

    <!-- ================= CHAT INPUT BAR CORE (WHITE CANVAS) ================= -->
    <div class="input-bar-core" class:has-question-above={!!activeQuestion}>
      <button 
        type="button" 
        class="action-circle-btn" 
        class:rotated={showPlusMenu}
        onclick={() => showPlusMenu = !showPlusMenu}
        aria-label="Open attachment menu"
        aria-expanded={showPlusMenu}
      >
        <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><line x1="12" y1="5" x2="12" y2="19"></line><line x1="5" y1="12" x2="19" y2="12"></line></svg>
      </button>

      <textarea
        bind:this={textareaEl}
        bind:value={textInput}
        oninput={adjustHeight}
        onkeydown={handleKeyDown}
        placeholder={activeQuestion ? "ส่งข้อความถึง DeepSeek..." : "ส่งข้อความถึง DeepSeek..."}
        rows="1"
        spellcheck="false"
        aria-label="Chat input prompt"
      ></textarea>

      <button 
        type="button" 
        class="quantum-send-style" 
        disabled={!textInput.trim()}
        onclick={triggerSubmit}
        aria-label="Send message"
      >
        <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><line x1="22" y1="2" x2="11" y2="13"></line><polygon points="22 2 15 22 11 13 2 9 22 2"></polygon></svg>
      </button>
    </div>
  </div>
</div>

<style>
  .chat-input-bar-sub-anchor {
    width: 100%;
    display: flex;
    justify-content: center;
    padding: 12px 0;
    pointer-events: auto;
  }

  .chat-input-container {
    width: 100%;
    max-width: 760px;
    position: relative;
    display: flex;
    flex-direction: column;
  }

  /* ⚪ ปรับแผงกระจกฝ้าด้านบนให้เป็นสีขาวสว่างใสแบบกระจกเงาหน้าต่างโปร่งแสง */
  .input-attached-question-banner {
    background: rgba(244, 244, 247, 0.85); 
    backdrop-filter: blur(12px); 
    -webkit-backdrop-filter: blur(12px);
    border: 1px solid #e5e5e9;
    border-bottom: none; 
    border-top-left-radius: 16px;
    border-top-right-radius: 16px;
    padding: 14px 16px 10px 16px;
    box-shadow: 0 -4px 12px rgba(0, 0, 0, 0.02);
    animation: slideUp 0.22s cubic-bezier(0.4, 0, 0.2, 1);
  }

  @keyframes slideUp {
    from { transform: translateY(6px); opacity: 0; }
    to { transform: translateY(0); opacity: 1; }
  }

  .q-badge-row {
    display: flex;
    align-items: center;
    gap: 6px;
    margin-bottom: 4px;
  }

  .q-spark { font-size: 12px; color: #4d6bfe; }
  .q-label-text {
    font-size: 11px;
    font-weight: 700;
    color: #4d6bfe; 
    letter-spacing: 0.02em;
  }

  .q-actual-content {
    margin: 0;
    font-size: 14px;
    line-height: 1.5;
    color: #1d1d1f;
  }

  /* ⚪ ตัวกล่องอินพุตบาร์หลักสีขาวนวลสะอาด ขอบโค้งมนหรูหรา */
  .input-bar-core {
    display: flex;
    align-items: flex-end;
    background-color: #ffffff;
    border: 1px solid #e5e5e9;
    border-radius: 16px;
    padding: 12px 16px;
    gap: 12px;
    box-shadow: 0 4px 16px rgba(0, 0, 0, 0.04);
    transition: border-color 0.2s ease, box-shadow 0.2s ease;
  }

  .input-bar-core.has-question-above {
    border-top-left-radius: 0px;
    border-top-right-radius: 0px;
    border-top-color: #f0f0f4;
  }

  .input-bar-core:focus-within {
    border-color: #4d6bfe;
    box-shadow: 0 4px 20px rgba(77, 107, 254, 0.08);
  }

  .action-circle-btn {
    width: 32px;
    height: 32px;
    border-radius: 50%;
    background-color: #f4f4f7;
    border: none;
    color: #66666d;
    display: flex;
    align-items: center;
    justify-content: center;
    cursor: pointer;
    transition: all 0.2s;
    flex-shrink: 0;
    margin-bottom: 2px;
  }

  .action-circle-btn:hover {
    background-color: #e5e5e9;
    color: #1d1d1f;
  }

  .action-circle-btn.rotated {
    transform: rotate(45deg);
    background-color: #ffeef0;
    color: #ff4d4f;
  }

  textarea {
    flex: 1;
    background: transparent;
    border: none !important;
    outline: none !important;
    box-shadow: none !important;
    resize: none;
    color: #1d1d1f;
    font-size: 15px;
    line-height: 22px;
    padding: 5px 0;
    margin: 0;
    max-height: 200px;
  }

  textarea::placeholder { color: #a1a1a7; }

  /* ปุ่มส่งสีฟ้า DeepSeek Blue แท้ 100% */
  .quantum-send-style {
    width: 32px;
    height: 32px;
    border-radius: 50%;
    background-color: #4d6bfe;
    color: #ffffff;
    border: none;
    display: flex;
    align-items: center;
    justify-content: center;
    cursor: pointer;
    transition: all 0.2s ease;
    flex-shrink: 0;
    margin-bottom: 2px;
  }

  .quantum-send-style:hover:not(:disabled) { background-color: #2b56ff; transform: scale(1.02); }
  .quantum-send-style:active:not(:disabled) { transform: scale(0.98); }
  .quantum-send-style:disabled { background: #f4f4f7; color: #ccd0d7; cursor: not-allowed; }

  .floating-menu {
    position: absolute;
    bottom: calc(100% + 8px);
    background-color: #ffffff;
    border: 1px solid #e5e5e9;
    border-radius: 12px;
    box-shadow: 0 6px 24px rgba(0, 0, 0, 0.08);
    overflow: hidden;
    padding: 6px;
    display: flex;
    flex-direction: column;
    gap: 2px;
    z-index: 60;
  }

  .slash-menu { left: 0; width: 100%; }
  .plus-menu { left: 0; width: 240px; }

  .menu-item {
    display: flex;
    align-items: center;
    width: 100%;
    padding: 8px 12px;
    background: transparent;
    border: none;
    border-radius: 8px;
    text-align: left;
    cursor: pointer;
    color: #1d1d1f;
    gap: 10px;
  }

  .menu-item.active, .menu-item:hover { background-color: #f4f4f7; }
  .menu-icon { font-size: 16px; display: flex; align-items: center; justify-content: center; width: 20px; }
  .menu-text-group { display: flex; flex-direction: column; }
  .menu-cmd-title { font-size: 14px; font-weight: 600; color: #4d6bfe; }
  .menu-cmd-desc { font-size: 12px; color: #66666d; }
  .menu-action-label { font-size: 14px; }
</style>