import subprocess
import tempfile
from pathlib import Path
from unittest import TestCase, mock

from aicage.errors import CliError
from aicage.runtime.tool_config import resolve_tool_config


class ToolConfigTests(TestCase):
    def test_resolve_tool_config_reads_label_and_creates_dir(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            tool_dir = Path(tmp_dir) / ".codex"
            completed = subprocess.CompletedProcess(args=["cmd"], returncode=0, stdout=str(tool_dir), stderr="")
            with mock.patch("aicage.runtime.tool_config.subprocess.run", return_value=completed):
                config = resolve_tool_config("ghcr.io/aicage/aicage:codex-ubuntu-latest")
            self.assertEqual(str(tool_dir), config.tool_path)
            self.assertTrue(config.tool_config_host.exists())

    def test_resolve_tool_config_missing_label_raises(self) -> None:
        completed = subprocess.CompletedProcess(args=["cmd"], returncode=0, stdout="", stderr="")
        with mock.patch("aicage.runtime.tool_config.subprocess.run", return_value=completed):
            with self.assertRaises(CliError):
                resolve_tool_config("ghcr.io/aicage/aicage:codex-ubuntu-latest")
