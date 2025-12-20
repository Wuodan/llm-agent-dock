from pathlib import Path
from unittest import TestCase, mock

from aicage.cli_types import ParsedArgs
from aicage.config import GlobalConfig, ProjectConfig
from aicage.config.context import ConfigContext
from aicage.runtime.run_plan import build_run_args
from aicage.runtime.tool_config import ToolConfig


class FakeStore:
    def __init__(self) -> None:
        self.saved = None

    def save_project(self, project_realpath: Path, config: ProjectConfig) -> None:
        self.saved = (project_realpath, config)


class RunPlanTests(TestCase):
    def test_build_run_args_merges_docker_args(self) -> None:
        store = FakeStore()
        project_path = Path("/tmp/project")
        context = ConfigContext(
            store=store,
            project_path=project_path,
            project_cfg=ProjectConfig(path=str(project_path), tools={"codex": {"docker_args": "--project"}}),
            global_cfg=GlobalConfig(
                image_registry="ghcr.io",
                image_registry_api_url="https://ghcr.io/v2",
                image_registry_api_token_url="https://ghcr.io/token?service=ghcr.io&scope=repository",
                image_repository="aicage/aicage",
                default_image_base="ubuntu",
                docker_args="--global",
                tools={},
            ),
        )
        parsed = ParsedArgs(False, "--cli", "codex", ["--flag"])
        tool_config = ToolConfig(tool_path="~/.codex", tool_config_host=Path("/tmp/.codex"))

        with (
            mock.patch(
                "aicage.runtime.run_plan.resolve_tool_image",
                return_value="ghcr.io/aicage/aicage:codex-ubuntu-latest",
            ),
            mock.patch("aicage.runtime.run_plan.resolve_tool_config", return_value=tool_config),
            mock.patch("aicage.runtime.run_plan.build_auth_mounts", return_value=([], False)),
        ):
            run_args = build_run_args(context, parsed)

        self.assertEqual("--global --project --cli", run_args.merged_docker_args)
        self.assertEqual(["--flag"], run_args.tool_args)

    def test_build_run_args_saves_when_prefs_updated(self) -> None:
        store = FakeStore()
        project_path = Path("/tmp/project")
        context = ConfigContext(
            store=store,
            project_path=project_path,
            project_cfg=ProjectConfig(path=str(project_path), tools={"codex": {}}),
            global_cfg=GlobalConfig(
                image_registry="ghcr.io",
                image_registry_api_url="https://ghcr.io/v2",
                image_registry_api_token_url="https://ghcr.io/token?service=ghcr.io&scope=repository",
                image_repository="aicage/aicage",
                default_image_base="ubuntu",
                docker_args="",
                tools={},
            ),
        )
        parsed = ParsedArgs(False, "", "codex", [])
        tool_config = ToolConfig(tool_path="~/.codex", tool_config_host=Path("/tmp/.codex"))

        with (
            mock.patch(
                "aicage.runtime.run_plan.resolve_tool_image",
                return_value="ghcr.io/aicage/aicage:codex-ubuntu-latest",
            ),
            mock.patch("aicage.runtime.run_plan.resolve_tool_config", return_value=tool_config),
            mock.patch("aicage.runtime.run_plan.build_auth_mounts", return_value=([], True)),
        ):
            build_run_args(context, parsed)

        self.assertIsNotNone(store.saved)
