from pathlib import Path

from ._exec import capture_stdout

__all__ = ["resolve_git_config_path"]


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
