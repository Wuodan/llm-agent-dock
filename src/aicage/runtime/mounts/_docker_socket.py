from pathlib import Path
from typing import Any

from aicage.runtime.prompts import prompt_yes_no
from aicage.runtime.run_args import MountSpec

_DOCKER_SOCKET_PATH = Path("/run/docker.sock")


def _resolve_docker_socket_mount(
    tool_cfg: dict[str, Any],
    cli_docker_socket: bool,
) -> list[MountSpec]:
    mounts_cfg = tool_cfg.get("mounts", {}) or {}
    docker_socket_enabled = cli_docker_socket or bool(mounts_cfg.get("docker"))
    if not docker_socket_enabled:
        return []

    mounts = [
        MountSpec(
            host_path=_DOCKER_SOCKET_PATH,
            container_path=_DOCKER_SOCKET_PATH,
        )
    ]

    if cli_docker_socket and mounts_cfg.get("docker") is None:
        if prompt_yes_no("Persist mounting the Docker socket for this project?", default=True):
            mounts_cfg["docker"] = True
            tool_cfg["mounts"] = mounts_cfg

    return mounts
