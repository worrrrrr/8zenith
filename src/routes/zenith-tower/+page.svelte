<script lang="ts">
  import TowerVisual from '$lib/components/zenith-tower/TowerVisual.svelte';
  import StatusCard from '$lib/components/zenith-tower/StatusCard.svelte';
  import ProblemCard from '$lib/components/zenith-tower/ProblemCard.svelte';
  import AddProblem from '$lib/components/zenith-tower/AddProblem.svelte';
  import {
    loadPlayerState,
    savePlayerState,
    getProblemForLevel,
    getTimeUntilReset,
    type PlayerState,
    type MathProblem,
  } from '$lib/utils/mathProblems';

  let state = $state<PlayerState>(loadPlayerState());
  let currentProblem = $state<MathProblem | null>(null);
  let gameMode = $state<'idle' | 'playing' | 'correct' | 'wrong'>('idle');
  let showAddForm = $state(false);
  let timeUntilReset = $state('');
  let timerInterval: ReturnType<typeof setInterval> | undefined;

  function startTimer() {
    timeUntilReset = getTimeUntilReset();
    if (timerInterval) clearInterval(timerInterval);
    timerInterval = setInterval(() => {
      timeUntilReset = getTimeUntilReset();
    }, 1000);
  }

  function startClimb() {
    const problem = getProblemForLevel(state.currentFloor);
    if (problem) {
      currentProblem = problem;
      gameMode = 'playing';
    } else {
      currentProblem = null;
      gameMode = 'idle';
    }
  }

  function handleCorrect() {
    state.totalCorrect++;
    state.totalAttempts++;
    state.streak = state.streak || 1;
    state.currentFloor++;
    if (state.currentFloor > state.highestFloor) {
      state.highestFloor = state.currentFloor;
    }
    savePlayerState(state);
    gameMode = 'correct';
  }

  function handleWrong() {
    state.totalAttempts++;
    state.diedToday = true;
    savePlayerState(state);
    gameMode = 'wrong';
  }

  function handleNext() {
    if (state.diedToday) return;
    const nextProblem = getProblemForLevel(state.currentFloor);
    if (nextProblem) {
      currentProblem = nextProblem;
      gameMode = 'playing';
    } else {
      currentProblem = null;
      gameMode = 'idle';
    }
  }

  function onAdded() {
    showAddForm = false;
    if (!currentProblem && gameMode === 'idle') {
      startClimb();
    }
  }

  $effect(() => {
    if (state.diedToday) {
      startTimer();
    }
    return () => {
      if (timerInterval) clearInterval(timerInterval);
    };
  });
</script>

<div class="cosmic-card p-6">
  <div class="flex items-center gap-3 mb-1">
    <span class="text-3xl">🏯</span>
    <div>
      <h2 class="text-gradient-primary text-2xl font-bold">Zenith Tower</h2>
      <p class="text-text-muted text-sm">ปีนหอคอย Zenith ด้วยโจทย์คณิตศาสตร์ — ผิดได้ครั้งเดียวต่อวัน!</p>
    </div>
  </div>

  <StatusCard {state} />

  {#if state.diedToday && gameMode !== 'correct'}
    <div class="death-screen">
      <span class="death-icon">💀</span>
      <p class="death-title">วันนี้คุณตายแล้ว!</p>
      <p class="death-sub">คุณตอบผิดที่ชั้น {state.currentFloor}</p>
      <p class="death-timer">⏳ รออีก {timeUntilReset} ก็กลับมาเกิดได้</p>
      <p class="death-hint">พรุ่งนี้จะกลับมาเริ่มที่ชั้น {state.currentFloor} อีกครั้ง 💪</p>
    </div>
  {/if}

  {#if !state.diedToday || gameMode === 'correct'}
    <div class="game-layout">
      <div class="tower-section">
        <TowerVisual {state} />
      </div>
      <div class="problem-section">
        <ProblemCard
          problem={currentProblem}
          {gameMode}
          oncorrect={handleCorrect}
          onwrong={handleWrong}
          onnext={handleNext}
        />
        {#if gameMode === 'idle' && !state.diedToday}
          <button class="quantum-btn start-btn" onclick={startClimb}>
            🚀 เริ่มปีน!
          </button>
        {/if}
      </div>
    </div>
  {/if}

  <div class="mt-4 pt-3 border-t border-border">
    <button
      class="text-sm text-text-muted hover:text-primary transition-colors"
      onclick={() => (showAddForm = !showAddForm)}
    >
      {showAddForm ? '✕ ปิด' : '➕ เพิ่มโจทย์ใหม่'}
    </button>

    {#if showAddForm}
      <AddProblem playerState={state} onadded={onAdded} />
    {/if}
  </div>
</div>

<style>
  .death-screen {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 0.5rem;
    padding: 2rem;
    background: rgba(239, 68, 68, 0.08);
    border: 1px solid rgba(239, 68, 68, 0.3);
    border-radius: var(--radius-card);
    text-align: center;
  }

  .death-icon {
    font-size: 3rem;
  }

  .death-title {
    font-size: 1.3rem;
    font-weight: 700;
    color: var(--color-danger);
  }

  .death-sub {
    font-size: 0.9rem;
    color: var(--color-text-muted);
  }

  .death-timer {
    font-size: 1.1rem;
    font-weight: 600;
    color: var(--color-accent);
    font-family: var(--font-mono);
  }

  .death-hint {
    font-size: 0.8rem;
    color: var(--color-text-muted);
    opacity: 0.7;
  }

  .game-layout {
    display: flex;
    gap: 1rem;
    align-items: flex-start;
  }

  .tower-section {
    flex-shrink: 0;
    width: 140px;
    max-height: 420px;
    overflow-y: auto;
    padding-right: 0.25rem;
  }

  .tower-section::-webkit-scrollbar {
    width: 3px;
  }

  .tower-section::-webkit-scrollbar-thumb {
    background: var(--color-border);
    border-radius: 99px;
  }

  .problem-section {
    flex: 1;
    min-width: 0;
  }

  .start-btn {
    width: 100%;
    padding: 0.9rem;
    font-size: 1.1rem;
    margin-top: 0.5rem;
  }

  @media (max-width: 640px) {
    .game-layout {
      flex-direction: column;
      align-items: center;
    }

    .tower-section {
      width: 100%;
      max-height: 200px;
    }
  }

  .border-t {
    border-top: 1px solid var(--color-border);
  }
</style>
