# Session 1 Instructions

## Goal

Close Part 1 of the task by turning the existing analysis into a concrete, approved implementation plan.

## Required reading

Read:

- [`../34-TASK-add-podman-support.md`](../34-TASK-add-podman-support.md)
- [`../34-CONTEXT-AND-HANDOFF.md`](../34-CONTEXT-AND-HANDOFF.md)
- [`../34-ANALYSIS-SUMMARY.md`](../34-ANALYSIS-SUMMARY.md)
- [`AGENTS.md`](/home/stefan/development/github/aicage/aicage/AGENTS.md)
- [`doc/python-test-structure-guidelines.md`](/home/stefan/development/github/aicage/aicage/doc/python-test-structure-guidelines.md)

## What to do

1. Re-check the code paths listed in `34-ANALYSIS-SUMMARY.md`.
2. Re-check Podman docs for the exact command forms used by `aicage`.
3. Produce a concrete implementation proposal for user approval.
4. Resolve these design decisions with the user:
   - runtime selection policy
   - `--docker` semantics in Podman mode
   - exact platform support statement for the first release

## Expected output of the session

The session should end with:

- a short design summary
- explicit approved decisions from the user
- a go/no-go decision for Session 2

## Do not do yet

- do not edit production code
- do not start the refactor before user approval
