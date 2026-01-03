# Subtask 02 summary

## Context

- Subtask id and title: 02 - Metadata and packaging for non-redistributable agents.
- Related subtasks touched or impacted: 03-10.

## Changes

- Key decisions (why): Added required `build_local` to agent metadata to avoid optional handling; added
  non-redistributable agents in the existing agents structure to keep packaging KISS.
- User-visible behavior changes: None (metadata and packaging only).
- Internal behavior changes: Images metadata now requires `build_local` for agents and includes NR agents; aicage
  metadata parsing and tests were updated to accept the new required field and NR entries; aicage-image CI now skips
  NR agents in refresh, fails fast in build when mis-invoked, and refresh is triggered via workflow_run after release.
- Files and modules with major changes:
  - aicage-image/agents/claude/agent.yaml
  - aicage-image/agents/claude/install.sh
  - aicage-image/agents/claude/version.sh
  - aicage-image/agents/droid/agent.yaml
  - aicage-image/agents/droid/install.sh
  - aicage-image/agents/droid/version.sh
  - aicage-image/doc/validation/agent.schema.json
  - aicage-image/doc/validation/images-metadata.schema.json
  - aicage-image/doc/images-metadata.md
  - aicage-image/scripts/common.sh
  - aicage-image/.github/workflows/build.yml
  - aicage-image/.github/workflows/refresh-images.yml
  - aicage-image/.github/workflows/release.yml
  - config/images-metadata.yaml
  - doc/validation/images-metadata.schema.json
  - src/aicage/registry/images_metadata/models.py
  - tests/aicage/registry/images_metadata/test_models.py
  - tests/aicage/registry/images_metadata/test_loader.py
  - tests/aicage/config/test_runtime_config.py
  - tests/aicage/config/test_context.py
  - tests/aicage/registry/test_remote_query.py
  - tests/aicage/registry/test_local_query.py
  - tests/aicage/registry/test_image_selection.py
  - tests/aicage/registry/test_image_pull.py
  - tests/aicage/runtime/test_run_plan.py
  - tests/aicage/runtime/test_prompts.py
  - tests/aicage/runtime/test_agent_config.py
  - tests/aicage/runtime/mounts/test_resolver.py
  - tests/aicage/cli/test_cli.py

## Testing and validation

- Tests run: None.
- Gaps or skipped tests and why: Not run in this session.

## Follow-ups

- Deferred items (explicitly list): None (Claude install/version updated post-review by user).
- Known risks or open questions: None.
- Suggested next steps: Run tests and proceed with Subtask 03.

## Notes

- Lessons learned: Defer summary creation until review completion; user was mad seeing commits and scope expansion
  without approval.
- Review feedback to carry forward: Keep KISS and avoid extra state or labels; limit scope to packaging inputs until
  explicitly approved to update consumers.
