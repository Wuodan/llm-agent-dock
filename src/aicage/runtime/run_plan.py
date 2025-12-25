from pathlib import Path

from aicage.cli_types import ParsedArgs
from aicage.config.runtime_config import RunConfig
from aicage.runtime.run_args import DockerRunArgs, merge_docker_args
from aicage.runtime.tool_config import ToolConfig, resolve_tool_config

__all__ = ["build_run_args"]


def build_run_args(config: RunConfig, parsed: ParsedArgs) -> DockerRunArgs:
    tool_config: ToolConfig = resolve_tool_config(config.image_ref)

    merged_docker_args: str = merge_docker_args(
        config.project_docker_args,
        parsed.docker_args,
    )

    return DockerRunArgs(
        image_ref=config.image_ref,
        project_path=config.project_path,
        tool_config_host=tool_config.tool_config_host,
        tool_mount_container=Path("/aicage/tool-config"),
        merged_docker_args=merged_docker_args,
        tool_args=parsed.tool_args,
        tool_path=tool_config.tool_path,
        mounts=config.mounts,
    )
