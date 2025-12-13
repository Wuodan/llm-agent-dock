# AI Agent Playbook

Audience: AI coding agents working in this repository (including submodules). Keep user-facing docs
clean and follow development guidance in `DEVELOPMENT.md` for commands and workflows.

## Ground rules

- Stay within the repo’s conventions: Bash scripts use `#!/usr/bin/env bash`, `set -euo pipefail`,
  and two-space indents; Dockerfiles declare args at the top and keep steps POSIX-friendly;
  Markdown wraps near ~100 chars.
- Prefer `rg` for searches; avoid reverting changes you did not make.
- Respect the separation of concerns: `README.md` is user-only; put build/test/process details into
  `DEVELOPMENT.md`.

## Where to work

- Base images live in `aicage-image-base/` with their own `README.md`, `DEVELOPMENT.md`, and
  `AGENTS.md`.
- Agent images live in `aicage-image/` with the same doc set.
- Use the per-repo development guides for exact commands, env vars, and test matrices.

## Testing expectations

- Run the relevant smoke suites after changing build or runtime behavior:
  - Base images: `aicage-image-base/scripts/test-all.sh`
  - Agent images: `aicage-image/scripts/test-all.sh`
- Note any skipped tests or platform limits when you cannot execute them.

## Style and quality

- Keep changes minimal and well explained in commit messages and PR descriptions.
- Add brief comments only where behavior is non-obvious; avoid restating code.
- When adding tools or bases, ensure corresponding smoke coverage is updated or created.
