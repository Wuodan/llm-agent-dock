# Repository Guidelines

These instructions are intentionally task-agnostic. Every future effort in this repo should follow
the workflow hardening and coding conventions below to keep hand-offs simple and recoverable.

## Workflow Hardening
- **Planning trail**: For every task `T###`, scaffold `doc/ai/tasks/T###_<slug>/plan/README.md` (start from
  `doc/ai/templates/task_plan_README.template.md`) plus one subfolder per subtask (copy
  `doc/ai/templates/subtask_plan_README.template.md`). Each plan file needs objective, deliverables,
  flow, checklist, explicit “commit `T###/S###: short summary`” step, and a Feedback section updated at
  completion.
- **Checkpointing**: Update plan checklists immediately after any progress. A stopped laptop should
  only need the latest checklist state to resume.
- **Research logs**: When using MCP `brave-search` or `fetch`, capture URLs + summaries in the
  relevant subtask doc (or under `doc/ai/research/` if reused later). Avoid repeating lookups.
- **Documentation hygiene**: Do not paste chat/discussion transcripts into repository documents; summarize outcomes and link to sanitized logs instead.
- **Commits per subtask**: Finish each subtask with `T###/S###: short summary`, where `S###` is the
  zero-padded subtask index (use `S000` for task-level commits when no subtask exists). Never mix
  unrelated work in a single commit.
- **Python tooling**: Activate the repo venv (`source .venv/bin/activate`) whenever you need the
  `python` command; the commit hook depends on `.venv/bin/python` being available.
- **Commit lint hook**: Run `git config core.hooksPath githooks` once per clone to enable the tracked
  `commit-msg` hook. It calls `devtools/check_commit_message.py` (via `.venv/bin/python`) to block
  subjects that do not match `T###/S###: short summary`.
- **Status visibility**: Keep a progress log in the root plan so new agents can inspect the latest
  timestamp and continue confidently.
- **Task catalog**: Number tasks as `T###` (e.g., `T001`) and track them under
  `doc/ai/tasks/README.md`. Each task owns a folder `doc/ai/tasks/T###_<slug>/` whose `README.md`
  holds the canonical brief. Mark the active task as `Status = Active` in the index. Every task doc
  (and each subtask file) needs a Feedback section with open problems, outstanding questions, and
  learnings for future sessions.

### Branch Workflow (Tasks & Subtasks)
1. **Start from `development`**: Before creating a task branch, run `git checkout development` and
   `git pull --ff-only origin development` so you branch from the latest tip.
2. **Task branch naming**: Create exactly one branch per active task named `task/T###_<slug>` (slug
   matches the task folder). Push it immediately via `git push -u origin task/T###_<slug>`—no work
   happens directly on `development`.
3. **Subtask branches**: For each subtask, branch from the task branch tip using
   `subtask/T###_S#_<slug>` (example: `subtask/T004_S1_branch-policy`). Push on creation so remote
   history mirrors the plan log.
4. **Push cadence**: Push after creation, after every meaningful checkpoint (tests run, major edits),
   and before ending a session. If you cannot push (offline), record the reason + next steps in the
   task plan progress log and push as soon as connectivity returns.
5. **Merge flow (`git merge --no-ff`)**: All merges happen locally. Subtasks merge into their task
   branch, and tasks merge into `development`. Always `git pull --ff-only origin <parent>` before the
   merge, run the required validations, `git merge --no-ff <child>`, resolve conflicts locally, rerun
   tests, then `git push origin <parent>`.
6. **Verification & deletion**: Only delete branches after confirming the merge exists locally and on
   origin (`git branch --merged`, `git log --oneline origin/<parent>`). Delete both local and remote
   refs (`git branch -d <child>`, `git push origin --delete <child>`) and update the plan checklist
   immediately.
7. **Force pushes**: `git push --force*` is forbidden on `development` and task branches. It is
   allowed on an unpublished subtask branch only to fix mistakes before hand-off or to excise
   sensitive data, and the plan’s Feedback section must record the reason.

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
- Commit subject format: `T###/S###: short summary` (≤72 chars). Example: `T004/S001: Add branch
  workflow policy`. `S###` is zero-padded (`S001`, `S002`, …); use `S000` for task-wide commits if no
  subtask applies.
- Use `.venv/bin/python devtools/check_commit_message.py --message "T123/S045: Example"` (or pass a
  commit message file) to lint manually; the `githooks/commit-msg` hook runs the same script
  automatically.
- PR descriptions must list affected matrix slices, commands executed, and links to governing tasks
  or planning docs. Include logs or screenshots only when diagnosing failures.
- Cross-reference planning docs (`doc/ai/tasks/T###_<slug>/plan/*.md`) whenever scope changes so
  reviewers can trace intent quickly.
- When merging, prefer local `git merge --no-ff` so the history shows explicit task/subtask
  milestones. Note the branch names and merge commit in the active plan’s progress log before
  deleting child branches.

## Security & Configuration Tips
- Keep secrets (registry tokens, SSH keys) out of Bake variables; inject via `docker buildx bake
  --set *.secrets` or CI secrets managers.
- Pin base images to digests during releases to avoid upstream drift; refresh digests quarterly or
  when security advisories land.
- Validate licenses and telemetry defaults before merging new agents or tooling. Document any
  opt-out steps directly in the Dockerfile comments and README.
