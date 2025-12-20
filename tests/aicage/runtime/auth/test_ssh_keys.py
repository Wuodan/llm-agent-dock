from pathlib import Path
from unittest import TestCase, mock

from aicage.runtime.auth._ssh_keys import default_ssh_dir


class SshKeyTests(TestCase):
    def test_default_ssh_dir_uses_home(self) -> None:
        with mock.patch("pathlib.Path.home", return_value=Path("/home/user")):
            path = default_ssh_dir()
        self.assertEqual(Path("/home/user/.ssh"), path)
