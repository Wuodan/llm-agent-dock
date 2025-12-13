# aicage

Prebuilt Docker images for popular AI coding agents. Pick a tool, choose a base OS, and start a
container with a user that matches your host IDs.

## Images at a glance

- Agents: `cline`, `codex`, and `droid`.
- Bases: aliases published from `wuodan/aicage-image-base` (e.g., `ubuntu`, `fedora`, `act`).
- Tags live at `wuodan/aicage` and support `linux/amd64` and `linux/arm64`.
- Images are thin: the agent is installed, you provide API keys at runtime.

## Tag format

- `${AICAGE_REPOSITORY:-wuodan/aicage}:<tool>-<base>-<version>` (e.g., `codex-ubuntu-latest`).
- Base layers come from `${AICAGE_BASE_REPOSITORY:-wuodan/aicage-image-base}:<base>-<version>`.
- `<base>-latest` tags are convenience aliases discovered from the base repository.

## Quick start

```bash
docker pull wuodan/aicage:codex-ubuntu-latest

docker run -it --rm \
  -e OPENAI_API_KEY=sk-... \
  -e AICAGE_UID=$(id -u) \
  -e AICAGE_GID=$(id -g) \
  -e AICAGE_USER=$(id -un) \
  -v "$(pwd)":/workspace \
  wuodan/aicage:cline-ubuntu-latest
```

Swap `codex` for `cline` or `droid`, and switch `ubuntu` to any available base alias.

## Runtime behavior

- Containers start as root, then `scripts/entrypoint.sh` creates a user from `AICAGE_UID`/`AICAGE_GID`/
  `AICAGE_USER` (defaults `1000`/`1000`/`aicage`) and switches into it with `gosu`.
- `/workspace` is created and owned by that user; mount your project there.

## Related repositories

- Base layers: `aicage-image-base` builds `${AICAGE_BASE_REPOSITORY}` tags.
- Final agent images: `aicage-image` consumes base layers and publishes `${AICAGE_REPOSITORY}` tags.
- Want to build or extend the images? See `DEVELOPMENT.md` in each repo for contributor guidance.
