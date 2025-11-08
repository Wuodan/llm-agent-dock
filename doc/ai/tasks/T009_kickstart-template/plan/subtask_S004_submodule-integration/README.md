# Task T009 / Subtask S004 — Submodule Integration & Wiring

## Objective
Document how to consume the workflow-ready template repo and keep instructions synchronized (with or without a submodule).

## Deliverables
- Submodule added at the agreed path.
- Documentation (in AGENTS) explaining how to fetch/update the template (submodule optional).
- Checklist + Feedback updates.

## Flow
1. After S001–S003, add the GitHub repo as a submodule (optional) or document how to fetch it externally.
2. Verify `.gitmodules`/path alignment if a submodule is used.
3. Update any references in this repo that point to the template folder or external repo.
4. Document maintenance steps (e.g., how to pull template updates manually or via submodule).
5. Commit `T009/S004: integrate template submodule` when complete.

## Notes
- Submodule lives at `submodules/workflow-ready-template`; initialization command documented in `AGENTS.md` along with
  the workflow for pulling upstream tags/branches and committing the pointer here.

## Checklist
- [x] Submodule (optional) path documented.
- [x] References/docs updated.
- [x] Feedback updated.
- [x] Commit `T009/S004: integrate template submodule`.

## Inputs & References
- GitHub template repo (once created).
- `AGENTS.md` instructions.

## Exit Criteria
- Submodule ready for use; contributors know how to update it.

## Feedback & Learnings
- **Open Problems**: None—the template repo is final; this repo currently references it externally (no submodule).
- **Questions**: None.
- **Learnings**: Documenting the submodule workflow directly in `AGENTS.md` keeps future agents from hunting through task plans for update commands.
