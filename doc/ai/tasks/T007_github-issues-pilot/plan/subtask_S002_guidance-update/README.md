# Task T007 / Subtask S002 — Update Contributor Guidance + Templates

## Objective
Revise `AGENTS.md` and the planning templates so contributors follow the new GitHub-issue-centric workflow without duplicating task briefs.

## Deliverables
- Updated `AGENTS.md` instructions describing when/how to create GitHub issues for tasks and how local docs should reference them.
- Adjusted task & subtask plan templates that explicitly call for GitHub issue links.
- Notes on any impacts to commit/branch workflow or task catalog maintenance.
- Updated plan checklist + Feedback entry.

## Flow
1. Summarize policy changes coming out of S001 and identify required doc edits.
2. Edit `AGENTS.md` plus relevant templates, ensuring instructions stay scoped per audience.
3. Verify Markdown structure (wrap at ~100 chars, heading case) per repository style.
4. Update Feedback with outstanding questions or follow-ups.
5. Commit `T007/S002: refresh guidance for gh issues` once complete.

## Checklist
- [x] Captured required policy changes from S001.
- [x] Edited `AGENTS.md` to reflect GitHub issue workflow.
- [x] Updated task/subtask plan templates to link GitHub issues.
- [x] Documented findings in Feedback.
- [x] Commit `T007/S002: refresh guidance for gh issues`.

## Inputs & References
- Output from Subtask S001.
- `AGENTS.md`, `doc/ai/templates/task_plan_README.template.md`, `doc/ai/templates/subtask_plan_README.template.md`.

## Exit Criteria
- All relevant docs updated, checklist checked, Feedback section notes outstanding work (if any).

## Feedback & Learnings
- **Open Problems**: Need to actually create the new `task` and `status:*` labels in GitHub—documented expectations assume they exist.
- **Questions**: Should we enforce GitHub issue comment cadence via automation (e.g., linting for missing links) or rely on plan reviews?
- **Learnings**: Existing docs already separated user- vs contributor-facing content, so adding GitHub issue guidance fit naturally under Workflow Hardening + templates.
