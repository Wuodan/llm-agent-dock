# Planning Index

Planning artifacts now live alongside their tasks (see `doc/ai/tasks/T###_<slug>/plan/`). This legacy
path remains as a convenience pointer.

| Task | Status | Plan Root |
|------|--------|-----------|
| T002 | Active | `doc/ai/tasks/T002_validate-builds-docker/plan/README.md` |
| T001 | Completed | `doc/ai/tasks/T001_llm-agent-dock-matrix-builder/plan/README.md` |

## Usage
- When kicking off a new task `T###`, create `doc/ai/tasks/T###_<slug>/plan/README.md` plus one subfolder per subtask (e.g., `subtask_S1_planning`).
- Update only the files inside that task’s `plan/` directory; never overwrite another task’s plan.
- Keep this index in sync so future agents can quickly find the latest active plan.

Refer to `AGENTS.md` for repository-wide workflow expectations.
