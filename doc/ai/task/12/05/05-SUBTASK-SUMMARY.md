# Subtask 05 summary

## Context

- Subtask id and title: 05 - Local build pipeline for non-redistributable agents.
- Related subtasks touched or impacted: 04, 06.

## Changes

- Key decisions (why): Non-redistributable agents build to local `aicage:<agent>-<base>` tags; packaged build
  context lives under `config/agent-build/` with only non-redistributable agents included; base image repository is
  configurable via `image_base_repository`.
- User-visible behavior changes: Non-redistributable agents now build locally before run, using base-image updates to
  decide rebuilds; build logs are written under `~/.aicage/logs/build/`.
- Internal behavior changes: Added local build metadata under `~/.aicage/state/local-build/`, integrated version checks
  for non-redistributable agents, and added base-image digest checks using the existing registry query flow.
- Files and modules with major changes:
  - src/aicage/cli.py
  - src/aicage/config/runtime_config.py
  - src/aicage/registry/_local_build.py
  - src/aicage/registry/image_selection.py
  - config/agent-build/Dockerfile
  - config/agent-build/agents/claude/agent.yaml
  - config/agent-build/agents/claude/install.sh
  - config/agent-build/agents/claude/version.sh
  - config/agent-build/agents/droid/agent.yaml
  - config/agent-build/agents/droid/install.sh
  - config/agent-build/agents/droid/version.sh

## Testing and validation

- Tests run: Not run (not requested).
- Gaps or skipped tests and why: Local changes not exercised in this session.

## Follow-ups

- Deferred items (explicitly list): None.
- Known risks or open questions: Build logic assumes local Docker availability; remote digest lookup for base images
  skips rebuilds if the registry query fails.
- Suggested next steps: Run pytest and linters; validate local build with a non-redistributable agent.

## Notes

- Lessons learned: Keep build artifacts packaged under config to avoid submodule dependency at runtime.
- Review feedback to carry forward: Maintain local image naming without registry prefixes.
