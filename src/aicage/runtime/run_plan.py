from aicage._proxy import proxy_env_vars_from_host
from aicage.cli_types import ParsedArgs
from aicage.config.run_config import RunConfig
from aicage.runtime._host_timezone import resolve_host_timezone
from aicage.runtime.run_args import DockerRunArgs, EnvVar, _merge_docker_args


def build_run_args(config: RunConfig, parsed: ParsedArgs) -> DockerRunArgs:
    merged_docker_args: str = _merge_docker_args(
        config.project_docker_args,
        parsed.docker_args,
    )
    return DockerRunArgs(
        image_ref=config.selection.image_ref,
        merged_docker_args=merged_docker_args,
        agent_args=parsed.agent_args,
        env=[*config.env, *_host_timezone_env(config.env), *proxy_env_vars_from_host()],
        mounts=list(config.mounts),
    )


def _host_timezone_env(existing_env: list[EnvVar]) -> list[EnvVar]:
    if any(env.name == "TZ" for env in existing_env):
        return []

    timezone = resolve_host_timezone()
    if not timezone:
        return []

    return [EnvVar(name="TZ", value=timezone)]
