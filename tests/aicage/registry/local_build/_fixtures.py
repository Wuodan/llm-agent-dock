from pathlib import Path

from aicage.config.global_config import GlobalConfig
from aicage.config.runtime_config import RunConfig
from aicage.registry.images_metadata.models import (
    _AGENT_KEY,
    _AICAGE_IMAGE_BASE_KEY,
    _AICAGE_IMAGE_KEY,
    _BASE_IMAGE_DESCRIPTION_KEY,
    _BASE_IMAGE_DISTRO_KEY,
    _BASES_KEY,
    _OS_INSTALLER_KEY,
    _ROOT_IMAGE_KEY,
    _TEST_SUITE_KEY,
    _VALID_BASES_KEY,
    _VERSION_KEY,
    AGENT_FULL_NAME_KEY,
    AGENT_HOMEPAGE_KEY,
    AGENT_PATH_KEY,
    BUILD_LOCAL_KEY,
    ImagesMetadata,
)


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
            _AICAGE_IMAGE_KEY: {_VERSION_KEY: "0.3.3"},
            _AICAGE_IMAGE_BASE_KEY: {_VERSION_KEY: "0.3.3"},
            _BASES_KEY: {
                "ubuntu": {
                    _ROOT_IMAGE_KEY: "ubuntu:latest",
                    _BASE_IMAGE_DISTRO_KEY: "Ubuntu",
                    _BASE_IMAGE_DESCRIPTION_KEY: "Default",
                    _OS_INSTALLER_KEY: "distro/debian/install.sh",
                    _TEST_SUITE_KEY: "default",
                }
            },
            _AGENT_KEY: {
                "claude": {
                    AGENT_PATH_KEY: "~/.claude",
                    AGENT_FULL_NAME_KEY: "Claude Code",
                    AGENT_HOMEPAGE_KEY: "https://example.com",
                    BUILD_LOCAL_KEY: build_local,
                    _VALID_BASES_KEY: {"ubuntu": "ghcr.io/aicage/aicage:claude-ubuntu"},
                }
            },
        }
    )
