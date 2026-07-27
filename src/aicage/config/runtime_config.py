from pathlib import Path

from aicage._logging import get_logger
from aicage.cli_types import ParsedArgs
from aicage.config.agent.loader import load_agents
from aicage.config.agent.models import AgentMetadata
from aicage.config.base.loader import load_bases
from aicage.config.config_store import SettingsStore
from aicage.config.context import ConfigContext
from aicage.config.extensions.loader import ExtensionMetadata, load_extensions
from aicage.config.image_refs import default_extended_image_ref
from aicage.config.project_config import AgentConfig, _ProjectConfig
from aicage.config.run_config import RunConfig
from aicage.config.run_config_draft import _create_run_config_draft
from aicage.registry.errors import RegistryError
from aicage.runtime.docker_args.resolve.resolver import resolve_docker_args
from aicage.runtime.menu.interaction import RuntimeInteraction


def load_run_config(
    agent: str,
    interaction: RuntimeInteraction,
    parsed: ParsedArgs | None = None,
) -> RunConfig:
    store = SettingsStore()
    project_path = Path.cwd().resolve()
    bases = load_bases()
    agents = load_agents(bases)
    _require_known_agent(agent, agents)
    draft = _create_run_config_draft(
        project_path, agent, store.load_project(project_path), parsed
    )
    context = ConfigContext(
        store=store,
        project_cfg=draft.project_cfg,
        agents=agents,
        bases=bases,
        extensions=load_extensions(),
    )
    _remove_missing_extensions(agent, context.project_cfg, context.extensions)
    result = interaction.configure_run(draft, context, agent)
    mounts, env = resolve_docker_args(context, agent, parsed)
    store.save_project(project_path, draft.project_cfg)

    return RunConfig(
        project_path=project_path,
        agent=agent,
        context=context,
        selection=result.selection,
        project_docker_args=result.project_docker_args,
        mounts=mounts,
        env=env,
    )


def _require_known_agent(agent: str, agents: dict[str, AgentMetadata]) -> None:
    if agent in agents:
        return
    if agent == "config":
        raise RegistryError(
            _unknown_agent_message(
                "Unknown agent 'config'. Use '--config' for config commands.",
                agents,
            )
        )
    raise RegistryError(_unknown_agent_message(f"Unknown agent '{agent}'.", agents))


def _unknown_agent_message(
    message: str,
    agents: dict[str, AgentMetadata],
) -> str:
    if not agents:
        return message
    agent_list = ", ".join(sorted(agents))
    return f"{message} Available agents: {agent_list}."


def _remove_missing_extensions(
    agent: str,
    project_cfg: _ProjectConfig,
    extensions: dict[str, ExtensionMetadata],
) -> None:
    agent_cfg = project_cfg.agents.get(agent)
    if not agent_cfg:
        return
    missing = [ext for ext in agent_cfg.extensions if ext not in extensions]
    if not missing:
        return
    get_logger().warning(
        "Removing unavailable extensions for agent %s: %s",
        agent,
        ", ".join(sorted(missing)),
    )
    _prune_agent_extensions(agent, agent_cfg, extensions)


def _prune_agent_extensions(
    agent: str,
    agent_cfg: AgentConfig,
    extensions: dict[str, ExtensionMetadata],
) -> None:
    remaining_extensions = [
        extension for extension in agent_cfg.extensions if extension in extensions
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
            extensions,
        )
        return
    agent_cfg.image_ref = None
