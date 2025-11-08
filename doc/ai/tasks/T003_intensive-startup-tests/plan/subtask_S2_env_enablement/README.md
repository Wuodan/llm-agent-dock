# Task T003 / Subtask S2 — Environment & Tooling Readiness

## Objective
Verify the local environment (docker, buildx, bats, QEMU) and scripts required for agent startup exercises, capturing reproducible commands + troubleshooting steps in the plan.

## Deliverables
- Logged outputs for `docker info`, `bats --version`, and any builder/bootstrap commands, stored in the subtask plan.
- Notes on available base images, registries, and required env vars (API placeholders) for upcoming tests.
- Updated Flow/Checklist statuses plus Feedback capturing constraints or blockers (e.g., missing Docker socket access).

## Flow
1. Run `docker info` and `bats --version`, recording sanitized outputs in the plan.
2. Inspect `scripts/dev/bootstrap.sh`, `scripts/build.sh`, and `scripts/test.sh` to confirm required arguments/env vars; document how to invoke them per base/tool.
3. Validate BuildKit/bake availability (dry-run or `docker buildx bake --print`) without launching long builds yet.
4. Capture any credential or network requirements for agent CLIs; prepare placeholder env vars/secrets list.
5. Update plan checklists + Feedback, then commit `T003/S002: summary` once done.

## Observations & Logs
- 2025-11-08T17:50Z — `docker info` confirms Engine 28.5.1 on Debian 13 with buildx v0.29.1 plugin available; containerd+runc present and binfmt already configured previously.
- 2025-11-08T17:50Z — `bats --version` reports 1.11.1 (matches requirement in `scripts/test.sh`).
- Script review:
  - `scripts/dev/bootstrap.sh` ensures `.env`, buildx builder (`llm-agent-dock`), and binfmt registration; rerun after Docker upgrades.
  - `scripts/build.sh <tool> <base>` wraps `docker buildx bake` with env overrides (`REGISTRY`, `REPOSITORY`, `VERSION`, `PLATFORMS`) and supports `--platform`, `--push`, `--load`, `--set`.
  - `scripts/test.sh <image-ref>` pulls (or skips via `--no-pull`) and invokess `bats` suites under `tests/smoke/`, using `LLM_AGENT_IMAGE` env var per test.
- Dry-run bake: `docker buildx bake -f docker-bake.hcl matrix --set "*.platform=linux/amd64" --print` succeeded, listing all nine targets (`cline|codex|factory_ai_droid` × `act|universal|ubuntu`) with tags `ghcr.io/wuodan/llm-agent-dock:<tool>-<base>-latest`.
- Registry access: direct `docker pull ghcr.io/wuodan/llm-agent-dock:cline-ubuntu-latest` failed with `denied` (private repo), so we must build locally for each combo.
- Dry-run bake: `docker buildx bake -f docker-bake.hcl matrix --set "*.platform=linux/amd64" --print` succeeded, listing all nine targets (`cline|codex|factory_ai_droid` × `act|universal|ubuntu`) with tags `ghcr.io/wuodan/llm-agent-dock:<tool>-<base>-latest`.
- Placeholder auth/env planning: expect to feed dummy API tokens via env vars (e.g., `OPENAI_API_KEY`, `CLINE_API_KEY`, `FACTORY_AI_DROID_TOKEN`) once actual CLI requirements are identified in S3; document exact names there.

## Checklist
- [x] `docker info` + `bats --version` captured and logged.
- [x] Script entrypoints + required flags documented.
- [x] Builder/bake readiness confirmed (or blockers recorded).
- [x] Document findings in Feedback.
- [x] Commit `T003/S002: summary`.

## Inputs & References
- `scripts/dev/bootstrap.sh`, `scripts/build.sh`, `scripts/test.sh`
- `doc/ai/tasks/T003_intensive-startup-tests/README.md`
- `AGENTS.md`

## Exit Criteria
- Environment checks completed or blockers documented, plan updated with logs/notes, and Feedback highlights any gaps before running agent startups.

## Feedback & Learnings
- **Open Problems**: Need definitive env-var contract per agent CLI to avoid real credential prompts; capture during S3.
- **Questions**: Should we pin BuildKit `--set *.platform` to linux/amd64 for CI smoke runs to avoid binfmt dependency, or keep multi-arch coverage?
- **Learnings**: Existing scripts already centralize registry/tag inputs, so future harnesses can wrap them rather than reimplementing docker commands.
