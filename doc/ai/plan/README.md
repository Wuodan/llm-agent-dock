# llm-agent-dock Execution Plan

Last updated: 2025-11-08T02:30Z by Codex

## Context
- Build a reusable, multi-arch Docker image matrix combining base OS variants with agentic developer tools.
- Deliverables: parameterized `Dockerfile`, `docker-bake.hcl` matrix, helper scripts, smoke tests, and synced documentation.
- Constraints: follow AGENTS.md conventions (scripts foldering, planning history, commit naming).

## Workflow Guardrails
1. Keep this plan and each subtask checklist up to date after every change.
2. Before implementing: review the relevant subtask doc, note prerequisites, and mark checklist items as work progresses.
3. After completing a subtask: update its **Feedback** section, mark its checklist complete, and record progress in the log below.
4. For agent installer details, research official instructions; if missing, use MCP `brave-search` followed by `fetch`, and summarize findings in the subtask doc.
5. Keep user-facing docs (e.g., `README.md`) focused on end users; park contributor/process notes in this plan or `AGENTS.md`.
6. Every subtask finishes with two required actions: update planning docs and make a commit `[codex][subtask-name]: summary`.

## Subtask Directory Map
| ID | Title | Status | Checklist |
|----|-------|--------|-----------|
| S1 | Planning & Scaffolding | ✅ complete | `doc/ai/plan/subtask_S1_planning/README.md` |
| S2 | Parameterized Dockerfile | ✅ complete | `doc/ai/plan/subtask_S2_dockerfile/README.md` |
| S3 | Matrix & Scripts | ✅ complete | `doc/ai/plan/subtask_S3_matrix/README.md` |
| S4 | Smoke Tests | ✅ complete | `doc/ai/plan/subtask_S4_tests/README.md` |
| S5 | Documentation & Polish | ✅ complete | `doc/ai/plan/subtask_S5_docs/README.md` |

## Master Checklist
- [x] Establish planning structure (S1).
- [x] Implement parameterized Dockerfile with agent installers (S2).
- [x] Author matrix build configs and helper scripts (S3).
- [x] Create smoke tests and wire into scripts (S4).
- [x] Finalize documentation, extension guides, and sync references (S5).

## Dependencies & Flow
1. **S2** depends on the scaffolding from **S1**.
2. **S3** consumes Dockerfile outputs; scripts expect build args defined in S2.
3. **S4** needs runnable images from S2/S3.
4. **S5** references artifacts from all earlier subtasks.

## Progress Log
- 2025-11-08T02:03Z — Initial roadmap drafted (S1 kick-off).
- 2025-11-08T02:15Z — Plan reorganized with per-subtask checklists and guardrails (S1 complete).
- 2025-11-08T02:30Z — README refocused on users; plan + subtasks updated to drop legacy references.
- 2025-11-08T02:43Z — S2 complete: parameterized Dockerfile added; sample build command documented (docker socket access pending).
- 2025-11-08T02:50Z — S3 complete: Bake matrix + helper scripts landed; bake --print validated.
- 2025-11-08T02:53Z — S4 complete: Bats smoke tests + helper added; test script now guides Bats setup.
- 2025-11-08T02:55Z — S5 complete: README refreshed with config/build/test guidance; planning docs finalized.
