# Repository Guidelines

## Project Layout

- `aicage-image-base/`: submodule with base Dockerfile, Bake file, scripts, and smoke tests.
- `aicage-image/`: submodule with final agent Dockerfile, Bake file, scripts, and smoke tests.
- `doc/`: user-facing docs and optional lightweight task notes.

## Build, Test, and Development Commands

- Python venv: `python -m venv .venv && source .venv/bin/activate` – create and use a clean interpreter.
- Python requirements: run `pip install -r requirements-dev.txt` in whichever repo you are working on
  (`aicage-image/` or `aicage-image-base/`) to pull lint/test tooling.
- Python linting: `ruff check` – enforce python formatting and import hygiene; use `--fix` for autofixes.
- Markdown linting: `pymarkdown --config .pymarkdown.json scan .` – check markdown formatting. For tables with
  long lines, wrap them into `<!-- pyml disable/enable line-length, no-bare-urls -->`
- Run Python tests (if present): `pytest --cov=src --cov-report=term-missing`.
- Build base: `(cd aicage-image-base && scripts/build.sh --base <ref> [--platform linux/amd64])`
- Build agent: `(cd aicage-image && scripts/build.sh --tool <tool> --base <base> [--platform linux/amd64])`
- Test base: `(cd aicage-image-base && scripts/test-all.sh)`
- Test agent: `(cd aicage-image && scripts/test-all.sh)`
- Test GitHub pipeline: `(cd aicage-image && act -W .github/workflows/final-images.yml -P ubuntu-latest=ghcr.io/catthehacker/ubuntu:act-latest)`

## Coding Style

- Bash: `#!/usr/bin/env bash`, `set -euo pipefail`, two-space indent, descriptive functions.
- Dockerfile: args at top (`BASE_IMAGE`, `TOOL`, `TARGETARCH`), POSIX-friendly steps, comment extension points.
- HCL/JSON: snake_case variables, kebab-case Bake targets.
- Markdown: ~100-char wrap, tables for matrix summaries.

## Testing Expectations

- Prefer `aicage-image/tests/smoke/*.bats` for agent coverage; name tests `test_<feature>`.
- Prefer `aicage-image-base/tests/smoke/*.bats` for base coverage.
- When changing scripts or Docker build behavior, run the relevant smoke tests and note the command used.
