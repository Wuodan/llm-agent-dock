# Task 34 Context And Handoff

This document preserves the useful context gathered in the first analysis session so later sessions can continue
without relying on chat history.

## Original task

Primary task description:
- [`34-TASK-add-podman-support.md`](./34-TASK-add-podman-support.md)

Required workflow from the task:
1. Read documentation and code to understand the task.
2. Ask questions if something is not clear.
3. Present an implementation solution and wait for approval.
4. Implement the change autonomously with test/fix loops.
5. Run linters with active venv using `scripts/lint.sh`.
6. Present the change for review.
7. React to review feedback.
8. Do not commit unless explicitly instructed.

## Constraints to carry forward

- Read and respect:
  - [`AGENTS.md`](/home/stefan/development/github/aicage/aicage/AGENTS.md)
  - [`doc/python-test-structure-guidelines.md`](/home/stefan/development/github/aicage/aicage/doc/python-test-structure-guidelines.md)
- Use the existing virtualenv in `.venv`.
- Keep changes minimal.
- Do not invent new public APIs or config fields unless explicitly approved.
- Keep visibility tight. Default to private names unless used outside the defining scope.

## Outcome of the first session

No code was changed.

The session produced:
- a complete inventory of current Docker usage in code and tests
- an initial compatibility assessment for Podman
- a recommendation to split the work across several sessions

## Agreed direction from the discussion

The user does not want this handled as one large session.

Planned split:
1. design/analysis closure
2. core refactor and unit tests
3. integration test parameterization and documentation
4. review/stabilization

## Important open decisions still needing user approval

These decisions were identified but not resolved yet:

1. Runtime selection policy
   - `docker` first and `podman` fallback
   - or explicit configuration/selection

2. Meaning of `--docker` when running with Podman
   - keep literal Docker socket semantics only
   - or treat it as "mount container runtime socket" and map to Podman behavior when using Podman

3. Supported platform scope for initial delivery
   - Linux fully tested
   - Windows/macOS best effort with manual checklist only

## Recommended execution order

Use the session documents in:
- [`session-1-analysis-design`](./session-1-analysis-design/)
- [`session-2-core-refactor`](./session-2-core-refactor/)
- [`session-3-integration-tests`](./session-3-integration-tests/)
- [`session-4-review-stabilization`](./session-4-review-stabilization/)

