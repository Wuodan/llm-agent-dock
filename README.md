# aicage

Docker images for popular AI coding agents, built from a single, repeatable recipe. Pick a tool and
base OS, pull the tag, and you get a ready-to-run shell with the agent preinstalled.

## What you get

- Prebuilt tags for `cline`, `codex`, and `droid`.
- Base choices live in the `aicage-base` submodule (`bases/<alias>/base.yaml` → upstream image +
  installer).
- Multi-arch images (`linux/amd64` and `linux/arm64`) via Buildx.
- Thin images: agent install only; you bring your own API keys.

## Image tags

Tags follow `${REPOSITORY}:<tool>-<base-alias>-<version>`.

Default repo: `wuodan/aicage` on Docker Hub. Base layers live separately at
`wuodan/aicage-base` and are pulled by the agent builds.

Tools and platforms are configured in `.env`. Base aliases come from tags on
`${AICAGE_BASE_REPOSITORY}:*-latest` (discovered automatically); their definitions live in the
`aicage-base/bases/` folders (alias = folder name, `base.yaml` describes upstream image and
installer script).

Examples:

- `wuodan/aicage:codex-ubuntu-latest`
- `wuodan/aicage:cline-fedora-latest`
- `wuodan/aicage-base:codex-act-latest` (pulled automatically by the agent images)

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
`wuodan/aicage-base:fedora-dev` and `wuodan/aicage-base:node-dev`). The `aicage-base` repo is a
submodule here; all base-only sources and scripts live there.

Build locally:

```bash
# Build a single base (loads locally)
cd aicage-base && scripts/build.sh --base fedora --platform linux/amd64

# Build all bases (loads locally)
cd aicage-base && scripts/build-all.sh --platform linux/amd64

# Run base smoke tests against local or pulled images
cd aicage-base && scripts/test-all.sh
```

Publish flow:

- Base pipeline: `aicage-base/.github/workflows/base-images.yml` (tags only; pushes to Docker Hub).
- Agent pipeline: `.github/workflows/final-images.yml` (tags only; pushes agent images, consuming
  whatever `${AICAGE_BASE_REPOSITORY}:*-latest` tags Docker Hub exposes).

## Final images (agents)

Agent builds now live under `final-images/`. Commands:

```bash
# Build and load a single agent image
final-images/scripts/build.sh --tool codex --base ubuntu --platform linux/amd64

# Build the full matrix
final-images/scripts/build-all.sh --platform linux/amd64

# Run smoke tests
final-images/scripts/test-all.sh
```
