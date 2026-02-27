# Task 34 Session 1 Design Proposal

This document captures the implementation proposal prepared in Session 1.

Status:

- analysis complete
- approved by user for implementation

## Recommendation

Implement Podman support in the smallest viable way:

1. Add an internal runtime command resolver that chooses the executable used for container operations.
2. Replace hardcoded `docker` command literals in runtime code with that resolver.
3. Replace Docker SDK image metadata and pull usage with CLI-based logic.
4. Parameterize integration tests/helpers so the same end-to-end scenarios run with Docker and Podman.
5. Limit the first fully supported automated scope to Linux.

## Why this approach

### CLI compatibility is strong enough

For the command forms currently used by `aicage`, Podman documents compatible support for:

- `run`
- `build`
- `pull`
- `image inspect --format`
- `image rm`
- `import`

This covers the operational paths currently used in production code and integration helpers.

### The Docker SDK is the weak point

Current code still uses the Docker Python SDK for:

- local image existence checks
- local image metadata lookup
- pull streaming

Podman can expose a Docker-compatible API through `podman system service`, but that introduces additional environment
requirements. The Podman docs describe this API service as Linux-hosted, with remote clients on macOS and Windows.

For reliability, `aicage` should prefer direct CLI execution over API dependence where possible.

## Proposed design

## 1. Runtime selection

Recommended default behavior:

- prefer `docker` when available
- fall back to `podman` when `docker` is not available

Reason:

- preserves existing user expectations
- keeps current Docker users unchanged
- gives Podman users a no-config path if Docker is absent

Do not add a new public config field in the first pass unless explicitly approved.

Internal implementation can use a small helper such as a private runtime command resolver module.

## 2. Runtime command abstraction

Use one internal place to resolve the executable name:

- `docker`
- `podman`

All command construction in runtime code should prepend that resolved executable instead of hardcoding `docker`.

## 3. Replace Docker SDK usage with CLI logic

Replace SDK-backed operations in:

- [`src/aicage/docker/query.py`](/home/stefan/development/github/aicage/aicage/src/aicage/docker/query.py)
- [`src/aicage/docker/pull.py`](/home/stefan/development/github/aicage/aicage/src/aicage/docker/pull.py)
- likely remove or retire [`src/aicage/docker/_client.py`](/home/stefan/development/github/aicage/aicage/src/aicage/docker/_client.py)

Suggested CLI replacements:

- `image inspect` for local existence and metadata
- `pull` subprocess output redirection for pull logging

This also allows removing the runtime dependency on the Docker SDK from the main execution path.

## 4. `--docker` flag semantics

This is the hardest product decision.

Current meaning in implementation:

- POSIX: mount `/run/docker.sock`
- Windows: set `DOCKER_HOST=tcp://host.docker.internal:2375`

Recommended product behavior for first release:

- keep the CLI flag name `--docker` for backward compatibility
- interpret it as "enable container runtime access inside the container"
- when the selected runtime is Docker, keep current behavior
- when the selected runtime is Podman, map to Podman socket behavior where supported

Reason:

- users care about the capability more than the engine brand
- keeping literal Docker-only semantics would make the flag misleading in Podman mode

Important caveat:

- Podman socket handling is platform-specific and more variable than Docker
- Linux rootless typically uses `$XDG_RUNTIME_DIR/podman/podman.sock`
- Linux rootful typically uses `/run/podman/podman.sock`
- macOS/Windows usually go through Podman machine / remote client workflows

Because of that, Linux should be the only fully automated support target in the first pass.

## 5. Integration test strategy

Do not duplicate the entire integration suite in separate files.

Instead:

- parameterize the runtime executable in integration helpers
- run the existing scenarios against both runtimes on Linux

Minimum automated matrix recommended:

- Docker on Linux
- Podman on Linux

Best-effort manual matrix only:

- Podman on Windows
- Podman on macOS

## 6. Documentation stance

For the first delivery:

- state Linux Docker and Linux Podman as tested paths
- state Windows/macOS Podman as manual/best-effort until validated

## Approved decisions

The user approved:

1. Runtime selection:
   - Docker first, Podman fallback

2. `--docker` behavior in Podman mode:
   - capability semantics rather than Docker-brand semantics
   - keep using pass-through runtime args for special Podman cases such as `--privileged`

3. Release scope:
   - Linux fully tested
   - Windows/macOS best-effort manual validation only

## Sources consulted

- [podman run](https://docs.podman.io/en/latest/markdown/podman-run.1.html)
- [podman build](https://docs.podman.io/en/latest/markdown/podman-build.1.html)
- [podman pull](https://docs.podman.io/en/latest/markdown/podman-pull.1.html)
- [podman inspect](https://docs.podman.io/en/latest/markdown/podman-inspect.1.html)
- [podman import](https://docs.podman.io/en/v4.4/markdown/podman-import.1.html)
- [podman system service](https://docs.podman.io/en/latest/markdown/podman-system-service.1.html)
