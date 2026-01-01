# Subtask 08: Custom local base images

## Goal

Allow users to define custom base images under ~/.aicage/custom/image-base/ and integrate them into
selection and local build/update logic.

## Rationale

Custom bases add complexity across selection and updates. They should be layered after the local
build pipeline and extensions are stable.

## Dependencies

- Architecture decisions from Subtask 01.
- Runtime discovery/version checks from Subtask 04.
- Local build pipeline from Subtask 05.
- Extensions flow from Subtask 07.
- Task 12 overview: doc/ai/task/12/12-TASK.md
- Agent workflow rules: AGENTS.md

## Scope

- Discover custom base definitions and validate base.yml.
- Build local base images with the defined naming rules.
- Update checks based on root_image and agent version.
- Integrate custom bases into selection flow with extensions.

## Out of scope

- CI strategy for non-redistributable agents.

## Expected outputs

- Custom base images build and update locally.
- Selection flow includes custom bases without breaking existing behavior.

## Sequencing

Run after Subtask 07.

## Notes

Follow the Task/SubTask Workflow in doc/ai/task/12/12-TASK.md and include a subtask summary at completion.
