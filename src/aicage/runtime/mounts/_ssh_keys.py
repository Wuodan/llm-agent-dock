from pathlib import Path
from typing import Any

from aicage.runtime.prompts import prompt_yes_no
from aicage.runtime.run_args import MountSpec

from ._signing import is_commit_signing_enabled, resolve_signing_format

__all__ = ["resolve_ssh_mount"]

_SSH_MOUNT = Path("/aicage/host/ssh")


def _default_ssh_dir() -> Path:
    return Path.home() / ".ssh"


def resolve_ssh_mount(project_path: Path, tool_cfg: dict[str, Any]) -> list[MountSpec]:
    if not is_commit_signing_enabled(project_path):
        return []
    if resolve_signing_format(project_path) != "ssh":
        return []

    ssh_dir = _default_ssh_dir()
    if not ssh_dir.exists():
        return []

    mounts_cfg = tool_cfg.get("mounts", {}) or {}
    pref = mounts_cfg.get("ssh")
    if pref is None:
        pref = prompt_yes_no(
            f"Mount SSH keys from '{ssh_dir}' so Git signing works like on your host?", default=True
        )
        mounts_cfg["ssh"] = pref
        tool_cfg["mounts"] = mounts_cfg

    if pref:
        return [MountSpec(host_path=ssh_dir, container_path=_SSH_MOUNT)]
    return []
