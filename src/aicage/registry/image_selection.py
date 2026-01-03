from __future__ import annotations

from pathlib import Path

from aicage.config.context import ConfigContext
from aicage.config.project_config import AGENT_BASE_KEY, AgentConfig
from aicage.errors import CliError
from aicage.registry.images_metadata.models import AgentMetadata, ImagesMetadata
from aicage.runtime.prompts import BaseSelectionRequest, prompt_for_base

from ._image_refs import local_image_ref


def select_agent_image(agent: str, context: ConfigContext) -> str:
    agent_cfg = context.project_cfg.agents.setdefault(agent, AgentConfig())
    agent_metadata = _require_agent_metadata(agent, context.images_metadata)
    base = agent_cfg.base or context.global_cfg.agents.get(agent, {}).get(AGENT_BASE_KEY)

    if not base:
        available_bases = _available_bases(agent, agent_metadata)
        if not available_bases:
            raise CliError(f"No base images found for agent '{agent}' in metadata.")

        request = BaseSelectionRequest(
            agent=agent,
            context=context,
            agent_metadata=agent_metadata,
        )
        base = prompt_for_base(request)
        agent_cfg.base = base
        context.store.save_project(Path(context.project_cfg.path), context.project_cfg)
    else:
        _validate_base(agent, base, agent_metadata)

    if agent_metadata.local_definition_dir is not None:
        return local_image_ref(context.global_cfg.local_image_repository, agent, base)

    return agent_metadata.valid_bases[base]


def _require_agent_metadata(agent: str, images_metadata: ImagesMetadata) -> AgentMetadata:
    agent_metadata = images_metadata.agents.get(agent)
    if not agent_metadata:
        raise CliError(f"Agent '{agent}' is missing from images metadata.")
    return agent_metadata


def _available_bases(
    agent: str,
    agent_metadata: AgentMetadata,
) -> list[str]:
    if not agent_metadata.valid_bases:
        raise CliError(f"Agent '{agent}' does not define any valid bases.")
    return sorted(agent_metadata.valid_bases)


def _validate_base(
    agent: str,
    base: str,
    agent_metadata: AgentMetadata,
) -> None:
    if base not in agent_metadata.valid_bases:
        raise CliError(f"Base '{base}' is not valid for agent '{agent}'.")
