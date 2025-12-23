import os
import shlex
from dataclasses import dataclass, field
from pathlib import Path

from ._env_vars import (
    AICAGE_GID,
    AICAGE_TOOL_PATH,
    AICAGE_UID,
    AICAGE_USER,
    AICAGE_WORKSPACE,
)

__all__ = ["MountSpec", "DockerRunArgs", "merge_docker_args", "assemble_docker_run"]


@dataclass
class MountSpec:
    host_path: Path
    container_path: Path
    read_only: bool = False


@dataclass
class DockerRunArgs:
    image_ref: str
    project_path: Path
    tool_config_host: Path
    tool_mount_container: Path
    merged_docker_args: str
    tool_args: list[str]
    tool_path: str | None = None
    env: list[str] = field(default_factory=list)
    mounts: list[MountSpec] = field(default_factory=list)


def merge_docker_args(*args: str) -> str:
    return " ".join(part for part in args if part).strip()


def _resolve_user_ids() -> list[str]:
    env_flags: list[str] = []
    try:
        uid = os.getuid()
        gid = os.getgid()
    except AttributeError:
        uid = gid = None

    user = os.environ.get("USER") or os.environ.get("USERNAME") or "aicage"
    if uid is not None:
        env_flags.extend(["-e", f"{AICAGE_UID}={uid}", "-e", f"{AICAGE_GID}{'='}{gid}"])
    env_flags.extend(["-e", f"{AICAGE_USER}={user}"])
    return env_flags


def assemble_docker_run(args: DockerRunArgs) -> list[str]:
    cmd: list[str] = ["docker", "run", "--rm", "-it"]
    cmd.extend(_resolve_user_ids())
    cmd.extend(["-e", f"{AICAGE_WORKSPACE}={args.project_path}"])
    if args.tool_path:
        cmd.extend(["-e", f"{AICAGE_TOOL_PATH}={args.tool_path}"])
    for env in args.env:
        cmd.extend(["-e", env])
    cmd.extend(["-v", f"{args.project_path}:/workspace"])
    cmd.extend(["-v", f"{args.project_path}:{args.project_path}"])
    cmd.extend(["-v", f"{args.tool_config_host}:{args.tool_mount_container}"])
    for mount in args.mounts:
        suffix = ":ro" if mount.read_only else ""
        cmd.extend(["-v", f"{mount.host_path}:{mount.container_path}{suffix}"])

    if args.merged_docker_args:
        cmd.extend(shlex.split(args.merged_docker_args))

    cmd.append(args.image_ref)
    cmd.extend(args.tool_args)
    return cmd
