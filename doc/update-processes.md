# Update processes overview

This document summarizes what gets built or updated, when it is updated, and where it runs. It
includes current and planned behavior.

## Update triggers matrix

| Item                           | Source of change                                | Update trigger                                     | Where it runs |
|--------------------------------|-------------------------------------------------|----------------------------------------------------|---------------|
| Base image (aicage-image-base) | Base config or upstream root image changes      | Scheduled weekly build + manual release            | CI            |
| Final image (prebuilt)         | Agent version or base image changes             | CI build on change + publish, runtime pull on use  | CI + client   |
| Final image (build_local=true) | Agent version or base image changes             | Local rebuild on run when changes are detected     | Client        |
| Local custom agent             | Agent version or base image changes             | Local rebuild on run when changes are detected     | Client        |
| Local extension (planned)      | Extension scripts or base/final image changes   | Local rebuild on run when changes are detected     | Client        |
| Local custom base (planned)    | Custom base definition or root image changes    | Local rebuild on run when changes are detected     | Client        |

## Artifact responsibilities

| Artifact                                | Built from                                 | Stored/published                    | Update signal (current/planned)              |
|-----------------------------------------|--------------------------------------------|-------------------------------------|----------------------------------------------|
| Base image                              | aicage-image-base bases/<BASE>              | Registry (ghcr.io)                  | Scheduled weekly + manual                    |
| Final image (prebuilt)                  | base image + agents/<AGENT>                 | Registry (ghcr.io)                  | Agent version + base image updates           |
| Local final image (build_local=true)    | base image + packaged agent-build/<AGENT>   | Local Docker engine                 | Agent version + base image digest change     |
| Local final image (custom agent)        | base image + ~/.aicage/custom/agent/<AGENT> | Local Docker engine                 | Agent version + base image digest change     |
| Local extended image (planned)          | final image + extensions                    | Local Docker engine                 | Extension changes + base/final image updates |
| Local custom base image (planned)       | custom base definition                       | Local Docker engine                 | Definition changes + root image updates      |

## Notes

- "Agent version" refers to running the agent's version.sh (builder image first, host fallback).
- "Base image digest change" refers to the registry digest for the base image tag changing; a
  local pull updates the base before rebuilding the local final image.
