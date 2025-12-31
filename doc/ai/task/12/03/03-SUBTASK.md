# Subtask 03: Runtime discovery and version checks

## Goal

Implement unified agent discovery and version checking for normal agents, non-redistributable agents,
and local custom agents.

## Rationale

Local builds and update checks require a consistent view of all agent types and a predictable version
check flow. This subtask provides the core runtime capability.

## Dependencies

- Architecture decisions from Subtask 01.
- Metadata packaging from Subtask 02.
- Task 12 overview: doc/ai/task/12/12-TASK.md
- Agent workflow rules: AGENTS.md

## Scope

- Discover agents from release metadata and ~/.aicage/custom/agent/.
- Add version check flow using aicage-builder first, with host fallback.
- Define and persist version check results in local metadata storage.

## Out of scope

- Building or updating local images.
- Extensions and custom base images.

## Expected outputs

- Runtime discovery list includes all agent sources.
- Version checks use defined fallback and error behavior.
- Tests cover new discovery and version logic.

## Sequencing

Run after Subtask 02. Required before local build logic.

## Notes

Follow the Task/SubTask Workflow in doc/ai/task/12/12-TASK.md and include a subtask summary at completion.
