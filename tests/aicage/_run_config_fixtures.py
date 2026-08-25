from pathlib import Path
from unittest import mock

from aicage.config.agent.models import AgentMetadata
from aicage.config.base.models import BaseMetadata
from aicage.config.context import ConfigContext
from aicage.config.project_config import _ProjectConfig
from aicage.config.runtime_config import RunConfig
from aicage.constants import DEFAULT_EXTENDED_IMAGE_NAME
from aicage.registry.image_selection.models import ImageSelection


def build_run_config(
    build_local: bool = True,
    local_definition_dir: Path = Path("/test-tmp/agent"),
) -> RunConfig:
    return _build_run_config(
        build_local=build_local,
        local_definition_dir=local_definition_dir,
    )


def build_custom_run_config() -> RunConfig:
    return _build_run_config(
        build_local=True, local_definition_dir=Path("/test-tmp/definition")
    )


def build_extended_run_config() -> RunConfig:
    return RunConfig(
        project_path=Path("/test-tmp/project"),
        agent="codex",
        context=ConfigContext(
            store=mock.Mock(),
            project_cfg=_ProjectConfig(path="/test-tmp/project", agents={}),
            agents={},
            bases={},
            extensions={},
        ),
        selection=ImageSelection(
            image_ref=f"{DEFAULT_EXTENDED_IMAGE_NAME}:codex-ubuntu-extra",
            base="ubuntu",
            extensions=["extra"],
            agent_image_ref="ghcr.io/aicage/aicage:codex-ubuntu",
        ),
        project_docker_args="",
        mounts=[],
        env=[],
    )


def build_agents_and_bases(
    build_local: bool = True,
    local_definition_dir: Path = Path("/test-tmp/agent"),
) -> tuple[dict[str, BaseMetadata], dict[str, AgentMetadata]]:
    bases = {
        "ubuntu": BaseMetadata(
            from_image="ubuntu:latest",
            base_image_distro="Ubuntu",
            base_image_description="Default",
            architectures=["amd64", "arm64"],
            build_local=False,
            local_definition_dir=Path("/test-tmp/base"),
        )
    }
    agents = {
        "claude": AgentMetadata(
            agent_path_files=[],
            agent_path_directories=["~/.claude"],
            agent_full_name="Claude Code",
            agent_homepage="https://example.com",
            build_local=build_local,
            valid_bases={"ubuntu": "ghcr.io/aicage/aicage:claude-ubuntu"},
            local_definition_dir=local_definition_dir,
        )
    }
    return bases, agents


def _build_run_config(build_local: bool, local_definition_dir: Path) -> RunConfig:
    bases, agents = build_agents_and_bases(
        build_local=build_local,
        local_definition_dir=local_definition_dir,
    )
    return RunConfig(
        project_path=Path("/test-tmp/project"),
        agent="claude",
        context=ConfigContext(
            store=mock.Mock(),
            project_cfg=_ProjectConfig(path="/test-tmp/project", agents={}),
            agents=agents,
            bases=bases,
            extensions={},
        ),
        selection=ImageSelection(
            image_ref="aicage:claude-ubuntu",
            base="ubuntu",
            extensions=[],
            agent_image_ref="aicage:claude-ubuntu",
        ),
        project_docker_args="",
        mounts=[],
        env=[],
    )
