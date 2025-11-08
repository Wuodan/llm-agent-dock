# Task T008 — Workflow Cost Management Additions & Improvements

## Status
- Status: Proposed (plan drafted, pending approval)
- Owner: TBD
- Links: `doc/ai/tasks/T008_workflow-cost-management/plan/README.md`

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
- Should token estimates be numeric (targets) or bucketed (e.g., S/M/L)?
- What’s the minimal data precision we can collect post-task without adding more overhead than benefit?
- How will we ingest actual token metrics if/when MCP access to the ChatGPT dashboard exists (future work)?

## Next Steps
- Approve this scope, then create the GitHub issue + task branch `task/T008_workflow-cost-management` to start S001.
