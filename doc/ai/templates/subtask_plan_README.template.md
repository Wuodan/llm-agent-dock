# Task TXXX / Subtask S? — <subtask title>

## Objective
Describe the singular goal for this subtask.

## Estimate Snapshot
- Token Bucket: XS (<10k), S (10–25k), M (25–60k), L (60–120k), XL (>120k); note assumptions.
- Complexity Level (1–5): explain triggers (e.g., multi-file, novel design, coordination).
- Work-Type Tags (≤3): choose from `docs`, `code`, `research`, `ops`, `infra`, `testing`, `automation`,
  `planning`, `integration`, `data`, `runtime`.
- LLM Tier Recommendation: `lite`, `standard`, `advanced`, or `specialized`; cite why and fallback.
- Confidence: High / Medium / Low; list blockers when Medium/Low.
- Dependencies / Risk Hotspots *(optional)*: approvals, sequencing, reviewers, token spikes.
- Update this block whenever scope or estimates shift ≥1 token bucket.

## Deliverables
- Bullet list of artifacts required.
- Include “Updated plan + Feedback section” if applicable.
- Reference the parent GitHub issue comment or checklist update that mirrors this work.

## Flow
1. Step-by-step actions (call out when to refresh the Estimate Snapshot if scope changes).
2. Include explicit reminder to run required tests.
3. Note when to leave a GitHub issue comment so remote collaborators see the same progress update.
4. End with “Commit `T###/S###: short summary` once all checklist items complete.”

## Checklist
- [ ] Estimate Snapshot populated (token bucket, complexity, tags, tier, confidence).
- [ ] Requirement 1.
- [ ] Requirement 2.
- [ ] Document findings in Feedback.
- [ ] Mirrored update in the GitHub issue comments.
- [ ] Commit `T###/S###: short summary`.

## Inputs & References
- Link to parent task README, the GitHub issue, and other supporting docs.

## Exit Criteria
- State what must be true before moving on (e.g., checklist checked, tests passing, Feedback updated, GitHub issue comment posted).

## Retro Metrics (fill after completion)
- Actual Token Bucket: XS/S/M/L/XL plus variance note (e.g., “Actual S vs. Estimate XS, +1 bucket”).
- Token Source & Confidence: `chat-export`, `dashboard`, or manual estimate + confidence rating.
- Time Spent: nearest 0.5 agent-hour (note days if work was spread out) and blockers.
- Estimate Accuracy Rating: `On target`, `Under`, or `Over` with ≤2 sentence rationale.
- LLM Tier Used: record deviations and why tier upgrades/downgrades happened.
- Variance Drivers & Learnings: bullet list for future planners; link to research logs if helpful.
- Populate within one working session after completion; escalate if variance ≥1 bucket.

## Feedback & Learnings
- **Open Problems**: _TBD_
- **Questions**: _TBD_
- **Learnings**: _TBD_
