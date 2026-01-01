# Subtask 01: Discovery and architecture decisions

## Goal

Establish the minimum viable architecture decisions that constrain all later work, without implementing
functionality. Define data model changes, storage layout, and the aicage-builder direction.

## Rationale

All later subtasks depend on shared decisions for agent classification, metadata formats, and local build
metadata. Getting these aligned first avoids rework and conflicting assumptions.

## Dependencies

- Task 12 overview: doc/ai/task/12/12-TASK.md
- Builder options: doc/ai/task/12/12-AICAGE-BUILDER.md
- Agent workflow rules: AGENTS.md
- Repo guidance: DEVELOPMENT.md

## Scope

- Decide how non-redistributable agents are represented in agent metadata (flag or folder structure).
- Decide how local custom agents and custom base images are discovered and how their metadata is validated.
- Define whether any local metadata is stored under ~/.aicage/ for build state and versions.
- Decide on aicage-builder image strategy (split images vs single image, fallback rules).
- Identify any schema changes required for agent.yml and the new extension.yml.

## Out of scope

- Any implementation changes in src/.
- Any documentation changes for end users.

## Expected outputs

- Approved architecture decisions documented in this subtask folder.
- Non-redistributable agents represented via a required agent.yml flag.
- No local state files for build/update decisions; deterministic tags and real image inspection only.
- No logs or cache under ~/.aicage/; build logs go to /tmp.
- Clear constraints and assumptions for all later subtasks.

## Sequencing

Execute this subtask first. All other subtasks depend on its outputs.

## Notes

Follow the Task/SubTask Workflow in doc/ai/task/12/12-TASK.md and include a subtask summary at completion.
