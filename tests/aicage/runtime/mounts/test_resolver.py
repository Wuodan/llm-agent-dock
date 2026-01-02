from pathlib import Path
from unittest import TestCase, mock

from aicage.cli_types import ParsedArgs
from aicage.config.context import ConfigContext
from aicage.config.global_config import GlobalConfig
from aicage.config.project_config import AgentConfig, ProjectConfig
from aicage.registry.images_metadata.models import ImagesMetadata
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
                version_check_image="ghcr.io/aicage/aicage-image-util:latest",
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
                "aicage.runtime.mounts.resolver._resolve_entrypoint_mount", return_value=[entry_mount]
            ) as entry_mock,
            mock.patch(
                "aicage.runtime.mounts.resolver._resolve_docker_socket_mount", return_value=[docker_mount]
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
                version_check_image="ghcr.io/aicage/aicage-image-util:latest",
                agents={},
            ),
            images_metadata=self._get_images_metadata(),
        )

        with (
            mock.patch("aicage.runtime.mounts.resolver.resolve_git_config_mount", return_value=[]),
            mock.patch("aicage.runtime.mounts.resolver.resolve_ssh_mount", return_value=[]),
            mock.patch("aicage.runtime.mounts.resolver.resolve_gpg_mount", return_value=[]),
            mock.patch("aicage.runtime.mounts.resolver._resolve_entrypoint_mount", return_value=[]),
            mock.patch("aicage.runtime.mounts.resolver._resolve_docker_socket_mount", return_value=[]),
        ):
            resolver.resolve_mounts(context, "codex", None)

        self.assertIsInstance(project_cfg.agents["codex"], AgentConfig)

    @staticmethod
    def _get_images_metadata() -> ImagesMetadata:
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
                    "codex": {
                        "agent_path": "~/.codex",
                        "agent_full_name": "Codex CLI",
                        "agent_homepage": "https://example.com",
                        "redistributable": True,
                        "valid_bases": {"ubuntu": "ghcr.io/aicage/aicage:codex-ubuntu"},
                    }
                },
            }
        )
