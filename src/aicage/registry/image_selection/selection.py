from aicage.config.context import ConfigContext
from aicage.config.project_config import AgentConfig

from ._fresh_selection import fresh_selection
from ._metadata import require_agent_metadata, validate_base
from .extensions.context import ExtensionSelectionContext
from .extensions.handler import handle_extension_selection
from .extensions.refs import base_image_ref
from .interaction import _SelectionInteraction
from .models import ImageSelection


def select_agent_image(
    agent: str,
    context: ConfigContext,
    selection_interaction: _SelectionInteraction,
) -> ImageSelection:
    extensions = context.extensions
    agent_cfg = context.project_cfg.agents.setdefault(agent, AgentConfig())
    agent_metadata = require_agent_metadata(agent, context)
    base = agent_cfg.base

    if agent_cfg.image_ref:
        if base is None:
            return fresh_selection(agent, context, extensions, selection_interaction)
        validate_base(agent, base, context)
        return ImageSelection(
            image_ref=agent_cfg.image_ref,
            base=base,
            extensions=list(agent_cfg.extensions),
            base_image_ref=base_image_ref(agent_metadata, agent, base, context),
        )

    if not base:
        return fresh_selection(agent, context, extensions, selection_interaction)

    validate_base(agent, base, context)
    return handle_extension_selection(
        ExtensionSelectionContext(
            agent=agent,
            base=base,
            agent_cfg=agent_cfg,
            agent_metadata=agent_metadata,
            extensions=extensions,
            context=context,
        ),
        selection_interaction,
    )
