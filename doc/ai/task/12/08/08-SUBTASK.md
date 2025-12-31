# Subtask 08: CI and test strategy for non-redistributable agents

## Goal

Define and implement CI/test strategy for non-redistributable agents without publishing images.

## Rationale

The current CI rebuild detection relies on published images. A replacement mechanism is required to
validate non-redistributable agent/base combinations.

## Dependencies

- Architecture decisions from Subtask 01.
- Metadata packaging from Subtask 02.
- Task 12 overview: doc/ai/task/12/12-TASK.md
- Agent workflow rules: AGENTS.md

## Scope

- Define rebuild detection using persisted metadata or checksums.
- Add CI steps to test agent-base combinations without pushing images.
- Document the CI mechanism for developers in DEVELOPMENT.md if needed.

## Out of scope

- Runtime build/update logic in the CLI.
- End-user documentation.

## Expected outputs

- CI validation for non-redistributable agents without image publishing.
- Clear, documented rebuild trigger rules.

## Sequencing

Run alongside Subtasks 02 to 04, but complete before merging local build logic.

## Notes

Follow the Task/SubTask Workflow in doc/ai/task/12/12-TASK.md and include a subtask summary at completion.
