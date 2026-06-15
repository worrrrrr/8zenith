<script lang="ts">
  import type { Project, Task, TaskStatus, Priority } from '$lib/utils/projectManager';
  import { getStatusLabel, getPriorityLabel } from '$lib/utils/projectManager';

  interface Props {
    project: Project;
    ontaskmove: (taskId: string, status: TaskStatus) => void;
    ontaskedit: (taskId: string) => void;
    ontaskdelete: (taskId: string) => void;
    onaddtask: () => void;
    editingTask: Task | null;
    editTitle: string;
    editDescription: string;
    editPriority: Priority;
    oneditTitleChange: (v: string) => void;
    oneditDescriptionChange: (v: string) => void;
    oneditPriorityChange: (v: Priority) => void;
    oneditSave: () => void;
    oneditCancel: () => void;
  }

  let {
    project,
    ontaskmove,
    ontaskedit,
    ontaskdelete,
    onaddtask,
    editingTask,
    editTitle,
    editDescription,
    editPriority,
    oneditTitleChange,
    oneditDescriptionChange,
    oneditPriorityChange,
    oneditSave,
    oneditCancel,
  }: Props = $props();

  const columns: TaskStatus[] = ['todo', 'in_progress', 'done'];
  const columnIcons: Record<TaskStatus, string> = {
    todo: '📋',
    in_progress: '🔄',
    done: '✅',
  };

  function getTasksByStatus(status: TaskStatus): Task[] {
    return project.tasks.filter((t) => t.status === status);
  }

  function canMoveLeft(task: Task): boolean {
    return task.status === 'in_progress' || task.status === 'done';
  }

  function canMoveRight(task: Task): boolean {
    return task.status === 'todo' || task.status === 'in_progress';
  }

  function moveLeft(task: Task) {
    const map: Record<TaskStatus, TaskStatus> = {
      todo: 'todo',
      in_progress: 'todo',
      done: 'in_progress',
    };
    ontaskmove(task.id, map[task.status]);
  }

  function moveRight(task: Task) {
    const map: Record<TaskStatus, TaskStatus> = {
      todo: 'in_progress',
      in_progress: 'done',
      done: 'done',
    };
    ontaskmove(task.id, map[task.status]);
  }

  function statusCount(status: TaskStatus): number {
    return project.tasks.filter((t) => t.status === status).length;
  }
</script>

<div class="board">
  <div class="board-header">
    <div class="project-title-area">
      <span class="color-dot" style="background: {project.color}"></span>
      <div>
        <h3 class="project-title">{project.name}</h3>
        {#if project.description}
          <p class="project-desc">{project.description}</p>
        {/if}
      </div>
    </div>
    <div class="task-stats">
      <span>{project.tasks.length} tasks</span>
      <span class="stat-sep">·</span>
      <span class="stat-done">{project.tasks.filter((t) => t.status === 'done').length} done</span>
    </div>
  </div>

  <button class="add-task-btn" onclick={onaddtask}>
    ＋ เพิ่ม Task ใหม่
  </button>

  <!-- Edit Task Form -->
  {#if editingTask}
    <div class="edit-form">
      <h4 class="edit-title">✏️ แก้ไข Task</h4>
      <input
        type="text"
        bind:value={editTitle}
        placeholder="ชื่อ task"
        class="form-input"
      />
      <textarea
        bind:value={editDescription}
        placeholder="รายละเอียด (ไม่ต้องก็ได้)"
        class="form-textarea"
        rows="2"
      ></textarea>
      <select bind:value={editPriority} class="form-select">
        <option value="low">🟢 ต่ำ</option>
        <option value="medium">🟡 กลาง</option>
        <option value="high">🔴 สูง</option>
      </select>
      <div class="edit-actions">
        <button class="save-btn" onclick={oneditSave}>💾 บันทึก</button>
        <button class="cancel-btn" onclick={oneditCancel}>ยกเลิก</button>
      </div>
    </div>
  {/if}

  <div class="columns">
    {#each columns as status}
      {@const tasks = getTasksByStatus(status)}
      <div class="column">
        <div class="column-header">
          <span>{columnIcons[status]} {getStatusLabel(status)}</span>
          <span class="col-count">{tasks.length}</span>
        </div>

        <div class="task-list">
          {#each tasks as task (task.id)}
            <div class="task-card" class:high-priority={task.priority === 'high'}>
              <div class="task-top">
                <span class="task-title">{task.title}</span>
                <span class="priority-badge priority-{task.priority}">{getPriorityLabel(task.priority)}</span>
              </div>

              {#if task.description}
                <p class="task-desc">{task.description}</p>
              {/if}

              <div class="task-actions">
                <div class="move-btns">
                  {#if canMoveLeft(task)}
                    <button
                      class="move-btn"
                      onclick={() => moveLeft(task)}
                      title="ย้ายซ้าย"
                    >◀</button>
                  {/if}
                  {#if canMoveRight(task)}
                    <button
                      class="move-btn"
                      onclick={() => moveRight(task)}
                      title="ย้ายขวา"
                    >▶</button>
                  {/if}
                </div>
                <div class="action-btns">
                  <button
                    class="action-btn edit"
                    onclick={() => ontaskedit(task.id)}
                    title="แก้ไข"
                  >✏️</button>
                  <button
                    class="action-btn delete"
                    onclick={() => ontaskdelete(task.id)}
                    title="ลบ"
                  >🗑️</button>
                </div>
              </div>
            </div>
          {/each}

          {#if tasks.length === 0}
            <p class="empty-col">ยังไม่มี task</p>
          {/if}
        </div>
      </div>
    {/each}
  </div>
</div>

<style>
  .board {
    display: flex;
    flex-direction: column;
    gap: 0.75rem;
    flex: 1;
    min-width: 0;
  }

  .board-header {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    gap: 0.5rem;
  }

  .project-title-area {
    display: flex;
    align-items: flex-start;
    gap: 0.5rem;
  }

  .color-dot {
    width: 12px;
    height: 12px;
    border-radius: 50%;
    flex-shrink: 0;
    margin-top: 0.2rem;
  }

  .project-title {
    font-size: 1.1rem;
    font-weight: 700;
    color: var(--color-text-base);
  }

  .project-desc {
    font-size: 0.75rem;
    color: var(--color-text-muted);
    margin-top: 0.1rem;
  }

  .task-stats {
    font-size: 0.7rem;
    color: var(--color-text-muted);
    font-family: var(--font-mono);
    white-space: nowrap;
  }

  .stat-sep {
    margin: 0 0.3rem;
  }

  .stat-done {
    color: var(--color-success);
  }

  .add-task-btn {
    padding: 0.5rem;
    font-size: 0.8rem;
    font-weight: 600;
    background: var(--color-surface-1);
    border: 1px dashed var(--color-border);
    border-radius: 8px;
    color: var(--color-text-muted);
    cursor: pointer;
    transition: all 0.15s;
  }

  .add-task-btn:hover {
    border-color: var(--color-primary);
    color: var(--color-primary);
    background: rgba(168, 85, 247, 0.08);
  }

  .edit-form {
    padding: 0.75rem;
    background: var(--color-surface-1);
    border: 1px solid var(--color-border-active);
    border-radius: var(--radius-card);
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
  }

  .edit-title {
    font-size: 0.85rem;
    font-weight: 600;
    color: var(--color-text-base);
  }

  .form-input, .form-textarea, .form-select {
    padding: 0.45rem 0.6rem;
    font-size: 0.8rem;
    background: var(--color-surface-2);
    border: 1px solid var(--color-border);
    border-radius: 6px;
    color: var(--color-text-base);
    outline: none;
    width: 100%;
  }

  .form-input:focus, .form-textarea:focus, .form-select:focus {
    border-color: var(--color-primary);
  }

  .form-textarea {
    resize: vertical;
    font-family: inherit;
  }

  .edit-actions {
    display: flex;
    gap: 0.4rem;
  }

  .save-btn, .cancel-btn {
    padding: 0.4rem 0.8rem;
    font-size: 0.75rem;
    border-radius: 6px;
    border: none;
    cursor: pointer;
    font-weight: 600;
  }

  .save-btn {
    background: var(--color-primary);
    color: white;
  }

  .cancel-btn {
    background: var(--color-surface-2);
    color: var(--color-text-muted);
    border: 1px solid var(--color-border);
  }

  .columns {
    display: grid;
    grid-template-columns: 1fr 1fr 1fr;
    gap: 0.5rem;
    flex: 1;
  }

  .column {
    display: flex;
    flex-direction: column;
    gap: 0.4rem;
    min-width: 0;
  }

  .column-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    font-size: 0.75rem;
    font-weight: 600;
    color: var(--color-text-base);
    padding: 0.4rem 0.5rem;
    background: var(--color-surface-1);
    border: 1px solid var(--color-border);
    border-radius: 8px;
  }

  .col-count {
    font-size: 0.65rem;
    color: var(--color-text-muted);
    font-family: var(--font-mono);
    background: var(--color-surface-2);
    padding: 0.05rem 0.4rem;
    border-radius: 999px;
  }

  .task-list {
    display: flex;
    flex-direction: column;
    gap: 0.3rem;
    min-height: 100px;
  }

  .task-card {
    padding: 0.5rem;
    background: var(--color-surface-1);
    border: 1px solid var(--color-border);
    border-radius: 8px;
    display: flex;
    flex-direction: column;
    gap: 0.3rem;
    transition: all 0.15s;
  }

  .task-card:hover {
    border-color: var(--color-border-active);
  }

  .task-card.high-priority {
    border-left: 3px solid var(--color-danger);
  }

  .task-top {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    gap: 0.3rem;
  }

  .task-title {
    font-size: 0.8rem;
    font-weight: 600;
    color: var(--color-text-base);
    word-break: break-word;
  }

  .priority-badge {
    font-size: 0.6rem;
    white-space: nowrap;
    padding: 0.05rem 0.35rem;
    border-radius: 4px;
  }

  .priority-low { color: var(--color-success); background: rgba(16,185,129,0.1); }
  .priority-medium { color: var(--color-accent); background: rgba(245,158,11,0.1); }
  .priority-high { color: var(--color-danger); background: rgba(239,68,68,0.1); }

  .task-desc {
    font-size: 0.7rem;
    color: var(--color-text-muted);
    line-height: 1.4;
  }

  .task-actions {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-top: 0.1rem;
  }

  .move-btns, .action-btns {
    display: flex;
    gap: 0.2rem;
  }

  .move-btn {
    font-size: 0.65rem;
    background: none;
    border: 1px solid var(--color-border);
    border-radius: 4px;
    cursor: pointer;
    padding: 0.1rem 0.25rem;
    color: var(--color-text-muted);
    transition: all 0.1s;
  }

  .move-btn:hover {
    color: var(--color-text-base);
    border-color: var(--color-border-active);
  }

  .action-btn {
    font-size: 0.7rem;
    background: none;
    border: none;
    cursor: pointer;
    padding: 0.1rem;
    opacity: 0.5;
    transition: opacity 0.15s;
  }

  .action-btn:hover {
    opacity: 1;
  }

  .empty-col {
    font-size: 0.7rem;
    color: var(--color-text-muted);
    text-align: center;
    padding: 1rem 0;
    opacity: 0.5;
  }

  @media (max-width: 768px) {
    .columns {
      grid-template-columns: 1fr;
    }
  }
</style>
