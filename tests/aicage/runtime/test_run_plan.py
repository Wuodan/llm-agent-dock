from pathlib import Path
from unittest import TestCase, mock

from aicage.cli_types import ParsedArgs
from aicage.config import RunConfig
from aicage.config.global_config import GlobalConfig
from aicage.registry.images_metadata.models import ImagesMetadata
from aicage.runtime.agent_config import AgentConfig
from aicage.runtime.run_plan import build_run_args


class RunPlanTests(TestCase):
    def test_build_run_args_merges_docker_args(self) -> None:
        project_path = Path("/tmp/project")
        config = RunConfig(
            project_path=project_path,
            agent="codex",
            base="ubuntu",
            image_ref="ghcr.io/aicage/aicage:codex-ubuntu",
            agent_version=None,
            global_cfg=self._get_global_config(),
            images_metadata=self._get_images_metadata(),
            project_docker_args="--project",
            mounts=[],
        )
        parsed = ParsedArgs(False, "--cli", "codex", ["--flag"], None, False, None)
        agent_config = AgentConfig(agent_path="~/.codex", agent_config_host=Path("/tmp/.codex"))

        with mock.patch("aicage.runtime.run_plan.resolve_agent_config", return_value=agent_config):
            run_args = build_run_args(config, parsed)

        self.assertEqual("--project --cli", run_args.merged_docker_args)
        self.assertEqual(["--flag"], run_args.agent_args)

    def test_build_run_args_uses_mounts_from_config(self) -> None:
        project_path = Path("/tmp/project")
        mount = mock.Mock()
        config = RunConfig(
            project_path=project_path,
            agent="codex",
            base="ubuntu",
            image_ref="ghcr.io/aicage/aicage:codex-ubuntu",
            agent_version=None,
            global_cfg=self._get_global_config(),
            images_metadata=self._get_images_metadata(),
            project_docker_args="",
            mounts=[mount],
        )
        parsed = ParsedArgs(False, "", "codex", [], None, False, None)
        agent_config = AgentConfig(agent_path="~/.codex", agent_config_host=Path("/tmp/.codex"))

        with mock.patch("aicage.runtime.run_plan.resolve_agent_config", return_value=agent_config):
            run_args = build_run_args(config, parsed)

        self.assertEqual([mount], run_args.mounts)

    @staticmethod
    def _get_global_config() -> GlobalConfig:
        return GlobalConfig(
            image_registry="ghcr.io",
            image_registry_api_url="https://ghcr.io/v2",
            image_registry_api_token_url="https://ghcr.io/token?service=ghcr.io&scope=repository",
            image_repository="aicage/aicage",
            image_base_repository="aicage/aicage-image-base",
            default_image_base="ubuntu",
            version_check_image="ghcr.io/aicage/aicage-image-util:latest",
            agents={},
        )

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
