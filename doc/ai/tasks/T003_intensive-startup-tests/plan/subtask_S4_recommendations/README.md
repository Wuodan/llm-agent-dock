# Task T003 / Subtask S4 — Recommendations & Documentation Updates

## Objective
Consolidate findings from S1–S3 into actionable recommendations, propose Dockerfile/test/script adjustments, and update all Feedback sections + downstream docs so future agents can reproduce the startup harness.

## Deliverables
- Summary of startup observations + required fixes within this subtask README (and referenced artifacts under `plan/`).
- List of proposed patches (Dockerfiles, tests, docs) with prioritization, including any quick fixes implemented during this task.
- Updated Feedback sections across task + subtasks, plus any new research notes or troubleshooting guides.
- Commit `[codex][subtask-S4_recommendations]: summary` capturing doc/code updates.

## Flow
1. Aggregate logs + notes from S3 to identify recurring issues (auth prompts, missing deps, log streaming blockers).
2. Draft recommended changes (Dockerfile tweaks, test harness updates, env var docs) and implement low-risk patches if in scope.
3. Update task-level Notes/Progress/References with links to new artifacts; ensure sanitized logs are referenced.
4. Review entire plan for completeness, fill Feedback with lessons + open problems, and capture follow-on tasks if needed.
5. Commit `[codex][subtask-S4_recommendations]: summary` after verifying documentation + code changes.

## Actions & Recommendations
- **Node 20 for Cline**: Switched the Dockerfile to download Node.js v20.17.0 tarballs per architecture so the Cline core boots without `Node.js version 20+ is required` errors. Keep this upgrade in mind when adding new bases.
- **Headless Codex login**: Verified `codex login --with-api-key` works with stdin, documented the flow in `README.md`, and suggested piping `OPENAI_API_KEY` for CI instead of invoking the local OAuth server.
- **Startup capture helper**: Promoted `scripts/dev/capture_agent_startup.py` (PTY + async streaming) with README instructions so future agents can reuse the harness.
- **Factory Droid home isolation**: Documented the need to set `HOME=/tmp/droid` (or similar) because `factory_ai_droid` writes into `~/.factory` on every run.
- **GHCR auth callout**: Added troubleshooting guidance noting that `ghcr.io/devcontainers/images/universal:2-linux` requires `docker login ghcr.io` with a PAT (`read:packages`).

## Outstanding Risks
- Universal base images remain inaccessible without a PAT; we still need a shared credentials story (or a different public base) before CI can cover that matrix slice.
- Codex headless login uses API keys; we must decide how to inject real secrets in CI (Vault, GitHub Actions vars, etc.) and how to mask logs.

## Checklist
- [x] Findings synthesized into prioritized recommendations.
- [x] Plan + Feedback sections updated across task + subtasks.
- [x] Required doc/code patches applied or queued with clear follow-up steps.
- [x] Document findings in Feedback.
- [x] Commit `[codex][subtask-S4_recommendations]: summary`.

## Inputs & References
- Outputs from S1–S3.
- `AGENTS.md`, task README, and any research logs.

## Exit Criteria
- T003 plan reflects final status, recommendations captured, and downstream files updated such that the next agent can act without ambiguity.

## Feedback & Learnings
- **Open Problems**: Need a sanctioned GHCR PAT (or mirror) for `devcontainers/images/universal`, plus a secrets plan for piping real Codex/OpenAI API keys in CI.
- **Questions**: Should we commit a redacted `~/.codex/config.toml` template or rely entirely on runtime `codex login --with-api-key`? Is there appetite for moving `factory_ai_droid` templates into a seeded volume to avoid runtime installs?
- **Learnings**: Installing Node via official tarballs keeps both arch builds in sync, Codex exposes a headless login mode, and disposable `$HOME` paths prevent Factory Droid from polluting image layers.
