import io
import tempfile
from pathlib import Path
from unittest import TestCase, mock

from aicage import cli
from aicage.cli import _print_config as print_config
from aicage.cli_types import ParsedArgs
from aicage.config import ConfigError, RunConfig
from aicage.config.global_config import GlobalConfig
from aicage.errors import CliError
from aicage.registry.images_metadata.models import ImagesMetadata
from aicage.runtime.run_args import DockerRunArgs


def _build_run_args(
    project_path: Path, image_ref: str, merged_docker_args: str, agent_args: list[str]
) -> DockerRunArgs:
    return DockerRunArgs(
        image_ref=image_ref,
        project_path=project_path,
        agent_config_host=project_path / ".codex",
        agent_config_mount_container=Path("/aicage/agent-config"),
        merged_docker_args=merged_docker_args,
        agent_args=agent_args,
        agent_path=str(project_path / ".codex"),
    )


def _build_run_config(project_path: Path, image_ref: str) -> RunConfig:
    return RunConfig(
        project_path=project_path,
        agent="codex",
        base="ubuntu",
        image_ref=image_ref,
        agent_version=None,
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
        images_metadata=_build_images_metadata(),
        project_docker_args="--project",
        mounts=[],
    )


def _build_images_metadata() -> ImagesMetadata:
    return ImagesMetadata.from_mapping(
        {
            "aicage-image": {"version": "0.3.3"},
            "aicage-image-base": {"version": "0.3.3"},
            "bases": {
                "alpine": {
                    "root_image": "alpine:latest",
                    "base_image_distro": "Alpine",
                    "base_image_description": "Minimal",
                    "os_installer": "distro/alpine/install.sh",
                    "test_suite": "default",
                },
                "debian": {
                    "root_image": "debian:latest",
                    "base_image_distro": "Debian",
                    "base_image_description": "Default",
                    "os_installer": "distro/debian/install.sh",
                    "test_suite": "default",
                },
                "ubuntu": {
                    "root_image": "ubuntu:latest",
                    "base_image_distro": "Ubuntu",
                    "base_image_description": "Default",
                    "os_installer": "distro/debian/install.sh",
                    "test_suite": "default",
                },
            },
            "agent": {
                "codex": {
                    "agent_path": "~/.codex",
                    "agent_full_name": "Codex CLI",
                    "agent_homepage": "https://example.com",
                    "build_local": False,
                    "valid_bases": {
                        "alpine": "ghcr.io/aicage/aicage:codex-alpine",
                        "debian": "ghcr.io/aicage/aicage:codex-debian",
                        "ubuntu": "ghcr.io/aicage/aicage:codex-ubuntu",
                    },
                }
            },
        }
    )


class MainFlowTests(TestCase):
    def test_print_project_config_missing(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            config_path = Path(tmp_dir) / "project.yaml"
            store = mock.Mock()
            store.project_config_path.return_value = config_path
            with (
                mock.patch("aicage.cli._print_config.SettingsStore", return_value=store),
                mock.patch("sys.stdout", new_callable=io.StringIO) as stdout,
            ):
                print_config.print_project_config()

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
                mock.patch("aicage.cli._print_config.SettingsStore", return_value=store),
                mock.patch("sys.stdout", new_callable=io.StringIO) as stdout,
            ):
                print_config.print_project_config()

        self.assertIn("(empty)", stdout.getvalue())

    def test_print_project_config_contents(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            config_path = Path(tmp_dir) / "project.yaml"
            config_path.write_text("agents: {}", encoding="utf-8")
            store = mock.Mock()
            store.project_config_path.return_value = config_path
            with (
                mock.patch("aicage.cli._print_config.SettingsStore", return_value=store),
                mock.patch("sys.stdout", new_callable=io.StringIO) as stdout,
            ):
                print_config.print_project_config()

        self.assertIn("agents: {}", stdout.getvalue())

    def test_main_config_print(self) -> None:
        with (
            mock.patch(
                "aicage.cli.entrypoint.parse_cli",
                return_value=ParsedArgs(False, "", "", [], None, False, "print"),
            ),
            mock.patch("aicage.cli.entrypoint.print_project_config") as print_mock,
            mock.patch("aicage.cli.entrypoint.load_run_config") as load_mock,
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
                "ghcr.io/aicage/aicage:codex-debian",
            )
            run_args = _build_run_args(
                project_path,
                "ghcr.io/aicage/aicage:codex-debian",
                "--project --cli",
                ["--flag"],
            )
            with (
                mock.patch(
                    "aicage.cli.entrypoint.parse_cli",
                    return_value=ParsedArgs(False, "--cli", "codex", ["--flag"], None, False, None),
                ),
                mock.patch("aicage.cli.entrypoint.load_run_config", return_value=run_config),
                mock.patch("aicage.cli.entrypoint.pull_image"),
                mock.patch("aicage.cli.entrypoint.build_run_args", return_value=run_args),
                mock.patch(
                    "aicage.cli.entrypoint.assemble_docker_run",
                    return_value=["docker", "run", "--flag"],
                ) as assemble_mock,
                mock.patch("aicage.cli.entrypoint.subprocess.run") as run_mock,
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
                "ghcr.io/aicage/aicage:codex-alpine",
            )
            run_args = _build_run_args(
                project_path,
                "ghcr.io/aicage/aicage:codex-alpine",
                "--project --cli",
                ["--flag"],
            )
            with (
                mock.patch(
                    "aicage.cli.entrypoint.parse_cli",
                    return_value=ParsedArgs(True, "--cli", "codex", ["--flag"], None, False, None),
                ),
                mock.patch("aicage.cli.entrypoint.load_run_config", return_value=run_config),
                mock.patch("aicage.cli.entrypoint.pull_image"),
                mock.patch("aicage.cli.entrypoint.build_run_args", return_value=run_args),
                mock.patch(
                    "aicage.cli.entrypoint.assemble_docker_run",
                    return_value=["docker", "run", "cmd"],
                ),
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
                "ghcr.io/aicage/aicage:codex-ubuntu",
            )
            with (
                mock.patch(
                    "aicage.cli.entrypoint.parse_cli",
                    return_value=ParsedArgs(True, "", "codex", [], None, False, None),
                ),
                mock.patch("aicage.cli.entrypoint.load_run_config", return_value=run_config),
                mock.patch("aicage.cli.entrypoint.pull_image"),
                mock.patch(
                    "aicage.cli.entrypoint.build_run_args",
                    side_effect=CliError("No base images found"),
                ),
                mock.patch("sys.stderr", new_callable=io.StringIO) as stderr,
            ):
                exit_code = cli.main([])

            self.assertEqual(1, exit_code)
            self.assertIn("No base images found", stderr.getvalue())

    def test_main_handles_config_error(self) -> None:
        with (
            mock.patch(
                "aicage.cli.entrypoint.parse_cli",
                return_value=ParsedArgs(False, "", "codex", [], None, False, None),
            ),
            mock.patch(
                "aicage.cli.entrypoint.load_run_config",
                side_effect=ConfigError("bad config"),
            ),
            mock.patch("sys.stderr", new_callable=io.StringIO) as stderr,
        ):
            exit_code = cli.main([])

        self.assertEqual(1, exit_code)
        self.assertIn("bad config", stderr.getvalue())

    def test_main_keyboard_interrupt(self) -> None:
        with mock.patch("aicage.cli.entrypoint.parse_cli", side_effect=KeyboardInterrupt):
            with mock.patch("sys.stdout", new_callable=io.StringIO):
                exit_code = cli.main([])
        self.assertEqual(130, exit_code)
