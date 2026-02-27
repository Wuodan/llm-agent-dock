# Task 34 Analysis Summary

This document captures the technical analysis completed before any code changes.

## Summary opinion

Adding Podman support looks moderately tricky, not hard.

The code changes are manageable because much of `aicage` already shells out to a container runtime CLI.
The larger risk is validation, especially around container socket behavior and cross-platform differences.

## Main conclusion

The safest implementation strategy is:

- introduce a small internal runtime abstraction
- move remaining Docker SDK operations to CLI-based execution
- parameterize integration tests so the same end-to-end flows run against Docker and Podman on Linux

## Current Docker usage inventory

### Runtime execution paths

Main files:

- [`src/aicage/docker/build.py`](/home/stefan/development/github/aicage/aicage/src/aicage/docker/build.py)
- [`src/aicage/docker/run.py`](/home/stefan/development/github/aicage/aicage/src/aicage/docker/run.py)
- [`src/aicage/docker/query.py`](/home/stefan/development/github/aicage/aicage/src/aicage/docker/query.py)
- [`src/aicage/docker/pull.py`](/home/stefan/development/github/aicage/aicage/src/aicage/docker/pull.py)
- [`src/aicage/docker/_client.py`](/home/stefan/development/github/aicage/aicage/src/aicage/docker/_client.py)
- [`src/aicage/registry/_signature.py`](/home/stefan/development/github/aicage/aicage/src/aicage/registry/_signature.py)

Current state:

- `build.py` uses CLI `docker build` and `docker image rm`
- `run.py` uses CLI `docker run`
- `registry/_signature.py` uses CLI `docker run` for Cosign
- `query.py` uses Docker SDK for image lookup and metadata, plus CLI for image removal
- `pull.py` uses Docker SDK pull streaming
- `_client.py` centralizes Docker SDK client creation

### Test and helper paths with hardcoded Docker CLI

Main files:

- [`tests/aicage/integration/_helpers.py`](/home/stefan/development/github/aicage/aicage/tests/aicage/integration/_helpers.py)
- [`tests/aicage/integration/remote_builtin/test_pull_newer.py`](/home/stefan/development/github/aicage/aicage/tests/aicage/integration/remote_builtin/test_pull_newer.py)
- multiple unit tests under [`tests/aicage/docker`](/home/stefan/development/github/aicage/aicage/tests/aicage/docker)

Current state:

- integration helpers directly run `docker import`, `docker pull`, and `docker image inspect`
- many unit tests assert literal command arrays beginning with `"docker"`

## Compatibility assessment

For the command shapes currently used by `aicage`, Podman CLI is expected to be broadly compatible:

- `run`
- `build`
- `pull`
- `image rm`
- `image inspect --format`
- `import`

The highest-risk compatibility area is not the common CLI flags above. It is the surrounding environment and host
integration behavior.

## Main implementation risk

The current Python Docker SDK dependency is the least portable part.

Why:

- Docker SDK naturally targets the Docker API
- Podman can expose a Docker-compatible API, but that usually depends on `podman system service` or Desktop/machine
  setup
- making Podman support depend on that extra setup would weaken reliability

Recommendation:
- replace runtime-critical SDK usage with CLI-based logic

## Main behavioral risk

`--docker` currently means "mount Docker access into the container".

Observed implementation:

- on POSIX, it mounts `/run/docker.sock`
- on Windows, it sets `DOCKER_HOST=tcp://host.docker.internal:2375`

Why this is tricky:

- Podman socket locations differ, especially with rootless Podman
- Podman on macOS/Windows often runs through Podman machine
- Docker-specific wording in CLI/help/prompts may no longer match runtime behavior

## Recommended initial delivery scope

Recommended first delivery:

- Linux: full support and automated integration coverage for Docker and Podman
- Windows/macOS: best-effort support only, with a manual verification checklist

Reason:

- the user can test Windows manually
- there is currently no Mac tester
- this keeps the shipped claim aligned with actual validation

## Coding recommendation

Keep the first implementation minimal:

1. Add a small internal runtime command resolver.
2. Replace hardcoded `"docker"` command literals in runtime code.
3. Replace Docker SDK image queries and pull logic with CLI-based implementation.
4. Update affected unit tests.
5. Parameterize Linux integration tests to run against Docker and Podman.

Avoid in the first pass unless explicitly requested:

- new public config fields
- large CLI/UI redesign
- broad renaming of `docker`-named internal modules
