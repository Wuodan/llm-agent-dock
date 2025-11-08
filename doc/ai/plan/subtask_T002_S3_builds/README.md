# Task T002 / Subtask S3 — Matrix Builds

## Objective
Execute `scripts/build.sh <tool> <base>` for required matrix slices (minimum: ubuntu base for each tool) and capture reproducible logs/config overrides.

## Deliverables
- Successful build logs per tool/base stored or referenced from the plan (include command, timestamp, outcome).
- Notes on any failures with triage details and next actions.
- Updated checklist documenting coverage status (ubuntu minimum + stretch matrix entries if time permits).

## Flow
1. Select target order (e.g., codex-ubuntu → cline-ubuntu → factory_ai_droid-ubuntu) and record it in the plan.
2. Run `scripts/build.sh` with necessary flags (`--load`, `--set`, etc.); capture stdout/stderr locally (outside the repo) if additional debugging artifacts are required.
3. After each build, update the checklist + Feedback with pass/fail info and artifact locations.
4. Iterate on additional bases/architectures once ubuntu baseline succeeds.

## Findings (2025-11-08)
- Commands executed: `scripts/build.sh codex ubuntu --platform linux/amd64 --load`, then the same for `cline` and `factory_ai_droid`. Each produced a local tag `ghcr.io/wuodan/llm-agent-dock:<tool>-ubuntu-latest` for S4.
- Failure history (summarized; raw logs were discarded per user direction):
  - Codex builds initially failed under Debian’s PEP 668 protections plus a `wheel` uninstall error—resolved by adding `--break-system-packages --ignore-installed` to the pip upgrade.
  - Cline required `make`/`g++` for `better-sqlite3`; adding `build-essential` fixed the node-gyp failure.
  - Factory AI Droid only ships the `droid-factory` binary today; the installer now wraps whichever CLI is present so smoke tests still find `factory_ai_droid`.

## Checklist
- [x] Build `codex-ubuntu`.
- [x] Build `cline-ubuntu`.
- [x] Build `factory_ai_droid-ubuntu`.
- [ ] (Stretch) Build additional base/tool pairs as time permits.
- [x] Record results/notes + open issues.

## Inputs & References
- `scripts/build.sh`
- `docker-bake.hcl`
- `doc/ai/tasks/T002_validate-builds-docker/README.md`

## Exit Criteria
- Ubuntu images for all tools built or blocked with documented evidence/logs.

## Feedback & Learnings
- **Open Problems**:
  - Stretch coverage (act/universal bases) still pending if time allows.
- **Questions**:
  - None now that ubuntu slice is stable.
- **Learnings**:
  - Debian 12+/Ubuntu 24 base images enforce PEP 668; use `pip --break-system-packages --ignore-installed` when upgrading core tooling.
  - Node CLIs with native addons (cline) require build chain packages inside the image; ship `build-essential` by default to avoid brittle installs.
  - For lesser-known CLIs, keep a fallback shim/wrapper pattern so smoke tests still locate a binary even if package names drift.
