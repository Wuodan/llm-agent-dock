# Task T007 — Pilot GitHub-Issue Task Tracking

Last updated: 2025-11-08T14:57Z by Codex

## Context
- Experiment with shifting task briefs from repo-only markdown to canonical GitHub issues so async contributors can track work without cloning.
- Deliverables: (1) define how GitHub issues represent tasks (templates, labels, linking rules); (2) update `AGENTS.md` and planning templates so they reference the new issue-first flow with minimal duplication; (3) execute a single pilot by creating a real GitHub issue for T007 and wiring local docs to it; (4) document sync expectations + fallbacks for offline work.
- Assumptions: contributors retain repo access, GitHub issues remain source of truth for task briefs, local docs primarily point to GitHub plus track progress/checklists per AGENTS guardrails.

## Workflow Guardrails
1. Update every checklist in this plan immediately after progress; laptops should be resumable from checklist state.
2. Follow `AGENTS.md` rules: branch discipline, commit format `T007/S###: ...`, research logging for any MCP `brave-search`/`fetch` usage, and Feedback updates at completion.
3. Capture any GitHub/product research URLs in `doc/ai/tasks/T007_github-issues-pilot/plan/research.md` (create if needed) or in the relevant subtask README Feedback section.
4. Each subtask finishes with documentation + checklist updates + commit `T007/S###: short summary` (use `S000` only for task-wide actions that span multiple subtasks).
5. Mirror every Progress Log entry to [GitHub issue #1](https://github.com/Wuodan/llm-agent-dock/issues/1); if offline, paste the pending comment text into the plan and post it later.

## Subtask Directory Map (T007)
| ID | Title | Status | Checklist |
|----|-------|--------|-----------|
| S001 | Define GitHub issue planning model | ☑ done | `plan/subtask_S001_issue-model/README.md`
| S002 | Update contributor guidance + templates | ☑ done | `plan/subtask_S002_guidance-update/README.md`
| S003 | Run pilot issue + link local docs | ☑ done | `plan/subtask_S003_pilot-sync/README.md`

## Master Checklist (T007)
- [x] S001 — Define GitHub issue planning model
- [x] S002 — Update contributor guidance + templates
- [x] S003 — Run pilot issue + link local docs

## Progress Log (T007)
- 2025-11-08T14:31Z — Created task plan scaffold and initial checklist entries (Codex).
- 2025-11-08T14:33Z — Drafted GitHub issue template plus label/linking policy (S001).
- 2025-11-08T14:36Z — Committed S001 deliverables and recorded GitHub issue model references.
- 2025-11-08T14:38Z — Updated AGENTS + plan templates with GitHub issue workflow (S002 in progress).
- 2025-11-08T14:39Z — Committed S002 guidance changes and logged outstanding label/automation questions.
- 2025-11-08T14:42Z — Created GitHub issue #1, seeded status labels, and mirrored prior log entries on GitHub (S003).
- 2025-11-08T14:43Z — Linked local docs to issue #1 and documented sync workflow (S003 complete).
- 2025-11-08T14:57Z — Closed GitHub issue #1, flipped labels to `status:completed`, and marked T007 as finished in the task catalog.
- 2025-11-08T15:31Z — Added session hand-off guardrail (no token impact; compliance-only reminder) per owner request.

## References
- `doc/ai/tasks/T007_github-issues-pilot/README.md`
- GitHub issue #1: https://github.com/Wuodan/llm-agent-dock/issues/1
- Repository workflow guardrails in `AGENTS.md`
- Task planning templates in `doc/ai/templates/`

## Notes
- Keep an eye on how subtasks will mirror GitHub issues in the future; capture open questions in Feedback sections for later iterations.
