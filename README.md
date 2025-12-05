# llm-agent-dock

Docker images for popular AI coding agents, built from a single, repeatable recipe. Pick a tool and
base OS, pull the tag, and you get a ready-to-run shell with the agent preinstalled.

## What you get
- Prebuilt tags for `cline`, `codex`, and `factory_ai_droid`.
- Base choices: `ubuntu` (24.04), `act` (CI-friendly), and `universal` (Dev Container base).
- Multi-arch images (`linux/amd64` and `linux/arm64`) via Buildx.
- Thin images: agent install only; you bring your own API keys.

## Image tags
Tags follow `${REGISTRY}/${REPOSITORY}:<tool>-<base>-<version>`.

Default registry/repo: `ghcr.io/wuodan/llm-agent-dock`.

Examples:
- `ghcr.io/wuodan/llm-agent-dock:codex-ubuntu-latest`
- `ghcr.io/wuodan/llm-agent-dock:cline-act-latest`

## Quick start (use prebuilt images)
```bash
# Pull an image
docker pull ghcr.io/wuodan/llm-agent-dock:codex-ubuntu-latest

# Run a shell with your API key injected
docker run -it --rm \
  -e OPENAI_API_KEY=sk-... \
  ghcr.io/wuodan/llm-agent-dock:codex-ubuntu-latest \
  bash
```

Swap `codex` for `cline` or `factory_ai_droid`, and `ubuntu` for `act` or `universal` as needed.

## Build locally
Prerequisites: Docker with Buildx, and (for multi-arch) binfmt/QEMU.

```bash
# One-time setup: create a buildx builder, seed .env defaults, and enable binfmt
scripts/dev/bootstrap.sh

# Build a single variant (loads into your local image store)
scripts/build.sh codex ubuntu --platform linux/amd64 --load
```

`scripts/build.sh` tags images as `${LLM_AGENT_DOCK_REGISTRY}/${LLM_AGENT_DOCK_REPOSITORY}:<tool>-<base>-<version>`.
Edit `.env` to change registry/repo/version/platform defaults.

## Smoke tests
Smoke suites live in `tests/smoke/` (one per tool). After building or pulling an image, run:

```bash
scripts/test.sh ghcr.io/wuodan/llm-agent-dock:codex-ubuntu-latest --tool codex
```

Use `--no-pull` to test a locally built image. Install `bats` if you plan to run the suites.

## Need to hack on this?
Developer-focused docs live in `doc/DEVELOPMENT.md` (scripts, tagging, adding bases/tools, testing
expectations).
