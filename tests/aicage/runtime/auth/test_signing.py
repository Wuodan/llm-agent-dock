from pathlib import Path
from unittest import TestCase, mock

from aicage.runtime.auth._signing import is_commit_signing_enabled, resolve_signing_format


class SigningTests(TestCase):
    def test_is_commit_signing_enabled_true_values(self) -> None:
        for value in ["true", "1", "yes", "on", "TRUE"]:
            with mock.patch("aicage.runtime.auth._signing.capture_stdout", return_value=f"{value}\n"):
                enabled = is_commit_signing_enabled(Path("/repo"))
            self.assertTrue(enabled)

    def test_is_commit_signing_enabled_false_on_empty(self) -> None:
        with mock.patch("aicage.runtime.auth._signing.capture_stdout", return_value=""):
            enabled = is_commit_signing_enabled(Path("/repo"))
        self.assertFalse(enabled)

    def test_resolve_signing_format(self) -> None:
        with mock.patch("aicage.runtime.auth._signing.capture_stdout", return_value="ssh\n"):
            fmt = resolve_signing_format(Path("/repo"))
        self.assertEqual("ssh", fmt)

        with mock.patch("aicage.runtime.auth._signing.capture_stdout", return_value=""):
            fmt = resolve_signing_format(Path("/repo"))
        self.assertIsNone(fmt)
