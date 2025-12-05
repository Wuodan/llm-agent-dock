# Development Guide

This project builds and tests Docker images that package AI coding agents. Use this guide when you
need to develop, extend, or debug the build/test tooling.

## Repo layout
- `Dockerfile` — single definition used for every base × tool combination.
- `docker-bake.hcl` — targets for each matrix entry plus a `matrix` group.
- `scripts/`
  - `dev/bootstrap.sh` — creates/uses a Buildx builder, seeds `.env`, enables binfmt.
  - `build.sh` — wraps `docker buildx bake` with guardrails.
  - `test.sh` — runs smoke tests via Bats.
  - `installers/` — per-tool installer scripts invoked during the Docker build.
- `tests/smoke/` — Bats smoke suites per tool.

## Prerequisites
- Docker CLI with Buildx (`docker buildx version`).
- binfmt/QEMU if you want multi-arch builds (`scripts/dev/bootstrap.sh` tries to configure it).
- Bats (`bats --version`) to run smoke tests.

## Bootstrap
Creates `.env` with defaults, ensures a Buildx builder, and attempts binfmt setup:
```bash
scripts/dev/bootstrap.sh
```

`.env` variables (edit to override):
- `LLM_AGENT_DOCK_REGISTRY` (default `ghcr.io`)
- `LLM_AGENT_DOCK_REPOSITORY` (default `wuodan/llm-agent-dock`)
- `LLM_AGENT_DOCK_VERSION` (default `dev`)
- `LLM_AGENT_DOCK_PLATFORMS` (default `linux/amd64,linux/arm64`)

## Build
```bash
scripts/build.sh <tool> <base> [--platform list] [--push|--load] [--print] [--set k=v]
```
- `tool`: `cline`, `codex`, `factory_ai_droid`
- `base`: `act`, `universal`, `ubuntu`
- Images are tagged `${REGISTRY}/${REPOSITORY}:<tool>-<base>-<version>` from `.env` (or env vars).

Examples:
```bash
# Build and load a single-arch image locally
scripts/build.sh codex ubuntu --platform linux/amd64 --load

# Preview bake config without building
scripts/build.sh cline act --print
```

## Test (smoke)
Run all suites or filter by tool:
```bash
scripts/test.sh ghcr.io/wuodan/llm-agent-dock:codex-ubuntu-dev --tool codex --no-pull
```
- `--pull` is on by default; add `--no-pull` for local images.
- `LLM_AGENT_IMAGE` can be set manually when running Bats directly.

## Adding a tool
1) Create `scripts/installers/install_<tool>.sh` (executable) that installs the agent; fail fast on
   errors.  
2) Add a Bake target for each base in `docker-bake.hcl` and list the tool in the `TOOLS` variable.  
3) Add a smoke suite at `tests/smoke/<tool>.bats`.  
4) Update README tables to mention the tool.

## Adding a base
1) Add a target to `docker-bake.hcl` with `BASE_IMAGE` set appropriately and list it in `BASES`.  
2) Extend the `Dockerfile` only if the base needs extra packages/config.  
3) Update README tables to mention the base.

## Coding style
- Bash: `#!/usr/bin/env bash`, `set -euo pipefail`, two-space indent, descriptive functions.
- Dockerfile: args at top (`BASE_IMAGE`, `TOOL`, `TARGETARCH`), POSIX-friendly steps.
- Markdown: wrap near ~100 chars, keep tables readable.

## Troubleshooting
- **Docker auth for `universal` base**: `docker login ghcr.io` with a PAT that has `read:packages`.
- **Missing bats**: `npm install -g bats` or `brew install bats-core`.
- **Multi-arch failures**: rerun `scripts/dev/bootstrap.sh` to recreate builder and reconfigure
  binfmt; pass `--platform linux/amd64` to build single-arch.
