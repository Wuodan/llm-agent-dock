# Task T004 — Enforce Branch Workflow & Merge Discipline

Last updated: 2025-11-08T15:20Z by Codex

## Context
- Repository policy allows direct pushes and history edits on `development`, which conflicts with the hardened workflow expectations in AGENTS.md.
- Deliverables: documented branch naming + flow for tasks/subtasks, push/merge/force-push guidelines, and reusable completion checklists that agents can follow.
- Assumptions: task branches build off `development`; no CI changes required; instructions must stay tool-agnostic for future agents.

## Workflow Guardrails
1. Update this master checklist and each subtask checklist immediately after progress so hand-offs are recoverable.
2. Follow AGENTS.md planning requirements: reference plan folders in commits, keep Docker/build/test logs in plan docs, and avoid dumping chat logs.
3. Document any external research (e.g., Git workflow references) under the relevant subtask plan or `doc/ai/research/` with URLs and summaries.
4. Every subtask finishes with commit `T004/S###: short summary` (use the matching subtask index) plus Feedback entries in both subtask and task plans.

## Subtask Directory Map (T004)
| ID | Title | Status | Checklist |
|----|-------|--------|-----------|
| S1 | Branch workflow policy decisions | ☑ complete | `plan/subtask_S1_branch-policy/README.md` |
| S2 | Update AGENTS.md and related docs | ☑ complete (rev. 2) | `plan/subtask_S2_doc-updates/README.md` |
| S3 | Checklist + template propagation | ☑ complete | `plan/subtask_S3_checklists/README.md` |

## Master Checklist (T004)
- [x] S1 — Branch workflow policy decisions
- [x] S2 — Update AGENTS.md and related docs (commit prefix + branch policy captured)
- [x] S3 — Checklist + template propagation

## Progress Log (T004)
- 2025-11-08T15:15Z — Initialized task plan scaffolding and updated task index to mark T004 active.
- 2025-11-08T15:45Z — Completed S1 policy decisions; branching rules + merge/force-push guidance captured in subtask doc for downstream docs.
- 2025-11-08T16:00Z — Began S2; inserted branch workflow rules + merge expectations into AGENTS.md per S1 decisions.
- 2025-11-08T16:10Z — Finished S2; AGENTS.md now documents branch naming, push cadence, merge/deletion checks, and force-push policy.
- 2025-11-08T16:35Z — Requirement change: commit titles must carry task/subtask prefix (`T###/S###: ...`). Re-opening S2 for doc updates and starting S3 template edits.
- 2025-11-08T16:45Z — Revisions applied to AGENTS + legacy task docs to codify the `T###/S###` commit format; S2 considered complete again pending S3 template propagation.
- 2025-11-08T16:55Z — Completed S3 by updating task/subtask templates with the new commit-prefix reminders; branch workflow task ready for validation.

## References
- `AGENTS.md`
- `doc/ai/templates/task_plan_README.template.md`
- `doc/ai/templates/subtask_plan_README.template.md`

## Notes
- Decide whether merges happen via GitHub PRs or enforced local `git merge --no-ff` during S1.
- Capture any push/force-push troubleshooting tips (e.g., diverged branches) for future agents.
