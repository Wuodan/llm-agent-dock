from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from aicage.cli_types import ParsedArgs
from aicage.config.config_store import SettingsStore
from aicage.config.context import ConfigContext
from aicage.config.file_locking import lock_config_files
from aicage.config.global_config import GlobalConfig
from aicage.config.project_config import ToolConfig
from aicage.registry.image_selection import select_tool_image
from aicage.runtime.mounts import resolve_mounts
from aicage.runtime.prompts import prompt_yes_no
from aicage.runtime.run_args import MountSpec

__all__ = ["RunConfig", "load_run_config"]


@dataclass(frozen=True)
class RunConfig:
    project_path: Path
    tool: str
    image_ref: str
    global_cfg: GlobalConfig
    project_docker_args: str
    mounts: list[MountSpec]


def load_run_config(tool: str, parsed: ParsedArgs | None = None) -> RunConfig:
    store = SettingsStore(ensure_global_config=False)
    project_path = Path.cwd().resolve()
    global_config_path = store.global_config()
    project_config_path = store.project_config_path(project_path)

    with lock_config_files(global_config_path, project_config_path):
        store.ensure_global_config()
        global_cfg = store.load_global()
        project_cfg = store.load_project(project_path)
        context = ConfigContext(
            store=store,
            project_cfg=project_cfg,
            global_cfg=global_cfg,
        )
        image_ref = select_tool_image(tool, context)
        tool_cfg = project_cfg.tools.setdefault(tool, ToolConfig())

        existing_project_docker_args: str = tool_cfg.docker_args

        mounts = resolve_mounts(context, tool, parsed)

        _persist_docker_args(tool_cfg, parsed)
        store.save_project(project_path, project_cfg)

        return RunConfig(
            project_path=project_path,
            tool=tool,
            image_ref=image_ref,
            global_cfg=global_cfg,
            project_docker_args=existing_project_docker_args,
            mounts=mounts,
        )

def _persist_docker_args(tool_cfg: ToolConfig, parsed: ParsedArgs | None) -> None:
    if parsed is None or not parsed.docker_args:
        return
    existing = tool_cfg.docker_args
    if existing == parsed.docker_args:
        return

    if existing:
        question = (
            f"Persist docker run args '{parsed.docker_args}' for this project "
            f"(replacing '{existing}')?"
        )
    else:
        question = f"Persist docker run args '{parsed.docker_args}' for this project?"

    if prompt_yes_no(question, default=True):
        tool_cfg.docker_args = parsed.docker_args
