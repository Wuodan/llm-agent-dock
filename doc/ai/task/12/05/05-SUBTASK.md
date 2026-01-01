# Subtask 05: Local build pipeline for non-redistributable agents

## Goal

Add local image build and update logic for non-redistributable agents, including metadata tracking
and logging.

## Rationale

This is the core feature that enables non-redistributable agents to run on user machines without
shipping images.

## Dependencies

- Architecture decisions from Subtask 01.
- Runtime discovery/version checks from Subtask 04.
- Task 12 overview: doc/ai/task/12/12-TASK.md
- Agent workflow rules: AGENTS.md

## Scope

- Decide when to build or rebuild local agent-base images.
- Implement local image naming and tagging rules.
- Store build metadata and logs under ~/.aicage/.
- Integrate build behavior into the existing aicage run flow.

## Out of scope

- Extension images and custom base images.
- User-facing extension documentation.

## Expected outputs

- Local builds for non-redistributable agents work end-to-end.
- Build/update decision logic is covered by CI pipelines that build and test images.

## Sequencing

Run after Subtask 04. Forms the baseline for local custom agents and extensions.

## Notes

Follow the Task/SubTask Workflow in doc/ai/task/12/12-TASK.md and include a subtask summary at completion.
