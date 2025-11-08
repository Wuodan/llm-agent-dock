# Task T008 / Subtask S003 — Add Post-Task Retrospective Metrics

## Objective
Define how agents capture actual token usage, time spent, and estimate accuracy after each task/subtask, keeping the process lightweight.

## Deliverables
- Retro checklist/fields for task + subtask plans (e.g., “Actual token bucket”, “Estimate accuracy”).
- Guidance on acceptable precision (e.g., qualitative buckets vs. exact dashboards).
- Instructions for logging discrepancies + learnings.
- Checklist + Feedback updates.

## Flow
1. Review estimates defined in S001 and determine matching retro fields.
2. Decide on collection method (plan files, GitHub comments, etc.) with minimal overhead.
3. Draft example retro entries.
4. Coordinate with S002 so template updates embed these sections.
5. Commit `T008/S003: define post-task metrics` after checklist completion.

## Retro Field Definitions (v1)
| Field | Required | Guidance |
|-------|----------|----------|
| **Actual Token Bucket** | Task + subtask | Use same XS/XL buckets; add variance note (e.g., “Actual: L, Estimate: M, +1 bucket / +30%”).
| **Token Source & Confidence** | Task + subtask | Cite data source (`chat-export`, `model dashboard`, `manual estimate`) and mark confidence High/Med/Low.
| **Time Spent** | Task + subtask | Round to nearest 0.5 agent-hour or note calendar days; include blockers that inflated duration.
| **Estimate Accuracy Rating** | Task + subtask | Choose `On target` (within same bucket & ±20%), `Under`, or `Over`; explain in ≤2 sentences.
| **LLM Tier Used** | Task + subtask | Record actual tier(s); mention deviations from recommendation + reason (e.g., “Started lite, upgraded to standard for code review pass”).
| **Variance Drivers & Learnings** | Task + subtask | Bullet list capturing what caused the variance and how to prevent/replicate it. Link to research logs if needed.

Precision expectations:
- Buckets stay qualitative—avoid raw token counts unless already available (future automation will feed numbers).
- Time uses half-hour increments up to 4h, then round to whole hours/days.
- If actual tokens cross ≥1 bucket higher than estimate, add an escalation note to the GitHub issue.

## Example Retro Entry
```
Actual Token Bucket: L (estimate M) — +1 bucket / +25%; heavy docker-bake logs pushed us over.
Token Source & Confidence: Manual estimate from MCP prompts (Medium) pending dashboard export.
Time Spent: 5.5 agent-hours spread across 2 calendar days (waiting on GH org access).
Estimate Accuracy: Over — new BuildKit warnings triggered extra research.
LLM Tier Used: Standard ➜ Advanced for debugging (1 run) due to hallucinated Bake error output.
Variance Drivers & Learnings:
- Running smoke tests on both amd64 + arm64 doubled token use; document expectation in future tasks.
- Next time pre-cache Bake logs locally to limit re-prompts.
```

## Template Integration
- Task + subtask templates now list each retro field explicitly (Actual Bucket, Token Source, Time,
  Accuracy rating, Tier used, Variance drivers) so contributors can paste quick bullets without
  reinventing structure.
- Retro instructions reference acceptable precision (“nearest 0.5h” and bucket deltas) and remind
  agents to note GitHub issue escalation if variance ≥1 bucket.
- No new standalone doc needed; plan templates remain the single source of truth for retros.

## Checklist
- [x] Retro fields defined (token/time/accuracy).
- [x] Guidance on data sources + precision level documented.
- [x] Example retro entry drafted.
- [x] Feedback updated.
- [x] Commit `T008/S003: define post-task metrics`.

## Inputs & References
- Outputs from S001 & S002.
- `AGENTS.md` cost guardrails.

## Exit Criteria
- Retro process clearly described and ready for template integration.

## Feedback & Learnings
- **Open Problems**: Need lightweight script to pull per-thread token totals once MCP exposes API;
  backlog for Task T010.
- **Questions**: Is capturing agent-hours sufficient, or should we track wall-clock days separately
  per reviewer? TBD after first few retros.
- **Learnings**: Buckets + qualitative confidence keep retros short while still trendable.
