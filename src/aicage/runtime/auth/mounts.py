from dataclasses import dataclass
from pathlib import Path
from typing import Any

from aicage.runtime.prompts import prompt_yes_no
from aicage.runtime.run_args import MountSpec

from ._git_config import resolve_git_config_path
from ._gpg import resolve_gpg_home
from ._signing import is_commit_signing_enabled, resolve_signing_format
from ._ssh_keys import default_ssh_dir

__all__ = ["MountPreferences", "load_mount_preferences", "store_mount_preferences", "build_auth_mounts"]

_GITCONFIG_MOUNT = Path("/aicage/host/gitconfig")
_GPG_HOME_MOUNT = Path("/aicage/host/gnupg")
_SSH_MOUNT = Path("/aicage/host/ssh")


@dataclass
class MountPreferences:
    gitconfig: bool | None = None
    gnupg: bool | None = None
    ssh: bool | None = None

    @classmethod
    def from_mapping(cls, data: dict[str, Any]) -> "MountPreferences":
        return cls(
            gitconfig=data.get("gitconfig"),
            gnupg=data.get("gnupg"),
            ssh=data.get("ssh"),
        )

    def to_mapping(self) -> dict[str, bool]:
        payload: dict[str, bool] = {}
        if self.gitconfig is not None:
            payload["gitconfig"] = self.gitconfig
        if self.gnupg is not None:
            payload["gnupg"] = self.gnupg
        if self.ssh is not None:
            payload["ssh"] = self.ssh
        return payload


def load_mount_preferences(tool_cfg: dict[str, Any]) -> MountPreferences:
    return MountPreferences.from_mapping(tool_cfg.get("mounts", {}))


def store_mount_preferences(tool_cfg: dict[str, Any], prefs: MountPreferences) -> None:
    mounts = tool_cfg.get("mounts", {}) or {}
    mounts.update(prefs.to_mapping())
    tool_cfg["mounts"] = mounts


def build_auth_mounts(project_path: Path, prefs: MountPreferences) -> tuple[list[MountSpec], bool]:
    mounts: list[MountSpec] = []
    updated = False

    git_config = resolve_git_config_path()
    if git_config and git_config.exists():
        if prefs.gitconfig is None:
            prefs.gitconfig = prompt_yes_no(
                f"Mount Git config from '{git_config}' so Git uses your usual name/email?", default=True
            )
            updated = True
        if prefs.gitconfig:
            mounts.append(MountSpec(host_path=git_config, container_path=_GITCONFIG_MOUNT))

    if is_commit_signing_enabled(project_path):
        signing_format = resolve_signing_format(project_path)
        if signing_format == "ssh":
            ssh_dir = default_ssh_dir()
            if ssh_dir.exists():
                if prefs.ssh is None:
                    prefs.ssh = prompt_yes_no(
                        f"Mount SSH keys from '{ssh_dir}' so Git signing works like on your host?", default=True
                    )
                    updated = True
                if prefs.ssh:
                    mounts.append(MountSpec(host_path=ssh_dir, container_path=_SSH_MOUNT))
        else:
            gpg_home = resolve_gpg_home()
            if gpg_home and gpg_home.exists():
                if prefs.gnupg is None:
                    prefs.gnupg = prompt_yes_no(
                        f"Mount GnuPG keys from '{gpg_home}' so Git signing works like on your host?", default=True
                    )
                    updated = True
                if prefs.gnupg:
                    mounts.append(MountSpec(host_path=gpg_home, container_path=_GPG_HOME_MOUNT))

    return mounts, updated
