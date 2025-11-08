# Task T001 / Subtask S3 — Matrix & Helper Scripts

## Objective
Wire the Dockerfile into a reproducible build system using `docker-bake.hcl` and helper scripts that
cover builder bootstrapping, matrix builds, and test execution.

## Deliverables
- `docker-bake.hcl` containing:
  - Global variables (registry, version, platforms, base/tool lists).
  - Target definitions for each base×tool combination under the `matrix` group.
  - Inline tag documentation.
- `scripts/dev/bootstrap.sh` — BuildKit/QEMU setup and `.env` defaults.
- `scripts/build.sh` — Validates inputs, wraps `docker buildx bake`, supports `BASE`, `TOOL`,
  `PLATFORM`, and registry overrides.
- `scripts/test.sh` — Pulls/builds image arguments and runs smoke suites.
- README snippets (placeholder OK until S5) explaining how to run the scripts.

## Flow
1. Define environment variable strategy (`.env` or defaults) for registry, tag, and platforms.
2. Draft `docker-bake.hcl` with locals for tool/base metadata; ensure it stays extendable.
3. Implement scripts with `#!/usr/bin/env bash`, `set -euo pipefail`, two-space indent.
4. Dry-run `docker buildx bake ... --print` to validate matrix expansion.
5. Document usage notes (temporary) inside script comments or this plan so README can stay user-only
   until S5.
6. Update plan checklists and commit `[codex][matrix-build]: add bake + scripts`.

## Checklist
- [x] Registry/tag/platform variable scheme defined.
- [x] `docker-bake.hcl` implements matrix + documentation comments.
- [x] `scripts/dev/bootstrap.sh` provisions builder & QEMU.
- [x] `scripts/build.sh` wraps Bake with validation.
- [x] `scripts/test.sh` glues to smoke tests.
- [x] Dry-run bake succeeds (`--print`).
- [x] Plan updated; commit `[codex][matrix-build]: add bake + scripts]`.

## Inputs & References
- Dockerfile from S2.
- AGENTS.md build instructions (`docker buildx bake -f docker-bake.hcl matrix ...`).

## Exit Criteria
- All checklist items checked.
- Build/test scripts runnable end-to-end for at least one matrix target.

## Feedback & Learnings
- `.env` now stores `LLM_AGENT_DOCK_*` defaults so scripts share registry (`REGISTRY`),
  repository, version, and platform overrides without hard-coding secrets.
- `docker buildx bake -f docker-bake.hcl matrix --print` succeeds and shows all 9 targets, even
  though actual builds remain blocked by the Docker socket permission issue noted in S2.
- `scripts/test.sh` enforces having `bats` + `docker`; it supports `--tool` to focus on a single
  suite once S4 lands.
