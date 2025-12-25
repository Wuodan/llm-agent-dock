from pathlib import Path
from typing import Any

from aicage.runtime.prompts import prompt_yes_no
from aicage.runtime.run_args import MountSpec

from ._exec import capture_stdout

__all__ = ["resolve_git_config_mount"]

_GITCONFIG_MOUNT = Path("/aicage/host/gitconfig")


def _resolve_git_config_path() -> Path | None:
    stdout = capture_stdout(["git", "config", "--global", "--show-origin", "--list"])
    if not stdout:
        return None
    for line in stdout.splitlines():
        if not line.startswith("file:"):
            continue
        parts = line[5:].split()
        if not parts:
            continue
        return Path(parts[0]).expanduser()
    return None


def resolve_git_config_mount(tool_cfg: dict[str, Any]) -> list[MountSpec]:
    git_config = _resolve_git_config_path()
    if not git_config or not git_config.exists():
        return []

    mounts_cfg = tool_cfg.get("mounts", {}) or {}
    pref = mounts_cfg.get("gitconfig")
    if pref is None:
        pref = prompt_yes_no(
            f"Mount Git config from '{git_config}' so Git uses your usual name/email?", default=True
        )
        mounts_cfg["gitconfig"] = pref
        tool_cfg["mounts"] = mounts_cfg

    if pref:
        return [MountSpec(host_path=git_config, container_path=_GITCONFIG_MOUNT)]
    return []
