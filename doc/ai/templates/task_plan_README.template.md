# Task TXXX — <short title>

Last updated: <ISO8601 timestamp> by <author>

## Context
- Summarize why this task exists.
- Enumerate primary goals/deliverables.
- Capture environment constraints or assumptions.

## Estimate Snapshot
- **Token Bucket**: XS (<10k), S (10–25k), M (25–60k), L (60–120k), XL (>120k); include 1-line rationale.
- **Complexity Level (1–5)**: cite triggers (e.g., multi-file, cross-repo, heavy research).
- **Work-Type Tags**: up to three from `docs`, `code`, `research`, `ops`, `infra`, `testing`, `automation`,
  `planning`, `integration`, `data`, `runtime` (add new ones sparingly and document in Feedback).
- **LLM Tier Recommendation**: `lite`, `standard`, `advanced`, or `specialized`, plus fallback and reason.
- **Confidence**: High / Medium / Low; highlight unknowns if Medium or Low.
- **Dependencies / Sequencing** *(optional)*: blocking tasks, approvals, or env setup.
- **Risk Hotspots** *(optional)*: security, availability, or reviewer considerations.
- Update the snapshot whenever scope changes or token projections shift ≥1 bucket (≈≥5% budget hit).

## GitHub Issue
- Link to the GitHub issue created from `.github/ISSUE_TEMPLATE/task.yml`.
- Record the current `status:*` label + assignee, and note when to update it.
- List the task + subtask branch names so reviewers can jump to history quickly.

## Workflow Guardrails
1. Explain how checklists/progress logs must be updated.
2. Reference AGENTS.md rules that apply.
3. Specify any research logging expectations.
4. Remind contributors to finish each subtask with documentation and commit `T###/S###: short summary` (use `S000` for task-level commits).
5. Every time you add a Progress Log entry, mirror the same summary as a GitHub issue comment (queue it locally if offline).

## Retro Metrics (fill after completion)
- **Actual Token Bucket**: XS/S/M/L/XL plus variance (e.g., “Actual: L vs. Estimate: M, +1 bucket / +30%”).
- **Token Source & Confidence**: `chat-export`, `dashboard`, or manual estimate + High/Med/Low confidence.
- **Time Spent**: nearest 0.5 agent-hour (or list calendar days) plus major blockers.
- **Estimate Accuracy Rating**: `On target`, `Under`, or `Over` with ≤2 sentence rationale.
- **LLM Tier Used**: actual tier(s) and why it differed from the recommendation (if applicable).
- **Variance Drivers & Learnings**: bullets noting what increased/decreased cost and how to act on it.
- Escalate in the Progress Log + GitHub issue if variance ≥1 bucket or confidence drops to Low.
- Leave placeholder text until the task/subtask finishes; populate within 1 working session.

## Subtask Directory Map (TXXX)
| ID | Title | Status | Checklist |
|----|-------|--------|-----------|
| S1 | <subtask 1> | ☐ pending | `plan/subtask_S1_<slug>/README.md` |
| S2 | ... | ... | ... |

## Master Checklist (TXXX)
- [ ] S1 — <subtask 1>
- [ ] S2 — ...

## Progress Log (TXXX)
- YYYY-MM-DDThh:mmZ — <entry> (mirror to GitHub issue comments)

## References
- Link to related tasks, research docs, etc.

## Notes
- Include reminders, blockers, or links to supporting artifacts.
