import io
import tempfile
from pathlib import Path
from unittest import TestCase, mock

from aicage import cli
from aicage.config import GlobalConfig, ProjectConfig
from aicage.config.context import ConfigContext
from aicage.errors import CliError
from aicage.runtime.base_image import BaseImageSelection


class MainFlowTests(TestCase):
    def test_main_uses_project_base(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            project_path = Path(tmp_dir)
            global_cfg = GlobalConfig(
                repository="aicage/aicage",
                default_base="ubuntu",
                docker_args="--global",
                tools={"codex": {"base": "fedora"}},
            )
            project_cfg = ProjectConfig(
                path=str(project_path),
                docker_args="--project",
                tools={"codex": {"base": "debian"}},
            )

            class FakeStore:
                def __init__(self, global_cfg: GlobalConfig, project_cfg: ProjectConfig) -> None:
                    self._global_cfg = global_cfg
                    self._project_cfg = project_cfg

                def load_global(self) -> GlobalConfig:
                    return self._global_cfg

                def load_project(self, project_realpath: Path) -> ProjectConfig:
                    self.loaded_path = project_realpath
                    return self._project_cfg

                def save_project(self, project_realpath: Path, config: ProjectConfig) -> None:
                    self.saved = (project_realpath, config)

            store = FakeStore(global_cfg, project_cfg)
            context = ConfigContext(
                store=store,
                project_path=project_path,
                project_cfg=project_cfg,
                global_cfg=global_cfg,
            )
            selection = BaseImageSelection(
                image_ref="aicage/aicage:codex-debian-latest",
                tool_path_label=str(project_path / ".codex"),
                tool_config_host=project_path / ".codex",
                project_dirty=False,
            )
            with (
                mock.patch("aicage.cli.parse_cli", return_value=cli.ParsedArgs(False, "--cli", "codex", ["--flag"])),
                mock.patch("aicage.cli.build_config_context", return_value=context),
                mock.patch("aicage.cli.resolve_base_image", return_value=selection),
                mock.patch(
                    "aicage.cli.assemble_docker_run",
                    return_value=["docker", "run", "--flag"],
                ) as assemble_mock,
                mock.patch("aicage.cli.build_auth_mounts", return_value=([], False)),
                mock.patch("aicage.cli.subprocess.run") as run_mock,
            ):
                exit_code = cli.main([])

            self.assertEqual(0, exit_code)
            assemble_mock.assert_called_once()
            run_mock.assert_called_once_with(["docker", "run", "--flag"], check=True)

    def test_main_prompts_and_saves_base(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            project_path = Path(tmp_dir)
            global_cfg = GlobalConfig(
                repository="aicage/aicage",
                default_base="ubuntu",
                docker_args="--global",
                tools={},
            )
            project_cfg = ProjectConfig(
                path=str(project_path), docker_args="--project", tools={"codex": {"base": "alpine"}}
            )

            class FakeStore:
                def __init__(self, global_cfg: GlobalConfig, project_cfg: ProjectConfig) -> None:
                    self._global_cfg = global_cfg
                    self._project_cfg = project_cfg
                    self.saved = None

                def load_global(self) -> GlobalConfig:
                    return self._global_cfg

                def load_project(self, project_realpath: Path) -> ProjectConfig:
                    self.loaded_path = project_realpath
                    return self._project_cfg

                def save_project(self, project_realpath: Path, config: ProjectConfig) -> None:
                    self.saved = (project_realpath, config)

            store = FakeStore(global_cfg, project_cfg)
            selection = BaseImageSelection(
                image_ref="aicage/aicage:codex-alpine-latest",
                tool_path_label=str(project_path / ".codex"),
                tool_config_host=project_path / ".codex",
                project_dirty=True,
            )
            context = ConfigContext(
                store=store,
                project_path=project_path,
                project_cfg=project_cfg,
                global_cfg=global_cfg,
            )
            with (
                mock.patch("aicage.cli.parse_cli", return_value=cli.ParsedArgs(True, "--cli", "codex", ["--flag"])),
                mock.patch("aicage.cli.build_config_context", return_value=context),
                mock.patch("aicage.cli.resolve_base_image", return_value=selection),
                mock.patch("aicage.cli.assemble_docker_run", return_value=["docker", "run", "cmd"]),
                mock.patch("sys.stderr", new_callable=io.StringIO) as stderr,
                mock.patch("sys.stdout", new_callable=io.StringIO) as stdout,
                mock.patch("aicage.cli.build_auth_mounts", return_value=([], False)),
            ):
                exit_code = cli.main([])

            self.assertEqual(0, exit_code)
            self.assertIn("docker run cmd", stdout.getvalue())
            self.assertIsNotNone(store.saved)
            saved_cfg = store.saved[1]
            self.assertEqual("alpine", saved_cfg.tools["codex"]["base"])
            self.assertEqual("", stderr.getvalue())

    def test_main_handles_no_available_bases(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            project_path = Path(tmp_dir)
            global_cfg = GlobalConfig(
                repository="aicage/aicage",
                default_base="ubuntu",
                docker_args="",
                tools={},
            )
            project_cfg = ProjectConfig(path=str(project_path), docker_args="", tools={})

            class FakeStore:
                def __init__(self, global_cfg: GlobalConfig, project_cfg: ProjectConfig) -> None:
                    self._global_cfg = global_cfg
                    self._project_cfg = project_cfg

                def load_global(self) -> GlobalConfig:
                    return self._global_cfg

                def load_project(self, project_realpath: Path) -> ProjectConfig:
                    return self._project_cfg

                def save_project(self, project_realpath: Path, config: ProjectConfig) -> None:
                    self.saved = (project_realpath, config)

            store = FakeStore(global_cfg, project_cfg)
            context = ConfigContext(
                store=store,
                project_path=project_path,
                project_cfg=project_cfg,
                global_cfg=global_cfg,
            )
            with (
                mock.patch("aicage.cli.parse_cli", return_value=cli.ParsedArgs(True, "", "codex", [])),
                mock.patch("aicage.cli.build_config_context", return_value=context),
                mock.patch("aicage.cli.resolve_base_image", side_effect=CliError("No base images found")),
                mock.patch("sys.stderr", new_callable=io.StringIO) as stderr,
            ):
                exit_code = cli.main([])

            self.assertEqual(1, exit_code)
            self.assertIn("No base images found", stderr.getvalue())

    def test_main_keyboard_interrupt(self) -> None:
        with mock.patch("aicage.cli.parse_cli", side_effect=KeyboardInterrupt):
            with mock.patch("sys.stdout", new_callable=io.StringIO):
                exit_code = cli.main([])
        self.assertEqual(130, exit_code)
