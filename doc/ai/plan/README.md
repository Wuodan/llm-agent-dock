# Planning Index

Each task keeps its own plan under `doc/ai/plan/T###/`. The current structure is:

| Task | Status | Plan Root |
|------|--------|-----------|
| T002 | Active | `doc/ai/plan/T002/README.md` |
| T001 | Completed | `doc/ai/plan/T001/README.md` |

## Usage
- When kicking off a new task `T###`, create `doc/ai/plan/T###/README.md` plus one subfolder per subtask (e.g., `subtask_S1_planning`).
- Update only the plan files inside the corresponding task folder; never overwrite another task’s plan.
- Keep this index in sync so future agents can quickly find the latest active plan.

Refer to `AGENTS.md` for repository-wide workflow expectations.
