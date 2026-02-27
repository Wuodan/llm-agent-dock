import os

from aicage.cli_types import ParsedArgs
from aicage.config.context import ConfigContext
from aicage.config.project_config import AgentConfig
from aicage.docker.runtime import get_container_runtime, get_container_runtime_socket_path
from aicage.runtime.docker_args._support._resolver_types import MountRequest, ResolvedArgs
from aicage.runtime.env_vars import DOCKER_HOST, WINDOWS_DOCKER_HOST
from aicage.runtime.prompts.confirm import prompt_persist_docker_socket
from aicage.runtime.run_args import EnvVar


def resolve(
    context: ConfigContext,
    agent: str,
    parsed: ParsedArgs | None,
) -> ResolvedArgs:
    agent_cfg: AgentConfig = context.project_cfg.agents[agent]
    mounts_cfg = agent_cfg.mounts
    cli_docker_socket = parsed.docker_socket if parsed else False
    docker_socket_enabled = cli_docker_socket or bool(mounts_cfg.docker)
    if not docker_socket_enabled:
        return ResolvedArgs()

    runtime = get_container_runtime()
    if os.name == "nt" and runtime == "docker":
        mounts: list[MountRequest] = []
        env = [EnvVar(name=DOCKER_HOST, value=WINDOWS_DOCKER_HOST)]
    elif os.name == "nt":
        mounts = []
        env = []
    else:
        mounts = [MountRequest(host_path=get_container_runtime_socket_path())]
        env = []

    if cli_docker_socket and mounts_cfg.docker is None:
        if prompt_persist_docker_socket():
            mounts_cfg.docker = True

    return ResolvedArgs(mounts=mounts, env=env)
