# Task T009 — Project Kickstart Template

Last updated: 2025-11-08T19:30Z by Codex

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
3. Keep template instructions concise but actionable for AGENTS-aware agents; README content can summarize but does not need to duplicate AGENTS.md.
4. Submodule path decision is part of the task—capture reasoning in plan logs.

## Subtask Directory Map (T009)
| ID | Title | Status | Checklist |
|----|-------|--------|-----------|
| S001 | Repo naming & description alignment | ☑ done | `plan/subtask_S001_repo-naming/README.md`
| S002 | Template structure & contents | ☑ done | `plan/subtask_S002_template-structure/README.md`
| S003 | Author README + AGENTS kickstart flow | ☑ done | `plan/subtask_S003_instruction-authoring/README.md`
| S004 | Submodule integration & wiring | ☐ pending | `plan/subtask_S004_submodule-integration/README.md`

## Master Checklist (T009)
- [x] S001 — Repo naming & description alignment
- [x] S002 — Template structure & contents
- [x] S003 — Author README + AGENTS kickstart flow
- [ ] S004 — Submodule integration & wiring

## Progress Log (T009)
- 2025-11-08T17:44Z — Drafted task plan scaffold pending naming discussion.
- 2025-11-08T18:06Z — Completed S001: selected repo name `workflow-ready-template`, description "Kickstarts new repos with the documented AGENTS workflow baked in.", and submodule path `submodules/workflow-ready-template` to keep its Git nature obvious.
- 2025-11-08T18:26Z — Completed S002: locked the initial template file map (README, AGENTS, doc/ai/tasks catalog, plan templates, `.gitignore`, and `.github/ISSUE_TEMPLATE/task.yml`) and documented the decision to stay documentation-first for now.
- 2025-11-08T18:54Z — Initial S003 draft (later replaced): added README, AGENTS kickstart notice, AGENTS reference, task catalog scaffold, and supporting templates inside the `workflow-ready-template` submodule.
- 2025-11-08T19:30Z — Reworked S003 per user feedback: replaced the human README instructions, removed AGENTS.reference, and copied the full AGENTS guardrails minus tech-specific sections into the submodule.
- 2025-11-08T20:05Z — Updated template README per latest guidance: split flows (new project vs. existing project), documented `.venv` prerequisite, tarball commands, and the “help me update and complete AGENTS.md” prompt.
- 2025-11-08T20:24Z — Simplified template README per user request (no tables, concise directions) and scrubbed `llm-agent-dock` references from the issue template.

## References
- T008 outputs (workflow guardrails) for reuse.
- Existing AGENTS.md / README patterns from this repo.

## Notes
- Submodule will live at `submodules/workflow-ready-template`; wire it up during S004 after the repo exists.
