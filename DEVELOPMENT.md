# Development Guide

This repo ties together two build-focused submodules:

- `aicage-image-base/` builds the base OS layers.
- `aicage-image/` builds the final agent images using those bases.

Work happens inside those submodules. Use this document to set up your machine and pick the right
entrypoint; the per-repo `DEVELOPMENT.md` files describe the details for each build.

## Prerequisites

- Docker with Buildx (`docker buildx version`).
- QEMU/binfmt for multi-arch builds (often included with Docker Desktop).
- Bats (`bats --version`) to run smoke tests.
- Python 3.11+; install per-repo tools with `pip install -r requirements-dev.txt` in the repo you
  are touching.

## Repo layout

- `aicage-image-base/` — base image Dockerfiles, Bake targets, smoke tests, and supporting scripts.
- `aicage-image/` — final agent Dockerfiles, Bake targets, smoke tests, and installers.
- `README.md` — user-facing overview of the published images.
- `AGENTS.md` — guidance for AI coding agents working in this repo.

## Setup

Create a virtual environment and install tooling in the submodule you plan to edit:

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements-dev.txt
```

Repeat in each submodule as needed; their dependency sets may differ.

## Build and test entrypoints

- Base images: `cd aicage-image-base && scripts/build.sh --base <alias> [--platform ...]`  
  Smoke tests: `scripts/test-all.sh`
- Agent images: `cd aicage-image && scripts/build.sh --tool <tool> --base <alias> [--platform ...]`  
  Smoke tests: `scripts/test-all.sh`

See each submodule’s `DEVELOPMENT.md` for configuration flags, environment variables, and matrix
options.

## Adding or changing images

- New base OS: follow `aicage-image-base/DEVELOPMENT.md` to add `bases/<alias>/base.yaml` and any
  installer changes.
- New agent tool: follow `aicage-image/DEVELOPMENT.md` to add an installer and smoke tests.

## CI and releases

- Base images: `aicage-image-base/.github/workflows/base-images.yml` publishes
  `${AICAGE_BASE_REPOSITORY}:<alias>-<version>` and `:<alias>-latest`.
- Agent images: `aicage-image/.github/workflows/final-images.yml` publishes
  `${AICAGE_REPOSITORY}:<tool>-<base>-<version>` using the published base layers.
