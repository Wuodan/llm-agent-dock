import io
import tempfile
from pathlib import Path
from subprocess import CompletedProcess
from unittest import TestCase, mock

import yaml

from aicage.config.global_config import GlobalConfig
from aicage.errors import CliError
from aicage.registry.agent_version import AgentVersionChecker, VersionCheckStore
from aicage.registry.images_metadata.models import AgentMetadata


class AgentVersionCheckTests(TestCase):
    def test_check_uses_builder_fallback_and_persists(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            agent_dir = Path(tmp_dir) / "custom"
            agent_dir.mkdir()
            (agent_dir / "version.sh").write_text("echo 1.2.3\n", encoding="utf-8")
            store_dir = Path(tmp_dir) / "state"
            checker = AgentVersionChecker(
                global_cfg=self._global_config(),
                store=VersionCheckStore(store_dir),
            )

            def _run_side_effect(args: list[str], **kwargs: object) -> CompletedProcess[str]:
                if args[0] == "/bin/sh":
                    return CompletedProcess(args, 1, stdout="", stderr="host failed")
                return CompletedProcess(args, 0, stdout="1.2.3\n", stderr="")

            with (
                mock.patch(
                    "aicage.registry.agent_version.checker.subprocess.run",
                    side_effect=_run_side_effect,
                ),
                mock.patch("sys.stderr", new_callable=io.StringIO),
            ):
                result = checker.get_version(
                    "custom",
                    self._agent_metadata(True),
                    definition_dir=agent_dir,
                )

            self.assertEqual("1.2.3", result)
            stored = store_dir / "custom.yaml"
            self.assertTrue(stored.is_file())
            data = yaml.safe_load(stored.read_text(encoding="utf-8"))
            self.assertEqual("1.2.3", data["version"])

    def test_check_raises_on_missing_version_script(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            agent_dir = Path(tmp_dir) / "custom"
            agent_dir.mkdir()
            store_dir = Path(tmp_dir) / "state"
            checker = AgentVersionChecker(
                global_cfg=self._global_config(),
                store=VersionCheckStore(store_dir),
            )
            with self.assertRaises(CliError):
                checker.get_version(
                    "custom",
                    self._agent_metadata(True),
                    definition_dir=agent_dir,
                )
            self.assertFalse((store_dir / "custom.yaml").exists())

    @staticmethod
    def _global_config() -> GlobalConfig:
        return GlobalConfig(
            image_registry="ghcr.io",
            image_registry_api_url="https://ghcr.io/v2",
            image_registry_api_token_url="https://ghcr.io/token?service=ghcr.io&scope=repository",
            image_repository="aicage/aicage",
            image_base_repository="aicage/aicage-image-base",
            default_image_base="ubuntu",
            version_check_image="ghcr.io/aicage/aicage-image-util:agent-version",
            agents={},
        )

    @staticmethod
    def _agent_metadata(is_custom: bool) -> AgentMetadata:
        return AgentMetadata(
            agent_path="~/.custom",
            agent_full_name="Custom",
            agent_homepage="https://example.com",
            redistributable=False,
            valid_bases={},
            is_custom=is_custom,
        )
