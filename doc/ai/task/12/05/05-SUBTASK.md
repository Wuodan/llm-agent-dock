# Subtask 05: Custom local agents

## Goal

Allow users to define local agents under ~/.aicage/custom/agent/ and integrate them into discovery,
selection, version checks, and local builds.

## Rationale

Custom agents should reuse the same local build pipeline as non-redistributable agents with minimal
delta, so this work is best built on the core pipeline.

## Dependencies

- Architecture decisions from Subtask 01.
- Runtime discovery/version checks from Subtask 03.
- Local build pipeline from Subtask 04.
- Task 12 overview: doc/ai/task/12/12-TASK.md
- Agent workflow rules: AGENTS.md

## Scope

- Discover custom agents from ~/.aicage/custom/agent/.
- Validate their agent.yml with existing schema.
- Include them in selection lists and local build logic.

## Out of scope

- Extensions and custom base images.
- End-user documentation for extensions.

## Expected outputs

- Local custom agents behave like non-redistributable agents at runtime.
- Tests cover discovery and build behavior for custom agents.

## Sequencing

Run after Subtask 04.

## Notes

Follow the Task/SubTask Workflow in doc/ai/task/12/12-TASK.md and include a subtask summary at completion.
