<script lang="ts">
  import { tick } from 'svelte';
  import { marked } from 'marked';
  import DOMPurify from 'dompurify';

  // 🟢 กำหนดรูปแบบ Interface บังคับเปิดรับ chatId เป็น string
  interface AgentWorkspaceProps {
    chatId: string;
  }

  // 🟢 บรรทัดนี้ห้ามพลาด: ต้องมีปีกกา { chatId } ครอบ เพื่อแตกค่าออกมารับเป็นราย Prop
  let { chatId }: AgentWorkspaceProps = $props();

  interface ChatMessage {
    id: string;
    role: 'user' | 'assistant';
    content: string;
    isQuestion?: boolean;
  }

  let chatInput = $state('');
  let isAgentActive = $state(false);
  let chatMessages = $state<ChatMessage[]>([]);
  let artifactContent = $state('');
  
  let chatScrollEl = $state<HTMLDivElement | null>(null);
  let artifactScrollEl = $state<HTMLDivElement | null>(null);

  $effect(() => {
    const currentId = chatId;
    initializeAgentRoom(currentId);
  });

  async function initializeAgentRoom(id: string) {
    chatMessages = [
      { id: 'init', role: 'assistant', content: `ระบบเปิดการเชื่อมต่อ Cosmic Agent ในห้อง: [${id.slice(0, 8)}] สำเร็จ ป้อนคำสั่งเพื่อเริ่มสร้างเนื้อหาฝั่งขวาได้เลยครับ` }
    ];
    artifactContent = `# 🌌 8zenith Workspace [${id.slice(0, 8)}]\n\n--- \n\n## 🔮 รายงานระนาบสัญกรณ์\n- รอคำสั่งบรีฟงานจากฝั่ง Agent Console ซ้ายมือ...\n`;
    
    await tick();
    if (chatScrollEl) chatScrollEl.scrollTop = 0;
    if (artifactScrollEl) artifactScrollEl.scrollTop = 0;
  }

  let renderedArtifactHtml = $derived.by(() => {
    if (!artifactContent) return '<p>เอกสารว่างเปล่า</p>';
    try {
      return DOMPurify.sanitize(marked.parse(artifactContent) as string);
    } catch {
      return artifactContent;
    }
  });

  async function scrollElements() {
    await tick();
    if (chatScrollEl) chatScrollEl.scrollTop = chatScrollEl.scrollHeight;
    if (artifactScrollEl) artifactScrollEl.scrollTop = artifactScrollEl.scrollHeight;
  }

  async function simulateAgentStreaming(rawAiResponse: string) {
    const chatMessageId = crypto.randomUUID();
    chatMessages = [...chatMessages, { id: chatMessageId, role: 'assistant', content: '' }];
    
    let currentIndex = 0;
    let isInArtifactMode = false;
    
    while (currentIndex < rawAiResponse.length) {
      await new Promise(r => setTimeout(r, 20));
      
      const nextChunkSize = Math.min(12, rawAiResponse.length - currentIndex);
      const chunk = rawAiResponse.slice(currentIndex, currentIndex + nextChunkSize);
      currentIndex += nextChunkSize;

      if (chunk.includes('<cosmic_artifact>')) {
        isInArtifactMode = true;
        continue;
      }

      if (chunk.includes('</cosmic_artifact>')) {
        isInArtifactMode = false;
        continue;
      }

      if (isInArtifactMode) {
        artifactContent += chunk;
      } else {
        chatMessages = chatMessages.map(msg => {
          if (msg.id === chatMessageId) {
            return { ...msg, content: msg.content + chunk };
          }
          return msg;
        });
      }
      await scrollElements();
    }
  }

  async function handleSendCommand(event: Event) {
    event.preventDefault();
    if (!chatInput.trim() || isAgentActive) return;

    const userPrompt = chatInput.trim();
    chatInput = '';
    isAgentActive = true;

    chatMessages = [...chatMessages, { id: crypto.randomUUID(), role: 'user', content: userPrompt }];
    await scrollElements();

    const mockPayload = `รับทราบคำสั่งครับ กำลังแปลงหัวข้อ "${userPrompt}" ไปจัดระเบียบโครงสร้างข้อมูล <cosmic_artifact>\n\n### 🪐 ผลการวิเคราะห์ข้อมูล: ${userPrompt}\n- **ข่ายพลังงาน:** จัดการข้อมูลเสร็จสิ้นผ่านห้อง ID [${chatId.slice(0, 8)}]\n- **สถานะระบบ:** ทำงานร่วมกับ Svelte 5 Runes สมบูรณ์แบบ\n\n> สัญกรณ์ก้อนนี้ถูกสกัดแยกหมวดหมู่ออกมาเรนเดอร์ฝั่งบอร์ดทำงานเด็ดขาด</cosmic_artifact>\n\nเรียบร้อยครับ! ผมอัปเดตไฟล์ชิ้นงานฝั่งขวาเสร็จสิ้นแล้ว ลองตรวจสอบความถูกต้องได้เลยครับ`;

    await simulateAgentStreaming(mockPayload);
    isAgentActive = false;
  }
</script>

<div class="agent-workspace-studio">
  <div class="studio-sidebar chat-console-pane">
    <div class="pane-title-bar">
      <div class="indicator-pulse" class:working={isAgentActive}></div>
      <span class="title-text-mono">COSMIC AGENT CONSOLE</span>
    </div>

    <div class="chat-flow-area" bind:this={chatScrollEl}>
      {#each chatMessages as msg (msg.id)}
        <div class="chat-bubble-card {msg.role}">
          <div class="sender-tag">{msg.role === 'user' ? 'YOU' : 'AGENT'}</div>
          <p>{msg.content}</p>
        </div>
      {/each}
    </div>

    <form onsubmit={handleSendCommand} class="console-input-bar">
      <input
        type="text"
        bind:value={chatInput}
        disabled={isAgentActive}
        placeholder={isAgentActive ? "Agent กำลังประมวลผล..." : "ป้อนคำสั่งเพื่อสั่งการ AI Agent..."}
      />
      <button type="submit" disabled={isAgentActive || !chatInput.trim()} class="quantum-btn-send">
        ส่งคำสั่ง
      </button>
    </form>
  </div>

  <div class="studio-main-workspace artifact-pane">
    <div class="pane-title-bar">
      <span class="title-text-mono text-gradient-primary">🎯 TARGET ARTIFACT WORKSPACE</span>
    </div>

    <div class="live-document-render" bind:this={artifactScrollEl}>
      <div class="markdown-output-gate">
        {@html renderedArtifactHtml}
      </div>
    </div>
  </div>
</div>

<style>
  .agent-workspace-studio {
    display: grid;
    grid-template-columns: 380px 1fr;
    gap: 20px;
    height: calc(100vh - 4rem);
    box-sizing: border-box;
    overflow: hidden;
  }

  @media (max-width: 1024px) {
    .agent-workspace-studio { grid-template-columns: 1fr; }
  }

  .pane-title-bar {
    background-color: var(--color-bg-surface);
    border-bottom: 1px solid var(--color-border);
    padding: 12px 16px;
    display: flex;
    align-items: center;
    gap: 10px;
    flex-shrink: 0;
  }

  .title-text-mono {
    font-family: var(--font-mono);
    font-size: 11px;
    font-weight: 800;
    letter-spacing: 0.05em;
    color: var(--color-text-muted);
  }

  .chat-console-pane {
    background-color: var(--color-bg-surface);
    border: 1px solid var(--color-border);
    border-radius: var(--radius-card);
    display: flex;
    flex-direction: column;
    overflow: hidden;
    box-shadow: var(--shadow-card);
  }

  .chat-flow-area {
    flex: 1;
    padding: 16px;
    overflow-y: auto;
    display: flex;
    flex-direction: column;
    gap: 14px;
    background-color: rgba(0, 0, 0, 0.15);
  }

  .chat-bubble-card {
    padding: 10px 12px;
    border-radius: var(--radius-button);
    font-size: 13.5px;
    line-height: 1.5;
    border: 1px solid var(--color-border);
    max-width: 90%;
  }

  .chat-bubble-card.user {
    background-color: var(--color-surface-2);
    align-self: flex-end;
    border-color: var(--color-border-active);
    color: var(--color-text-base);
  }

  .chat-bubble-card.assistant {
    background-color: var(--color-surface-1);
    align-self: flex-start;
    color: var(--color-text-base);
  }

  .sender-tag {
    font-family: var(--font-mono);
    font-size: 10px;
    font-weight: 700;
    color: var(--color-text-muted);
    margin-bottom: 4px;
  }

  .user .sender-tag { color: var(--color-secondary); }
  .assistant .sender-tag { color: var(--color-primary); }

  .chat-bubble-card p { margin: 0; white-space: pre-wrap; }

  .console-input-bar {
    display: flex;
    padding: 12px;
    background-color: var(--color-bg-surface);
    border-top: 1px solid var(--color-border);
    gap: 10px;
    flex-shrink: 0;
  }

  .console-input-bar input {
    flex: 1;
    background-color: var(--color-surface-1);
    border: 1px solid var(--color-border) !important;
    outline: none !important;
    box-shadow: none !important;
    border-radius: 8px;
    padding: 8px 12px;
    color: var(--color-text-base);
    font-size: 13.5px;
  }

  .console-input-bar input:focus {
    border-color: var(--color-border-active) !important;
  }

  .quantum-btn-send {
    padding: 0 14px;
    border-radius: 8px;
    background: linear-gradient(135deg, var(--color-primary), var(--color-secondary));
    color: white;
    border: none;
    font-weight: 600;
    font-size: 13px;
    cursor: pointer;
  }

  .quantum-btn-send:disabled {
    background: var(--color-surface-2);
    color: var(--color-text-muted);
    cursor: not-allowed;
  }

  .artifact-pane {
    background: var(--color-surface-1);
    border: 1px solid var(--color-border);
    border-radius: var(--radius-card);
    display: flex;
    flex-direction: column;
    overflow: hidden;
    box-shadow: var(--shadow-card);
    backdrop-filter: blur(16px);
  }

  .live-document-render {
    flex: 1;
    padding: 24px;
    overflow-y: auto;
    background-color: rgba(0, 0, 0, 0.1);
  }

  .markdown-output-gate {
    font-size: 15px;
    line-height: 1.65;
    color: var(--color-text-base);
  }

  :global(.markdown-output-gate h1) {
    font-size: 1.85rem;
    margin-bottom: 1rem;
    background: linear-gradient(135deg, var(--color-primary), var(--color-secondary));
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
  }
  :global(.markdown-output-gate h2) { color: var(--color-secondary); font-size: 1.35rem; margin-top: 1.75rem; border-bottom: 1px solid var(--color-border); padding-bottom: 6px; }
  :global(.markdown-output-gate p) { margin-bottom: 1rem; }
  :global(.markdown-output-gate strong) { color: var(--color-accent); }
  :global(.markdown-output-gate blockquote) {
    background: rgba(168, 85, 247, 0.05);
    border-left: 4px solid var(--color-primary);
    padding: 10px 14px;
    margin: 1rem 0;
    border-radius: 4px;
  }

  .indicator-pulse {
    width: 7px;
    height: 7px;
    border-radius: 50%;
    background-color: var(--color-text-muted);
  }
  .indicator-pulse.working {
    background-color: var(--color-accent);
    animation: pulse 1.5s infinite;
  }
  @keyframes pulse {
    0% { box-shadow: 0 0 0 0 rgba(245, 158, 11, 0.5); }
    100% { box-shadow: 0 0 0 8px rgba(245, 158, 11, 0); }
  }
</style>