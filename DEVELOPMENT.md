# Development Guide

This repo ships the `aicage` CLI. Image build logic lives in the submodules; this file is for
advanced/power users who want to tweak or extend things.

## Repo layout

- [README.md](README.md): end-user overview.
- [AGENTS.md](AGENTS.md): instructions for AI coding agents.
- `src/`: the `aicage` CLI implementation.
- `tests/`: Python tests for the CLI.
- `scripts/`: helper scripts.
- `doc/`: task notes for AI agents.

## Related projects (build docker images)

- [aicage-image-base/](https://github.com/aicage/aicage-image-base): builds base OS layers.
- [aicage-image/](https://github.com/aicage/aicage-image): builds tools/coding agents on those bases.
