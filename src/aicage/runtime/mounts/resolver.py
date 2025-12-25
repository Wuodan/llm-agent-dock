from __future__ import annotations

from aicage.cli_types import ParsedArgs
from aicage.config.context import ConfigContext
from aicage.runtime.run_args import MountSpec

from ._docker_socket import _resolve_docker_socket_mount
from ._entrypoint import _resolve_entrypoint_mount
from ._git_config import resolve_git_config_mount
from ._gpg import resolve_gpg_mount
from ._ssh_keys import resolve_ssh_mount


def resolve_mounts(
    context: ConfigContext,
    tool: str,
    parsed: ParsedArgs | None,
) -> list[MountSpec]:
    tool_cfg = context.project_cfg.tools.setdefault(tool, {})

    git_mounts = resolve_git_config_mount(tool_cfg)
    ssh_mounts = resolve_ssh_mount(context.project_path, tool_cfg)
    gpg_mounts = resolve_gpg_mount(context.project_path, tool_cfg)
    entrypoint_mounts = _resolve_entrypoint_mount(
        tool_cfg,
        parsed.entrypoint if parsed else None,
    )
    docker_mounts = _resolve_docker_socket_mount(
        tool_cfg,
        parsed.docker_socket if parsed else False,
    )

    mounts: list[MountSpec] = []
    mounts.extend(git_mounts)
    mounts.extend(ssh_mounts)
    mounts.extend(gpg_mounts)
    mounts.extend(entrypoint_mounts)
    mounts.extend(docker_mounts)
    return mounts
