# Task T002 — Validate llm-agent-dock Builds & Docker Access

## Background
- Task T001 delivered the parameterized Dockerfile, Bake matrix, helper scripts, smoke tests, and documentation.
- No real images were built because the container user lacked access to `/var/run/docker.sock`.
- Smoke tests could not run because `bats` was missing. The host will provide `bats` before this task begins.
- The next session must focus on executing the automation end-to-end and documenting how to grant Docker access when working under similar constraints.

## Goals
1. Verify that host prerequisites are satisfied (Docker daemon permissions + `bats`).
2. Execute `scripts/build.sh <tool> <base>` for representative matrix entries (at least one per tool) and capture logs.
3. Run `scripts/test.sh` for every tool using the images produced above; document results and failures.
4. Produce guidance for enabling Docker socket access in constrained environments (or document the escalation path if host changes are required).
5. Update README/plan docs with validated commands, known issues, and any additional troubleshooting notes.

## Scope & Deliverables
- Use the existing matrix: bases (`act`, `universal`, `ubuntu`) × tools (`cline`, `codex`, `factory_ai_droid`).
- At minimum, build `ubuntu`-based images for each tool; stretch goal is full matrix coverage.
- Smoke tests (`tests/smoke/*.bats`) must pass for every tool or have documented blockers.
- Provide build/test logs or summaries in the Feedback section and planning docs.

## Workflow Expectations
1. **S1 Planning & Environment Check** — Create/refresh planning artifacts for T002 (new `doc/ai/tasks/T002_validate-builds-docker/plan/` entries or an addendum) capturing prerequisites and risks.
2. **S2 Docker Access Enablement** — Determine whether Docker socket access is already available; if not, outline the exact steps (group membership, rootless Docker, etc.) and work with the host to enable it.
3. **S3 Matrix Builds** — Run `scripts/build.sh` for selected targets (start with `codex ubuntu amd64`) and expand coverage once stable.
4. **S4 Smoke Tests** — Execute `scripts/test.sh <image>` for each tool; include `--tool` filtering to speed up iteration when necessary.
5. **S5 Documentation & Handoff** — Update README, AGENTS, and planning docs with validated commands, log locations, and any long-term lessons.

## Prerequisites & Assumptions
- `bats` should be installed on the host before starting this task (`bats --version` should succeed).
- Docker access is still uncertain. First action is to run `docker info` to confirm permissions; if it fails, capture the error and document the remediation steps.
- Existing automation assumes internet access to npm registries for agent installers; coordinate with the host if additional proxies are required.

## References
- Task T001 artifacts: `doc/ai/tasks/T001_llm-agent-dock-matrix-builder/README.md`.
- Planning/log context: `doc/ai/tasks/T002_validate-builds-docker/plan/README.md` and its subtask folders (S1–S5).
- Automation entry points: `scripts/dev/bootstrap.sh`, `scripts/build.sh`, `scripts/test.sh`.

## Execution Summary — 2025-11-08
- Docker access verified after enabling the danger-full-access sandbox (`docker info` now succeeds).
- Built ubuntu variants for every tool via `scripts/build.sh <tool> ubuntu --platform linux/amd64 --load`, producing local tags `ghcr.io/wuodan/llm-agent-dock:<tool>-ubuntu-latest` for codex, cline, and factory_ai_droid.
- Smoke tests ran with `scripts/test.sh ghcr.io/wuodan/llm-agent-dock:<tool>-ubuntu-latest --tool <tool> --no-pull`; all suites passed once the factory shim fix landed.
- Notable fixes itemized here so they’re easy to recreate without raw logs:
  - Added `build-essential` to satisfy Cline’s native module build (better-sqlite3).
  - Used `python3 -m pip install --break-system-packages --ignore-installed …` to appease Debian’s PEP 668 enforcement.
  - Factory AI Droid installer now drops a wrapper around whichever CLI binary (`droid`, `factory-ai`, `droid-factory`) is available, so smoke tests can locate `factory_ai_droid` even when scoped packages 404.

## Feedback — Open Problems, Questions, Learnings
- **Open Problems**
  - Stretch work: replicate the same build/test validation for the `act` and `universal` bases (ubuntu slice is done).
  - Multi-arch pushes still depend on a remote builder or QEMU setup; current runs used `--platform linux/amd64 --load` for local smoke testing only.
- **Questions**
  - Which registry should host published images once builds succeed? (Currently defaults to `ghcr.io/wuodan/llm-agent-dock`.)
  - Are there SLAs for how many matrix combinations must be built per run (subset vs. entire 9 variants)?
- **Learnings**
  - Document a Docker-access checklist upfront (run `docker info`, fall back to docker group/rootless/remote builder) and link it from README Troubleshooting.
  - Debian/Ubuntu bases enforce PEP 668; pair `--break-system-packages` with `--ignore-installed` when upgrading pip/setuptools/wheel.
  - Shipping `build-essential` (or at least `make`/`g++`) keeps Node CLIs with native addons working out of the box, and the wrapper pattern ensures smoke tests still find `factory_ai_droid` when npm packages move around.
