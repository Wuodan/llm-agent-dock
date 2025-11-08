# Task T007 — Pilot GitHub-Issue Task Tracking

Last updated: 2025-11-08T14:31Z by Codex

## Context
- Experiment with shifting task briefs from repo-only markdown to canonical GitHub issues so async contributors can track work without cloning.
- Deliverables: (1) define how GitHub issues represent tasks (templates, labels, linking rules); (2) update `AGENTS.md` and planning templates so they reference the new issue-first flow with minimal duplication; (3) execute a single pilot by creating a real GitHub issue for T007 and wiring local docs to it; (4) document sync expectations + fallbacks for offline work.
- Assumptions: contributors retain repo access, GitHub issues remain source of truth for task briefs, local docs primarily point to GitHub plus track progress/checklists per AGENTS guardrails.

## Workflow Guardrails
1. Update every checklist in this plan immediately after progress; laptops should be resumable from checklist state.
2. Follow `AGENTS.md` rules: branch discipline, commit format `T007/S###: ...`, research logging for any MCP `brave-search`/`fetch` usage, and Feedback updates at completion.
3. Capture any GitHub/product research URLs in `doc/ai/tasks/T007_github-issues-pilot/plan/research.md` (create if needed) or in the relevant subtask README Feedback section.
4. Each subtask finishes with documentation + checklist updates + commit `T007/S###: short summary` (use `S000` only for task-wide actions that span multiple subtasks).

## Subtask Directory Map (T007)
| ID | Title | Status | Checklist |
|----|-------|--------|-----------|
| S001 | Define GitHub issue planning model | ☐ pending | `plan/subtask_S001_issue-model/README.md`
| S002 | Update contributor guidance + templates | ☐ pending | `plan/subtask_S002_guidance-update/README.md`
| S003 | Run pilot issue + link local docs | ☐ pending | `plan/subtask_S003_pilot-sync/README.md`

## Master Checklist (T007)
- [ ] S001 — Define GitHub issue planning model
- [ ] S002 — Update contributor guidance + templates
- [ ] S003 — Run pilot issue + link local docs

## Progress Log (T007)
- 2025-11-08T14:31Z — Created task plan scaffold and initial checklist entries (Codex).

## References
- `doc/ai/tasks/T007_github-issues-pilot/README.md`
- Repository workflow guardrails in `AGENTS.md`
- Task planning templates in `doc/ai/templates/`

## Notes
- Keep an eye on how subtasks will mirror GitHub issues in the future; capture open questions in Feedback sections for later iterations.
