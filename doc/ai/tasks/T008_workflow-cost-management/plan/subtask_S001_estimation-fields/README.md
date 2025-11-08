# Task T008 / Subtask S001 — Define Estimation Attributes & Taxonomies

## Objective
Specify the required estimate fields for tasks/subtasks (token usage, complexity, work-type tags, LLM tier, etc.) and provide guidance so agents can fill them consistently.

## Deliverables
- Attribute list with definitions + example scales (e.g., token buckets, complexity levels).
- Starter tag catalog (extendable) with usage tips.
- Recommendations on optional attributes that inform “worth it?” decisions (LLM tier, dependencies, risk notes).
- Updated plan checklist + Feedback notes.

## Flow
1. Review current planning templates + AGENTS guardrails.
2. Draft attribute definitions and sample values.
3. Validate that attributes stay lightweight (bullet tables, short scales).
4. Capture findings in a doc (can be embedded in this README or referenced by S002).
5. Commit `T008/S001: define estimation attributes` once checklist complete.

## Estimation Attribute Catalog (Draft v1)

| Attribute | Required Scope | Scale / Allowed Values | Notes |
|-----------|----------------|------------------------|-------|
| Token Estimate Bucket | Task + every subtask | XS (<10k), S (10–25k), M (25–60k), L (60–120k), XL (>120k) total bidirectional tokens | Count combined MCP + manual chat usage; escalate if projected bucket jumps ≥1 level or implies ≥5% token budget increase.
| Complexity Level | Task + subtask | 1 (trivial), 2 (routine), 3 (multi-file/coordination), 4 (cross-system or research heavy), 5 (novel/ambiguous) | Complexity drives staffing + review depth; default to 2 unless at least two triggers for higher bands exist.
| Work-Type Tags | Task + subtask (≤3 tags) | `docs`, `code`, `research`, `ops`, `infra`, `testing`, `automation`, `planning`, `integration`, `data`, `runtime` | Tags help filter workload; use the most specific ones that apply.
| LLM Tier Recommendation | Task level (optional per subtask) | `lite` (e.g., GPT-4o-mini), `standard` (GPT-4o), `advanced` (GPT-4.1/GPT-4o1-preview), `specialized` (multimodal/coding-specialist) | Choose the cheapest tier that still meets accuracy + tool needs; note fallbacks.
| Confidence in Estimate | Task + subtask | High / Medium / Low | Reflects how solid the estimate is; low confidence requires noting unknowns in Feedback.
| Dependencies / Sequencing | Task level, optional subtask | Free text bullet noting blocking tasks, env needs, or required approvals | Keeps branch + GitHub issue status aligned.
| Risk Hotspots | Task level | Bullet list referencing security, availability, data sensitivity, or process gaps | Feeds escalation + reviewer selection.

### Token Bucket Guidance
- Buckets are sized around _total conversational tokens_ (prompt + completion) per task/subtask. Historical runs show ~8–10k tokens/day baseline; buckets align to ~1, 2.5, 6, 12, 12+ agent-hours of dialogue.
- When combining subtasks, round up to the next bucket if >80% of the threshold to avoid under-reporting.
- If a task spans multiple agents, list the aggregate bucket plus a short breakdown (e.g., “M overall — S for docs, XS for script tweak”).

### Complexity Triggers
- **Level 1** – strictly documentation edits ≤50 lines or single-script tweaks without branching or new decisions.
- **Level 2** – single subsystem edits, light research, or template updates with no behavioral changes.
- **Level 3** – multi-file or multi-language changes, or anything needing coordination with Docker/tests/research.
- **Level 4** – cross-repo integration, novel design choices, net-new tooling, or long research chains.
- **Level 5** – ambiguous requirements, undefined interfaces, or security-sensitive work where mistakes are costly.

### Work-Type Tag Catalog
- `docs` — Markdown, READMEs, plans, audits.
- `code` — Any source update beyond docs.
- `research` — Web/MCP investigations whose outputs feed the repo.
- `ops` — Branching, GitHub issue management, release steps.
- `infra` — Dockerfiles, bake files, CI plumbing.
- `testing` — Automated or manual verification artifacts.
- `automation` — Scripts, bots, tooling improvements.
- `planning` — Templates, process docs, estimation-only passes.
- `integration` — Cross-service glue, API wiring, auth, secrets.
- `data` — Schema migrations, fixture curation.
- `runtime` — Production config, launch scripts, deployment knobs.

Agents may introduce additional tags when justified; append them to the S001 Feedback list before using broadly so future subtasks can adopt them consistently.

### LLM Tier Notes
- `lite`: prefer when work is mostly deterministic editing or templated docs with low ambiguity.
- `standard`: default tier; choose when moderate reasoning, file context, or lightweight code edits occur.
- `advanced`: reserve for novel design, debugging, or multi-hop reasoning tasks where lower tiers degraded prior outcomes.
- `specialized`: use when a domain-specific or multimodal model is required (e.g., vision, audio). Document why.

### Optional Decision Aids
- **Confidence** — highlight known unknowns (e.g., “Low confidence: waiting on GHCR token policy”).
- **Dependencies** — note blockers so GitHub issue status can shift to `status:blocked` quickly if needed.
- **Risk Hotspots** — capture what could trigger rework or approvals (security, tokens, reviewer scarcity).
- **Suggested Safeguards** — optional bullet (tests to run, sign-offs needed) for subtasks ≥ Level 4 complexity.

## Guidance Examples
- _Template edit example_: “Token Bucket: XS (<10k), Complexity 2, Tags: docs, planning, LLM Tier: lite, Confidence: High.”
- _New Docker target example_: “Token Bucket: L (60–120k) — heavy bake/test logs, Complexity 4, Tags: infra, testing, automation, LLM Tier: advanced, Confidence: Medium, Risks: cache churn, builder availability.”

## Integration Notes
- S002 should embed the required fields in both task and subtask templates (Token Bucket, Complexity, Tags, LLM Tier, Confidence) plus optional fields (Dependencies, Risks) with concise instructions.
- S003 will reference the same buckets for retro accuracy (e.g., “Estimated: M, Actual: L, Accuracy: +1 bucket / +25% tokens”).
- `AGENTS.md` needs a new subsection clarifying how to escalate when estimates cross buckets or confidence drops to Low.

## Checklist
- [x] Attribute list drafted (token, complexity, tags, tier, etc.).
- [x] Example guidance for tagging + complexity scales.
- [x] Optional attributes (e.g., risk, LLM suitability) recommended.
- [x] Findings captured in Feedback section.
- [x] Commit `T008/S001: define estimation attributes`.

## Inputs & References
- `AGENTS.md`
- `doc/ai/templates/task_plan_README.template.md`
- `doc/ai/templates/subtask_plan_README.template.md`

## Exit Criteria
- Attribute catalog ready for S002 to embed into templates/instructions.

## Feedback & Learnings
- **Open Problems**: Need historical data to validate bucket thresholds; coordinate with future cost tooling (Task T010) once available.
- **Questions**: Should `runtime` vs. `infra` remain separate tags or merge under heavy overlap? Revisit after 2–3 tasks to avoid churn.
- **Learnings**: Token bucket framing tied to agent-hour rough cut keeps estimates intuitive without forcing hard numbers.
