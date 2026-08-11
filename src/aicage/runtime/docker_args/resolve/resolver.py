from itertools import chain
from pathlib import Path

from aicage.cli_types import ParsedArgs
from aicage.config.context import ConfigContext
from aicage.config.project_config import AgentConfig
from aicage.errors import AicageError
from aicage.paths import container_project_path
from aicage.runtime.docker_args.support.resolver_types import ResolvedArgs, Resolver
from aicage.runtime.env_vars import _AICAGE_WORKSPACE
from aicage.runtime.run_args import EnvVar, MountSpec

from ..resolvers import (
    agent_config,
    docker_socket,
    git_config,
    git_root,
    gpg,
    project,
    shares,
    ssh_keys,
)
from ._mounts import map_mount_requests


def resolve_docker_args(
    context: ConfigContext,
    agent: str,
    parsed: ParsedArgs | None,
) -> tuple[list[MountSpec], list[EnvVar]]:
    context.project_cfg.agents.setdefault(agent, AgentConfig())
    project_path = Path(context.project_cfg.path).resolve()
    resolved = [
        _resolve_provider(provider, context, agent, parsed)
        for provider in _resolver_sequence()
    ]
    mount_requests = list(chain.from_iterable(item.mounts for item in resolved))
    env = list(chain.from_iterable(item.env for item in resolved))
    host_home = Path.home().resolve()
    mounts = map_mount_requests(mount_requests)
    _validate_home_mount_safety(mounts, host_home)
    workspace_path = container_project_path(project_path)
    env.append(EnvVar(name=_AICAGE_WORKSPACE, value=workspace_path.as_posix()))
    return mounts, env


def _resolve_provider(
    provider: Resolver,
    context: ConfigContext,
    agent: str,
    parsed: ParsedArgs | None,
) -> ResolvedArgs:
    return provider(context, agent, parsed)


def _resolver_sequence() -> tuple[Resolver, ...]:
    return (
        project.resolve,
        agent_config.resolve,
        git_config.resolve,
        gpg.resolve,
        ssh_keys.resolve,
        git_root.resolve,
        docker_socket.resolve,
        shares.resolve,
    )


def _validate_home_mount_safety(mounts: list[MountSpec], host_home: Path) -> None:
    for mount in mounts:
        host_path = mount.host_path.resolve()
        if host_path == host_home or host_path in host_home.parents:
            raise AicageError(
                "Refusing to start: this would expose your home directory to the container via "
                f"{host_path}.\n"
                "Use one of these safer options instead:\n"
                "- Start aicage from the project repository directory. If needed, add folders "
                "outside it with `--share <path>`.\n"
                "- For multi-project setups, keep repositories under a folder such as "
                "~/workspace and start aicage from there.",
            )
