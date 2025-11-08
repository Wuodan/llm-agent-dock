# Task T004 / Subtask S2 — Update AGENTS.md & Related Docs

## Objective
Propagate the approved branch workflow policies into AGENTS.md and any other contributor-facing docs that mention branching, merging, or commit practices.

## Deliverables
- Revised `AGENTS.md` describing branch naming, push cadence, merge method, and deletion rules.
- Any supplemental updates to task descriptions or README files referencing the workflow (link them here).
- Updated plan + Feedback section summarizing what changed and why.

## Flow
1. Pull finalized decisions from S1 and map each policy to the sections in AGENTS.md that need edits (workflow hardening, testing, commit/PR expectations).
2. Update AGENTS.md with concise instructions, ensuring they align with repository tone and cite required commands (e.g., `git merge --no-ff`).
3. Adjust other docs if they duplicate workflow guidance (e.g., root README, task index) and cross-link to AGENTS.md instead of duplicating text.
4. Run formatting/lint checks if applicable (Markdown lint manual review; no automated tests required but proofread links/paths).
5. Update plan checklist + Feedback; ensure research references (if any) are logged.
6. Commit `T004/S002: summary` once all checklist items complete.

## Documentation Changes
- Added a "Branch Workflow" subsection under `AGENTS.md` Workflow Hardening describing branch naming (`task/T###_<slug>`, `subtask/T###_S#_<slug>`), creation steps, push cadence, merge flow with `git merge --no-ff`, deletion verification, and force-push limits.
- Extended the Commit/PR expectations to remind contributors to log branch names and use local no-ff merges before deleting child branches.
- Confirmed README and task index do not currently repeat branching guidance, so no changes needed there.
- **2025-11-08**: Requirement update from user—commit titles must include task/subtask prefix `T###/S###:`. Updated `AGENTS.md` plus legacy task docs (T001–T003) to describe the new format and provide examples; templates will carry the reminder via S3.

## Checklist
- [x] Map S1 decisions to specific documentation sections needing updates.
- [x] Apply edits to AGENTS.md (and other docs, if needed) with consistent naming + flow instructions.
- [x] Self-review for clarity/formatting; capture summary in plan Feedback.
- [x] Document findings in Feedback.
- [x] Commit `T004/S002: summary`.

## Inputs & References
- `doc/ai/tasks/T004_branch-workflow-discipline/README.md`
- `doc/ai/tasks/T004_branch-workflow-discipline/plan/subtask_S1_branch-policy/README.md`
- `AGENTS.md`

## Exit Criteria
- All targeted docs mention the new workflow, references are updated, and plan feedback reflects completion.

## Feedback & Learnings
- **Open Problems**: Consider adding an automated lint (pre-commit or CI) to enforce the `T###/S###` prefix so reviewers don’t have to police it manually.
- **Questions**: For rare task-level commits without subtasks, should we require `S000` explicitly in AGENTS examples? (Currently documented but needs verification during validation.)
- **Learnings**: A short `T###/S###` prefix keeps commit subjects searchable without reintroducing long agent tags; AGENTS.md is now the single reference for both branching and commit policy.
