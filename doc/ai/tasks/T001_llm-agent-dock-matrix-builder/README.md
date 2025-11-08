# Task T001 — Build the llm-agent-dock Matrix Builder

> This README mirrors `doc/ai/TASK.md`. Edit both files together so the active task description stays
> consistent regardless of entry point.

## Background
This repository must evolve into a reusable multi-architecture Docker build system for agentic
developer tools. The system combines “fat” public base images with thin tool-specific layers and
delivers every permutation via a matrix build.

## Goals
1. Produce a parameterized Dockerfile that installs any supported tool on top of any supported base.
2. Define a `docker-bake.hcl` matrix plus helper scripts to build, test, and publish multi-arch
   images.
3. Create smoke tests that assert containers boot, agent binaries respond, and critical CLIs exist.
4. Document structure, workflows, and extension steps so future contributors can resume instantly.

## Scope (initial matrix, extendable)

| Base Alias | Image Reference                                |
|------------|------------------------------------------------|
| `act`      | `ghcr.io/catthehacker/ubuntu:act-latest`       |
| `universal`| `ghcr.io/devcontainers/images/universal:2-linux` |
| `ubuntu`   | `ubuntu:24.04`                                 |

| Tool Key          | Description            |
|-------------------|------------------------|
| `cline`           | Cline CLI / VSCode AI  |
| `codex`           | Codex coding agent     |
| `factory_ai_droid`| Factory.AI Droid agent |

Platforms: `linux/amd64`, `linux/arm64`. Every combination base×tool×arch must be addressable from a
single configuration.

## Required Workflow (non-negotiable)
1. **Planning first**: Author `doc/ai/plan/README.md` plus one subfolder per subtask (S1–S5). Each
   file records objectives, deliverables, flow, checklist, and feedback.
2. **Subtasks**:
   - S1 Planning & scaffolding.
   - S2 Parameterized Dockerfile + installer research.
   - S3 Matrix + scripts (Bake, bootstrap, build, test).
   - S4 Smoke tests.
   - S5 Documentation & polish.
3. **Checkpointing**: Update checklists and logs immediately after progress so work can resume after
   interruptions.
4. **Research logging**: When agent installer details are unclear, use MCP `brave-search` followed by
   `fetch`; summarize findings and URLs inside the relevant subtask doc (or `doc/ai/research/` if
   shared).
5. **Commits**: Complete each subtask with a dedicated commit using `[codex][subtask-name]: summary`
   and include references to the updated plan docs.

## Deliverables & Acceptance Criteria
1. `Dockerfile` — uses `ARG BASE_IMAGE`, `ARG TOOL`, `ARG TARGETARCH`; includes shared base prep,
   tool installers, and commented extension hooks.
2. `docker-bake.hcl` — defines matrix targets, registry/tag variables, and documentation inline.
3. `scripts/dev/bootstrap.sh`, `scripts/build.sh`, `scripts/test.sh` — reproducible helpers described
   in README.
4. `tests/smoke/` — Bats suites per tool plus helpers; runnable via `scripts/test.sh`.
5. `README.md` — intro, architecture description, matrix summary, quick-start commands, extension
   guide, testing instructions.
6. `doc/ai/plan/` — up-to-date plan, subtask logs, and feedback entries for each phase.

Definition of done:
- Matrix builds succeed locally via `docker buildx bake ... --print` and at least one real build.
- Smoke tests execute against a built image without fatal errors (document gaps if tooling missing).
- Documentation matches implemented behavior and lists commands to reproduce results.
- No pending checklist items in any subtask doc.

## Sequencing
1. Plan & scaffolding (S1) → Dockerfile (S2) → Bake/scripts (S3) → Tests (S4) → Documentation (S5).
2. Each stage must update the master plan log with timestamps.
3. If new bases/tools are introduced mid-task, append them to the Scope tables and adjust scripts,
   tests, and docs accordingly before proceeding.

## Validation
- Dry-run matrix: `docker buildx bake -f docker-bake.hcl matrix --print`.
- Sample build: `scripts/build.sh cline ubuntu --platform linux/amd64`.
- Smoke tests: `scripts/test.sh ghcr.io/<registry>/llm-agent-dock:cline-ubuntu-latest`.
- Document results and any known issues in the relevant subtask feedback section.

## Additional Notes
- Start with scaffolding; do not attempt to implement every build until the plan and structure are in
  place.
- Include inline comments wherever future bases/tools will plug in.
- Keep human-readable documentation synchronized with automation files to avoid drift.

## Feedback — Open Problems, Questions, Learnings
- **Open Problems**
  - Local `docker build` attempts fail because this environment cannot access `/var/run/docker.sock`.
    Once permissions are fixed, rerun `scripts/build.sh …` to validate real builds.
  - `scripts/test.sh` currently requires `bats` on the host; install guidance is documented, but CI
    plumbing is still outstanding.
- **Questions**
  - Should images publish to a shared registry namespace or remain per-user? Define this before
    enabling `--push` in automation.
  - Are additional tools/bases planned for the near term? If so, reserve Task IDs (e.g., `T002`) and
    extend the scope tables early.
- **Learnings**
  - Capturing installer fallbacks (like npm shim scripts) keeps builds reproducible even when
    registries throttle.
  - Structuring plans + subtasks with explicit feedback sections makes hand-offs resilient when
    tooling (Docker/Bats) is unavailable mid-task.
