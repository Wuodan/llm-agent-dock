# Subtask 02: Metadata and packaging for non-redistributable agents

## Goal

Ensure non-redistributable agents are represented in release artifacts and available to the aicage CLI
at runtime, without shipping built images.

## Rationale

Runtime behavior depends on accurate agent metadata being present in aicage releases. This subtask
unblocks later local build logic.

## Dependencies

- Architecture decisions from Subtask 01.
- Task 12 overview: doc/ai/task/12/12-TASK.md
- Agent workflow rules: AGENTS.md

## Scope

- Add metadata for non-redistributable agents to aicage packaging inputs.
- Update schema or validation artifacts as required for new agent flags or locations.
- Ensure images-metadata.yaml includes these agents in a consumable form.

## Out of scope

- Local build or runtime logic changes in the CLI.
- CI/testing of non-redistributable agent images.

## Expected outputs

- Release artifacts updated to include non-redistributable agent metadata.
- Schema or validation updates documented and tested.

## Sequencing

Run after Subtask 01. Required before any runtime discovery or local build work.

## Notes

Follow the Task/SubTask Workflow in doc/ai/task/12/12-TASK.md and include a subtask summary at completion.
