# Task 34 Manual Validation Checklist

This checklist covers the runtime combinations that are not in the automated integration scope for Task 34.

## Automated scope

- Linux with Docker
- Linux with Podman

## Manual scope

- Windows with Podman
- macOS with Podman

## Preconditions

- Podman CLI is installed and available on `PATH`.
- `aicage` is run from the project virtualenv.
- On Windows or macOS, Podman machine is started if required by the local setup.

## Manual checks

1. Run `python -m aicage --help` and confirm `--docker` is described as mounting the host container runtime socket.
2. Run `python -m aicage codex --version` and confirm the container starts successfully with Podman selected.
3. Run `python -m aicage --docker codex --version` and confirm runtime access works or document the local Podman setup
   requirement if extra Podman flags are needed.
4. Run `python -m aicage -- --env AICAGE_ENTRYPOINT_CMD=bash codex -lc 'echo ok'` and confirm forwarded runtime args still
   work with Podman.
5. Run `AICAGE_RUN_INTEGRATION=1 pytest tests/aicage/integration` with Podman selected and record any failures that are
   specific to the platform setup.
