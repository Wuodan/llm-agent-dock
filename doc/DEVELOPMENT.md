# Development Guide

This project builds and tests Docker images that package AI coding agents. Use this guide when you
need to develop, extend, or debug the build/test tooling.

## Prerequisites
- Docker CLI with Buildx enabled (`docker buildx version`).
- QEMU/binfmt for multi-arch builds (provided by Docker Desktop; otherwise install manually).
- Bats (`bats --version`) to run smoke tests.

Example setup (Debian/Ubuntu):
```bash
sudo apt install docker.io docker-buildx-plugin qemu-user-static bats
```

## Repo layout
- `Dockerfile` — single definition used for every base × tool combination.
- `docker-bake.hcl` — single flexible Bake target; scripts set TOOL/BASE_IMAGE/tags via `--set`.
- `scripts/`
  - `build.sh` — wraps `docker buildx bake` with guardrails.
  - `build-all.sh` — builds every tool/base combination, forwarding build flags.
  - `test.sh` — runs smoke tests via Bats.
  - `test-all.sh` — runs smoke suites for every tool/base using derived image tags.
  - `installers/` — per-tool installer scripts invoked during the Docker build.
  - `entrypoint.sh` — runtime user bootstrap (creates UID/GID, workspace, drops to gosu).
- `tests/smoke/` — Bats smoke suites per tool.

`.env` variables (edit to override):
- `AICAGE_REPOSITORY` (default `wuodan/aicage`)
- `AICAGE_VERSION` (default `dev`)
- `AICAGE_PLATFORMS` (default `linux/amd64 linux/arm64`, space-separated)
- `AICAGE_TOOLS` (default `cline codex droid`, space-separated)
- `AICAGE_BASES` (default `ghcr.io/catthehacker/ubuntu:act-latest ubuntu:24.04`, space-separated)
- `AICAGE_BASE_ALIASES` (default `act ubuntu`, space-separated, aligned by index with `AICAGE_BASES`)

## Build
```bash
scripts/build.sh <tool> <base> [--platform list]
```
- `tool` values come from `.env` (`AICAGE_TOOLS`).
- `base` values come from `.env` (`AICAGE_BASES`) and are paired with aliases in `AICAGE_BASE_ALIASES`.
- Images are tagged `${REPOSITORY}:<tool>-<base-alias>-<version>`.

Examples:
```bash
# Build and load a single-arch image locally
scripts/build.sh codex ubuntu --platform linux/amd64

# Build the full matrix
scripts/build-all.sh

# Build only one platform via build-all
scripts/build-all.sh --platform linux/amd64
```

## Test (smoke)
Run all suites or filter by tool:
```bash
scripts/test.sh wuodan/aicage:codex-ubuntu-24.04-dev --tool codex
```
- `AICAGE_IMAGE` can be set manually when running Bats directly.

Test the full matrix using derived tags:
```bash
scripts/test-all.sh
```

Smoke suites live in `tests/smoke/` (one per tool). Install `bats` to run the suites (e.g.,
`npm install -g bats`).

## Runtime user
Images start as root and rely on `scripts/entrypoint.sh` to create a user at runtime. It reads
`AICAGE_UID`/`AICAGE_GID`/`AICAGE_USER` (defaults `1000`/`1000`/`aicage`), creates the group/user
if missing, creates `/workspace`, chowns it, and switches to that account with `gosu`. Mount host
code into `/workspace` and pass your host IDs, e.g.
`-e AICAGE_UID=$(id -u) -e AICAGE_GID=$(id -g) -e AICAGE_USER=$(id -un)`.

## Adding a tool
1) Create `scripts/installers/install_<tool>.sh` (executable) that installs the agent; fail fast on
   errors.  
2) Add the tool to `AICAGE_TOOLS` in `.env`.  
3) Add a smoke suite at `tests/smoke/<tool>.bats`.  
4) Update README tables to mention the tool.

## Adding a base
1) Add the full base image reference to `.env` (`AICAGE_BASES`).  
2) Extend the `Dockerfile` only if the base needs extra packages/config.  
3) Update README tables to mention the base and alias.

## Coding style
- Bash: `#!/usr/bin/env bash`, `set -euo pipefail`, two-space indent, descriptive functions.
- Dockerfile: args at top (`BASE_IMAGE`, `TOOL`, `TARGETARCH`), POSIX-friendly steps.
- Markdown: wrap near ~100 chars, keep tables readable.

## Troubleshooting
- **Missing bats**: `npm install -g bats` or `brew install bats-core`.
- **Multi-arch failures**: recreate a buildx builder and reconfigure binfmt; pass
  `--platform linux/amd64` to build single-arch.
