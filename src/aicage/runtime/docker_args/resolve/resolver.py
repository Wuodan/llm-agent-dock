from itertools import chain
from pathlib import Path

from aicage.cli_types import ParsedArgs
from aicage.config.context import ConfigContext
from aicage.config.project_config import AgentConfig
from aicage.errors import AicageError
from aicage.paths import container_project_path
from aicage.runtime.docker_args._support._resolver_types import MountRequest, ResolvedArgs, Resolver
from aicage.runtime.env_vars import AICAGE_WORKSPACE
from aicage.runtime.run_args import EnvVar, MountSpec

from .._resolvers import _agent_config, _docker_socket, _git_config, _git_root, _gpg, _project, _shares, _ssh_keys
from .._support._mount_prompt import resolve_mount_prompt_prefs
from ._mounts import map_mount_requests


def resolve_docker_args(
    context: ConfigContext,
    agent: str,
    parsed: ParsedArgs | None,
) -> tuple[list[MountSpec], list[EnvVar]]:
    agent_cfg = context.project_cfg.agents.setdefault(agent, AgentConfig())
    project_path = Path(context.project_cfg.path).resolve()
    mount_prompt_prefs = resolve_mount_prompt_prefs(project_path, agent_cfg, context.extensions)
    if mount_prompt_prefs is not None:
        for key in ("gitconfig", "gitroot", "gnupg", "ssh"):
            if getattr(agent_cfg.mounts, key) is None:
                setattr(agent_cfg.mounts, key, key in mount_prompt_prefs.git_mounts)
        agent_cfg.extension_mounts.update(mount_prompt_prefs.extension_mounts)
    resolved = [_resolve_provider(provider, context, agent, parsed) for provider in _resolver_sequence()]
    mount_requests = list(chain.from_iterable(item.mounts for item in resolved))
    env = list(chain.from_iterable(item.env for item in resolved))
    host_home = Path.home().resolve()
    mounts = _map_mount_requests(mount_requests)
    _validate_home_mount_safety(mounts, host_home)
    workspace_path = container_project_path(project_path)
    env.append(EnvVar(name=AICAGE_WORKSPACE, value=workspace_path.as_posix()))
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
        _project.resolve,
        _agent_config.resolve,
        _git_config.resolve,
        _gpg.resolve,
        _ssh_keys.resolve,
        _git_root.resolve,
        _docker_socket.resolve,
        _shares.resolve,
    )


def _map_mount_requests(
    requests: list[MountRequest],
) -> list[MountSpec]:
    return map_mount_requests(requests)


def _validate_home_mount_safety(mounts: list[MountSpec], host_home: Path) -> None:
    for mount in mounts:
        host_path = mount.host_path.resolve()
        if host_path == host_home or host_path in host_home.parents:
            raise AicageError(
                "Refusing to start: this would mount your home directory into the container: "
                f"{host_path}",
            )
