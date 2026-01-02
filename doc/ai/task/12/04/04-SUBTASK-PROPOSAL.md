# Subtask 04 proposal: Runtime discovery and version checks (draft)

## Scope alignment

This subtask depends on pieces that are not implemented yet (custom agents, aicage-image-util, etc.).
The proposal below therefore uses stubs and interfaces where needed, keeping real logic minimal and
deferring actual integration until later subtasks.

## Goals

- Unified discovery list for:
  - Release agents from `images-metadata.yaml` (redistributable + non-redistributable).
  - Local custom agents at `~/.aicage/custom/agent/<AGENT>/` (stub until Subtask 06).
- Version check flow:
  - Try aicage-builder version-check image first (stub until helper image exists).
  - Fall back to host execution of `version.sh`.
  - Persist version check result in local metadata storage (exact storage deferred).

## Key constraints and assumptions

- No implementation of local builds (Subtask 05).
- No actual aicage-image-util image available; version-check execution must be stubbed.
- Local custom agents are not implemented yet; discovery relies on placeholder interfaces.
- Version check results must be persisted, but storage mechanism is deferred due to prior decisions.

## Proposed design

### Discovery data model

- Keep `ImagesMetadata` as the central runtime source of truth.
- Add a lightweight `AgentSource` concept in runtime (not in metadata YAML):
  - `source_kind`: `"release"` or `"custom"`.
  - `is_redistributable`: from agent metadata.
- Use `source_kind` only to decide downstream behavior (e.g., local build vs pull).

### Agent discovery flow (stubbed)

1. Load packaged `images-metadata.yaml` as today.
2. Merge additional agents from `~/.aicage/custom/agent/<AGENT>/`:
   - Parse `agent.yml` using the same schema.
   - Compute `valid_bases` by filtering bases from packaged metadata using
     `base_exclude` and `base_distro_exclude`.
   - Mark `source_kind="custom"`.
3. If a custom agent name conflicts with a packaged name, raise a `CliError`
   (avoid silent shadowing).

### Version check flow (stubbed)

Expose a shared function that returns a version string or raises on failure:

1. Try running `version.sh` inside the version-check builder image:
   - `docker run --rm -v <agent_dir>:/agent:ro <image> /agent/version.sh`
   - If the helper image does not exist or docker fails, record the error.
2. Fall back to host execution:
   - `subprocess.run(["/bin/sh", "<agent_dir>/version.sh"], ...)`.
3. If both fail, raise `CliError` with combined diagnostics.

### Persistence of version check results

This proposal defers the concrete storage mechanism until Subtask 05.
For Subtask 04, the version check API should return a structured result:

- `agent_name`
- `version`
- `source_kind`
- `checked_at` (ISO-8601)
- `errors` (optional)

Subtask 05 can then decide where to persist this structure (file, db, etc.).

## Concrete file-level changes

### New modules

- `src/aicage/registry/agent_discovery.py`
  - `discover_agents(images_metadata: ImagesMetadata) -> ImagesMetadata`
  - Loads and merges custom agents (stub if folder missing).
- `src/aicage/registry/custom_agent_loader.py`
  - Parses `agent.yml`, validates, computes `valid_bases`.
- `src/aicage/registry/agent_version_check.py`
  - `AgentVersionChecker` with builder-first + host fallback.
  - `AgentVersionResult` dataclass.

### Updated modules

- `src/aicage/registry/images_metadata/loader.py`
  - Call `discover_agents(...)` after loading packaged metadata.
- `src/aicage/config/global_config.py` + `config/config.yaml`
  - Add `version_check_image` (or similar) for the helper image reference.
- `src/aicage/registry/image_selection.py`
  - No behavior change; will pass through expanded metadata.

### Tests (stubs or minimal behavior)

- `tests/aicage/registry/test_agent_discovery.py`
  - Ensure release agents remain unchanged.
  - Ensure missing custom agent folder yields no changes.
  - Ensure conflict detection works.
- `tests/aicage/registry/test_agent_version_check.py`
  - Simulate builder failure and host fallback.
  - Validate error aggregation when both fail.

## Workflow impacts

- Discovery will look for `~/.aicage/custom/agent/` on startup.
- Version checks attempt the builder image first, then host.
- Persistence of version check results is not implemented in this subtask.

## Decisions resolved for this proposal

1. Persist version check results under a subfolder of `~/.aicage/` (exact layout to be decided in
   Subtask 05).
2. Custom agents override packaged agent names.
3. Execute `version.sh` with `/bin/sh` (or `/bin/bash` if required) to tolerate missing `chmod +x`,
   and log a warning about non-executable `version.sh`.

## Open questions

- None for Subtask 04. Remaining details are deferred to Subtask 05.
