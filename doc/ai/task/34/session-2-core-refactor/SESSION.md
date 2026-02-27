# Session 2 Instructions

## Goal

Implement the approved core Podman support changes in production code and cover them with unit tests.

## Required reading

Read:

- [`../34-TASK-add-podman-support.md`](../34-TASK-add-podman-support.md)
- [`../34-CONTEXT-AND-HANDOFF.md`](../34-CONTEXT-AND-HANDOFF.md)
- [`../34-ANALYSIS-SUMMARY.md`](../34-ANALYSIS-SUMMARY.md)
- the approved design decisions recorded at the end of Session 1
- [`AGENTS.md`](/home/stefan/development/github/aicage/aicage/AGENTS.md)
- [`doc/python-test-structure-guidelines.md`](/home/stefan/development/github/aicage/aicage/doc/python-test-structure-guidelines.md)

## Recommended implementation scope

Likely focus areas:

- [`src/aicage/docker/cli.py`](/home/stefan/development/github/aicage/aicage/src/aicage/docker/cli.py)
- [`src/aicage/docker/build.py`](/home/stefan/development/github/aicage/aicage/src/aicage/docker/build.py)
- [`src/aicage/docker/run.py`](/home/stefan/development/github/aicage/aicage/src/aicage/docker/run.py)
- [`src/aicage/docker/query.py`](/home/stefan/development/github/aicage/aicage/src/aicage/docker/query.py)
- [`src/aicage/docker/pull.py`](/home/stefan/development/github/aicage/aicage/src/aicage/docker/pull.py)
- [`src/aicage/registry/_signature.py`](/home/stefan/development/github/aicage/aicage/src/aicage/registry/_signature.py)

## Implementation intent

Target the smallest workable change set:

1. Introduce an internal runtime command abstraction.
2. Replace hardcoded runtime executable names where needed.
3. Remove or reduce Docker SDK dependence in runtime-critical paths.
4. Keep naming/API churn low unless the user explicitly approved broader cleanup.

## Tests to add/update

Update unit tests under:

- [`tests/aicage/docker`](/home/stefan/development/github/aicage/aicage/tests/aicage/docker)
- any affected registry tests

Make sure test names and modules continue to follow:
- [`doc/python-test-structure-guidelines.md`](/home/stefan/development/github/aicage/aicage/doc/python-test-structure-guidelines.md)

## Required verification

With active `.venv`, run targeted unit tests for affected modules first.

Then run the broader test selection needed to confirm no regressions.

## Deliverable

At the end of Session 2, produce:

- code changes
- passing unit tests for the changed scope
- a short summary of what remains for Session 3
