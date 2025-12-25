import io
import tempfile
from pathlib import Path
from unittest import TestCase, mock

from aicage import cli
from aicage.config import ConfigError, RunConfig
from aicage.config.global_config import GlobalConfig
from aicage.errors import CliError
from aicage.runtime.run_args import DockerRunArgs


def _build_run_args(project_path: Path, image_ref: str, merged_docker_args: str, tool_args: list[str]) -> DockerRunArgs:
    return DockerRunArgs(
        image_ref=image_ref,
        project_path=project_path,
        tool_config_host=project_path / ".codex",
        tool_mount_container=Path("/aicage/tool-config"),
        merged_docker_args=merged_docker_args,
        tool_args=tool_args,
        tool_path=str(project_path / ".codex"),
    )


def _build_run_config(project_path: Path, image_ref: str) -> RunConfig:
    return RunConfig(
        project_path=project_path,
        tool="codex",
        image_ref=image_ref,
        global_cfg=GlobalConfig(
            image_registry="ghcr.io",
            image_registry_api_url="https://ghcr.io/v2",
            image_registry_api_token_url="https://ghcr.io/token?service=ghcr.io&scope=repository",
            image_repository="aicage/aicage",
            default_image_base="ubuntu",
        ),
        project_docker_args="--project",
        mounts=[],
        mount_preferences=mock.Mock(),
    )


class MainFlowTests(TestCase):
    def test_print_project_config_missing(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            config_path = Path(tmp_dir) / "project.yaml"
            store = mock.Mock()
            store.project_config_path.return_value = config_path
            with (
                mock.patch("aicage.cli.SettingsStore", return_value=store),
                mock.patch("sys.stdout", new_callable=io.StringIO) as stdout,
            ):
                cli._print_project_config()

        output = stdout.getvalue()
        self.assertIn("Project config path:", output)
        self.assertIn(str(config_path), output)
        self.assertIn("(missing)", output)

    def test_print_project_config_empty(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            config_path = Path(tmp_dir) / "project.yaml"
            config_path.write_text("", encoding="utf-8")
            store = mock.Mock()
            store.project_config_path.return_value = config_path
            with (
                mock.patch("aicage.cli.SettingsStore", return_value=store),
                mock.patch("sys.stdout", new_callable=io.StringIO) as stdout,
            ):
                cli._print_project_config()

        self.assertIn("(empty)", stdout.getvalue())

    def test_print_project_config_contents(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            config_path = Path(tmp_dir) / "project.yaml"
            config_path.write_text("tools: {}", encoding="utf-8")
            store = mock.Mock()
            store.project_config_path.return_value = config_path
            with (
                mock.patch("aicage.cli.SettingsStore", return_value=store),
                mock.patch("sys.stdout", new_callable=io.StringIO) as stdout,
            ):
                cli._print_project_config()

        self.assertIn("tools: {}", stdout.getvalue())

    def test_main_config_print(self) -> None:
        with (
            mock.patch(
                "aicage.cli.parse_cli",
                return_value=cli.ParsedArgs(False, "", "", [], None, False, "print"),
            ),
            mock.patch("aicage.cli._print_project_config") as print_mock,
            mock.patch("aicage.cli.load_run_config") as load_mock,
        ):
            exit_code = cli.main([])

        self.assertEqual(0, exit_code)
        print_mock.assert_called_once()
        load_mock.assert_not_called()

    def test_main_uses_project_base(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            project_path = Path(tmp_dir)
            run_config = _build_run_config(
                project_path,
                "ghcr.io/aicage/aicage:codex-debian-latest",
            )
            run_args = _build_run_args(
                project_path,
                "ghcr.io/aicage/aicage:codex-debian-latest",
                "--project --cli",
                ["--flag"],
            )
            with (
                mock.patch(
                    "aicage.cli.parse_cli",
                    return_value=cli.ParsedArgs(False, "--cli", "codex", ["--flag"], None, False, None),
                ),
                mock.patch("aicage.cli.load_run_config", return_value=run_config),
                mock.patch("aicage.cli.pull_image"),
                mock.patch("aicage.cli.build_run_args", return_value=run_args),
                mock.patch(
                    "aicage.cli.assemble_docker_run",
                    return_value=["docker", "run", "--flag"],
                ) as assemble_mock,
                mock.patch("aicage.cli.subprocess.run") as run_mock,
            ):
                exit_code = cli.main([])

            self.assertEqual(0, exit_code)
            assemble_mock.assert_called_once()
            run_mock.assert_called_once_with(["docker", "run", "--flag"], check=True)

    def test_main_prompts_and_saves_base(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            project_path = Path(tmp_dir)
            run_config = _build_run_config(
                project_path,
                "ghcr.io/aicage/aicage:codex-alpine-latest",
            )
            run_args = _build_run_args(
                project_path,
                "ghcr.io/aicage/aicage:codex-alpine-latest",
                "--project --cli",
                ["--flag"],
            )
            with (
                mock.patch(
                    "aicage.cli.parse_cli",
                    return_value=cli.ParsedArgs(True, "--cli", "codex", ["--flag"], None, False, None),
                ),
                mock.patch("aicage.cli.load_run_config", return_value=run_config),
                mock.patch("aicage.cli.pull_image"),
                mock.patch("aicage.cli.build_run_args", return_value=run_args),
                mock.patch("aicage.cli.assemble_docker_run", return_value=["docker", "run", "cmd"]),
                mock.patch("sys.stderr", new_callable=io.StringIO) as stderr,
                mock.patch("sys.stdout", new_callable=io.StringIO) as stdout,
            ):
                exit_code = cli.main([])

            self.assertEqual(0, exit_code)
            self.assertIn("docker run cmd", stdout.getvalue())
            self.assertEqual("", stderr.getvalue())

    def test_main_handles_no_available_bases(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            project_path = Path(tmp_dir)
            run_config = _build_run_config(
                project_path,
                "ghcr.io/aicage/aicage:codex-ubuntu-latest",
            )
            with (
                mock.patch(
                    "aicage.cli.parse_cli",
                    return_value=cli.ParsedArgs(True, "", "codex", [], None, False, None),
                ),
                mock.patch("aicage.cli.load_run_config", return_value=run_config),
                mock.patch("aicage.cli.pull_image"),
                mock.patch("aicage.cli.build_run_args", side_effect=CliError("No base images found")),
                mock.patch("sys.stderr", new_callable=io.StringIO) as stderr,
            ):
                exit_code = cli.main([])

            self.assertEqual(1, exit_code)
            self.assertIn("No base images found", stderr.getvalue())

    def test_main_handles_config_error(self) -> None:
        with (
            mock.patch(
                "aicage.cli.parse_cli",
                return_value=cli.ParsedArgs(False, "", "codex", [], None, False, None),
            ),
            mock.patch("aicage.cli.load_run_config", side_effect=ConfigError("bad config")),
            mock.patch("sys.stderr", new_callable=io.StringIO) as stderr,
        ):
            exit_code = cli.main([])

        self.assertEqual(1, exit_code)
        self.assertIn("bad config", stderr.getvalue())

    def test_main_keyboard_interrupt(self) -> None:
        with mock.patch("aicage.cli.parse_cli", side_effect=KeyboardInterrupt):
            with mock.patch("sys.stdout", new_callable=io.StringIO):
                exit_code = cli.main([])
        self.assertEqual(130, exit_code)
