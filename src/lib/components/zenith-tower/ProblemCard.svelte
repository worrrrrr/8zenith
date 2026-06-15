<script lang="ts">
  import type { MathProblem } from '$lib/utils/mathProblems';

  interface Props {
    problem: MathProblem | null;
    gameMode: 'idle' | 'playing' | 'correct' | 'wrong';
    oncorrect: () => void;
    onwrong: () => void;
    onnext: () => void;
  }

  let { problem, gameMode, oncorrect, onwrong, onnext }: Props = $props();

  let userAnswer = $state('');
  let answerError = $state('');

  function submit() {
    answerError = '';
    const trimmed = userAnswer.trim();
    if (!trimmed || isNaN(Number(trimmed))) {
      answerError = 'ใส่ตัวเลขเท่านั้น!';
      return;
    }
    const num = Number(trimmed);
    if (num === problem!.answer) {
      oncorrect();
    } else {
      onwrong();
    }
  }

  function handleKeydown(e: KeyboardEvent) {
    if (e.key === 'Enter' && gameMode === 'playing') {
      submit();
    }
    if (e.key === 'Enter' && (gameMode === 'correct')) {
      onnext();
    }
  }

  $effect(() => {
    if (gameMode === 'playing') {
      userAnswer = '';
      answerError = '';
    }
  });
</script>

<div class="problem-card">
  {#if gameMode === 'idle'}
    <div class="center-message">
      <span class="big-icon">🏯</span>
      <p class="msg-text">พร้อมปีนหรือยัง?</p>
    </div>

  {:else if problem}
    <div class="problem-header">
      <span class="level-badge">ชั้น {problem.level}</span>
    </div>

    <div class="question-box">
      <p class="question-text">{problem.question}</p>
    </div>

    {#if gameMode === 'playing'}
      <div class="answer-area">
        <input
          type="text"
          inputmode="numeric"
          bind:value={userAnswer}
          placeholder="พิมพ์คำตอบ..."
          class="answer-input"
          class:input-error={!!answerError}
          disabled={gameMode !== 'playing'}
          onkeydown={handleKeydown}
        />
        {#if answerError}
          <p class="error-msg">{answerError}</p>
        {/if}
        <button class="quantum-btn submit-btn" onclick={submit}>
          ✨ ตอบเลย!
        </button>
      </div>

    {:else if gameMode === 'correct'}
      <div class="result correct-result">
        <span class="result-icon">✅</span>
        <span class="result-text">ถูกต้อง! {problem.solution}</span>
      </div>
      <button class="quantum-btn next-btn" onclick={onnext}>
        🚀 ขึ้นชั้นต่อไป
      </button>

    {:else if gameMode === 'wrong'}
      <div class="result wrong-result">
        <span class="result-icon">💀</span>
        <div class="wrong-details">
          <p class="wrong-text">ผิด! คำตอบคือ <strong>{problem.answer}</strong></p>
          <p class="solution-text">{problem.solution}</p>
          <p class="dead-msg">วันนี้จบแค่นี้ พรุ่งนี้มาลองใหม่!</p>
        </div>
      </div>
    {/if}
  {:else}
    <div class="center-message">
      <span class="big-icon">🎉</span>
      <p class="msg-text">คุณเคลียร์ทุกด่านที่มีแล้ว!</p>
      <p class="msg-sub">เพิ่มโจทย์ของคุณเองด้านล่าง</p>
    </div>
  {/if}
</div>

<style>
  .problem-card {
    display: flex;
    flex-direction: column;
    gap: 1rem;
  }

  .center-message {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: 2rem;
    gap: 0.5rem;
  }

  .big-icon {
    font-size: 3rem;
  }

  .msg-text {
    font-size: 1.1rem;
    color: var(--color-text-muted);
  }

  .msg-sub {
    font-size: 0.85rem;
    color: var(--color-text-muted);
    opacity: 0.7;
  }

  .problem-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
  }

  .level-badge {
    display: inline-block;
    padding: 0.25rem 0.75rem;
    border-radius: 999px;
    font-size: 0.75rem;
    font-weight: 600;
    background: linear-gradient(135deg, rgba(168,85,247,0.2), rgba(6,182,212,0.15));
    border: 1px solid var(--color-border-active);
    color: var(--color-text-base);
    font-family: var(--font-mono);
  }

  .question-box {
    padding: 1.25rem;
    background: var(--color-surface-2);
    border: 1px solid var(--color-border);
    border-radius: var(--radius-card);
    text-align: center;
  }

  .question-text {
    font-size: 1.4rem;
    font-weight: 600;
    color: var(--color-text-base);
    font-family: var(--font-mono);
    letter-spacing: 0.05em;
  }

  .answer-area {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
  }

  .answer-input {
    padding: 0.7rem 1rem;
    font-size: 1.2rem;
    text-align: center;
    background: var(--color-surface-1);
    border: 2px solid var(--color-border);
    border-radius: var(--radius-button);
    color: var(--color-text-base);
    font-family: var(--font-mono);
    font-weight: 600;
    outline: none;
    transition: border-color 0.2s;
  }

  .answer-input:focus {
    border-color: var(--color-primary);
  }

  .answer-input.input-error {
    border-color: var(--color-danger);
  }

  .answer-input:disabled {
    opacity: 0.4;
  }

  .error-msg {
    font-size: 0.75rem;
    color: var(--color-danger);
    text-align: center;
  }

  .submit-btn, .next-btn {
    width: 100%;
    padding: 0.7rem;
    font-size: 1rem;
  }

  .result {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    padding: 1rem;
    border-radius: var(--radius-card);
    border: 1px solid;
  }

  .result-icon {
    font-size: 1.5rem;
  }

  .result-text {
    font-size: 0.9rem;
    line-height: 1.5;
  }

  .correct-result {
    background: rgba(16, 185, 129, 0.1);
    border-color: rgba(16, 185, 129, 0.4);
    color: var(--color-success);
  }

  .wrong-result {
    background: rgba(239, 68, 68, 0.1);
    border-color: rgba(239, 68, 68, 0.4);
  }

  .wrong-details {
    display: flex;
    flex-direction: column;
    gap: 0.3rem;
  }

  .wrong-text {
    font-size: 0.9rem;
    color: var(--color-danger);
  }

  .wrong-text strong {
    font-family: var(--font-mono);
    font-size: 1.1rem;
  }

  .solution-text {
    font-size: 0.85rem;
    color: var(--color-text-muted);
  }

  .dead-msg {
    font-size: 0.8rem;
    color: var(--color-text-muted);
    opacity: 0.7;
    margin-top: 0.2rem;
  }
</style>
