<script lang="ts">
  import { tick } from 'svelte';
  import { marked } from 'marked';
  import DOMPurify from 'dompurify';
  import ChatInputBar from '$lib/components/ChatInputBar.svelte';

  interface Message {
    id: string;
    role: 'user' | 'assistant';
    content: string;
    timestamp: string;
  }

  let { data } = $props();
  let messages = $state<Message[]>([]);
  let chatViewportEl = $state<HTMLDivElement | null>(null);
  let currentAiQuestion = $state(''); 
  let isCopied = $state(false);
  let isAiGenerating = $state(false);
  let conversationSummary = $state('');
  let isSummarizing = $state(false);

  // 🟢 1. เปลี่ยนมาใช้สเตตัสบูลีนเพียวๆ ในการควบคุมการเปิด/ปิด สารบัญขวา
  let isScrollableActive = $state(false);

  // 🟢 2. สร้างฟังก์ชันคำนวณตรวจสอบความสูงจาก Element ตรงๆ ปลอดภัยจาก TypeScript
  function updateScrollState() {
    if (chatViewportEl) {
      isScrollableActive = chatViewportEl.scrollHeight > chatViewportEl.clientHeight;
    }
  }

  // จุดคำนวณชื่อแสดงผลห้องทำงานตามคำถามแรกของผู้ใช้
  let chatDisplayName = $derived(() => {
    const firstUserMsg = messages.find(msg => msg.role === 'user');
    if (firstUserMsg && firstUserMsg.content.trim()) {
      const cleanText = firstUserMsg.content.trim();
      return cleanText.length > 40 ? cleanText.slice(0, 40) + '...' : cleanText;
    }
    return `Cosmic Master Node: [${data.chatId.slice(0, 8)}]`;
  });

  let rightNavItems = $derived(
    messages.filter(msg => msg.role === 'user')
  );

  let totalCombinedAiText = $derived(
    messages
      .filter(msg => msg.role === 'assistant')
      .map(msg => msg.content)
      .join('\n\n')
  );

  $effect(() => {
    const currentId = data.chatId;
    loadChatHistoryOfRoom(currentId);
  });

  async function loadChatHistoryOfRoom(id: string) {
    currentAiQuestion = '';
    messages = [
      {
        id: 'init-core',
        role: 'assistant',
        content: `# 🌌 แฟ้มข้อมูลระนาบสัญกรณ์ 8zenith\n\nเปิดพื้นที่การประมวลผลสำหรับ Node: **[${id.slice(0, 8)}]** เรียบร้อยแล้ว ป้อนชุดคำสั่งที่ด้านล่างเพื่อเริ่มระดมสมองคำนวณวงจรธาตุ\n\n---`,
        timestamp: '14:04'
      }
    ];
    await tick();
    if (chatViewportEl) {
      chatViewportEl.scrollTop = 0;
      updateScrollState(); // ซิงค์สถานะความสูงเริ่มต้น
    }
  }

  function renderMarkdown(rawText: string): string {
    if (!rawText) return '';
    try {
      return DOMPurify.sanitize(marked.parse(rawText) as string);
    } catch {
      return rawText;
    }
  }

  function jumpToCommandAnchor(msgId: string) {
    const element = document.getElementById(`ai-block-${msgId}`);
    if (element) {
      element.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
  }

  async function copyMasterDocumentToClipboard() {
    if (!totalCombinedAiText || isCopied) return;
    try {
      await navigator.clipboard.writeText(totalCombinedAiText);
      isCopied = true;
      setTimeout(() => { isCopied = false; }, 2000);
    } catch (err) {
      console.error('Failed to copy document context:', err);
    }
  }

  async function executeStreamingPipeline(payload: object) {
    isAiGenerating = true;
    const aiMessageId = crypto.randomUUID();
    
    messages = [...messages, { id: aiMessageId, role: 'assistant', content: '', timestamp: '' }];
    await tick();

    try {
      const response = await fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });

      if (!response.ok) throw new Error('Failed to fetch stream pipeline');

      const reader = response.body?.getReader();
      const decoder = new TextDecoder();
      if (!reader) return;

      let accumulativeText = '';

      while (true) {
        const { value, done } = await reader.read();
        if (done) break;

        accumulativeText += decoder.decode(value, { stream: true });

        const questionStartIndex = accumulativeText.indexOf('<question>');
        
        if (questionStartIndex !== -1) {
            const mainContent = accumulativeText.slice(0, questionStartIndex);
            updateAiMessageContent(aiMessageId, mainContent);

            const rawQuestionContent = accumulativeText.slice(questionStartIndex + 10);
            const questionEndIndex = rawQuestionContent.indexOf('</question>');

            if (questionEndIndex !== -1) {
                currentAiQuestion = rawQuestionContent.slice(0, questionEndIndex);
            } else {
                currentAiQuestion = rawQuestionContent;
            }
        } else {
            updateAiMessageContent(aiMessageId, accumulativeText);
        }

        await tick();
        if (chatViewportEl) {
          chatViewportEl.scrollTop = chatViewportEl.scrollHeight;
          updateScrollState(); // 🟢 ตรวจสอบและอัปเดตสเตตัส Scrollbar ระหว่างที่ข้อความกำลังสตรีมไหลออกจอ
        }
      }
    } catch (error) {
      console.error('Streaming connection broke:', error);
    } finally {
      isAiGenerating = false;
    }
  }

  function updateAiMessageContent(id: string, text: string) {
    messages = messages.map(msg => {
      if (msg.id === id) {
        return { ...msg, content: text };
      }
      return msg;
    });
  }

  async function handleNewIncomingMessage(text: string) {
    const timeString = new Date().toLocaleTimeString('th-TH', { hour: '2-digit', minute: '2-digit' });
    currentAiQuestion = ''; 

    messages = [
      ...messages,
      { id: crypto.randomUUID(), role: 'user', content: text, timestamp: timeString }
    ];
    await tick();
    updateScrollState(); // ตรวจสอบความสูงหลังผู้ใช้ดันคำถามใหม่เข้าสู่ระบบ

    // Trim history: keep system msg + last 20 exchanges (40 messages max)
    const MAX_KEEP = 40;
    const trimmed = messages.length > MAX_KEEP
      ? [messages[0], ...messages.slice(-(MAX_KEEP - 1))]
      : messages;
    // Inject astrology context from localStorage if available
    let astroContext = '';
    try { const raw = localStorage.getItem('astrology_chart'); if (raw) {
      const d = JSON.parse(raw);
      astroContext = `\n📅 ${d.birthDate} ${d.birthTime} ${d.birthPlace}\n`;
      if (d.bazi) astroContext += `🀄 DayMaster:${d.bazi.dayMaster} Pillars:${d.bazi.pillars.map((p:any)=>p.stem+p.branch+`(${p.element})`).join(' ')}\n`;
      if (d.western) astroContext += `🌍 Sun:${d.western.sunSign} Moon:${d.western.moonSign} Rising:${d.western.risingSign}\n`;
      if (d.humandesign) astroContext += `🔷 HD:${d.humandesign.type}\n`;
    }} catch {}
    const contextMsg = astroContext ? [{ role: 'system', content: `ข้อมูลดวงที่คำนวณจาก Swiss Ephemeris (ใช้ตอบเฉพาะคำถามเกี่ยวกับดวงชะตาเท่านั้น):${astroContext}` }] : [];
    await executeStreamingPipeline({ messages: [...contextMsg, ...trimmed.map(m => ({ role: m.role, content: m.content }))] });
  }
</script>

<div class="deepseek-style-workspace">
  
  <div class="room-top-banner">
    <div class="indicator-glow"></div>
    <span class="banner-title"><span class="dynamic-title-text">{chatDisplayName()}</span></span>
    
    <button 
      type="button" 
      class="master-copy-action-btn" 
      disabled={messages.length <= 1 || isAiGenerating}
      onclick={copyMasterDocumentToClipboard}
    >
      {#if isCopied} ✓ คัดลอกแล้ว! {:else} 📋 คัดลอกเอกสารทั้งหมด {/if}
    </button>
  </div>

  <div class="core-studio-layout">
    
    <div 
      class="chat-viewport-column" 
      bind:this={chatViewportEl}
    >
      <div class="cosmic-single-sheet-paper">
        {#each messages as msg (msg.id)}
          {#if msg.role === 'assistant'}
            <div id="ai-block-{msg.id}" class="document-pure-paragraph-block animate-fade">
              {@html renderMarkdown(msg.content)}
            </div>
          {/if}
        {/each}
      </div>
    </div>

    <div class="deepseek-floating-nav-sidebar" class:is-overflow-active={isScrollableActive}>
      
      <div class="nav-ghost-guide-line">
        <span class="guide-bullet">❯</span>
      </div>

      <div class="nav-sticky-container">
        <div class="sidebar-header-tag">COMMAND CONTEXT</div>
        {#if rightNavItems.length === 0}
          <div class="empty-nav-state">รอป้อนชุดคำสั่ง...</div>
        {:else}
          <div class="nav-buttons-vertical-stack">
            {#each rightNavItems as item, idx (item.id)}
              <button 
                type="button" 
                class="deepseek-nav-item-btn"
                onclick={() => {
                  const cmdIdx = messages.findIndex(m => m.id === item.id);
                  if (messages[cmdIdx + 1]) {
                    jumpToCommandAnchor(messages[cmdIdx + 1].id);
                  }
                }}
                title={item.content}
              >
                <span class="nav-number-indicator">❯</span>
                <span class="nav-truncate-textfilename">{item.content}</span>
              </button>
            {/each}
          </div>
        {/if}
      </div>

    </div>
  </div>

  <div class="footer-input-anchor">
    <ChatInputBar onsend={handleNewIncomingMessage} activeQuestion={currentAiQuestion} />
  </div>
</div>

<style>
  .deepseek-style-workspace {
    display: flex;
    flex-direction: column;
    height: 100%;
    position: relative;
    box-sizing: border-box;
    background-color: #ffffff;
  }

  .room-top-banner {
    display: flex;
    align-items: center;
    padding: 10px 16px;
    background-color: #f4f4f7;
    border: 1px solid #e5e5e9;
    border-radius: 10px;
    margin-bottom: 0.75rem;
    flex-shrink: 0;
    gap: 10px;
  }

  .indicator-glow { width: 8px; height: 8px; background-color: #22c55e; border-radius: 50%; box-shadow: 0 0 6px #22c55e; }
  .banner-title { font-size: 13px; color: #66666d; flex: 1; display: flex; align-items: center; overflow: hidden; }
  
  .dynamic-title-text { 
    font-weight: 600; 
    color: #1d1d1f; 
    white-space: nowrap; 
    overflow: hidden; 
    text-overflow: ellipsis; 
  }

  .master-copy-action-btn {
    background-color: #ffffff;
    border: 1px solid #e5e5e9;
    color: #1d1d1f;
    font-size: 12px;
    padding: 5px 12px;
    border-radius: 6px;
    cursor: pointer;
    font-weight: 600;
    transition: all 0.2s ease;
    flex-shrink: 0;
  }
  .master-copy-action-btn:hover:not(:disabled) { border-color: #4d6bfe; background-color: rgba(77, 107, 254, 0.05); color: #4d6bfe; }
  .master-copy-action-btn:disabled { opacity: 0.3; cursor: not-allowed; }

  .core-studio-layout {
    flex: 1;
    display: grid;
    grid-template-columns: 1fr 200px;
    gap: 20px;
    overflow: hidden;
    padding-bottom: 95px;
  }

  @media (max-width: 1024px) {
    .core-studio-layout { grid-template-columns: 1fr; }
    .deepseek-floating-nav-sidebar { display: none; }
  }

  .chat-viewport-column {
    flex: 1;
    overflow-y: auto;
    padding-right: 4px;
  }

  .cosmic-single-sheet-paper {
    max-width: 740px;
    margin: 0 auto;
    background: #ffffff;
    padding: 10px 20px;
    min-height: 100%;
    display: flex;
    flex-direction: column;
    gap: 16px;
    box-sizing: border-box;
  }

  .document-pure-paragraph-block {
    font-size: 15.5px;
    line-height: 1.65;
    color: #1d1d1f;
  }

  .deepseek-floating-nav-sidebar {
    position: relative;
    height: 100%;
    cursor: pointer;
    display: none; 
    opacity: 0;
    visibility: hidden;
    transition: opacity 0.2s ease;
  }

  .deepseek-floating-nav-sidebar.is-overflow-active {
    display: block;
    opacity: 1;
    visibility: visible;
  }

  .nav-ghost-guide-line {
    position: absolute;
    left: 10px;
    top: 14px;
    display: flex;
    align-items: center;
    justify-content: center;
    width: 24px;
    height: 24px;
    border-radius: 6px;
    background-color: #f4f4f7;
    border: 1px solid #e5e5e9;
    color: #a1a1a7;
    font-size: 11px;
    transition: opacity 0.2s ease, transform 0.2s ease;
    opacity: 0.4;
    z-index: 5;
  }

  .nav-sticky-container {
    position: sticky;
    top: 0;
    display: flex;
    flex-direction: column;
    background: #f4f4f7;
    border: 1px solid #e5e5e9;
    border-radius: 12px;
    padding: 14px 12px;
    max-height: 85%;
    overflow-y: auto;
    box-shadow: 0 4px 12px rgba(0,0,0,0.02);
    opacity: 0;
    visibility: hidden;
    transform: translateX(10px); 
    transition: opacity 0.22s cubic-bezier(0.4, 0, 0.2, 1),
                transform 0.22s cubic-bezier(0.4, 0, 0.2, 1),
                visibility 0.22s;
    z-index: 10;
  }

  .deepseek-floating-nav-sidebar.is-overflow-active:hover .nav-sticky-container {
    opacity: 1;
    visibility: visible;
    transform: translateX(0);
  }

  .deepseek-floating-nav-sidebar.is-overflow-active:hover .nav-ghost-guide-line {
    opacity: 0;
    transform: scale(0.8);
  }

  .sidebar-header-tag {
    font-size: 10px;
    font-weight: 700;
    color: #88888d;
    letter-spacing: 0.04em;
    margin-bottom: 10px;
    padding-left: 4px;
  }

  .empty-nav-state { font-size: 11.5px; color: #a1a1a7; font-style: italic; padding-left: 4px; }
  .nav-buttons-vertical-stack { display: flex; flex-direction: column; gap: 4px; }

  .deepseek-nav-item-btn {
    display: flex;
    align-items: center;
    gap: 8px;
    background: transparent;
    border: none;
    text-align: left;
    padding: 8px 10px;
    border-radius: 6px;
    cursor: pointer;
    color: #66666d;
    transition: all 0.15s ease;
    width: 100%;
    overflow: hidden;
  }

  .deepseek-nav-item-btn:hover {
    background-color: #eaeaea;
    color: #4d6bfe;
  }

  .nav-number-indicator { font-size: 11px; font-weight: 700; color: #4d6bfe; }
  .nav-truncate-textfilename { font-size: 13px; overflow: hidden; white-space: nowrap; text-overflow: ellipsis; flex: 1; }
  .footer-input-anchor { position: absolute; bottom: 0; left: 0; right: 0; pointer-events: none; }

  :global(.document-pure-paragraph-block h1) { font-size: 1.75rem; margin: 0 0 1rem 0; color: #1d1d1f; font-weight: 700; border-bottom: 1px solid #e5e5e9; padding-bottom: 8px; }
  :global(.document-pure-paragraph-block h2) { font-size: 1.45rem; margin: 1.5rem 0 0.75rem 0; color: #1d1d1f; font-weight: 700; }
  :global(.document-pure-paragraph-block h3) { color: #4d6bfe; font-size: 1.2rem; margin: 1.25rem 0 0.5rem 0; font-weight: 700; }
  :global(.document-pure-paragraph-block p) { margin: 0 0 12px 0; color: #1d1d1f; }
  :global(.document-pure-paragraph-block strong) { color: #1d1d1f; font-weight: 700; background-color: rgba(77, 107, 254, 0.04); padding: 1px 4px; border-radius: 4px; }
  :global(.document-pure-paragraph-block hr) { border: none; height: 1px; background: #e5e5e9; margin: 1.5rem 0; }
  :global(.document-pure-paragraph-block ul, .document-pure-paragraph-block ol) { padding-left: 20px; margin: 0 0 12px 0; }
  :global(.document-pure-paragraph-block li) { margin-bottom: 6px; color: #1d1d1f; }
  :global(.document-pure-paragraph-block table) { width: 100%; border-collapse: collapse; margin: 16px 0; font-size: 14px; }
  :global(.document-pure-paragraph-block th) { background-color: #f4f4f7; color: #1d1d1f; font-weight: 600; text-align: left; padding: 8px 12px; border: 1px solid #e5e5e9; }
  :global(.document-pure-paragraph-block td) { padding: 8px 12px; border: 1px solid #e5e5e9; color: #1d1d1f; }

  .animate-fade { animation: fade 0.22s ease-out; }
  @keyframes fade { from { opacity: 0; transform: translateY(2px); } to { opacity: 1; transform: translateY(0); } }
</style>