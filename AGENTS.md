# Repository Guidelines

## Project Structure & Module Organization
- Root `Dockerfile` stays parameterized via `BASE_IMAGE` and `TOOL` arguments so a single definition feeds every variant.
- `docker-bake.hcl` owns the base×tool×arch matrix; keep new targets under the `matrix` group and document tags inline.
- `scripts/` stores reproducible helpers (`build.sh`, `test.sh`, `lint.sh`); mirror their responsibilities in `README.md` whenever behavior changes.
- `tests/` holds smoke suites (prefer `tests/smoke/*.bats`) that assert image boot, agent binaries, and critical CLIs.
- `doc/ai/plan/` captures planning artifacts; never delete history—append timestamped entries so other agents can replay decisions.

## Build, Test, and Development Commands
- `docker buildx bake -f docker-bake.hcl matrix --set "*.platform=linux/amd64,linux/arm64"` builds the full grid; scope with `matrix.<target>` when iterating.
- `scripts/build.sh cline ubuntu:24.04` should wrap Bake with validation and default tags; design it to accept `BASE`, `TOOL`, and `PLATFORM`.
- `scripts/test.sh ghcr.io/org/llm-agent-dock:cline-ubuntu-latest` runs all `tests/` suites against a pushed or local image.
- `scripts/dev/bootstrap.sh` provisions BuildKit builders, QEMU emulation, and `.env` defaults; rerun after upgrading Docker.

## Coding Style & Naming Conventions
- Bash scripts: `#!/usr/bin/env bash`, `set -euo pipefail`, two-space indentation, and descriptive function names (`build_matrix`, `push_variant`). Lint with `shellcheck`/`shfmt`.
- Dockerfiles: group ARG declarations at the top, then base OS prep, then tool install; comment extension points (`# Add new agent installers below`).
- HCL/JSON: snake_case variables, kebab-case target names (`cline-arm64`).
- Markdown: title case headings, wrap lines at ~100 chars, favor tables over prose when listing matrices.

## Testing Guidelines
- Tests rely on `bats` (or lightweight Bash) inside `tests/smoke/`; each file mirrors a tool (`cline.bats`, `codex.bats`).
- Name tests `test_<feature>` and cover: image boots, agent CLI responds, required OS packages exist.
- Gate merges on `scripts/test.sh --all` so both architectures run; at minimum, ensure each matrix dimension is sampled weekly.

## Commit & Pull Request Guidelines
- Follow `[codex][subtask-name]: summary` commit subjects (e.g., `[codex][matrix-setup]: add docker-bake definition`); keep bodies wrapped at 72 chars.
- PRs must describe the affected matrix slice, list commands run, and link the governing task ID. Include screenshots/log snippets only when diagnosing failures.
- Cross-reference planning docs (`doc/ai/plan/*.md`) whenever the change alters scope so reviewers can trace intent.

## Security & Configuration Tips
- Keep secrets (registry tokens, SSH keys) out of Bake vars; load them via `docker buildx bake --set *.secrets` or GitHub Actions secrets.
- Pin base images to digests during releases to prevent unexpected upstream changes; refresh digests quarterly.
- When adding new agents, validate licenses and runtime telemetry defaults before merging.
