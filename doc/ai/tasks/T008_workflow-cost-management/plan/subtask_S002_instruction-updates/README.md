# Task T008 / Subtask S002 — Update Templates & AGENTS Instructions

## Objective
Embed the new estimation attributes into the task/subtask plan templates and document the workflow changes in `AGENTS.md`, including when to escalate cost concerns.

## Deliverables
- Updated `doc/ai/templates/task_plan_README.template.md` and `doc/ai/templates/subtask_plan_README.template.md`.
- Revised `AGENTS.md` guidance covering estimate fields, tag usage, and approval thresholds.
- Notes explaining how agents should record estimates during planning sessions.
- Updated checklist + Feedback entries.

## Flow
1. Based on S001 outputs, map each attribute to a location in the templates.
2. Edit templates + AGENTS.md, keeping instructions concise (≤100 chars per line where possible).
3. Verify examples/reference text for the new fields.
4. Document any follow-up needs (e.g., future automation) in Feedback.
5. Commit `T008/S002: refresh cost planning templates` when done.

## Template & Instruction Updates (2025-11-08)
- Added `## Estimate Snapshot` block to the task + subtask plan templates with required fields:
  token bucket, complexity level, ≤3 work-type tags, LLM tier, confidence, dependencies/risks.
- Added `## Retro Metrics` placeholders so retros capture actual bucket, time spent, accuracy deltas,
  tier actually used, and learnings. (S003 will define formatting references but placeholders exist.)
- Updated subtask checklist to include “Estimate Snapshot populated” entry and Flow reminder to
  refresh the snapshot when scope changes.
- Extended `AGENTS.md` Workflow Hardening guidance with Estimate Snapshot + Retro Metrics bullets,
  tying them to the existing ≥5%/bucket escalation rule.
- Highlighted tag catalog plus XS–XL buckets in each template to keep instructions discoverable.

## Planning Notes
- Planners should fill the Estimate Snapshot immediately after writing Context to catch scope drift
  early; revisit after research spikes or GitHub issue updates.
- Retro Metrics placeholders ensure we have a consistent landing zone for S003 outputs and keep
  contributors from forgetting to log actuals.

## Checklist
- [x] Templates updated with estimate/retro sections.
- [x] `AGENTS.md` instructions extended.
- [x] Examples + references validated.
- [x] Feedback updated.
- [x] Commit `T008/S002: refresh cost planning templates`.

## Inputs & References
- Output from S001.
- Existing templates + guardrails.

## Exit Criteria
- Contributors following the templates will naturally capture estimates and know when to seek approval.

## Feedback & Learnings
- **Open Problems**: Need automation (future task) to ingest actual token usage so Retro fields can
  include real counts, not just buckets.
- **Questions**: Should Estimate Snapshot live ahead of Context to force completion sooner? Evaluate
  after a couple of tasks.
- **Learnings**: Embedding tier guidance directly in templates reduces AGENT flipping when planning.
