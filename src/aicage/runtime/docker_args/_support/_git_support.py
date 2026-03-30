from dataclasses import dataclass
from pathlib import Path
from typing import Protocol

from aicage.paths import HOST_GNUPG_DIR, HOST_SSH_DIR

from ._exec import capture_stdout
from ._signing import is_commit_signing_enabled, resolve_signing_format

_REMOTE_WITH_URL_FIELD_COUNT: int = 2
_REMOTE_URL_INDEX: int = 1


@dataclass(frozen=True)
class _GitSupportPromptItem:
    key: str
    label: str
    path: Path


class _MountPrefs(Protocol):
    gitconfig: bool | None
    gitroot: bool | None
    gnupg: bool | None
    ssh: bool | None


def resolve_git_config_path() -> Path | None:
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


def resolve_git_root(project_path: Path) -> Path | None:
    superproject = _resolve_git_path(
        ["git", "rev-parse", "--show-superproject-working-tree"],
        project_path,
    )
    if superproject:
        return superproject
    return _resolve_git_path(["git", "rev-parse", "--show-toplevel"], project_path)


def _resolve_git_path(command: list[str], project_path: Path) -> Path | None:
    stdout = capture_stdout(command, cwd=project_path)
    if not stdout:
        return None
    value = stdout.strip()
    if not value:
        return None
    return Path(value).resolve()


def resolve_gpg_home() -> Path | None:
    stdout = capture_stdout(["gpgconf", "--list-dirs", "homedir"])
    if stdout:
        path = stdout.strip()
        if path:
            gpg_home = Path(path).expanduser()
            if gpg_home.exists():
                return gpg_home
    fallback = HOST_GNUPG_DIR
    return fallback if fallback.exists() else None


def resolve_ssh_dir() -> Path:
    return HOST_SSH_DIR


def uses_ssh_remotes(project_path: Path) -> bool:
    stdout = capture_stdout(["git", "remote", "-v"], cwd=project_path)
    if not stdout:
        return False
    for line in stdout.splitlines():
        fields = line.split()
        if len(fields) < _REMOTE_WITH_URL_FIELD_COUNT:
            continue
        remote_url = fields[_REMOTE_URL_INDEX]
        if remote_url.startswith("ssh://") or "@" in remote_url:
            return True
    return False


def git_support_prompt_items(
    project_path: Path,
    mounts_cfg: _MountPrefs,
) -> list[tuple[str, str]]:
    git_items: list[_GitSupportPromptItem] = []

    git_config = resolve_git_config_path()
    if git_config and git_config.exists() and mounts_cfg.gitconfig is None:
        git_items.append(_GitSupportPromptItem("gitconfig", "Git config (name/email)", git_config))

    git_root = resolve_git_root(project_path)
    if git_root and git_root != project_path and mounts_cfg.gitroot is None:
        git_items.append(_GitSupportPromptItem("gitroot", "Git root (repository access)", git_root))

    signing_enabled = is_commit_signing_enabled(project_path)
    signing_format = resolve_signing_format(project_path) if signing_enabled else None
    ssh_needed = (signing_enabled and signing_format == "ssh") or uses_ssh_remotes(project_path)

    if ssh_needed and mounts_cfg.ssh is None:
        ssh_dir = resolve_ssh_dir()
        if ssh_dir.exists():
            git_items.append(
                _GitSupportPromptItem(
                    "ssh",
                    "SSH keys (for Git SSH/signing)",
                    ssh_dir,
                )
            )

    needs_gnupg = signing_enabled and signing_format != "ssh"
    if needs_gnupg and mounts_cfg.gnupg is None:
        gpg_home = resolve_gpg_home()
        if gpg_home and gpg_home.exists():
            git_items.append(
                _GitSupportPromptItem(
                    "gnupg",
                    "GnuPG keys (for Git signing)",
                    gpg_home,
                )
            )
    return [(item.key, f"{item.label}: {item.path}") for item in git_items]
