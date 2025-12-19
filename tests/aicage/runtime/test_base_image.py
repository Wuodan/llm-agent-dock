import tempfile
from pathlib import Path
from unittest import TestCase, mock

from aicage.config import GlobalConfig, ProjectConfig
from aicage.config.context import ConfigContext
from aicage.errors import CliError
from aicage.runtime import base_image
from aicage.runtime.base_image import BaseImageSelection


class BaseImageResolutionTests(TestCase):
    def test_resolve_uses_existing_base(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            project_path = Path(tmp_dir) / "project"
            project_path.mkdir()
            tool_dir = Path(tmp_dir) / ".codex"
            context = ConfigContext(
                store=mock.Mock(),
                project_path=project_path,
                project_cfg=ProjectConfig(path=str(project_path), docker_args="", tools={}),
                global_cfg=GlobalConfig(repository="aicage/aicage", default_base="ubuntu", docker_args="", tools={}),
            )
            tool_cfg = {"base": "debian"}
            with mock.patch("aicage.runtime.base_image._pull_image"), mock.patch(
                "aicage.runtime.base_image._read_tool_label", return_value=str(tool_dir)
            ):
                selection = base_image.resolve_base_image("codex", tool_cfg, context)

            self.assertIsInstance(selection, BaseImageSelection)
            self.assertFalse(selection.project_dirty)
            self.assertEqual("aicage/aicage:codex-debian-latest", selection.image_ref)
            self.assertEqual(tool_dir, selection.tool_config_host)

    def test_resolve_prompts_and_marks_dirty(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            project_path = Path(tmp_dir) / "project"
            project_path.mkdir()
            tool_dir = Path(tmp_dir) / ".codex"
            context = ConfigContext(
                store=mock.Mock(),
                project_path=project_path,
                project_cfg=ProjectConfig(path=str(project_path), docker_args="", tools={}),
                global_cfg=GlobalConfig(repository="aicage/aicage", default_base="ubuntu", docker_args="", tools={}),
            )
            tool_cfg: dict = {}
            with mock.patch(
                "aicage.runtime.base_image._discover_available_bases", return_value=["alpine", "ubuntu"]
            ), mock.patch(
                "aicage.runtime.base_image._pull_image"
            ), mock.patch(
                "aicage.runtime.base_image._read_tool_label", return_value=str(tool_dir)
            ), mock.patch(
                "aicage.runtime.base_image.prompt_for_base", return_value="alpine"
            ):
                selection = base_image.resolve_base_image("codex", tool_cfg, context)

            self.assertTrue(selection.project_dirty)
            self.assertEqual("alpine", tool_cfg["base"])
            self.assertEqual(tool_dir, selection.tool_config_host)

    def test_resolve_raises_without_bases(self) -> None:
        context = ConfigContext(
            store=mock.Mock(),
            project_path=Path("/tmp/project"),
            project_cfg=ProjectConfig(path="/tmp/project", docker_args="", tools={}),
            global_cfg=GlobalConfig(repository="aicage/aicage", default_base="ubuntu", docker_args="", tools={}),
        )
        tool_cfg: dict = {}
        with mock.patch("aicage.runtime.base_image._discover_available_bases", return_value=[]):
            with self.assertRaises(CliError):
                base_image.resolve_base_image("codex", tool_cfg, context)
