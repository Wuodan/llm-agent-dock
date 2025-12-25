from __future__ import annotations

from aicage.cli_types import ParsedArgs
from aicage.config.context import ConfigContext
from aicage.runtime.run_args import MountSpec

from ._auth import _resolve_auth_mounts
from ._docker_socket import _resolve_docker_socket_mount
from ._entrypoint import _resolve_entrypoint_mount


def resolve_mounts(
    context: ConfigContext,
    tool: str,
    parsed: ParsedArgs | None,
) -> list[MountSpec]:
    tool_cfg = context.project_cfg.tools.setdefault(tool, {})

    auth_mounts, auth_updated = _resolve_auth_mounts(context.project_path, tool_cfg)
    entrypoint_mounts, entrypoint_updated = _resolve_entrypoint_mount(
        tool_cfg,
        parsed.entrypoint if parsed else None,
    )
    docker_mounts, docker_updated = _resolve_docker_socket_mount(
        tool_cfg,
        parsed.docker_socket if parsed else False,
    )

    if auth_updated or entrypoint_updated or docker_updated:
        context.store.save_project(context.project_path, context.project_cfg)

    mounts: list[MountSpec] = []
    mounts.extend(auth_mounts)
    mounts.extend(entrypoint_mounts)
    mounts.extend(docker_mounts)
    return mounts
