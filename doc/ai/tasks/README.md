# Task Index & Numbering

## Numbering Scheme
- Tasks use identifiers `T###` (e.g., `T001`, `T002`).
- Folder naming pattern: `doc/ai/tasks/T###_<slug>/`.
- The task description **lives inside each folder’s `README.md`** (same content mirrored in `doc/ai/TASK.md`
  for compatibility) and may include extra helper files for that task only.
- Every `README.md` must link to:
  - Its plan folder under `doc/ai/plan/T###/` (and related subtask checklists) for execution detail.
  - Relevant commits, research notes, or supporting artifacts.
  - A Feedback section with open problems, outstanding questions, and learnings.

## Active Task
- Mark the active task as `Status = Active` in the log below so the current folder is obvious.
- Keep `doc/ai/TASK.md` synchronized with the active task’s `README.md`.

## Historical Log
| Task ID | Title | Status | Notes |
|---------|-------|--------|-------|
| T001 | Build the llm-agent-dock Matrix Builder | Completed | `doc/ai/tasks/T001_llm-agent-dock-matrix-builder/README.md`
| T002 | Validate llm-agent-dock Builds & Docker Access | Active | `doc/ai/tasks/T002_validate-builds-docker/README.md`

Update this table as tasks finish or new ones start. Always keep `doc/ai/TASK.md` aligned with the active task ID.
