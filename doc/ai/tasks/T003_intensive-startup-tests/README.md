# Task T003 — Intensive Agent Startup & Prompt Capture

> Scope definition only. Do **not** draft the plan or begin implementation until explicitly scheduled.

## Background
- T002 validated ubuntu builds + smoke tests but never exercised the agent CLIs interactively.
- We need confidence that cline, codex, and factory_ai_droid launch cleanly, surface whatever authentication prompts they require (API keys, OAuth, etc.), and stream output without hanging CI.
- Prior attempts showed these CLIs block on stdin/stdout; future automation must capture logs without freezing the harness.

## Goals
1. Boot each agent image (all supported bases) and observe the initial startup behavior (do they launch, what prompts appear, how soon?).
2. Capture stdout/stderr asynchronously (e.g., background threads or `pexpect`-style wrappers) so blocking prompts don’t stall tests.
3. Record whether the tools request API keys, browser auth, etc., and document how to supply placeholders/env vars without completing a real login.
4. Identify any missing OS packages/services required for startup (XDG paths, git, editors, etc.).
5. Produce actionable recommendations or patches for the Dockerfiles/tests to keep startup reliable.

## Scope & Deliverables
- Focus on existing tools (`cline`, `codex`, `factory_ai_droid`) across every base (`ubuntu`, `act`, `universal`).
- Run agents in non-interactive CI-friendly modes whenever possible; otherwise document deterministic mocks.
- Provide reference logs, reproduction scripts, and troubleshooting guidance.
- Update downstream docs (README, AGENTS, templates) only after findings are captured in the plan.

## Workflow Expectations
1. Kick off by creating `doc/ai/tasks/T003_intensive-startup-tests/plan/` using the standard templates (task + subtasks).
2. Track subtasks similar to earlier tasks (S1 planning, S2 env enablement, S3 per-agent startup tests, etc.).
3. Each subtask must finish with feedback + `[codex][subtask-name]: summary` commit—no exceptions.
4. Avoid embedding chat logs or raw interactive transcripts; summarize observations and store sanitized logs if needed.
5. Escalate blockers (missing credentials, rate limits, sandbox issues) via the plan feedback section before proceeding.

## Open Problems & Outstanding Work
- Interactive CLIs currently untested; need a reproducible harness for stdin/stdout capture.
- act/universal base images still lack live build/test validation (stretch goal from T002).
- Guidance for remote builders and multi-arch pushes remains open (cf. T002 feedback).

## References
- `doc/ai/tasks/T002_validate-builds-docker/README.md` (recent build/test context).
- Templates: `doc/ai/templates/task_plan_README.template.md`, `doc/ai/templates/subtask_plan_README.template.md`.
- AGENTS.md for workflow hardening and documentation tone (no discussion transcripts).

## Feedback — Open Questions, Learnings, Risks
- **Questions**: Which auth flows (API keys vs. OAuth) must be supported, and can we rely on env vars to bypass prompts?
- **Risks**: Agents blocking on stdin will hang CI unless we stream logs asynchronously.
- **Learnings**: None yet (task not started).
