# Subtask 06: Extensions for final images

## Goal

Implement extension discovery, selection, and build/update logic for extended final images, and add
end-user documentation for extension authoring.

## Rationale

Extensions add a new selection and build layer that should not destabilize the base local build and
update logic. Deferring them ensures the extension flow can reuse stable local build primitives and
keeps earlier subtasks focused.

## Dependencies

- Architecture decisions from Subtask 01.
- Runtime discovery/version checks from Subtask 03.
- Local build pipeline from Subtask 04.
- Task 12 overview: doc/ai/task/12/12-TASK.md
- Agent workflow rules: AGENTS.md

## Scope

- Discover extensions under ~/.aicage/custom/extension/.
- Implement extension selection and extended image naming rules.
- Build/update extended images based on upstream final image updates.
- Add end-user documentation for extension.yml, Dockerfile, and scripts.

## Out of scope

- Custom base images.
- CI strategy for non-redistributable agents.

## Expected outputs

- Extended images build and update correctly with clear logging.
- Documentation provides a complete, usable extension authoring guide.

## Sequencing

Run after Subtask 05.

## Notes

Follow the Task/SubTask Workflow in doc/ai/task/12/12-TASK.md and include a subtask summary at completion.
