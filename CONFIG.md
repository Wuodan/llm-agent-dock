# Configuration

## Locations

- Global config: `~/.aicage/config.yaml`
- Project config: `~/.aicage/projects/<sha256>.yaml`
- `aicage --config print` prints the current project config path and contents.

Project config filenames are the SHA-256 digest of the resolved project path string.

## Global config schema

`~/.aicage/config.yaml` is required and created from the packaged defaults on first run.

```yaml
image_registry: string
image_registry_api_url: string
image_registry_api_token_url: string
image_repository: string
default_image_base: string
```

| Key                            | Type   | Presence | Description                                      |
|--------------------------------|--------|----------|--------------------------------------------------|
| `image_registry`               | string | Always   | Registry host used for image pulls.              |
| `image_registry_api_url`       | string | Always   | Registry API base URL for discovery/auth.        |
| `image_registry_api_token_url` | string | Always   | Token endpoint used to request registry access.  |
| `image_repository`             | string | Always   | Image repository name (without tag).             |
| `default_image_base`           | string | Always   | Default base when selecting an image for a tool. |

## Project config schema

`~/.aicage/projects/<sha256>.yaml` stores per-project tool settings.

```yaml
path: string
tools:
  <tool>:
    base: string
    docker_args: string
    entrypoint: string
    mounts:
      gitconfig: bool
      gnupg: bool
      ssh: bool
      docker: bool
```

| Key            | Type   | Presence | Description                     |
|----------------|--------|----------|---------------------------------|
| `path`         | string | Always   | Absolute project path.          |
| `tools`        | map    | Always   | Per-tool configuration.         |
| `tools.<tool>` | map    | Always   | Tool config schema (see below). |

## Tool config schema

Used under `tools.<tool>` in the project config.

| Key                | Type   | Presence | Description                                             |
|--------------------|--------|----------|---------------------------------------------------------|
| `base`             | string | Always   | Image base to use for this tool in this project.        |
| `docker_args`      | string | Optional | Persisted `docker run` args for this tool.              |
| `entrypoint`       | string | Optional | Persisted host path to an executable entrypoint script. |
| `mounts`           | map    | Optional | Host resource mount preferences.                        |
| `mounts.gitconfig` | bool   | Optional | Mount the host Git config file.                         |
| `mounts.gnupg`     | bool   | Optional | Mount the host GnuPG home for Git signing.              |
| `mounts.ssh`       | bool   | Optional | Mount the host SSH keys for SSH-based Git signing.      |
| `mounts.docker`    | bool   | Optional | Mount `/run/docker.sock` into the container.            |
