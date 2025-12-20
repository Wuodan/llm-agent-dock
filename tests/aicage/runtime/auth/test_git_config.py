from pathlib import Path
from unittest import TestCase, mock

from aicage.runtime.auth._git_config import resolve_git_config_path


class GitConfigTests(TestCase):
    def test_resolve_git_config_path_parses_first_file(self) -> None:
        output = "file:/home/user/.gitconfig user.name=Name\nfile:/tmp/other key=value\n"
        with mock.patch("aicage.runtime.auth._git_config.capture_stdout", return_value=output):
            path = resolve_git_config_path()
        self.assertEqual(Path("/home/user/.gitconfig"), path)

    def test_resolve_git_config_path_handles_empty(self) -> None:
        with mock.patch("aicage.runtime.auth._git_config.capture_stdout", return_value=""):
            path = resolve_git_config_path()
        self.assertIsNone(path)
