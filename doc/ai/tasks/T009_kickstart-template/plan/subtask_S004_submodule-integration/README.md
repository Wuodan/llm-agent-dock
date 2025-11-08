# Task T009 / Subtask S004 — Submodule Integration & Wiring

## Objective
Add the new template repository as a git submodule in this project, ensure instructions reference it, and describe how to keep it synchronized.

## Deliverables
- Submodule added at the agreed path.
- Documentation (in AGENTS) explaining how to initialize/update the template.
- Checklist + Feedback updates.

## Flow
1. After S001–S003, add the GitHub repo as a submodule (once created and accessible).
2. Verify `.gitmodules` and path alignment with plan decisions.
3. Update any references in this repo that point to the template folder.
4. Document maintenance steps (e.g., when to pull submodule updates).
5. Commit `T009/S004: integrate template submodule` when complete.

## Notes
- Submodule lives at `submodules/workflow-ready-template`; initialization command documented in `AGENTS.md` along with
  the workflow for pulling upstream tags/branches and committing the pointer here.

## Checklist
- [x] Submodule added + initialized.
- [x] References/docs updated.
- [x] Feedback updated.
- [ ] Commit `T009/S004: integrate template submodule`.

## Inputs & References
- GitHub template repo (once created).
- `AGENTS.md` instructions.

## Exit Criteria
- Submodule ready for use; contributors know how to update it.

## Feedback & Learnings
- **Open Problems**: None—the template repo is now final per user direction.
- **Questions**: None.
- **Learnings**: Documenting the submodule workflow directly in `AGENTS.md` keeps future agents from hunting through task plans for update commands.
