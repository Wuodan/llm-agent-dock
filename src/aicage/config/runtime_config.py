from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from aicage.cli_types import ParsedArgs
from aicage.config._file_locking import lock_project_config
from aicage.config.config_store import SettingsStore
from aicage.config.context import ConfigContext
from aicage.config.global_config import GlobalConfig
from aicage.config.project_config import AgentConfig
from aicage.registry._agent_version_check import AgentVersionChecker
from aicage.registry.image_selection import select_agent_image
from aicage.registry.images_metadata.loader import load_images_metadata
from aicage.registry.images_metadata.models import ImagesMetadata
from aicage.runtime.mounts import resolve_mounts
from aicage.runtime.prompts import prompt_yes_no
from aicage.runtime.run_args import MountSpec

__all__ = ["RunConfig", "load_run_config"]


@dataclass(frozen=True)
class RunConfig:
    project_path: Path
    agent: str
    image_ref: str
    global_cfg: GlobalConfig
    images_metadata: ImagesMetadata
    project_docker_args: str
    mounts: list[MountSpec]


def load_run_config(agent: str, parsed: ParsedArgs | None = None) -> RunConfig:
    store = SettingsStore()
    project_path = Path.cwd().resolve()
    project_config_path = store.project_config_path(project_path)

    with lock_project_config(project_config_path):
        global_cfg = store.load_global()
        images_metadata = load_images_metadata()
        project_cfg = store.load_project(project_path)
        context = ConfigContext(
            store=store,
            project_cfg=project_cfg,
            global_cfg=global_cfg,
            images_metadata=images_metadata,
        )
        image_ref = select_agent_image(agent, context)
        _check_agent_version(agent, global_cfg, images_metadata)
        agent_cfg = project_cfg.agents.setdefault(agent, AgentConfig())

        existing_project_docker_args: str = agent_cfg.docker_args

        mounts = resolve_mounts(context, agent, parsed)

        _persist_docker_args(agent_cfg, parsed)
        store.save_project(project_path, project_cfg)

        return RunConfig(
            project_path=project_path,
            agent=agent,
            image_ref=image_ref,
            global_cfg=global_cfg,
            images_metadata=images_metadata,
            project_docker_args=existing_project_docker_args,
            mounts=mounts,
        )


def _persist_docker_args(agent_cfg: AgentConfig, parsed: ParsedArgs | None) -> None:
    if parsed is None or not parsed.docker_args:
        return
    existing = agent_cfg.docker_args
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
        agent_cfg.docker_args = parsed.docker_args


def _check_agent_version(
    agent: str,
    global_cfg: GlobalConfig,
    images_metadata: ImagesMetadata,
) -> None:
    agent_metadata = images_metadata.agents[agent]
    if not agent_metadata.is_custom:
        return
    checker = AgentVersionChecker(global_cfg)
    checker.get_version(agent, agent_metadata)
