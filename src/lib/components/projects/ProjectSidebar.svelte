<script lang="ts">
  import type { Project } from '$lib/utils/projectManager';
  import { getColorClass } from '$lib/utils/projectManager';

  interface Props {
    projects: Project[];
    activeId: string | null;
    onselect: (id: string) => void;
    ondelete: (id: string) => void;
    onnew: () => void;
  }

  let { projects, activeId, onselect, ondelete, onnew }: Props = $props();
</script>

<div class="sidebar">
  <div class="sidebar-header">
    <span class="sidebar-title">📋 โปรเจค</span>
    <span class="project-count">{projects.length}</span>
  </div>

  <div class="project-list">
    {#each projects as project (project.id)}
      <div
        class="project-item"
        class:active={project.id === activeId}
        role="button"
        tabindex="0"
        onclick={() => onselect(project.id)}
        onkeydown={(e) => e.key === 'Enter' && onselect(project.id)}
      >
        <div class="project-info">
          <span class="color-dot" style="background: {project.color}"></span>
          <div class="project-text">
            <span class="project-name">{project.name}</span>
            <span class="task-count">{project.tasks.length} task{project.tasks.length !== 1 ? 's' : ''}</span>
          </div>
        </div>
        <button
          class="delete-btn"
          onclick={(e) => { e.stopPropagation(); ondelete(project.id); }}
          title="ลบโปรเจค"
        >✕</button>
      </div>
    {/each}

    {#if projects.length === 0}
      <p class="empty-msg">ยังไม่มีโปรเจค</p>
    {/if}
  </div>

  <button class="new-btn" onclick={onnew}>
    ＋ โปรเจคใหม่
  </button>
</div>

<style>
  .sidebar {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
    width: 220px;
    flex-shrink: 0;
    background: var(--color-surface-1);
    border: 1px solid var(--color-border);
    border-radius: var(--radius-card);
    padding: 0.75rem;
  }

  .sidebar-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
  }

  .sidebar-title {
    font-size: 0.8rem;
    font-weight: 700;
    color: var(--color-text-base);
  }

  .project-count {
    font-size: 0.7rem;
    color: var(--color-text-muted);
    background: var(--color-surface-2);
    padding: 0.1rem 0.45rem;
    border-radius: 999px;
    font-family: var(--font-mono);
  }

  .project-list {
    display: flex;
    flex-direction: column;
    gap: 0.2rem;
    flex: 1;
    overflow-y: auto;
    max-height: 400px;
  }

  .project-item {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0.45rem 0.5rem;
    border-radius: 8px;
    background: transparent;
    border: 1px solid transparent;
    cursor: pointer;
    transition: all 0.15s;
    width: 100%;
    text-align: left;
  }

  .project-item:hover {
    background: var(--color-surface-2);
    border-color: var(--color-border);
  }

  .project-item.active {
    background: var(--color-surface-2);
    border-color: var(--color-border-active);
  }

  .project-info {
    display: flex;
    align-items: center;
    gap: 0.4rem;
    min-width: 0;
  }

  .color-dot {
    width: 8px;
    height: 8px;
    border-radius: 50%;
    flex-shrink: 0;
  }

  .project-text {
    display: flex;
    flex-direction: column;
    gap: 0.05rem;
    min-width: 0;
  }

  .project-name {
    font-size: 0.8rem;
    font-weight: 600;
    color: var(--color-text-base);
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }

  .task-count {
    font-size: 0.62rem;
    color: var(--color-text-muted);
  }

  .delete-btn {
    font-size: 0.6rem;
    color: var(--color-text-muted);
    opacity: 0;
    background: none;
    border: none;
    cursor: pointer;
    padding: 0.2rem;
    transition: all 0.15s;
  }

  .project-item:hover .delete-btn {
    opacity: 0.6;
  }

  .delete-btn:hover {
    color: var(--color-danger);
    opacity: 1 !important;
  }

  .empty-msg {
    font-size: 0.75rem;
    color: var(--color-text-muted);
    text-align: center;
    padding: 1rem;
  }

  .new-btn {
    padding: 0.5rem;
    font-size: 0.8rem;
    font-weight: 600;
    background: var(--color-surface-2);
    border: 1px dashed var(--color-border);
    border-radius: 8px;
    color: var(--color-text-muted);
    cursor: pointer;
    transition: all 0.15s;
    text-align: center;
  }

  .new-btn:hover {
    border-color: var(--color-primary);
    color: var(--color-primary);
    background: rgba(168, 85, 247, 0.1);
  }
</style>
