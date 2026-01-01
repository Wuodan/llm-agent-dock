from pathlib import Path
from unittest import TestCase, mock

from aicage.config.context import ConfigContext, build_config_context
from aicage.config.global_config import GlobalConfig
from aicage.config.project_config import ProjectConfig
from aicage.registry.images_metadata.models import ImagesMetadata


class ContextTests(TestCase):
    def test_image_repository_ref(self) -> None:
        context = ConfigContext(
            store=mock.Mock(),
            project_cfg=ProjectConfig(path="/work/project", agents={}),
            global_cfg=GlobalConfig(
                image_registry="ghcr.io",
                image_registry_api_url="https://ghcr.io/v2",
                image_registry_api_token_url="https://ghcr.io/token?service=ghcr.io&scope=repository",
                image_repository="aicage/aicage",
                default_image_base="ubuntu",
                agents={},
            ),
            images_metadata=self._get_images_metadata(),
        )
        self.assertEqual("ghcr.io/aicage/aicage", context.image_repository_ref())

    def test_build_config_context_uses_store(self) -> None:
        global_cfg = GlobalConfig(
            image_registry="ghcr.io",
            image_registry_api_url="https://ghcr.io/v2",
            image_registry_api_token_url="https://ghcr.io/token?service=ghcr.io&scope=repository",
            image_repository="aicage/aicage",
            default_image_base="ubuntu",
            agents={},
        )
        project_cfg = ProjectConfig(path="/work/project", agents={})
        with (
            mock.patch("aicage.config.context.SettingsStore") as store_cls,
            mock.patch("aicage.config.context.Path.cwd", return_value=Path("/work/project")),
            mock.patch("aicage.config.context.load_images_metadata") as load_metadata,
        ):
            store = store_cls.return_value
            store.load_global.return_value = global_cfg
            store.load_project.return_value = project_cfg
            load_metadata.return_value = self._get_images_metadata()

            context = build_config_context()

        self.assertEqual(global_cfg, context.global_cfg)
        self.assertEqual(project_cfg, context.project_cfg)
        self.assertEqual(self._get_images_metadata(), context.images_metadata)

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
