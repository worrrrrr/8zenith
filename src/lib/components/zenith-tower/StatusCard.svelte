<script lang="ts">
  import type { PlayerState } from '$lib/utils/mathProblems';

  interface Props {
    state: PlayerState;
  }

  let { state }: Props = $props();

  let successRate = $derived(
    state.totalAttempts > 0
      ? Math.round((state.totalCorrect / state.totalAttempts) * 100)
      : 0
  );
</script>

<div class="status-card">
  <div class="stat">
    <span class="stat-icon">🏯</span>
    <div class="stat-text">
      <span class="stat-label">ชั้นปัจจุบัน</span>
      <span class="stat-value accent">{state.currentFloor}</span>
    </div>
  </div>

  <div class="stat">
    <span class="stat-icon">🔝</span>
    <div class="stat-text">
      <span class="stat-label">สูงสุด</span>
      <span class="stat-value primary">{state.highestFloor}</span>
    </div>
  </div>

  <div class="stat">
    <span class="stat-icon">❤️</span>
    <div class="stat-text">
      <span class="stat-label">ชีพวันนี้</span>
      <span class="stat-value" class:alive={!state.diedToday} class:dead={state.diedToday}>
        {state.diedToday ? '0/1' : '1/1'}
      </span>
    </div>
  </div>

  <div class="stat">
    <span class="stat-icon">🔥</span>
    <div class="stat-text">
      <span class="stat-label">ติดต่อ</span>
      <span class="stat-value accent">{state.streak} วัน</span>
    </div>
  </div>

  <div class="stat">
    <span class="stat-icon">📊</span>
    <div class="stat-text">
      <span class="stat-label">สำเร็จ</span>
      <span class="stat-value">{successRate}%</span>
    </div>
  </div>
</div>

<style>
  .status-card {
    display: flex;
    flex-wrap: wrap;
    gap: 0.5rem;
    margin-bottom: 1rem;
    padding: 0.75rem;
    background: var(--color-surface-1);
    border: 1px solid var(--color-border);
    border-radius: var(--radius-card);
  }

  .stat {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    flex: 1;
    min-width: 110px;
  }

  .stat-icon {
    font-size: 1.2rem;
  }

  .stat-text {
    display: flex;
    flex-direction: column;
    gap: 0.05rem;
  }

  .stat-label {
    font-size: 0.65rem;
    color: var(--color-text-muted);
    text-transform: uppercase;
    letter-spacing: 0.05em;
  }

  .stat-value {
    font-size: 1rem;
    font-weight: 700;
    color: var(--color-text-base);
    font-family: var(--font-mono);
  }

  .stat-value.accent {
    color: var(--color-accent);
  }

  .stat-value.primary {
    color: var(--color-primary);
  }

  .stat-value.alive {
    color: var(--color-success);
  }

  .stat-value.dead {
    color: var(--color-danger);
  }
</style>
