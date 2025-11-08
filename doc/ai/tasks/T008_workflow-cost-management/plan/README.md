# Task T008 — Workflow Cost Management Additions & Improvements

Last updated: 2025-11-08T18:21Z by Codex

## Context
- We want every task/subtask plan to estimate cost, complexity, and work-type tags so token-heavy efforts are visible early.
- Need lightweight post-task tracking (actuals, accuracy) to calibrate future estimates without bloating the workflow.
- Need a shared workflow cost audit document (`doc/ai/workflow/workflow_cost_audit.md`) that lists current steps, their expected token/time footprint, and candidates for future optimization (inputs for Task C).
- Scope deliberately focuses on process/doc updates and the first version of the audit doc; automation/MCP integrations remain out of scope (feed into later tasks).

## GitHub Issue
- [Issue #2](https://github.com/Wuodan/llm-agent-dock/issues/2)
- Current label: `status:completed` (set after `T008/S000` merge on 2025-11-08). Historical flow: proposed → active → completed.
- Planned/used branches: `task/T008_workflow-cost-management` plus `subtask/T008_S00{1-4}_<slug>`.

## Workflow Guardrails
1. Keep token-awareness additions lightweight—prefer short estimate fields vs. long prose.
2. Record any external research (e.g., token-metric references) under this plan’s subtasks or `doc/ai/workflow/workflow_cost_audit.md` as appropriate.
3. Ensure every new template/guardrail includes instructions about when to escalate cost concerns (ties into the 5% approval rule added in T007).
4. For each subtask, end with the usual checklist + commit `T008/S###: short summary`; mirror Progress Log updates to the future GitHub issue once created.

## Subtask Directory Map (T008)
| ID | Title | Status | Checklist |
|----|-------|--------|-----------|
| S001 | Define estimation attributes & taxonomies | ☑ complete | `plan/subtask_S001_estimation-fields/README.md`
| S002 | Update templates & AGENTS.md instructions | ☑ complete | `plan/subtask_S002_instruction-updates/README.md`
| S003 | Add post-task retrospective metrics | ☑ complete | `plan/subtask_S003_retros-metrics/README.md`
| S004 | Draft workflow cost audit doc | ☑ complete | `plan/subtask_S004_workflow-audit/README.md`

## Master Checklist (T008)
- [x] S001 — Define estimation attributes & taxonomies
- [x] S002 — Update templates & AGENTS.md instructions
- [x] S003 — Add post-task retrospective metrics
- [x] S004 — Draft workflow cost audit doc

## Progress Log (T008)
- 2025-11-08T17:29Z — Drafted T008 plan scaffold and subtask structure (Codex).
- 2025-11-08T18:05Z — Completed S001 attribute catalog + guidance on branch `subtask/T008_S001_estimation-fields` (Codex).
- 2025-11-08T18:14Z — Embedded Estimate Snapshot + Retro placeholders in templates and AGENTS per S002 on branch `subtask/T008_S002_instruction-updates` (Codex).
- 2025-11-08T18:16Z — Defined retro fields, precision guidance, and example entries on branch `subtask/T008_S003_retros-metrics` (Codex).
- 2025-11-08T18:19Z — Drafted workflow cost audit doc + backlog on branch `subtask/T008_S004_workflow-audit` (Codex).
- 2025-11-08T18:21Z — Merged `task/T008_workflow-cost-management` into `development` via `T008/S000` commit (Codex).

## References
- `AGENTS.md` cost guardrails.
- `doc/ai/templates/task_plan_README.template.md` and `doc/ai/templates/subtask_plan_README.template.md`.
- Planned audit doc: `doc/ai/workflow/workflow_cost_audit.md`.

## Notes
- Token tracking automation is deferred to future tasks (likely Task C). Document placeholders for where real metrics would plug in later.
