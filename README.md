# aicage

Docker images for popular AI coding agents, built from a single, repeatable recipe. Pick a tool and
base OS, pull the tag, and you get a ready-to-run shell with the agent preinstalled.

## What you get

- Prebuilt tags for `cline`, `codex`, and `droid`.
- Base choices defined in `.env` (defaults: `ubuntu:24.04` and `ghcr.io/catthehacker/ubuntu:act-latest`).
- Multi-arch images (`linux/amd64` and `linux/arm64`) via Buildx.
- Thin images: agent install only; you bring your own API keys.

## Image tags

Tags follow `${REPOSITORY}:<tool>-<base-alias>-<version>`.

Default repo: `wuodan/aicage` on Docker Hub. Base layers live separately at
`wuodan/aicage-base` and are pulled by the agent builds.

Tools, bases, platforms, and base image references are defined once in `.env` and respected by the
scripts and Bake targets.

Examples:

- `wuodan/aicage:codex-ubuntu-latest`
- `wuodan/aicage:cline-act-latest`
- `wuodan/aicage-base:ubuntu-base-dev` (pulled automatically by the agent images)

## Quick start (use prebuilt images)

```bash
# Pull an image
docker pull wuodan/aicage:codex-ubuntu-latest

# Run a shell with your API key injected and a user matching your host UID/GID
docker run -it --rm \
  -e OPENAI_API_KEY=sk-... \
  -e AICAGE_UID=$(id -u) \
  -e AICAGE_GID=$(id -g) \
  -e AICAGE_USER=$(id -un) \
  -v "$(pwd)":/workspace \
  wuodan/aicage:codex-ubuntu-latest \
  bash
```

Swap `codex` for `cline` or `droid`, and use the base alias from `.env` (e.g., `act` or `ubuntu`).

The image boots as root, then `scripts/entrypoint.sh` creates a matching user/group from
`AICAGE_UID`/`AICAGE_GID` (defaults `1000`) and switches into it with `gosu`. `/workspace` is
created and chowned to that user.

## Base images

Base images are built once per upstream base and published to Docker Hub separately from the final
agent images. They are tagged `${AICAGE_BASE_REPOSITORY}:<base-alias>-<AICAGE_VERSION>` (defaults to
`wuodan/aicage-base:ubuntu-dev` and `wuodan/aicage-base:act-dev`).

Build locally:

```bash
# Build a single base (loads locally)
base-images/scripts/build.sh --base ubuntu:24.04 --platform linux/amd64

# Build all bases (loads locally)
base-images/scripts/build-all.sh --platform linux/amd64

# Run base smoke tests against local or pulled images
base-images/scripts/test-all.sh
```

Publish flow:

- Base pipeline: `.github/workflows/build-base.yml` (pushes to Docker Hub on `base-*` tags).
- Agent pipeline: `.github/workflows/build-publish.yml` (pushes agent images on tags via
  `final-images` scripts, consuming the published base images).

## Final images (agents)

Agent builds now live under `final-images/`. Commands:

```bash
# Build and load a single agent image
final-images/scripts/build.sh --tool codex --base ubuntu:24.04 --platform linux/amd64

# Build the full matrix
final-images/scripts/build-all.sh --platform linux/amd64

# Run smoke tests
final-images/scripts/test-all.sh
```
