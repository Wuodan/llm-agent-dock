# Task Index & Numbering

## Numbering Scheme
- Tasks use identifiers `T###` (e.g., `T001`, `T002`).
- Folder naming pattern: `doc/ai/tasks/T###_<slug>/`.
- The task description **lives inside each folder’s `README.md`** and may include extra helper files for that task only.
- Every `README.md` must link to:
  - Its plan folder under `doc/ai/tasks/T###_<slug>/plan/` (and related subtask checklists) for execution detail.
  - Relevant commits, research notes, or supporting artifacts.
  - A Feedback section with open problems, outstanding questions, and learnings.

## Task Overview
| Task ID | Title | Status | Plan Folder | Notes |
|---------|-------|--------|-------------|-------|
| T001 | Build the llm-agent-dock Matrix Builder | Completed | `doc/ai/tasks/T001_llm-agent-dock-matrix-builder/plan/` | `doc/ai/tasks/T001_llm-agent-dock-matrix-builder/README.md`
| T002 | Validate llm-agent-dock Builds & Docker Access | Active | `doc/ai/tasks/T002_validate-builds-docker/plan/` | `doc/ai/tasks/T002_validate-builds-docker/README.md`

Update this table as tasks finish or new ones start. Mark exactly one row as **Active** so the current folder is obvious.

### Creating a New Task
1. Copy `doc/ai/templates/task_plan_README.template.md` to `doc/ai/tasks/T###_<slug>/plan/README.md` and
   fill in the placeholders.
2. For each subtask, copy `doc/ai/templates/subtask_plan_README.template.md` into a matching folder
   (`plan/subtask_S1_<slug>/README.md`, etc.). Keep the commit + feedback checklist items intact.
3. Link the new plan and subtask files inside the task README and update the table above.
