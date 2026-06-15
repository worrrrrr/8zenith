<script lang="ts">
  import type { PlayerState } from '$lib/utils/mathProblems';

  interface Props {
    state: PlayerState;
  }

  let { state }: Props = $props();

  let floors = $derived.by(() => {
    const count = Math.max(state.highestFloor + 2, 8);
    return Array.from({ length: count }, (_, i) => i + 1).reverse();
  });
</script>

<div class="tower-wrapper">
  <div class="tower-body">
    <div class="spire">
      <svg width="32" height="24" viewBox="0 0 32 24">
        <polygon points="16,0 0,24 32,24" fill="url(#spire-grad)" />
        <defs>
          <linearGradient id="spire-grad" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stop-color="var(--color-primary)" />
            <stop offset="100%" stop-color="var(--color-secondary)" stop-opacity="0.4" />
          </linearGradient>
        </defs>
      </svg>
      <div class="spire-glow"></div>
    </div>

    <div class="floors-container">
      {#each floors as level (level)}
        {@const completed = level < state.currentFloor}
        {@const current = level === state.currentFloor}
        <div
          class="floor"
          class:completed
          class:current
          class:locked={!completed && !current}
        >
          <span class="floor-num">{level}</span>
          {#if current}
            <span class="you-here">👈</span>
          {/if}
          {#if completed && level % 3 === 0}
            <span class="star">⭐</span>
          {/if}
        </div>
      {/each}
    </div>

    <div class="ground">
      <div class="ground-line"></div>
    </div>
  </div>
</div>

<style>
  .tower-wrapper {
    display: flex;
    justify-content: center;
    padding: 0.5rem;
  }

  .tower-body {
    display: flex;
    flex-direction: column;
    align-items: center;
    width: 100%;
    max-width: 160px;
  }

  .spire {
    position: relative;
    display: flex;
    justify-content: center;
    margin-bottom: -2px;
  }

  .spire svg {
    filter: drop-shadow(0 0 8px rgba(168, 85, 247, 0.6));
  }

  .spire-glow {
    position: absolute;
    top: 4px;
    width: 8px;
    height: 8px;
    background: var(--color-primary);
    border-radius: 50%;
    filter: blur(6px);
    animation: pulse-spire 2s ease-in-out infinite;
  }

  @keyframes pulse-spire {
    0%, 100% { opacity: 0.4; transform: scale(1); }
    50% { opacity: 1; transform: scale(1.5); }
  }

  .floors-container {
    display: flex;
    flex-direction: column-reverse;
    gap: 4px;
    width: 100%;
  }

  .floor {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 6px;
    height: 30px;
    border-radius: 6px;
    border: 1px solid var(--color-border);
    background: var(--color-surface-1);
    transition: all 0.3s ease;
    position: relative;
    overflow: hidden;
  }

  .floor.locked {
    opacity: 0.35;
  }

  .floor.completed {
    background: linear-gradient(90deg, rgba(168, 85, 247, 0.25), rgba(6, 182, 212, 0.2));
    border-color: rgba(168, 85, 247, 0.5);
    box-shadow: 0 0 8px rgba(168, 85, 247, 0.15);
  }

  .floor.current {
    background: linear-gradient(90deg, rgba(168, 85, 247, 0.45), rgba(6, 182, 212, 0.35));
    border-color: var(--color-secondary);
    box-shadow: 0 0 14px rgba(6, 182, 212, 0.4), inset 0 0 20px rgba(168, 85, 247, 0.1);
    animation: pulse-current 1.5s ease-in-out infinite;
  }

  @keyframes pulse-current {
    0%, 100% { box-shadow: 0 0 14px rgba(6, 182, 212, 0.4), inset 0 0 20px rgba(168, 85, 247, 0.1); }
    50% { box-shadow: 0 0 22px rgba(6, 182, 212, 0.6), inset 0 0 30px rgba(168, 85, 247, 0.2); }
  }

  .floor-num {
    font-size: 0.75rem;
    font-weight: 600;
    color: var(--color-text-muted);
    font-family: var(--font-mono);
  }

  .completed .floor-num {
    color: var(--color-text-base);
  }

  .current .floor-num {
    color: var(--color-primary);
    font-weight: 700;
  }

  .you-here {
    font-size: 0.7rem;
    animation: bounce-here 1.2s ease-in-out infinite;
  }

  @keyframes bounce-here {
    0%, 100% { transform: translateX(0); }
    50% { transform: translateX(3px); }
  }

  .star {
    font-size: 0.6rem;
    position: absolute;
    right: 6px;
  }

  .ground {
    width: 100%;
    margin-top: 4px;
    display: flex;
    justify-content: center;
  }

  .ground-line {
    width: 100%;
    height: 3px;
    background: linear-gradient(90deg, transparent, var(--color-primary), var(--color-secondary), transparent);
    border-radius: 2px;
    opacity: 0.5;
  }
</style>
