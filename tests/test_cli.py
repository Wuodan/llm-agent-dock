import io
import json
import sys
import tempfile
from pathlib import Path
from unittest import TestCase, mock

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from aicage import cli  # noqa: E402
from aicage.config_store import SettingsStore  # noqa: E402
from aicage.discovery import discover_base_aliases  # noqa: E402


class ParseCliTests(TestCase):
    def test_parse_with_docker_args(self) -> None:
        dry_run, docker_args, tool, tool_args = cli.parse_cli(
            ["--dry-run", "--network=host", "codex", "--foo"]
        )
        self.assertTrue(dry_run)
        self.assertEqual("--network=host", docker_args)
        self.assertEqual("codex", tool)
        self.assertEqual(["--foo"], tool_args)

    def test_parse_with_separator(self) -> None:
        dry_run, docker_args, tool, tool_args = cli.parse_cli(["--dry-run", "--", "codex", "--bar"])
        self.assertTrue(dry_run)
        self.assertEqual("", docker_args)
        self.assertEqual("codex", tool)
        self.assertEqual(["--bar"], tool_args)

    def test_parse_without_docker_args(self) -> None:
        dry_run, docker_args, tool, tool_args = cli.parse_cli(["codex", "--flag"])
        self.assertFalse(dry_run)
        self.assertEqual("", docker_args)
        self.assertEqual("codex", tool)
        self.assertEqual(["--flag"], tool_args)


class DiscoveryTests(TestCase):
    def test_discover_base_aliases_parses_latest(self) -> None:
        payload = {
            "results": [
                {"name": "codex-ubuntu-latest"},
                {"name": "codex-fedora-1.0"},
                {"name": "codex-debian-latest"},
                {"name": "cline-ubuntu-latest"},
            ],
            "next": "",
        }

        class FakeResponse:
            def __enter__(self):  # noqa: D401
                return io.BytesIO(json.dumps(payload).encode("utf-8"))

            def __exit__(self, exc_type, exc, tb):  # noqa: D401
                return False

        def fake_urlopen(url: str):  # pylint: disable=unused-argument
            return FakeResponse()

        with mock.patch("urllib.request.urlopen", fake_urlopen):
            aliases = discover_base_aliases("wuodan/aicage", "codex")

        self.assertEqual(["debian", "ubuntu"], aliases)


class ConfigStoreTests(TestCase):
    def test_global_and_project_round_trip(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            base_dir = Path(tmp_dir)
            store = SettingsStore(base_dir=base_dir)
            central_path = store.central_config()
            self.assertTrue(central_path.exists())
            self.assertIn("AICAGE_REPOSITORY: wuodan/aicage", central_path.read_text())

            global_cfg = store.load_global()
            self.assertEqual({"docker_args": "", "tools": {}}, global_cfg)

            global_cfg["docker_args"] = "--network=host"
            global_cfg["tools"]["codex"] = {"base": "ubuntu"}
            store.save_global(global_cfg)

            reloaded_global = store.load_global()
            self.assertEqual(global_cfg, reloaded_global)

            project_path = base_dir / "project"
            project_path.mkdir(parents=True, exist_ok=True)
            project_cfg = store.load_project(project_path)
            self.assertEqual({"path": str(project_path), "docker_args": "", "tools": {}}, project_cfg)

            project_cfg["docker_args"] = "--add-host=host.docker.internal:host-gateway"
            project_cfg["tools"]["codex"] = {"base": "fedora"}
            store.save_project(project_path, project_cfg)

            reloaded_project = store.load_project(project_path)
            self.assertEqual(project_cfg, reloaded_project)


class PromptTests(TestCase):
    def test_prompt_requires_tty(self) -> None:
        with mock.patch("sys.stdin.isatty", return_value=False):
            with self.assertRaises(cli.CliError):
                cli.prompt_for_base("codex", "ubuntu", ["ubuntu"])

    def test_assemble_includes_workspace_mount(self) -> None:
        with mock.patch("aicage.cli.resolve_user_ids", return_value=[]):
            cmd = cli.assemble_docker_run(
                image_ref="wuodan/aicage:codex-ubuntu-latest",
                project_path=Path("/work/project"),
                tool_config_host=Path("/host/.codex"),
                tool_mount_container=Path("/aicage/tool-config"),
                merged_docker_args="--network=host",
                tool_args=["--flag"],
                extra_env=["-e", "AICAGE_TOOL_PATH=~/.codex"],
            )
        self.assertEqual(
            [
                "docker",
                "run",
                "--rm",
                "-it",
                "-e",
                "AICAGE_TOOL_PATH=~/.codex",
                "-v",
                "/work/project:/workspace",
                "-v",
                "/host/.codex:/aicage/tool-config",
                "--network=host",
                "wuodan/aicage:codex-ubuntu-latest",
                "--flag",
            ],
            cmd,
        )
