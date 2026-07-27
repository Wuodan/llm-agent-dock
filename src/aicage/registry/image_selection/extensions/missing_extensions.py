from aicage._logging import get_logger
from aicage.config.context import ConfigContext
from aicage.config.image_refs import default_extended_image_ref
from aicage.config.project_config import AgentConfig


def ensure_extensions_exist(
    agent: str,
    context: ConfigContext,
) -> bool:
    agent_cfg = context.project_cfg.agents.get(agent)
    if not agent_cfg:
        return False
    missing = [ext for ext in agent_cfg.extensions if ext not in context.extensions]
    if not missing:
        return False
    get_logger().warning(
        "Removing unavailable extensions for agent %s: %s",
        agent,
        ", ".join(sorted(missing)),
    )
    _remove_missing_extensions(agent, agent_cfg, context)
    return True


def _remove_missing_extensions(
    agent: str,
    agent_cfg: AgentConfig,
    context: ConfigContext,
) -> None:
    remaining_extensions = [
        extension
        for extension in agent_cfg.extensions
        if extension in context.extensions
    ]
    agent_cfg.extensions = remaining_extensions
    agent_cfg.extension_mounts = {
        key: value
        for key, value in agent_cfg.extension_mounts.items()
        if key in remaining_extensions
    }
    if remaining_extensions and agent_cfg.base:
        agent_cfg.image_ref = default_extended_image_ref(
            agent,
            agent_cfg.base,
            remaining_extensions,
            context.extensions,
        )
    else:
        agent_cfg.image_ref = None
