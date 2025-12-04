# Repository Guidelines

## Project Layout
- `Dockerfile`, `docker-bake.hcl`: build matrix for base × tool variants.
- `scripts/`: build/test helpers (`dev/bootstrap.sh`, `build.sh`, `test.sh`).
- `tests/smoke/`: Bats smoke suites per tool.
- `doc/`: user-facing docs and optional lightweight task notes.

## Build & Test
- Bootstrap (when needed): `scripts/dev/bootstrap.sh`
- Build a variant: `scripts/build.sh <tool> <base> [--platform linux/amd64 --load]`
- Test an image: `scripts/test.sh <image-ref> [--tool <name>] [--no-pull]`
- Helpful prereqs: `docker info`, `bats --version`

## Coding Style
- Bash: `#!/usr/bin/env bash`, `set -euo pipefail`, two-space indent, descriptive functions.
- Dockerfile: args at top (`BASE_IMAGE`, `TOOL`, `TARGETARCH`), POSIX-friendly steps, comment extension points.
- HCL/JSON: snake_case variables, kebab-case Bake targets.
- Markdown: ~100-char wrap, tables for matrix summaries.

## Testing Expectations
- Prefer `tests/smoke/*.bats` for tool coverage; name tests `test_<feature>`.
- When changing scripts or Docker build behavior, run the relevant smoke tests and note the command used.
