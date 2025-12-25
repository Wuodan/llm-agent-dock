import tempfile
from pathlib import Path
from unittest import TestCase, mock

from aicage.config import GlobalConfig, ProjectConfig
from aicage.config.context import ConfigContext
from aicage.config.project_config import ToolConfig
from aicage.errors import CliError
from aicage.registry import image_selection


class ImageSelectionTests(TestCase):
    def test_resolve_uses_existing_base(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            project_path = Path(tmp_dir) / "project"
            project_path.mkdir()
            store = mock.Mock()
            context = ConfigContext(
                store=store,
                project_cfg=ProjectConfig(path=str(project_path), tools={}),
                global_cfg=GlobalConfig(
                    image_registry="ghcr.io",
                    image_registry_api_url="https://ghcr.io/v2",
                    image_registry_api_token_url="https://ghcr.io/token?service=ghcr.io&scope=repository",
                    image_repository="aicage/aicage",
                    default_image_base="ubuntu",
                    tools={},
                ),
            )
            context.project_cfg.tools["codex"] = ToolConfig(base="debian")
            selection = image_selection.select_tool_image("codex", context)

            self.assertIsInstance(selection, str)
            self.assertEqual("ghcr.io/aicage/aicage:codex-debian-latest", selection)
            store.save_project.assert_not_called()

    def test_resolve_prompts_and_marks_dirty(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            project_path = Path(tmp_dir) / "project"
            project_path.mkdir()
            store = mock.Mock()
            context = ConfigContext(
                store=store,
                project_cfg=ProjectConfig(path=str(project_path), tools={}),
                global_cfg=GlobalConfig(
                    image_registry="ghcr.io",
                    image_registry_api_url="https://ghcr.io/v2",
                    image_registry_api_token_url="https://ghcr.io/token?service=ghcr.io&scope=repository",
                    image_repository="aicage/aicage",
                    default_image_base="ubuntu",
                    tools={},
                ),
            )
            with mock.patch(
                "aicage.registry.discovery.catalog.discover_tool_bases", return_value=["alpine", "ubuntu"]
            ), mock.patch(
                "aicage.registry.image_selection.prompt_for_base", return_value="alpine"
            ):
                image_selection.select_tool_image("codex", context)

            self.assertEqual("alpine", context.project_cfg.tools["codex"].base)
            store.save_project.assert_called_once_with(project_path, context.project_cfg)

    def test_resolve_raises_without_bases(self) -> None:
        context = ConfigContext(
            store=mock.Mock(),
            project_cfg=ProjectConfig(path="/tmp/project", tools={}),
            global_cfg=GlobalConfig(
                image_registry="ghcr.io",
                image_registry_api_url="https://ghcr.io/v2",
                image_registry_api_token_url="https://ghcr.io/token?service=ghcr.io&scope=repository",
                image_repository="aicage/aicage",
                default_image_base="ubuntu",
                tools={},
            ),
        )
        with mock.patch("aicage.registry.discovery.catalog.discover_tool_bases", return_value=[]):
            with self.assertRaises(CliError):
                image_selection.select_tool_image("codex", context)
