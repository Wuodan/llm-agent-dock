from aicage.config.agent.models import AgentMetadata
from aicage.config.base.filter import filter_bases
from aicage.config.context import ConfigContext
from aicage.config.extended_images import (
    ExtendedImageConfig,
    extended_image_config_path,
    write_extended_image_config,
)
from aicage.config.image_refs import default_extended_image_ref, extended_image_name
from aicage.config.run_config_draft import RunConfigDraft
from aicage.registry.errors import RegistryError
from aicage.registry.image_selection.extensions.refs import base_image_ref
from aicage.registry.image_selection.models import ImageSelection


def resolve_overview_selection(
    draft: RunConfigDraft,
    context: ConfigContext,
) -> ImageSelection:
    agent_cfg = draft.agent_cfg
    if not agent_cfg.base:
        raise RuntimeError(
            f"Base must be set before resolving overview selection for agent '{draft.agent}'."
        )
    agent_metadata = _require_agent_metadata(draft.agent, context)
    if agent_cfg.base not in filter_bases(context, agent_metadata):
        raise RegistryError(
            f"Base '{agent_cfg.base}' is not valid for agent '{draft.agent}'."
        )
    if agent_cfg.extensions:
        _write_extended_image_ref(draft, context)
    else:
        agent_cfg.image_ref = base_image_ref(
            agent_metadata, draft.agent, agent_cfg.base, context
        )

    return ImageSelection(
        image_ref=agent_cfg.image_ref or "",
        base=agent_cfg.base,
        extensions=list(agent_cfg.extensions),
        base_image_ref=base_image_ref(
            agent_metadata, draft.agent, agent_cfg.base, context
        ),
    )


def _write_extended_image_ref(draft: RunConfigDraft, context: ConfigContext) -> None:
    image_ref = draft.agent_cfg.image_ref or default_extended_image_ref(
        draft.agent,
        draft.agent_cfg.base or "",
        draft.agent_cfg.extensions,
        context.extensions,
    )
    draft.agent_cfg.image_ref = image_ref
    write_extended_image_config(
        ExtendedImageConfig(
            name=extended_image_name(image_ref),
            agent=draft.agent,
            base=draft.agent_cfg.base or "",
            extensions=list(draft.agent_cfg.extensions),
            image_ref=image_ref,
            path=extended_image_config_path(extended_image_name(image_ref)),
        )
    )


def _require_agent_metadata(agent: str, context: ConfigContext) -> AgentMetadata:
    agent_metadata = context.agents.get(agent)
    if not agent_metadata:
        raise RegistryError(f"Agent '{agent}' is missing from config context.")
    return agent_metadata
