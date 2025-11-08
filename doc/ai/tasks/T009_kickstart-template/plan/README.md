# Task T009 — Project Kickstart Template

Last updated: 2025-11-08T17:44Z by Codex

## Context
- We want to spin up a reusable template repo that captures our workflow best practices without project-specific details.
- Task includes interactive naming/description decisions, submodule placement, and authoring lightweight README/AGENTS content tailored for kickstart scenarios.
- Template must instruct future agents/users how to turn the scaffold into a real project (create README, merge AGENTS, etc.).

## GitHub Issue
- Not yet created (create via `.github/ISSUE_TEMPLATE/task.yml` once scope approved and naming decisions made).
- Expected branches: `task/T009_kickstart-template` plus subtasks as needed.

## Workflow Guardrails
1. Handle naming + repo description interactively with the user before creating files.
2. No empty directories—only commit files that carry instructions or necessary configs.
3. Keep template instructions concise but actionable for agents that support AGENTS.md; mirror essentials in README for agents that don’t.
4. Submodule path decision is part of the task—capture reasoning in plan logs.

## Subtask Directory Map (T009)
| ID | Title | Status | Checklist |
|----|-------|--------|-----------|
| S001 | Repo naming & description alignment | ☐ pending | `plan/subtask_S001_repo-naming/README.md`
| S002 | Template structure & contents | ☐ pending | `plan/subtask_S002_template-structure/README.md`
| S003 | Author README + AGENTS kickstart flow | ☐ pending | `plan/subtask_S003_instruction-authoring/README.md`
| S004 | Submodule integration & wiring | ☐ pending | `plan/subtask_S004_submodule-integration/README.md`

## Master Checklist (T009)
- [ ] S001 — Repo naming & description alignment
- [ ] S002 — Template structure & contents
- [ ] S003 — Author README + AGENTS kickstart flow
- [ ] S004 — Submodule integration & wiring

## Progress Log (T009)
- 2025-11-08T17:44Z — Drafted task plan scaffold pending naming discussion.

## References
- T008 outputs (workflow guardrails) for reuse.
- Existing AGENTS.md / README patterns from this repo.

## Notes
- Leave actual repo creation + submodule addition until S001 decides the name/path.
