<script lang="ts">
  import ProjectSidebar from '$lib/components/projects/ProjectSidebar.svelte';
  import KanbanBoard from '$lib/components/projects/KanbanBoard.svelte';
  import {
    loadProjects,
    saveProjects,
    createProject,
    createTask,
    updateTaskStatus,
    deleteTask,
    updateTask,
    getProjectColors,
    type Project,
    type Task,
    type TaskStatus,
    type Priority,
  } from '$lib/utils/projectManager';

  let projects = $state<Project[]>(loadProjects());
  let activeProjectId = $state<string | null>(null);
  let showNewProject = $state(false);
  let newName = $state('');
  let newDesc = $state('');
  let newColor = $state('#a855f7');
  let showAddTask = $state(false);
  let newTaskTitle = $state('');
  let newTaskDesc = $state('');
  let newTaskPriority = $state<Priority>('medium');

  let aiLoading = $state(false);
  let aiTasks = $state<{ title: string; description: string; priority: Priority }[]>([]);
  let aiError = $state('');

  let editingTask = $state<Task | null>(null);
  let editTitle = $state('');
  let editDescription = $state('');
  let editPriority = $state<Priority>('medium');

  let activeProject = $derived(
    projects.find((p) => p.id === activeProjectId) ?? null
  );

  function sync() {
    saveProjects(projects);
  }

  function selectProject(id: string) {
    activeProjectId = id;
    showAddTask = false;
    editingTask = null;
  }

  function deleteProjectHandler(id: string) {
    projects = projects.filter((p) => p.id !== id);
    if (activeProjectId === id) activeProjectId = projects[0]?.id ?? null;
    sync();
  }

  function newProject() {
    showNewProject = true;
    newName = '';
    newDesc = '';
    newColor = PROJECT_COLORS[0];
    aiTasks = [];
    aiError = '';
  }

  async function generateWithAI() {
    if (!newName.trim()) return;
    aiLoading = true;
    aiError = '';
    aiTasks = [];
    try {
      const res = await fetch('/api/generate-tasks', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name: newName.trim(), description: newDesc.trim() }),
      });
      const json = await res.json();
      if (json.success) {
        aiTasks = json.tasks.map((t: any) => ({
          title: t.title,
          description: t.description || '',
          priority: (['low', 'medium', 'high'].includes(t.priority) ? t.priority : 'medium') as Priority,
        }));
      } else {
        aiError = json.error || 'AI ไม่สามารถสร้าง task ได้';
      }
    } catch (e) {
      aiError = 'เกิดข้อผิดพลาดในการเชื่อมต่อ AI';
    } finally {
      aiLoading = false;
    }
  }

  function createProjectHandler() {
    if (!newName.trim()) return;
    const p = createProject(newName.trim(), newDesc.trim(), newColor);
    // Add AI-generated tasks to project
    if (aiTasks.length > 0) {
      p.tasks = aiTasks.map((t) => createTask(t.title, t.description, t.priority));
    }
    projects = [...projects, p];
    activeProjectId = p.id;
    showNewProject = false;
    sync();
  }

  function addTask() {
    showAddTask = true;
    newTaskTitle = '';
    newTaskDesc = '';
    newTaskPriority = 'medium';
  }

  function createTaskHandler() {
    if (!newTaskTitle.trim() || !activeProjectId) return;
    const task = createTask(newTaskTitle.trim(), newTaskDesc.trim(), newTaskPriority);
    projects = projects.map((p) =>
      p.id === activeProjectId ? { ...p, tasks: [...p.tasks, task] } : p
    );
    showAddTask = false;
    sync();
  }

  function moveTask(taskId: string, status: TaskStatus) {
    if (!activeProjectId) return;
    projects = updateTaskStatus(projects, activeProjectId, taskId, status);
    sync();
  }

  function editTaskHandler(taskId: string) {
    if (!activeProject) return;
    const task = activeProject.tasks.find((t) => t.id === taskId);
    if (!task) return;
    editingTask = task;
    editTitle = task.title;
    editDescription = task.description;
    editPriority = task.priority;
  }

  function saveEdit() {
    if (!editingTask || !activeProjectId) return;
    if (!editTitle.trim()) return;
    projects = updateTask(projects, activeProjectId, editingTask.id, {
      title: editTitle.trim(),
      description: editDescription.trim(),
      priority: editPriority,
    });
    editingTask = null;
    sync();
  }

  function cancelEdit() {
    editingTask = null;
  }

  function deleteTaskHandler(taskId: string) {
    if (!activeProjectId) return;
    projects = deleteTask(projects, activeProjectId, taskId);
    sync();
  }

  const PROJECT_COLORS = getProjectColors();
</script>

<div class="cosmic-card p-6">
  <div class="flex items-center gap-3 mb-4">
    <span class="text-3xl">📋</span>
    <div>
      <h2 class="text-gradient-primary text-2xl font-bold">Zenith Projects</h2>
      <p class="text-text-muted text-sm">จัดการโปรเจคและ task แบบคัมบัง</p>
    </div>
  </div>

  <div class="layout">
    <ProjectSidebar
      {projects}
      activeId={activeProjectId}
      onselect={selectProject}
      ondelete={deleteProjectHandler}
      onnew={newProject}
    />

    {#if showNewProject}
      <div class="new-project-form">
        <h3 class="form-title">＋ โปรเจคใหม่</h3>
        <input
          type="text"
          bind:value={newName}
          placeholder="ชื่อโปรเจค"
          class="form-input"
        />
        <input
          type="text"
          bind:value={newDesc}
          placeholder="คำอธิบาย (ไม่ต้องก็ได้)"
          class="form-input"
        />
        <div class="color-picker">
          <span class="color-label">สี</span>
          <div class="color-options">
            {#each PROJECT_COLORS as color}
              <button
                class="color-btn"
                class:selected={newColor === color}
                style="background: {color}"
                onclick={() => (newColor = color)}
              ></button>
            {/each}
          </div>
        </div>

        <button
          class="ai-btn"
          onclick={generateWithAI}
          disabled={aiLoading || !newName.trim()}
        >
          {#if aiLoading}
            🤖 กำลังสร้าง task ด้วย AI...
          {:else}
            🤖 ให้ AI ช่วยสร้าง Task
          {/if}
        </button>

        {#if aiError}
          <p class="ai-error">{aiError}</p>
        {/if}

        {#if aiTasks.length > 0}
          <div class="ai-tasks-preview">
            <p class="ai-tasks-label">🤖 AI แนะนำ {aiTasks.length} tasks:</p>
            {#each aiTasks as t, i}
              <div class="ai-task-item">
                <span class="ai-task-num">{i + 1}.</span>
                <div class="ai-task-body">
                  <span class="ai-task-title">{t.title}</span>
                  {#if t.description}
                    <span class="ai-task-desc">{t.description}</span>
                  {/if}
                </div>
                <span class="ai-task-prio prio-{t.priority}">
                  {t.priority === 'high' ? '🔴' : t.priority === 'medium' ? '🟡' : '🟢'}
                </span>
              </div>
            {/each}
          </div>
        {/if}

        <div class="form-actions">
          <button class="quantum-btn" onclick={createProjectHandler} disabled={!newName.trim()}>
            ✅ สร้างโปรเจค{aiTasks.length > 0 ? ` (${aiTasks.length} tasks)` : ''}
          </button>
          <button class="cancel-btn" onclick={() => (showNewProject = false)}>
            ยกเลิก
          </button>
        </div>
      </div>

    {:else if activeProject}
      <KanbanBoard
        project={activeProject}
        ontaskmove={moveTask}
        ontaskedit={editTaskHandler}
        ontaskdelete={deleteTaskHandler}
        onaddtask={addTask}
        {editingTask}
        bind:editTitle
        bind:editDescription
        bind:editPriority
        oneditTitleChange={(v) => (editTitle = v)}
        oneditDescriptionChange={(v) => (editDescription = v)}
        oneditPriorityChange={(v) => (editPriority = v)}
        oneditSave={saveEdit}
        oneditCancel={cancelEdit}
      />

      {#if showAddTask}
        <div class="add-task-form">
          <h4 class="form-title">＋ เพิ่ม Task</h4>
          <input
            type="text"
            bind:value={newTaskTitle}
            placeholder="ชื่อ task"
            class="form-input"
          />
          <textarea
            bind:value={newTaskDesc}
            placeholder="รายละเอียด (ไม่ต้องก็ได้)"
            class="form-textarea"
            rows="2"
          ></textarea>
          <select bind:value={newTaskPriority} class="form-select">
            <option value="low">🟢 ต่ำ</option>
            <option value="medium">🟡 กลาง</option>
            <option value="high">🔴 สูง</option>
          </select>
          <div class="form-actions">
            <button class="quantum-btn" onclick={createTaskHandler} disabled={!newTaskTitle.trim()}>
              💾 บันทึก
            </button>
            <button class="cancel-btn" onclick={() => (showAddTask = false)}>
              ยกเลิก
            </button>
          </div>
        </div>
      {/if}

    {:else}
      <div class="no-project">
        <span class="big-icon">📋</span>
        <p>เลือกโปรเจคหรือสร้างใหม่</p>
      </div>
    {/if}
  </div>
</div>

<style>
  .layout {
    display: flex;
    gap: 1rem;
    align-items: flex-start;
  }

  .new-project-form, .add-task-form {
    flex: 1;
    padding: 1rem;
    background: var(--color-surface-1);
    border: 1px solid var(--color-border-active);
    border-radius: var(--radius-card);
    display: flex;
    flex-direction: column;
    gap: 0.6rem;
  }

  .form-title {
    font-size: 0.9rem;
    font-weight: 600;
    color: var(--color-text-base);
  }

  .form-input, .form-textarea, .form-select {
    padding: 0.5rem 0.7rem;
    font-size: 0.85rem;
    background: var(--color-surface-2);
    border: 1px solid var(--color-border);
    border-radius: 8px;
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

  .color-picker {
    display: flex;
    align-items: center;
    gap: 0.5rem;
  }

  .color-label {
    font-size: 0.75rem;
    color: var(--color-text-muted);
  }

  .color-options {
    display: flex;
    gap: 0.3rem;
  }

  .color-btn {
    width: 22px;
    height: 22px;
    border-radius: 50%;
    border: 2px solid transparent;
    cursor: pointer;
    transition: all 0.15s;
  }

  .color-btn:hover {
    transform: scale(1.15);
  }

  .color-btn.selected {
    border-color: var(--color-text-base);
    box-shadow: 0 0 8px rgba(168,85,247,0.4);
  }

  .form-actions {
    display: flex;
    gap: 0.5rem;
    margin-top: 0.25rem;
  }

  .form-actions .quantum-btn {
    padding: 0.5rem 1rem;
    font-size: 0.85rem;
    flex: 1;
  }

  .cancel-btn {
    padding: 0.5rem 1rem;
    font-size: 0.85rem;
    background: var(--color-surface-2);
    border: 1px solid var(--color-border);
    border-radius: var(--radius-button);
    color: var(--color-text-muted);
    cursor: pointer;
    font-weight: 600;
  }

  .cancel-btn:hover {
    border-color: var(--color-border-active);
  }

  .ai-btn {
    padding: 0.6rem;
    font-size: 0.85rem;
    font-weight: 600;
    background: linear-gradient(135deg, rgba(168,85,247,0.15), rgba(6,182,212,0.12));
    border: 1px solid var(--color-border-active);
    border-radius: var(--radius-button);
    color: var(--color-text-base);
    cursor: pointer;
    transition: all 0.2s;
  }

  .ai-btn:hover:not(:disabled) {
    background: linear-gradient(135deg, rgba(168,85,247,0.25), rgba(6,182,212,0.2));
    box-shadow: 0 0 12px rgba(168,85,247,0.2);
  }

  .ai-btn:disabled {
    opacity: 0.4;
    cursor: not-allowed;
  }

  .ai-error {
    font-size: 0.75rem;
    color: var(--color-danger);
    text-align: center;
  }

  .ai-tasks-preview {
    padding: 0.6rem;
    background: rgba(16, 185, 129, 0.06);
    border: 1px solid rgba(16, 185, 129, 0.25);
    border-radius: 8px;
    display: flex;
    flex-direction: column;
    gap: 0.35rem;
  }

  .ai-tasks-label {
    font-size: 0.7rem;
    font-weight: 600;
    color: var(--color-success);
    margin-bottom: 0.1rem;
  }

  .ai-task-item {
    display: flex;
    align-items: flex-start;
    gap: 0.35rem;
    font-size: 0.75rem;
  }

  .ai-task-num {
    color: var(--color-text-muted);
    font-family: var(--font-mono);
    font-size: 0.65rem;
    flex-shrink: 0;
    margin-top: 0.1rem;
  }

  .ai-task-body {
    flex: 1;
    display: flex;
    flex-direction: column;
    gap: 0.05rem;
  }

  .ai-task-title {
    color: var(--color-text-base);
    font-weight: 500;
  }

  .ai-task-desc {
    color: var(--color-text-muted);
    font-size: 0.65rem;
  }

  .ai-task-prio {
    flex-shrink: 0;
    font-size: 0.65rem;
  }

  .no-project {
    flex: 1;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: 3rem;
    gap: 0.5rem;
    color: var(--color-text-muted);
  }

  .big-icon {
    font-size: 3rem;
    opacity: 0.5;
  }

  @media (max-width: 768px) {
    .layout {
      flex-direction: column;
    }
  }
</style>
