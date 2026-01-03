from pathlib import Path

from aicage.config.global_config import GlobalConfig
from aicage.config.runtime_config import RunConfig
from aicage.registry.images_metadata.models import ImagesMetadata


def build_run_config(
    agent_version: str | None = "1.2.3",
    build_local: bool = True,
) -> RunConfig:
    return RunConfig(
        project_path=Path("/tmp/project"),
        agent="claude",
        base="ubuntu",
        image_ref="aicage:claude-ubuntu",
        agent_version=agent_version,
        global_cfg=GlobalConfig(
            image_registry="ghcr.io",
            image_registry_api_url="https://ghcr.io/v2",
            image_registry_api_token_url="https://ghcr.io/token?service=ghcr.io&scope=repository",
            image_repository="aicage/aicage",
            image_base_repository="aicage/aicage-image-base",
            default_image_base="ubuntu",
            version_check_image="ghcr.io/aicage/aicage-image-util:agent-version",
            local_image_repository="aicage",
            agents={},
        ),
        images_metadata=build_images_metadata(build_local=build_local),
        project_docker_args="",
        mounts=[],
    )


def build_images_metadata(build_local: bool = True) -> ImagesMetadata:
    return ImagesMetadata.from_mapping(
        {
            "aicage-image": {"version": "0.3.3"},
            "aicage-image-base": {"version": "0.3.3"},
            "bases": {
                "ubuntu": {
                    "root_image": "ubuntu:latest",
                    "base_image_distro": "Ubuntu",
                    "base_image_description": "Default",
                    "os_installer": "distro/debian/install.sh",
                    "test_suite": "default",
                }
            },
            "agent": {
                "claude": {
                    "agent_path": "~/.claude",
                    "agent_full_name": "Claude Code",
                    "agent_homepage": "https://example.com",
                    "build_local": build_local,
                    "valid_bases": {"ubuntu": "ghcr.io/aicage/aicage:claude-ubuntu"},
                }
            },
        }
    )
