import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from aicage.errors import CliError
from aicage.runtime.prompts import prompt_yes_no
from aicage.runtime.run_args import MountSpec

_ENTRYPOINT_CONTAINER_PATH = Path("/usr/local/bin/entrypoint.sh")
_DOCKER_SOCKET_PATH = Path("/run/docker.sock")


@dataclass
class _ExtraMountPreferences:
    docker_socket: bool | None = None
    entrypoint: str | None = None

    @classmethod
    def from_mapping(cls, tool_cfg: dict[str, Any]) -> "_ExtraMountPreferences":
        mounts = tool_cfg.get("mounts", {}) or {}
        return cls(
            docker_socket=mounts.get("docker"),
            entrypoint=tool_cfg.get("entrypoint"),
        )


def _load_extra_mount_preferences(tool_cfg: dict[str, Any]) -> _ExtraMountPreferences:
    return _ExtraMountPreferences.from_mapping(tool_cfg)


def _store_extra_mount_preferences(tool_cfg: dict[str, Any], prefs: _ExtraMountPreferences) -> None:
    if prefs.entrypoint is not None:
        tool_cfg["entrypoint"] = prefs.entrypoint

    mounts = tool_cfg.get("mounts", {}) or {}
    if prefs.docker_socket is not None:
        mounts["docker"] = prefs.docker_socket
    if mounts:
        tool_cfg["mounts"] = mounts


def _build_extra_mounts(
    cli_entrypoint: str | None,
    cli_docker_socket: bool,
    prefs: _ExtraMountPreferences,
) -> tuple[list[MountSpec], bool]:
    mounts: list[MountSpec] = []
    updated = False

    entrypoint_path = _resolve_entrypoint_path(cli_entrypoint) if cli_entrypoint else None
    if entrypoint_path is None and prefs.entrypoint:
        entrypoint_path = _resolve_entrypoint_path(prefs.entrypoint)
    if entrypoint_path is not None:
        _validate_entrypoint_path(entrypoint_path)
        mounts.append(
            MountSpec(
                host_path=entrypoint_path,
                container_path=_ENTRYPOINT_CONTAINER_PATH,
                read_only=True,
            )
        )
        if cli_entrypoint and prefs.entrypoint is None:
            if prompt_yes_no(f"Persist entrypoint '{entrypoint_path}' for this project?", default=True):
                prefs.entrypoint = str(entrypoint_path)
                updated = True

    docker_socket_enabled = cli_docker_socket or bool(prefs.docker_socket)
    if docker_socket_enabled:
        mounts.append(
            MountSpec(
                host_path=_DOCKER_SOCKET_PATH,
                container_path=_DOCKER_SOCKET_PATH,
            )
        )
        if cli_docker_socket and prefs.docker_socket is None:
            if prompt_yes_no("Persist mounting the Docker socket for this project?", default=True):
                prefs.docker_socket = True
                updated = True

    return mounts, updated


def _resolve_entrypoint_path(entrypoint: str) -> Path:
    return Path(entrypoint).expanduser().resolve()


def _validate_entrypoint_path(path: Path) -> None:
    if not path.exists() or not path.is_file():
        raise CliError(f"Entrypoint '{path}' does not exist or is not a file.")
    if os.name != "nt" and not os.access(path, os.X_OK):
        raise CliError(f"Entrypoint '{path}' is not executable.")
