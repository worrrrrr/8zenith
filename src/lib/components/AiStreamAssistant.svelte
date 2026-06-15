<script lang="ts">
  // นำเข้า tick จากแพ็กเกจหลักของ svelte อย่างถูกต้อง
  import { tick } from 'svelte';

  // ประกาศ State สำหรับเก็บรายการข้อความ
  let messages = $state<string[]>([
    'สวัสดีครับ ยินดีต้อนรับเข้าสู่ระบบรันไทม์',
    'ลองกดปุ่มเพิ่มข้อความด้านล่าง เพื่อดูการทำงานของระบบควบคุมคิวงาน (Tick Engine)'
  ]);

  // ตัวแปรเก็บ Element Reference ของกล่องข้อความ
  let chatContainer = $state<HTMLDivElement | null>(null);
  
  // ตัวแปรเก็บค่าความสูงที่วัดได้เพื่อนำมาแสดงผลบนหน้าจอให้เห็นภาพ
  let measuredHeightBefore = $state(0);
  let measuredHeightAfter = $state(0);

  async function addNewMessage() {
    // 1. ทำการอัปเดตสเตท เพิ่มข้อความใหม่เข้าไปในระบบ
    messages = [...messages, `ข้อความใหม่ลำดับที่ ${messages.length + 1} ถูกเพิ่มเข้ามาในระบบแล้ว`];

    // 🔴 ทดสอบจังหวะที่ 1: วัดค่าความสูงทันทีก่อนหน้าจอจะอัปเดต
    if (chatContainer) {
      measuredHeightBefore = chatContainer.scrollHeight;
    }

    /**
     * 🟢 จังหวะสำคัญ: เรียกใช้งาน tick() พร้อมโครงสร้าง await
     * บรรทัดนี้จะหยุดการทำงานของฟังก์ชันนี้ไว้ชั่วคราว เพื่อปล่อยให้ Svelte นำค่าสเตทใหม่
     * ไปเรนเดอร์ลงบนหน้าจอ HTML จริงๆ ในคิว Microtask ให้เสร็จสิ้นก่อน
     */
    await tick();

    // 🔵 ทดสอบจังหวะที่ 2: วัดค่าความสูงหลังจากผ่านกระบวนการ tick เรียบร้อยแล้ว
    if (chatContainer) {
      measuredHeightAfter = chatContainer.scrollHeight;
      
      // เมื่อมั่นใจว่า DOM อัปเดตสมบูรณ์แล้ว จึงทำการเลื่อน Scrollbar ลงไปล่างสุดอย่างแม่นยำ
      chatContainer.scrollTop = chatContainer.scrollHeight;
    }
  }
</script>

<div class="demo-box">
  <div class="chat-viewport" bind:this={chatContainer}>
    {#each messages as msg}
      <div class="msg-item">{msg}</div>
    {/each}
  </div>

  <div class="telemetry-panel">
    <div class="metric">
      <span class="label">ความสูงก่อนใช้ tick:</span>
      <span class="value val-red">{measuredHeightBefore} px</span>
    </div>
    <div class="metric">
      <span class="label">ความสูงหลังใช้ tick (ค่าจริง):</span>
      <span class="value val-green">{measuredHeightAfter} px</span>
    </div>
  </div>

  <button onclick={addNewMessage} class="btn-trigger">
    เพิ่มข้อความและเลื่อนหน้าจออัตโนมัติ
  </button>
</div>

<style>
  .demo-box {
    background-color: #1e293b;
    border-radius: 12px;
    padding: 20px;
    max-width: 550px;
    width: 100%;
    box-sizing: border-box;
    font-family: system-ui, -apple-system, sans-serif;
    color: #f8fafc;
    box-shadow: 0 20px 25px -5px rgb(0 0 0 / 0.1);
  }

  .chat-viewport {
    height: 180px;
    background-color: #0f172a;
    border: 1px solid #334155;
    border-radius: 8px;
    padding: 12px;
    overflow-y: auto;
    display: flex;
    flex-direction: column;
    gap: 8px;
  }

  .msg-item {
    background-color: #1e293b;
    border: 1px solid #475569;
    padding: 8px 12px;
    border-radius: 6px;
    font-size: 14px;
    line-height: 1.5;
  }

  .telemetry-panel {
    background-color: #0f172a;
    margin: 16px 0;
    padding: 12px;
    border-radius: 8px;
    display: flex;
    flex-direction: column;
    gap: 6px;
    border: 1px dashed #334155;
  }

  .metric {
    display: flex;
    justify-content: space-between;
    font-size: 13px;
  }

  .metric .label {
    color: #94a3b8;
  }

  .metric .value {
    font-family: monospace;
    font-weight: bold;
  }

  .val-red { color: #f87171; }
  .val-green { color: #4ade80; }

  .btn-trigger {
    width: 100%;
    padding: 12px;
    background-color: #2563eb;
    color: white;
    border: none;
    border-radius: 6px;
    font-weight: 600;
    cursor: pointer;
    transition: background-color 0.2s;
  }

  .btn-trigger:hover {
    background-color: #1d4ed8;
  }
</style>