# Task T008 / Subtask S004 — Draft Workflow Cost Audit Doc

## Objective
Create `doc/ai/workflow/workflow_cost_audit.md`, summarizing the current workflow steps, their expected token/time footprint, and candidates for future optimization (input to Task C).

## Deliverables
- New audit document with sections for planning, branching, documentation, reviews, etc.
- Qualitative or quantitative cost estimates per step (even if rough).
- Highlighted “potential savings” list feeding into future tasks.
- Updated checklist + Feedback notes.

## Flow
1. Enumerate major workflow steps from `AGENTS.md`, plan templates, and observed practice.
2. For each, estimate relative token usage/time (e.g., Low/Med/High, or bucket ranges if available).
3. Capture notes about tooling/offload ideas to revisit in Task C.
4. Store the doc at `doc/ai/workflow/workflow_cost_audit.md` and link it from T008 plan.
5. Commit `T008/S004: publish workflow cost audit` after checklist completion.

## Audit Outline (2025-11-08)
- Document now tracks methodology/buckets, a 9-step workflow catalog, detailed notes per phase, a
  potential-savings backlog, and data-gap next steps.
- Steps cover task intake through governance; each row lists token bucket, time cost, primary
  drivers, and optimization ideas keyed to future tasks (kickstart template, git helper, research
  cache, etc.).
- Potential savings section prioritizes five candidates with rough time/token impact so Task C can
  evaluate ROI quickly.

## Findings
- Planning + implementation dominate cost (S–L buckets) while branching/logging stay XS; savings
  should target automation for high-frequency but low-variance steps (plan autofill, git helpers).
- Token-heavy research spikes can be mitigated by central research logs; flagged as candidate #3.
- Retro capture remains XS but crucial for calibration—embedding instructions keeps the audit data
  flowing without new tools yet.

## Checklist
- [x] Workflow steps cataloged.
- [x] Cost/complexity estimates recorded.
- [x] Potential savings/opportunities listed.
- [x] Feedback updated.
- [x] Commit `T008/S004: publish workflow cost audit`.

## Inputs & References
- `AGENTS.md`
- Observed workflow from T007.

## Exit Criteria
- Audit doc ready for future refinement (Task C) and referenced in AGENTS/guides as needed.

## Feedback & Learnings
- **Open Problems**: Need better data capture for automated token/time stats to validate savings
  estimates; blocked on telemetry (future Task T010).
- **Questions**: Should we version the audit quarterly or keep a rolling doc? Leaning toward rolling
  updates with changelog.
- **Learnings**: Cost framing tied directly to Estimate Snapshot buckets keeps downstream consumers
  aligned without introducing new scales.
