# Task T007 — Pilot GitHub-Issue Task Tracking

## Status
- Status: Completed (2025-11-08)
- Owner: Codex (closing agent)
- Links: `doc/ai/tasks/T007_github-issues-pilot/plan/README.md`, [GitHub issue #1](https://github.com/Wuodan/llm-agent-dock/issues/1)

## GitHub Issue Sync
- Canonical tracker: [#1 — T007: Pilot GitHub-Issue Task Tracking](https://github.com/Wuodan/llm-agent-dock/issues/1).
- Labels: `task` + `status:completed` (use `status:needs-review` while waiting on merge, `status:completed` once merged).
- Comment cadence: leave a GitHub comment every time the plan Progress Log gains a timestamp; if offline, paste the comment text into the plan and post it once reconnected.
- Offline fallback: keep updating the plan + Feedback sections; when back online, replay the queued comments so GitHub mirrors the log.

## Background
All planning currently lives in repo files. We want to experiment with managing tasks at the GitHub
issue level to reduce duplication, yet coding agents still need clear instructions. This task should
introduce a lightweight integration where each task is mirrored (or primarily described) on GitHub,
while avoiding double documentation.

## Goals & Deliverables
1. Decide how task-level planning is represented on GitHub (issue templates, labels, linking style)
   and how local docs reference those issues.
2. Update `AGENTS.md`/templates so new tasks either (a) create a GitHub issue and keep local files as
   pointers, or (b) follow another agreed pattern with no redundant text.
3. Capture a “test balloon” implementation: select one task, create the corresponding GitHub issue,
   and document how status/feedback is synchronized.
4. Ensure instructions clarify that if planning is hosted on GitHub, local copies should not duplicate
   the content; instead they should link to the canonical issue.

## Out of Scope
- Full migration of all historical tasks/subtasks. Start with a single pilot task.
- Fine-grained subtask updates on GitHub (task-level only for now).

## Dependencies & Inputs
- Existing AGENTS.md workflow guardrails.
- GitHub permissions for creating/editing issues.

## Open Questions
- Should subtasks remain in-repo, or do we reference GitHub for them too later?
- How do we handle offline work if issues are the canonical source (e.g., fallbacks)?

## Next Steps
- When ready, open a plan folder referencing the GitHub issue ID and outline the pilot execution.
