# Task T008 — Workflow Cost Management Additions & Improvements

## Status
- Status: Completed (merged into `development` via `T008/S000` on 2025-11-08)
- Owner: Codex (latest session)
- Links: `doc/ai/tasks/T008_workflow-cost-management/plan/README.md`, `doc/ai/workflow/workflow_cost_audit.md`, [GitHub Issue #2](https://github.com/Wuodan/llm-agent-dock/issues/2)

## Background
Token usage is becoming a limiting factor, so we need better visibility into estimated vs. actual cost for each task, plus clear workflows for flagging expensive changes. Existing plans lack structured estimates, and retros rarely capture accuracy data. Additionally, the workflow steps in `AGENTS.md` haven’t been analyzed end-to-end for cost impact.

## Goals & Deliverables
1. Define planning-time attributes (token buckets, complexity, work-type tags, LLM tier recommendations) so every task/subtask includes them.
2. Update plan templates + `AGENTS.md` to require those estimates and clarify escalation paths when projected cost rises ≥5%.
3. Introduce lightweight post-task retros capturing actual token usage/time and estimate accuracy.
4. Author the first `doc/ai/workflow/workflow_cost_audit.md`, listing current workflow steps, their relative cost, and candidates for optimization (inputs to future tasks like Task C).

## Out of Scope
- Automating token capture from ChatGPT dashboards or MCP integrations (defer to future tasks).
- Changing workflow steps without owner approval (this task only documents/estimates them).

## Dependencies & Inputs
- `AGENTS.md` guardrails (especially the new workflow cost check rules).
- Current plan templates in `doc/ai/templates/`.
- Observed process from prior tasks (e.g., T007).

## Open Questions
- Can we automate Estimate Snapshot + Retro field population once MCP exposes per-thread token
  counts (ties into Task T010)?
- Should we refresh the workflow cost audit on a rolling basis or publish quarterly snapshots?
- What is the lightest-weight method to capture real GitHub issue linkage for legacy tasks (GitHub
  issue for T008 still pending per guardrails)?

## Next Steps
- Adopt the updated templates + AGENTS instructions across new tasks immediately.
- Create and backfill the GitHub issue (per `.github/ISSUE_TEMPLATE/task.yml`) so future references
  link to the canonical tracker.
- Schedule the first workflow cost audit refresh once another 2–3 tasks land to validate the savings
  backlog and feed Task C.
