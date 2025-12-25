from pathlib import Path
from unittest import TestCase, mock

from aicage.cli_types import ParsedArgs
from aicage.config import RunConfig
from aicage.config.global_config import GlobalConfig
from aicage.runtime.run_plan import build_run_args
from aicage.runtime.tool_config import ToolConfig


class RunPlanTests(TestCase):
    def test_build_run_args_merges_docker_args(self) -> None:
        project_path = Path("/tmp/project")
        config = RunConfig(
            project_path=project_path,
            tool="codex",
            image_ref="ghcr.io/aicage/aicage:codex-ubuntu-latest",
            global_cfg=self._get_global_config(),
            global_docker_args="--global",
            project_docker_args="--project",
            mounts=[],
            mount_preferences=mock.Mock(),
        )
        parsed = ParsedArgs(False, "--cli", "codex", ["--flag"], None, False, None)
        tool_config = ToolConfig(tool_path="~/.codex", tool_config_host=Path("/tmp/.codex"))

        with mock.patch("aicage.runtime.run_plan.resolve_tool_config", return_value=tool_config):
            run_args = build_run_args(config, parsed)

        self.assertEqual("--global --project --cli", run_args.merged_docker_args)
        self.assertEqual(["--flag"], run_args.tool_args)

    def test_build_run_args_uses_mounts_from_config(self) -> None:
        project_path = Path("/tmp/project")
        mount = mock.Mock()
        config = RunConfig(
            project_path=project_path,
            tool="codex",
            image_ref="ghcr.io/aicage/aicage:codex-ubuntu-latest",
            global_cfg=self._get_global_config(),
            global_docker_args="",
            project_docker_args="",
            mounts=[mount],
            mount_preferences=mock.Mock(),
        )
        parsed = ParsedArgs(False, "", "codex", [], None, False, None)
        tool_config = ToolConfig(tool_path="~/.codex", tool_config_host=Path("/tmp/.codex"))

        with mock.patch("aicage.runtime.run_plan.resolve_tool_config", return_value=tool_config):
            run_args = build_run_args(config, parsed)

        self.assertEqual([mount], run_args.mounts)

    @staticmethod
    def _get_global_config() -> GlobalConfig:
        return GlobalConfig(
            image_registry="ghcr.io",
            image_registry_api_url="https://ghcr.io/v2",
            image_registry_api_token_url="https://ghcr.io/token?service=ghcr.io&scope=repository",
            image_repository="aicage/aicage",
            default_image_base="ubuntu",
        )
