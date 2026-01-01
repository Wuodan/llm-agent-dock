# Task 12: aicage-builder idea

## Purpose

`aicage-builder` is a dedicated Docker image used for:

- Local image builds for non-redistributable agents, extensions, and custom base images.
- Agent `version.sh` checks when required tools are not available on the host.

The goal is to make local builds reproducible and independent of host tooling.

## Options

### Split images

Two images: one for building, one for version checks. This is the decided direction.

Pros:

- Smaller images per use case.
- Cleaner dependency separation.

Cons:

- More configuration and runtime branching.
- Additional image to maintain and publish.

### No builder image

Rely on host tooling for `docker build` and agent version checks. Not chosen.

Pros:

- No additional image to maintain.
- Less complexity in `aicage` runtime.

Cons:

- Fails on hosts without required tools (e.g., `npm`).
- Harder to ensure reproducibility and consistency.

## Repository layout options

Current direction:

- One git repo containing both images (KISS).
- Repo name: `aicage/aicage-image-util`.
- Repo is included here as submodule `aicage-image-util/`.

Other options:

- Separate git repo for `aicage-builder`.
- In-repo under a new top-level folder.
- Two repos if split images are used.

## Version check image details

- Base image: `ubuntu:latest`.
- Single current image (no per-distro variants).
- Runtime order is fixed:
  - Try version check inside the image first.
  - If that fails, fall back to running the same command on the host.

Rationale: the image ensures a known toolchain; fallback keeps working if the image is missing or broken. The order
could be reversed in the future if host tooling becomes the preferred default.

## Expected toolchain

Likely tools needed in builder images:

- Docker CLI / BuildKit support
- Python + pip
- `git`, `curl`, `tar`
- Node.js + `npm` (for version checks)

## Open questions

- Should the builder image be pinned to a specific base distro?
- How to version builder images relative to `aicage` releases?
- Should the builder image be optional, with a host-tooling fallback?
- Should build logs be captured from inside the builder or by `aicage`?
