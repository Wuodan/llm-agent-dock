from pathlib import Path
from unittest import TestCase, mock

from aicage.cli_types import ParsedArgs
from aicage.config.context import ConfigContext
from aicage.config.global_config import GlobalConfig
from aicage.config.project_config import AgentConfig, ProjectConfig
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
from aicage.runtime.mounts import resolver
from aicage.runtime.run_args import MountSpec


class ResolverTests(TestCase):
    def test_resolve_mounts_aggregates_mounts(self) -> None:
        project_cfg = ProjectConfig(path="/tmp/project", agents={"codex": AgentConfig()})
        context = ConfigContext(
            store=mock.Mock(),
            project_cfg=project_cfg,
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
            images_metadata=self._get_images_metadata(),
        )
        parsed = ParsedArgs(False, "", "codex", [], None, False, None)
        git_mount = MountSpec(host_path=Path("/tmp/git"), container_path=Path("/git"))
        ssh_mount = MountSpec(host_path=Path("/tmp/ssh"), container_path=Path("/ssh"))
        gpg_mount = MountSpec(host_path=Path("/tmp/gpg"), container_path=Path("/gpg"))
        entry_mount = MountSpec(host_path=Path("/tmp/entry"), container_path=Path("/entry"), read_only=True)
        docker_mount = MountSpec(host_path=Path("/tmp/docker"), container_path=Path("/run/docker.sock"))

        with (
            mock.patch("aicage.runtime.mounts.resolver.resolve_git_config_mount", return_value=[git_mount]) as git_mock,
            mock.patch("aicage.runtime.mounts.resolver.resolve_ssh_mount", return_value=[ssh_mount]) as ssh_mock,
            mock.patch("aicage.runtime.mounts.resolver.resolve_gpg_mount", return_value=[gpg_mount]) as gpg_mock,
            mock.patch(
                "aicage.runtime.mounts.resolver.resolve_entrypoint_mount", return_value=[entry_mount]
            ) as entry_mock,
            mock.patch(
                "aicage.runtime.mounts.resolver.resolve_docker_socket_mount", return_value=[docker_mount]
            ) as docker_mock,
        ):
            mounts = resolver.resolve_mounts(context, "codex", parsed)

        self.assertEqual([git_mount, ssh_mount, gpg_mount, entry_mount, docker_mount], mounts)
        git_mock.assert_called_once_with(project_cfg.agents["codex"])
        ssh_mock.assert_called_once_with(Path("/tmp/project"), project_cfg.agents["codex"])
        gpg_mock.assert_called_once_with(Path("/tmp/project"), project_cfg.agents["codex"])
        entry_mock.assert_called_once_with(project_cfg.agents["codex"], None)
        docker_mock.assert_called_once_with(project_cfg.agents["codex"], False)

    def test_resolve_mounts_inserts_agent_config(self) -> None:
        project_cfg = ProjectConfig(path="/tmp/project", agents={})
        context = ConfigContext(
            store=mock.Mock(),
            project_cfg=project_cfg,
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
            images_metadata=self._get_images_metadata(),
        )

        with (
            mock.patch("aicage.runtime.mounts.resolver.resolve_git_config_mount", return_value=[]),
            mock.patch("aicage.runtime.mounts.resolver.resolve_ssh_mount", return_value=[]),
            mock.patch("aicage.runtime.mounts.resolver.resolve_gpg_mount", return_value=[]),
            mock.patch("aicage.runtime.mounts.resolver.resolve_entrypoint_mount", return_value=[]),
            mock.patch("aicage.runtime.mounts.resolver.resolve_docker_socket_mount", return_value=[]),
        ):
            resolver.resolve_mounts(context, "codex", None)

        self.assertIsInstance(project_cfg.agents["codex"], AgentConfig)

    @staticmethod
    def _get_images_metadata() -> ImagesMetadata:
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
                    "codex": {
                        AGENT_PATH_KEY: "~/.codex",
                        AGENT_FULL_NAME_KEY: "Codex CLI",
                        AGENT_HOMEPAGE_KEY: "https://example.com",
                        BUILD_LOCAL_KEY: False,
                        _VALID_BASES_KEY: {"ubuntu": "ghcr.io/aicage/aicage:codex-ubuntu"},
                    }
                },
            }
        )
