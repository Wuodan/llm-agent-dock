# Task T003 / Subtask S1 — Scope & Planning Alignment

## Objective
Stand up the planning scaffolding for T003, confirm scope boundaries, and outline the subtask execution path with live checklists + progress log entries.

## Deliverables
- Completed task-level plan (`plan/README.md`) populated with context, guardrails, checklists, progress log, and references.
- Subtask templates duplicated + tailored for S1–S4 with objectives, flows, and exit criteria.
- Updated `doc/ai/tasks/README.md` status row + plan link for T003.
- Feedback section documenting any clarifications or blockers discovered while planning.

## Flow
1. Read `doc/ai/tasks/T003_intensive-startup-tests/README.md` and prior task plans for precedent.
2. Copy templates into `plan/` and customize context, guardrails, checklist, and progress log entries.
3. Define subtask objectives/flows/deliverables in each subtask README, ensuring the commit requirement is explicit.
4. Update `doc/ai/tasks/README.md` to point to the new plan and mark T003 as Active with no “plan pending”.
5. Review the plan for completeness, fill in Feedback, and prepare commit message outline.
6. Commit `T003/S001: summary` once the checklist and Feedback are done.

## Checklist
- [x] Plan README context, guardrails, checklists, and progress log populated.
- [x] Subtask S1–S4 README files customized with objectives, flows, deliverables, and exit criteria.
- [x] Task index updated with T003 plan path + status confirmation.
- [x] Document findings in Feedback.
- [x] Commit `T003/S001: summary`.

## Inputs & References
- `doc/ai/tasks/T003_intensive-startup-tests/README.md`
- `doc/ai/tasks/T002_validate-builds-docker/plan/`
- `AGENTS.md`
- Planning templates under `doc/ai/templates/`

## Exit Criteria
- Task and subtask plan files fully populated, checklists reflecting current status, task index references updated, and Feedback section captures any planning discoveries.

## Feedback & Learnings
- **Open Problems**: Need to pick an approach for streaming stdout/stderr without blocking (likely `script`, `stdbuf`, or `pexpect` wrapper inside tests).
- **Questions**: Can we rely on placeholder API keys via env vars (e.g., `OPENAI_API_KEY=dummy`) without the CLIs attempting network calls?
- **Learnings**: T002 plans set a good precedent for subtask naming and plan structure—mirroring them keeps documentation consistent.
