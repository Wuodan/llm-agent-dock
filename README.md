# aicage

Docker images for popular AI coding agents, built from a single, repeatable recipe. Pick a tool and
base OS, pull the tag, and you get a ready-to-run shell with the agent preinstalled.

## What you get
- Prebuilt tags for `cline`, `codex`, and `droid`.
- Base choices: `ubuntu` (24.04) and `act` (CI-friendly).
- Multi-arch images (`linux/amd64` and `linux/arm64`) via Buildx.
- Thin images: agent install only; you bring your own API keys.

## Image tags
Tags follow `${REPOSITORY}:<tool>-<base>-<version>`.

Default repo: `wuodan/aicage` on Docker Hub.

Examples:
- `wuodan/aicage:codex-ubuntu-latest`
- `wuodan/aicage:cline-act-latest`

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

Swap `codex` for `cline` or `droid`, and `ubuntu` for `act` as needed.

The image boots as root, then `scripts/entrypoint.sh` creates a matching user/group from
`AICAGE_UID`/`AICAGE_GID` (defaults `1000`) and switches into it with `gosu`. `/workspace` is
created and chowned to that user.
