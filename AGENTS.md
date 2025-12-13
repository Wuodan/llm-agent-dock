# Repository Guidelines

## Project Layout

- `aicage-base/`: submodule with base Dockerfile, Bake file, scripts, and smoke tests.
- `final-images/`: agent Dockerfile, Bake file, scripts, and smoke tests.
- `doc/`: user-facing docs and optional lightweight task notes.

## Build, Test, and Development Commands

- Python venv: `python -m venv .venv && source .venv/bin/activate` – create and use a clean interpreter.
- Python requirements: `pip install -r requirements-dev.txt` – pull runtime plus lint/test tooling.
- Python linting: `ruff check` – enforce python formatting and import hygiene; use `--fix` for autofixes.
- Markdown linting: `pymarkdown --config .pymarkdown.json scan .` – check markdown formatting. For tables with
  long lines, wrap them into `<!-- pyml disable/enable line-length, no-bare-urls -->`
- Run Python tests: `pytest --cov=src --cov-report=term-missing` – test python code.
- Build base: `(cd aicage-base && scripts/build.sh --base <ref> [--platform linux/amd64])`
- Build agent: `final-images/scripts/build.sh --tool <tool> --base <base> [--platform linux/amd64]`
- Test base: `(cd aicage-base && scripts/test-all.sh)`
- Test agent: `final-images/scripts/test-all.sh`
- Test GitHub pipeline: `act`

## Coding Style

- Bash: `#!/usr/bin/env bash`, `set -euo pipefail`, two-space indent, descriptive functions.
- Dockerfile: args at top (`BASE_IMAGE`, `TOOL`, `TARGETARCH`), POSIX-friendly steps, comment extension points.
- HCL/JSON: snake_case variables, kebab-case Bake targets.
- Markdown: ~100-char wrap, tables for matrix summaries.

## Testing Expectations

- Prefer `final-images/tests/smoke/*.bats` for agent coverage; name tests `test_<feature>`.
- Prefer `aicage-base/tests/smoke/*.bats` for base coverage.
- When changing scripts or Docker build behavior, run the relevant smoke tests and note the command used.
