# Session 3 Instructions

## Goal

Add near-real-life end-to-end coverage for the supported runtime matrix.

## Required reading

Read:

- [`../34-TASK-add-podman-support.md`](../34-TASK-add-podman-support.md)
- [`../34-CONTEXT-AND-HANDOFF.md`](../34-CONTEXT-AND-HANDOFF.md)
- [`../34-ANALYSIS-SUMMARY.md`](../34-ANALYSIS-SUMMARY.md)
- Session 2 change summary
- [`AGENTS.md`](/home/stefan/development/github/aicage/aicage/AGENTS.md)
- [`doc/python-test-structure-guidelines.md`](/home/stefan/development/github/aicage/aicage/doc/python-test-structure-guidelines.md)

## Main work

Focus on:

- parameterizing integration tests/helpers to use the selected runtime
- preserving the existing Docker integration coverage
- adding equivalent Podman integration runs for the supported environment, expected to be Linux first

Likely files:

- [`tests/aicage/integration/_helpers.py`](/home/stefan/development/github/aicage/aicage/tests/aicage/integration/_helpers.py)
- integration tests that hardcode `docker`

## Required verification

Run the integration suite for the supported matrix from the approved design.

At minimum, if approved in Session 1:

- Docker on Linux
- Podman on Linux

If Windows/macOS are not in automated scope, add or update a manual verification checklist document.

## Deliverable

At the end of Session 3, produce:

- updated integration tests
- test commands used
- explicit statement of what was automated and what remains manual
