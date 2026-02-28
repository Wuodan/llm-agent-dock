# Task 34 Abort Summary

Task 34 is aborted.

## Result

Podman support looked feasible during the initial CLI-focused analysis, but the first real end-to-end run showed a
breaking runtime behavior difference inside the container that is outside the acceptable compatibility scope for this
project.

The work done so far is kept as a development snapshot only.

## What was validated

- Docker-first runtime selection with Podman fallback was implemented.
- Integration helpers were cleaned up so they no longer hardcode `docker`.
- A real Podman run was executed with agent `codex` and a bind-mounted `~/.codex` directory.

## Key findings

### 1. Plain rootless Podman bind mounts showed wrong ownership inside the container

When `~/.codex` was bind-mounted into the container with Podman, the directory was visible but appeared as
`root:root` inside the container even though the host user had the same user name, UID, and GID.

This was traced to Podman rootless user namespace behavior, not to a simple mount formatting problem in `aicage`.

### 2. Fixing the ownership view required Podman-specific user namespace behavior

Adding `--userns=keep-id` to the Podman run command corrected the bind-mount ownership behavior from the container
point of view.

This already showed that Podman support was not just a matter of Docker-compatible CLI flags on the host.

### 3. `--userns=keep-id` changed container startup semantics in a way that breaks the image entrypoint

With `--userns=keep-id`, Podman exposes the host user inside the container before the image entrypoint runs.

Observed behavior:

- `id` inside the container already reported `uid=1000(stefan) gid=1000(stefan)`
- `getent passwd 1000` already returned `stefan`

The image entrypoint still attempted to run:

- `useradd ... stefan`

That failed with:

- `useradd: user 'stefan' already exists`

So Podman compatibility now depended on changing container-internal user/bootstrap logic, not just adapting host-side
runtime command construction.

## Why the task is aborted

The expected scope for Podman support was small host/runtime differences with mostly Docker-compatible behavior.

The real behavior found here is different:

- ownership behavior for bind mounts changed
- a Podman-specific `--userns` mode was required
- that mode changed the container's user model before the image entrypoint ran
- the image startup logic then needed Podman-specific compatibility handling

That is beyond the intended support boundary for this project.

Continuing would mean accepting an ongoing maintenance burden around Podman-specific behavior both outside and inside
the container.

## Recommended branch handling

If this work should be preserved before resetting the development branch, create a backup branch from the current
state and keep it as the Task 34 Podman investigation snapshot.
