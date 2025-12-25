from pathlib import Path
from unittest import TestCase, mock

from aicage.config.context import ConfigContext, build_config_context
from aicage.config.global_config import GlobalConfig
from aicage.config.project_config import ProjectConfig


class ContextTests(TestCase):
    def test_image_repository_ref(self) -> None:
        context = ConfigContext(
            store=mock.Mock(),
            project_cfg=ProjectConfig(path="/work/project", tools={}),
            global_cfg=GlobalConfig(
                image_registry="ghcr.io",
                image_registry_api_url="https://ghcr.io/v2",
                image_registry_api_token_url="https://ghcr.io/token?service=ghcr.io&scope=repository",
                image_repository="aicage/aicage",
                default_image_base="ubuntu",
                tools={},
            ),
        )
        self.assertEqual("ghcr.io/aicage/aicage", context.image_repository_ref())

    def test_build_config_context_uses_store(self) -> None:
        global_cfg = GlobalConfig(
            image_registry="ghcr.io",
            image_registry_api_url="https://ghcr.io/v2",
            image_registry_api_token_url="https://ghcr.io/token?service=ghcr.io&scope=repository",
            image_repository="aicage/aicage",
            default_image_base="ubuntu",
            tools={},
        )
        project_cfg = ProjectConfig(path="/work/project", tools={})
        with (
            mock.patch("aicage.config.context.SettingsStore") as store_cls,
            mock.patch("aicage.config.context.Path.cwd", return_value=Path("/work/project")),
        ):
            store = store_cls.return_value
            store.load_global.return_value = global_cfg
            store.load_project.return_value = project_cfg

            context = build_config_context()

        self.assertEqual(global_cfg, context.global_cfg)
        self.assertEqual(project_cfg, context.project_cfg)
