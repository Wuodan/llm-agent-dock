# Repository Guidelines

These instructions are intentionally task-agnostic. Every future effort in this repo should follow
the workflow hardening and coding conventions below to keep hand-offs simple and recoverable.

## Workflow Hardening
- **Planning trail**: For every task `T###`, scaffold `doc/ai/tasks/T###_<slug>/plan/README.md` (start from
  `doc/ai/templates/task_plan_README.template.md`) plus one subfolder per subtask (copy
  `doc/ai/templates/subtask_plan_README.template.md`). Each plan file needs objective, deliverables,
  flow, checklist, explicit “commit `[codex][subtask-name]: summary`” step, and a Feedback section
  updated at completion.
- **Checkpointing**: Update plan checklists immediately after any progress. A stopped laptop should
  only need the latest checklist state to resume.
- **Research logs**: When using MCP `brave-search` or `fetch`, capture URLs + summaries in the
  relevant subtask doc (or under `doc/ai/research/` if reused later). Avoid repeating lookups.
- **Commits per subtask**: Finish each subtask with `[codex][subtask-name]: summary`. Never mix
  unrelated work in a single commit.
- **Status visibility**: Keep a progress log in the root plan so new agents can inspect the latest
  timestamp and continue confidently.
- **Task catalog**: Number tasks as `T###` (e.g., `T001`) and track them under
  `doc/ai/tasks/README.md`. Each task owns a folder `doc/ai/tasks/T###_<slug>/` whose `README.md`
  holds the canonical brief. Mark the active task as `Status = Active` in the index. Every task doc
  (and each subtask file) needs a Feedback section with open problems, outstanding questions, and
  learnings for future sessions.

### Planning Templates
- Task-level plan template: `doc/ai/templates/task_plan_README.template.md`
- Subtask plan template: `doc/ai/templates/subtask_plan_README.template.md`
- Always copy these templates when creating new task or subtask plan files and keep the commit +
  feedback checklist items intact.

## Project Structure & Ownership
- Root `Dockerfile` stays parameterized via `BASE_IMAGE`, `TOOL`, and `TARGETARCH` so the same
  definition feeds every variant. Extension points must be commented (`# Add new agent installers
  below`).
- `docker-bake.hcl` owns the base×tool×arch matrix. Add new targets under the `matrix` group and
  document tag formats inline for quick audits.
- `scripts/` stores reproducible helpers (`dev/bootstrap.sh`, `build.sh`, `test.sh`, optional
  `lint.sh`). Any behavior change must be mirrored in README usage docs.
- `tests/` (prefer `tests/smoke/*.bats`) validates container boot, agent binaries, and required CLIs.
- Each `doc/ai/tasks/T###_<slug>/plan/` folder captures planning artifacts; never delete history—append
  timestamped entries so other agents can replay decisions.

## Build, Test, and Development Commands
- Use `docker buildx bake -f docker-bake.hcl matrix --set "*.platform=linux/amd64,linux/arm64"` to
  build the full grid; scope with `matrix.<target>` when iterating.
- `scripts/dev/bootstrap.sh` provisions BuildKit builders, QEMU emulation, and `.env` defaults; rerun
  after Docker upgrades or new hosts.
- `scripts/build.sh <tool> <base>` should wrap Bake with validation and support overrides for
  registry, tag, and platform.
- `scripts/test.sh <image-ref>` pulls (or builds) the given image and runs all smoke tests.
- Before invoking build/test scripts, run `docker info` and `bats --version`; log the output in the
  active plan. If the Docker socket is unavailable, follow the README troubleshooting steps
  (docker group, rootless Docker, or remote builder) and document the outcome.
- When iterating locally without a multi-arch builder, prefer
  `scripts/build.sh <tool> <base> --platform linux/amd64 --load` followed by
  `scripts/test.sh <image> --tool <name> --no-pull` so smoke tests run against the freshly built
  image.

## Coding Style & Naming Conventions
- Bash scripts: `#!/usr/bin/env bash`, `set -euo pipefail`, two-space indentation, descriptive
  function names (`build_matrix`, `push_variant`). Lint with `shellcheck`/`shfmt`.
- Dockerfiles: declare ARGs at the top, then base OS prep, then tool install steps. Keep logic
  POSIX-friendly for BuildKit portability.
- HCL/JSON: snake_case variables, kebab-case Bake targets (e.g., `cline-arm64`).
- Markdown: title case headings, wrap lines at ~100 chars, favor tables for matrix summaries.

## Testing Guidelines
- Tests rely on `bats` (or lightweight Bash) inside `tests/smoke/`; each file mirrors a tool
  (`cline.bats`, `codex.bats`, etc.).
- Name tests `test_<feature>` and cover container boot, agent CLI response, and required OS packages.
- `scripts/test.sh --all` (or equivalent) should gate merges so both architectures are sampled at
  least weekly.

## Commit, PR, and Review Expectations
- Commit subject format: `[codex][subtask-name]: summary` with wrapped bodies ≤72 chars.
- PR descriptions must list affected matrix slices, commands executed, and links to governing tasks
  or planning docs. Include logs or screenshots only when diagnosing failures.
- Cross-reference planning docs (`doc/ai/tasks/T###_<slug>/plan/*.md`) whenever scope changes so reviewers can trace
  intent quickly.

## Security & Configuration Tips
- Keep secrets (registry tokens, SSH keys) out of Bake variables; inject via `docker buildx bake
  --set *.secrets` or CI secrets managers.
- Pin base images to digests during releases to avoid upstream drift; refresh digests quarterly or
  when security advisories land.
- Validate licenses and telemetry defaults before merging new agents or tooling. Document any
  opt-out steps directly in the Dockerfile comments and README.
