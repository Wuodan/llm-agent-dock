# Task T003 — Intensive Agent Startup & Prompt Capture

Last updated: 2025-11-08T17:45Z by Codex

## Context
- Validate startup behavior for `cline`, `codex`, and `factory_ai_droid` agents across `ubuntu`, `act`, and `universal` bases so CI can exercise their CLIs deterministically.
- Capture prompts, auth flows, stdout/stderr timing, and any missing package requirements, then recommend Dockerfile/test adjustments.
- Operate within existing repo tooling (`scripts/build.sh`, `scripts/test.sh`) and document everything through the plan + subtask feedback loops.

## Workflow Guardrails
1. Maintain live checklists in every plan/subtask README; update immediately after progress so a restart can follow the latest box states.
2. Follow AGENTS.md conventions (templated plans, commit format `[codex][subtask-name]: summary`, Docker build guidance, doc hygiene).
3. Log any MCP `brave-search`/`fetch` usage with URL + summary inside the relevant subtask plan (or `doc/ai/research/` if reused).
4. Each subtask closes only after Feedback is updated and the dedicated commit is made; no mixing of subtasks in one commit.

## Subtask Directory Map (T003)
| ID | Title | Status | Checklist |
|----|-------|--------|-----------|
| S1 | Scope & planning alignment | ☑ done | `plan/subtask_S1_planning/README.md` |
| S2 | Environment + tooling readiness | ☑ done | `plan/subtask_S2_env_enablement/README.md` |
| S3 | Agent startup capture (`cline`, `codex`, `factory_ai_droid`) | ◔ in-progress | `plan/subtask_S3_agent_startup_tests/README.md` |
| S4 | Recommendations & documentation updates | ☐ pending | `plan/subtask_S4_recommendations/README.md` |

## Master Checklist (T003)
- [x] S1 — Scope & planning alignment
- [x] S2 — Environment + tooling readiness
- [ ] S3 — Agent startup capture
- [ ] S4 — Recommendations & documentation updates

## Progress Log (T003)
- 2025-11-08T17:45Z — Initialized plan scaffolding and subtask folders per AGENTS.md.
- 2025-11-08T17:52Z — Ran docker/bats diagnostics and reviewed build/test scripts for S2 prep.
- 2025-11-08T18:15Z — Built act/ubuntu images, documented GHCR 403 for universal base, and captured startup logs via the new capture script.

## References
- `doc/ai/tasks/T003_intensive-startup-tests/README.md`
- `doc/ai/tasks/T002_validate-builds-docker/README.md`
- `doc/ai/templates/*.md`
- Repository root `AGENTS.md`

## Notes
- Record Docker/bats version outputs before running build/test scripts.
- Keep sanitized logs (no secrets) for each agent/base combo under `doc/ai/tasks/T003_intensive-startup-tests/plan/`.
