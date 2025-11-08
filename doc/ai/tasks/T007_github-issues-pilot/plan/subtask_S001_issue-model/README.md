# Task T007 / Subtask S001 — Define GitHub Issue Planning Model

## Objective
Design a lightweight yet explicit model for representing llm-agent-dock tasks as GitHub issues, including metadata, labels, and linking strategy back to repo docs.

## Deliverables
- Draft GitHub issue template (or updates to existing templates) capturing task context, plan links, and status fields.
- Proposed label taxonomy / naming conventions for tracking task lifecycle.
- Documentation of how local task folders reference the canonical GitHub issue without duplicating content.
- Updated plan checklist + Feedback section.

## Flow
1. Review current task docs plus GitHub issue templates/labels in the repo or org.
2. Identify required metadata fields (status, owner, links) and draft template + label mapping.
3. Document linking policy between GitHub issues and local `doc/ai/tasks/T###_*` folders.
4. Record decisions + open questions in this subtask’s Feedback.
5. Commit `T007/S001: define github issue model` once checklist items are complete.

## Checklist
- [x] Audited existing issue templates/labels.
- [x] Authored or updated GitHub issue template draft.
- [x] Defined label + linking policy and documented locally.
- [x] Documented findings in Feedback.
- [x] Commit `T007/S001: define github issue model`.

## Inputs & References
- `doc/ai/tasks/T007_github-issues-pilot/README.md`
- `AGENTS.md` workflow expectations.
- Existing `.github/ISSUE_TEMPLATE` files (if present).

## Exit Criteria
- GitHub issue model documented, reviewed against checklist, Feedback updated with open questions.

## Feedback & Learnings
- **Open Problems**: Need to add the `task` + `status:*` labels inside GitHub once permissions confirmed; automation for label flips could come later.
- **Questions**: Should we allow multiple simultaneous `status:*` labels for edge cases (e.g., Active + Blocked), or enforce the single-label rule defined here?
- **Learnings**: No prior issue templates existed, so mirroring the repo plan requires a form that mandates links + sync plans to prevent documentation drift.
