import os
from pathlib import Path
from typing import Any

from aicage.errors import CliError
from aicage.runtime.prompts import prompt_yes_no
from aicage.runtime.run_args import MountSpec

_ENTRYPOINT_CONTAINER_PATH = Path("/usr/local/bin/entrypoint.sh")


def _resolve_entrypoint_mount(
    tool_cfg: dict[str, Any],
    cli_entrypoint: str | None,
) -> list[MountSpec]:
    entrypoint_value = cli_entrypoint or tool_cfg.get("entrypoint")
    if not entrypoint_value:
        return []

    entrypoint_path = _resolve_entrypoint_path(entrypoint_value)
    _validate_entrypoint_path(entrypoint_path)
    mounts = [
        MountSpec(
            host_path=entrypoint_path,
            container_path=_ENTRYPOINT_CONTAINER_PATH,
            read_only=True,
        )
    ]

    if cli_entrypoint and tool_cfg.get("entrypoint") is None:
        if prompt_yes_no(f"Persist entrypoint '{entrypoint_path}' for this project?", default=True):
            tool_cfg["entrypoint"] = str(entrypoint_path)

    return mounts


def _resolve_entrypoint_path(entrypoint: str) -> Path:
    return Path(entrypoint).expanduser().resolve()


def _validate_entrypoint_path(path: Path) -> None:
    if not path.exists() or not path.is_file():
        raise CliError(f"Entrypoint '{path}' does not exist or is not a file.")
    if os.name != "nt" and not os.access(path, os.X_OK):
        raise CliError(f"Entrypoint '{path}' is not executable.")
