from pathlib import Path

from ._exec import capture_stdout

__all__ = ["is_commit_signing_enabled", "resolve_signing_format"]


def is_commit_signing_enabled(repo_path: Path) -> bool:
    stdout = capture_stdout(["git", "config", "commit.gpgsign"], cwd=repo_path)
    if not stdout:
        return False
    value = stdout.strip().lower()
    return value in {"true", "1", "yes", "on"}


def resolve_signing_format(repo_path: Path) -> str | None:
    stdout = capture_stdout(["git", "config", "gpg.format"], cwd=repo_path)
    if not stdout:
        return None
    value = stdout.strip().lower()
    return value or None
