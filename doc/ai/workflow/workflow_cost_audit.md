# Workflow Cost Audit (v1)

_Last updated: 2025-11-08 by Codex_

## Methodology & Buckets
- Inputs: AGENTS workflow guardrails, task plans (T001–T008), and retrospective notes captured through
  November 8, 2025.
- Token cost references use the planning XS/XL buckets defined in T008/S001 (combined prompt +
  completion tokens per task/subtask). Time references use estimated agent-hours rounded to the
  nearest 0.5h.
- Ratings focus on relative magnitude so we can track deltas over time without granular telemetry.

## Workflow Step Catalog
| Step | Description | Token Bucket (Typical) | Time Cost (Typical) | Primary Drivers | Potential Optimization |
|------|-------------|------------------------|---------------------|-----------------|------------------------|
| 1. Task intake & issue mirroring | Review task index, create/update GitHub issue, align labels/status | XS (≤10k) | 0.3–0.5h | Context switching across docs + issue template churn | Script to prefill issue + plan metadata from template inputs |
| 2. Planning & estimate snapshot | Draft Context, Estimate Snapshot, subtask breakdown, checklist updates | S (10–25k) | 0.5–1.0h | Iterating on scope statements, capturing dependencies/tags | Provide plan snippet library + autofill from prior tasks |
| 3. Subtask branching & sync | Create/push task + subtask branches, run pull/merge boilerplate | XS | 0.2–0.4h | Repetitive git commands + documentation logging | Shell helper to wrap checkout/push/log updates |
| 4. Research & design spikes | Web/MCP research, taxonomy design, quoting specs | S–M | 1–2h | External browsing plus summarization for plan docs | Cache research summaries under `doc/ai/research/` for reuse |
| 5. Implementation & doc edits | Update templates, AGENTS, workflow docs, etc. | S–L | 1.5–3h | Multi-file edits + validation, cross-referencing instructions | Lightweight lint/preview scripts to catch format drift early |
| 6. Testing & validation | Run scripts/tests (when applicable), sanity-check instructions | XS–S | 0.3–0.7h | Environment bootstrap (venv, docker info), manual verification | Add bats tests for template linting + doc link checking |
| 7. Progress logging & GitHub sync | Update plan checklists, add Progress Log entries, mirror to issues | XS | 0.2–0.4h | Manual timestamping, referencing branch names | Create CLI helper to stamp ISO timestamps + branch refs |
| 8. Retro metrics capture | Fill Retro Metrics block, summarize learnings | XS | 0.2h | Remembering deltas + data sources | Provide markdown snippet + optional form to capture actuals |
| 9. Workflow audit & governance | Aggregating observations into shared audits like this doc | XS–S | 0.5–0.8h | Collating info from multiple plans/issues | Maintain rolling audit log and link from AGENTS for incremental updates |

### Detailed Notes
1. **Task intake** — Minimal token use, but latency occurs when issue template + plan need duplicate
   edits. Automation opportunity tied to Task T009 (kickstart template).
2. **Planning snapshot** — Most planning cost stems from articulating Estimate Snapshot fields; reuse
   of tag definitions should keep bucket stable unless new work-types appear.
3. **Branching** — The enforced branch policy adds predictable git steps; cost mostly time, not tokens.
4. **Research spikes** — Web/MCP usage jumps tokens quickly; ensure research notes live under
   `doc/ai/research/` so repeated lookups are avoided.
5. **Implementation** — Largest spread; editing AGENTS + templates touches wide files, so reviewers
   should budget at least an `M` bucket for doc-heavy changes even without code.
6. **Testing** — Currently light but will grow once scripts/test harness expand; capturing Docker +
   bats outputs in plan logs prevents reruns.
7. **Progress logging** — Manual but necessary to keep hand-offs clean; the new Estimate Snapshot
   rule means logs must mention bucket jumps immediately.
8. **Retros** — Cheap yet often skipped; embedding prompts + examples lowers friction.
9. **Governance** — Audit updates should happen quarterly or after major workflow changes.

## Potential Savings & Candidates
1. **Plan & issue autofill (est. XS token, 0.3h saved per task)** — Build a `scripts/plan/init_task.sh`
   helper that copies templates, injects timestamps, and optionally posts draft GitHub issues.
2. **Branch orchestration helper (XS token, 0.2h saved per subtask)** — Provide `scripts/git/new_subtask.sh`
   to run checkout, push, and log updates with a single command, reducing manual mistakes.
3. **Research snippet library (S→XS token reduction)** — Store MCP search summaries in
   `doc/ai/research/` with tags so future tasks reuse them instead of issuing new queries.
4. **Template lint + link check (XS time, prevents rework)** — Simple CI or local script to confirm
   Estimate Snapshot / Retro sections exist before commits.
5. **Retro capture assistant (XS token, 0.1h saved)** — Markdown form or VS Code snippet that
   pre-populates retro fields, nudging contributors to log actuals before context is lost.

## Data Gaps & Next Steps
- Need token telemetry integration (future Task T010) to replace manual bucket confidence with real
  counts sourced from ChatGPT dashboards or MCP APIs.
- Track cumulative variance in a lightweight spreadsheet or JSON summary so audits can graph bucket
  accuracy trends over time.
- Schedule quarterly audit refresh to compare planned vs. actual improvements and update candidate
  backlog (feeds Task C / cost reduction roadmap).
