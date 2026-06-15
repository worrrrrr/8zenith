<script lang="ts">
  import { addUserProblem, type PlayerState } from '$lib/utils/mathProblems';

  type Props = {
    playerState: PlayerState;
    onadded: () => void;
  };

  let { playerState, onadded }: Props = $props();

  let level = $state(playerState.currentFloor);
  let question = $state('');
  let answer = $state('');
  let solution = $state('');
  let errorMsg = $state('');
  let success = $state(false);

  function submit() {
    errorMsg = '';
    success = false;

    if (!question.trim()) {
      errorMsg = 'ใส่โจทย์ก่อน';
      return;
    }
    if (!answer.trim() || isNaN(Number(answer))) {
      errorMsg = 'ใส่คำตอบเป็นตัวเลข';
      return;
    }
    level = Math.max(1, Math.floor(level));

    const problem = {
      id: `user_${Date.now()}_${Math.random().toString(36).slice(2, 6)}`,
      level,
      question: question.trim(),
      answer: Number(answer),
      solution: solution.trim() || 'เฉลย: ' + answer,
    };

    addUserProblem(problem);
    success = true;
    question = '';
    answer = '';
    solution = '';
    level = playerState.currentFloor;
    onadded();
  }
</script>

<div class="add-card">
  <h3 class="add-title">➕ เพิ่มโจทย์ใหม่</h3>

  <div class="form-group">
    <label class="form-label">ระดับชั้น</label>
    <input type="number" bind:value={level} min="1" class="form-input" />
  </div>

  <div class="form-group">
    <label class="form-label">โจทย์</label>
    <input
      type="text"
      bind:value={question}
      placeholder="z. B. 1 + 2 = ?"
      class="form-input"
    />
  </div>

  <div class="form-group">
    <label class="form-label">คำตอบ (ตัวเลข)</label>
    <input
      type="text"
      inputmode="numeric"
      bind:value={answer}
      placeholder="z. B. 3"
      class="form-input"
    />
  </div>

  <div class="form-group">
    <label class="form-label">เฉลย (ไม่ต้องก็ได้)</label>
    <input
      type="text"
      bind:value={solution}
      placeholder="z. B. 1 + 2 = 3"
      class="form-input"
    />
  </div>

  {#if errorMsg}
    <p class="form-error">{errorMsg}</p>
  {/if}

  {#if success}
    <p class="form-success">✅ เพิ่มโจทย์สำเร็จ!</p>
  {/if}

  <button class="quantum-btn add-btn" onclick={submit}>
    💾 บันทึกโจทย์
  </button>
</div>

<style>
  .add-card {
    margin-top: 1rem;
    padding: 1rem;
    background: var(--color-surface-1);
    border: 1px solid var(--color-border);
    border-radius: var(--radius-card);
  }

  .add-title {
    font-size: 0.9rem;
    font-weight: 600;
    color: var(--color-text-base);
    margin-bottom: 0.75rem;
  }

  .form-group {
    display: flex;
    flex-direction: column;
    gap: 0.2rem;
    margin-bottom: 0.6rem;
  }

  .form-label {
    font-size: 0.7rem;
    color: var(--color-text-muted);
    text-transform: uppercase;
    letter-spacing: 0.05em;
  }

  .form-input {
    padding: 0.5rem 0.7rem;
    font-size: 0.85rem;
    background: var(--color-surface-2);
    border: 1px solid var(--color-border);
    border-radius: 8px;
    color: var(--color-text-base);
    outline: none;
  }

  .form-input:focus {
    border-color: var(--color-primary);
  }

  .form-error {
    font-size: 0.75rem;
    color: var(--color-danger);
    margin-bottom: 0.4rem;
  }

  .form-success {
    font-size: 0.75rem;
    color: var(--color-success);
    margin-bottom: 0.4rem;
  }

  .add-btn {
    width: 100%;
    padding: 0.5rem;
    font-size: 0.85rem;
  }
</style>
