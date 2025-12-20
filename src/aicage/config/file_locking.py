from __future__ import annotations

from contextlib import ExitStack, contextmanager
from pathlib import Path
from typing import Iterator

import portalocker

from aicage.config.errors import ConfigError

__all__ = ["lock_config_files"]

_LOCK_TIMEOUT_SECONDS = 30


@contextmanager
def lock_config_files(global_config_path: Path, project_config_path: Path) -> Iterator[None]:
    try:
        with ExitStack() as stack:
            stack.enter_context(_lock_file(global_config_path))
            stack.enter_context(_lock_file(project_config_path))
            yield
    except portalocker.exceptions.LockException as exc:  # pragma: no cover - rare file lock failure
        raise ConfigError(f"Failed to lock configuration files: {exc}") from exc


def _lock_file(path: Path) -> portalocker.Lock:
    path.parent.mkdir(parents=True, exist_ok=True)
    return portalocker.Lock(str(path), timeout=_LOCK_TIMEOUT_SECONDS, mode="a+")
