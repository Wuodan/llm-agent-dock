# Task T002 / Subtask S4 — Smoke Tests

## Objective
Run `scripts/test.sh` against each freshly built image (per tool) to validate agent boot, CLI presence, and required OS packages, documenting pass/fail outcomes.

## Deliverables
- Command logs for each test invocation, including image reference + tool filter.
- Captured failures with diagnostic notes and planned fixes or follow-ups.
- Checklist state reflecting which tool suites passed.

## Flow
1. Enumerate image tags produced in S3 and decide test order.
2. Execute `scripts/test.sh <image-ref> --tool <name>` (or full suite) for every tool; reuse `--no-pull` when images already local.
3. Update plan + Feedback immediately after each run with timestamps and issues discovered.
4. Coordinate fixes (Dockerfile/script changes) or raise blockers before marking complete.

## Findings (2025-11-08)
- Commands: `scripts/test.sh ghcr.io/wuodan/llm-agent-dock:<tool>-ubuntu-latest --tool <tool> --no-pull` for codex, cline, and factory_ai_droid. All suites passed once the factory shim fix landed.
- Earlier failure (summarized here) showed `command -v factory_ai_droid` missing; updating the installer wrapper to point at `droid-factory` resolved it.

## Checklist
- [x] Test codex image(s).
- [x] Test cline image(s).
- [x] Test factory_ai_droid image(s).
- [x] Document outcomes + failures.

## Inputs & References
- `scripts/test.sh`
- `tests/smoke/*.bats`

## Exit Criteria
- All smoke suites executed with recorded results or justified blockers preventing execution.

## Feedback & Learnings
- **Open Problems**: None — all smoke suites now green.
- **Questions**: Should we extend tests to verify fallback shims (e.g., assert `factory_ai_droid` prints underlying command) or is presence enough?
- **Learnings**:
  - Keep `--no-pull` flag on when iterating quickly; it avoids clobbering locally tagged builds.
  - When tests fail, capture the log in-place before patching Dockerfile; referencing the timestamped log simplified documentation.
