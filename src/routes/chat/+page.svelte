<script lang="ts">
  import { goto } from '$app/navigation';

  function createNewChatSession() {
    // 🟢 สร้างระบบสุ่มรหัส ID ห้องแชท (ในระบบจริงจุดนี้อาจเป็นการยิง API ไปเซฟห้องแชทลงฐานข้อมูลก่อน)
    const newChatId = crypto.randomUUID();
    
    // 🟢 สั่งย้ายหน้าไปหน้าห้องแชทย่อยทันทีแบบเรียลไทม์
    goto(`/chat/${newChatId}`);
  }
</script>

<div class="welcome-container">
  <div class="cosmic-card welcome-card">
    <div class="card-header">
      <span class="chat-icon">💬</span>
      <h2 class="text-gradient-primary">Cosmic Chat</h2>
    </div>
    <hr class="neon-divider" />
    <p class="desc-text">เริ่มต้นปรึกษาปัญญาประดิษฐ์ในบรรยากาศส่วนตัวแบบ Holographic Glassmorphism ระบุระบบผูกดวงชะตาและชุดคำสั่งส่วนตัว</p>
    
    <button onclick={createNewChatSession} class="quantum-btn">
      เริ่มบทสนทนาใหม่
    </button>
  </div>
</div>

<style>
  .welcome-container {
    display: flex;
    justify-content: center;
    align-items: center;
    height: calc(100vh - 4rem);
    box-sizing: border-box;
    padding-bottom: 40px;
  }

  .welcome-card {
    width: 100%;
    max-width: 640px;
    padding: 2.5rem;
    text-align: left;
  }

  .card-header {
    display: flex;
    align-items: center;
    gap: 1rem;
  }

  .chat-icon {
    font-size: 2rem;
  }

  .desc-text {
    color: var(--color-text-muted);
    margin-bottom: 2rem;
    font-size: 1.05rem;
    line-height: 1.6;
  }
</style>