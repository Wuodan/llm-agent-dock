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
| S4 | Commit prefix lint enforcement | ☑ complete (lint v2) | `plan/subtask_S4_commit-lint/README.md` |

## Master Checklist (T004)
- [x] S1 — Branch workflow policy decisions
- [x] S2 — Update AGENTS.md and related docs (commit prefix + branch policy captured)
- [x] S3 — Checklist + template propagation
- [x] S4 — Commit prefix lint enforcement (python hook + .venv doc)

## Progress Log (T004)
- 2025-11-08T15:15Z — Initialized task plan scaffolding and updated task index to mark T004 active.
- 2025-11-08T15:45Z — Completed S1 policy decisions; branching rules + merge/force-push guidance captured in subtask doc for downstream docs.
- 2025-11-08T16:00Z — Began S2; inserted branch workflow rules + merge expectations into AGENTS.md per S1 decisions.
- 2025-11-08T16:10Z — Finished S2; AGENTS.md now documents branch naming, push cadence, merge/deletion checks, and force-push policy.
- 2025-11-08T16:35Z — Requirement change: commit titles must carry task/subtask prefix (`T###/S###: ...`). Re-opening S2 for doc updates and starting S3 template edits.
- 2025-11-08T16:45Z — Revisions applied to AGENTS + legacy task docs to codify the `T###/S###` commit format; S2 considered complete again pending S3 template propagation.
- 2025-11-08T16:55Z — Completed S3 by updating task/subtask templates with the new commit-prefix reminders; branch workflow task ready for validation.
- 2025-11-08T17:05Z — Added S4 subtask to implement commit-message lint + hook per user request; scope captured in new plan doc.
- 2025-11-08T17:20Z — Implemented `scripts/check-commit-message.sh`, tracked `githooks/commit-msg`, and documented hook setup/tests; awaiting final review + commit for S4.
- 2025-11-08T17:30Z — Completed S4 with docs + hook instructions and validated good/bad samples via the new script.
- 2025-11-08T17:45Z — Requirement update: lint must live outside product `scripts/` tree and leverage `.venv` Python; re-opening S4 to migrate hook + docs.
- 2025-11-08T17:55Z — Migrated lint to `devtools/check_commit_message.py`, updated hook + docs with `.venv` instructions, and revalidated good/bad samples.
- 2025-11-08T18:05Z — Final validation complete; documented outstanding ideas (CI commit-lint, hotfix branch prefix) in Feedback and preparing to close T004.

## References
- `AGENTS.md`
- `doc/ai/templates/task_plan_README.template.md`
- `doc/ai/templates/subtask_plan_README.template.md`

## Feedback & Learnings
- **Open Problems**: consider adding CI coverage for the commit-prefix lint (run `devtools/check_commit_message.py` in workflows) and evaluate whether rare hotfix work should use a reserved branch prefix.
- **Questions**: none outstanding; waiting on product owners if CI automation becomes priority.
- **Learnings**: separating product docs, contributor guides, and AI-specific instructions avoids user confusion and keeps AGENTS.md the single source of truth.
