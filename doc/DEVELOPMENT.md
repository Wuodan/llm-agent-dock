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
- `aicage-image-base/` — submodule with base image Dockerfile, Bake file, scripts, and smoke tests (rooted
  at the submodule).
- `aicage-image/` — submodule with agent Dockerfile/Bake plus all agent build/test scripts and installers.
  - `scripts/` — build/test helpers (agent-specific).
  - `tests/smoke/` — Bats smoke suites for agents.
- `.env` — each submodule includes its own defaults for build/test matrices.

`.env` variables (edit to override inside each submodule):
- `AICAGE_REPOSITORY` (default `wuodan/aicage`)
- `AICAGE_VERSION` (default `dev`)
- `AICAGE_PLATFORMS` (default `linux/amd64 linux/arm64`, space-separated)
- `AICAGE_TOOLS` (default `cline codex droid`, space-separated)
- `AICAGE_BASE_REPOSITORY` (default `wuodan/aicage-image-base`, must differ from `AICAGE_REPOSITORY`)
- `AICAGE_BASE_ALIASES` is optional; when unset we auto-discover `<alias>-latest` tags from
  `${AICAGE_BASE_REPOSITORY}` via Docker Hub and `docker images`.
- Base definitions live in `aicage-image-base/bases/<alias>/base.yaml` with keys:
  - `base_image` (upstream image reference, e.g., `fedora:latest`)
  - `os_installer` (relative path to the install script to run, e.g., `scripts/install_os_packages_redhat.sh`)
- `yq` is required for parsing `base.yaml` files inside the `aicage-image-base` submodule.

## Build
### Base images
```bash
cd aicage-image-base && scripts/build.sh --base <alias> [--platform list] [--version <tag>]
cd aicage-image-base && scripts/build-all.sh [--platform list]
```
- `base` values come from folders in `aicage-image-base/bases/` (folder name is the alias, files define upstream and installer).
- Images are tagged `${AICAGE_BASE_REPOSITORY}:<base-alias>-<AICAGE_VERSION>`.

### Agent (final) images
```bash
cd aicage-image && scripts/build.sh --tool <tool> --base <alias> [--platform list] [--version <tag>]
cd aicage-image && scripts/build-all.sh [--platform list]
```
- `tool` values come from `aicage-image/.env` (`AICAGE_TOOLS`).
- `base` values come from `${AICAGE_BASE_REPOSITORY}:*-latest` tags; override with
  `AICAGE_BASE_ALIASES` to pin a subset.
- Images are tagged `${REPOSITORY}:<tool>-<base-alias>-<version>`.

## Test (smoke)
Run all suites or filter by tool:
```bash
cd aicage-image && scripts/test.sh --image wuodan/aicage:codex-node-dev --tool codex
```
- `AICAGE_IMAGE` can be set manually when running Bats directly.

Test the full matrix using derived tags:
```bash
cd aicage-image && scripts/test-all.sh
```

Smoke suites live in `aicage-image/tests/smoke/` (one per tool). Install `bats` to run the suites (e.g.,
`npm install -g bats`).

Base images also have a smoke sweep:
```bash
cd aicage-image-base && scripts/test-all.sh
```

## Runtime user
Images start as root and rely on `scripts/entrypoint.sh` to create a user at runtime. It reads
`AICAGE_UID`/`AICAGE_GID`/`AICAGE_USER` (defaults `1000`/`1000`/`aicage`), creates the group/user
if missing, creates `/workspace`, chowns it, and switches to that account with `gosu`. Mount host
code into `/workspace` and pass your host IDs, e.g.
`-e AICAGE_UID=$(id -u) -e AICAGE_GID=$(id -g) -e AICAGE_USER=$(id -un)`.

## Publish workflows
- Base images: `aicage-image-base/.github/workflows/base-images.yml` builds/tests on tags only and
  publishes multi-arch base images to `${AICAGE_BASE_REPOSITORY}`.
- Agent images: `aicage-image/.github/workflows/final-images.yml` builds/tests agents on tags only and publishes
  to `${AICAGE_REPOSITORY}`, consuming `${AICAGE_BASE_REPOSITORY}:*-latest` tags.

## Adding a tool
1) Create `aicage-image/scripts/installers/install_<tool>.sh` (executable) that installs the agent;
   fail fast on errors.  
2) Add the tool to `AICAGE_TOOLS` in `aicage-image/.env`.  
3) Add a smoke suite at `aicage-image/tests/smoke/<tool>.bats`.  
4) Update README tables to mention the tool.

## Adding a base
1) Create `aicage-image-base/bases/<alias>/base.yaml` with `base_image` and `os_installer`.  
2) Extend the Dockerfile only if the base needs extra packages/config.  
3) Update README tables to mention the base and alias (and propagate to `aicage-image-base` if needed).

## Coding style
- Bash: `#!/usr/bin/env bash`, `set -euo pipefail`, two-space indent, descriptive functions.
- Dockerfile: args at top (`BASE_IMAGE`, `TOOL`, `TARGETARCH`), POSIX-friendly steps.
- Markdown: wrap near ~100 chars, keep tables readable.

## Troubleshooting
- **Missing bats**: `npm install -g bats` or `brew install bats-core`.
- **Multi-arch failures**: recreate a buildx builder and reconfigure binfmt; pass
  `--platform linux/amd64` to build single-arch.
