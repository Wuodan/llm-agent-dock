from pathlib import Path
from typing import Any

from aicage.runtime.prompts import prompt_yes_no
from aicage.runtime.run_args import MountSpec

from ._exec import capture_stdout
from ._signing import is_commit_signing_enabled, resolve_signing_format

__all__ = ["resolve_gpg_mount"]

_GPG_HOME_MOUNT = Path("/aicage/host/gnupg")


def _resolve_gpg_home() -> Path | None:
    stdout = capture_stdout(["gpgconf", "--list-dirs", "homedir"])
    if not stdout:
        return None
    path = stdout.strip()
    return Path(path).expanduser() if path else None


def resolve_gpg_mount(project_path: Path, tool_cfg: dict[str, Any]) -> list[MountSpec]:
    if not is_commit_signing_enabled(project_path):
        return []
    if resolve_signing_format(project_path) == "ssh":
        return []

    gpg_home = _resolve_gpg_home()
    if not gpg_home or not gpg_home.exists():
        return []

    mounts_cfg = tool_cfg.get("mounts", {}) or {}
    pref = mounts_cfg.get("gnupg")
    if pref is None:
        pref = prompt_yes_no(
            f"Mount GnuPG keys from '{gpg_home}' so Git signing works like on your host?", default=True
        )
        mounts_cfg["gnupg"] = pref
        tool_cfg["mounts"] = mounts_cfg

    if pref:
        return [MountSpec(host_path=gpg_home, container_path=_GPG_HOME_MOUNT)]
    return []
