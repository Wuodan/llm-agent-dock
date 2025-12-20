import subprocess
from pathlib import Path
from unittest import TestCase, mock

from aicage.runtime.auth._exec import capture_stdout


class CaptureStdoutTests(TestCase):
    def test_capture_stdout_returns_output(self) -> None:
        completed = subprocess.CompletedProcess(args=["cmd"], returncode=0, stdout="ok", stderr="")
        with mock.patch("aicage.runtime.auth._exec.subprocess.run", return_value=completed) as run_mock:
            result = capture_stdout(["cmd"], cwd=Path("/tmp"))
        self.assertEqual("ok", result)
        run_mock.assert_called_once()

    def test_capture_stdout_returns_none_on_failure(self) -> None:
        with mock.patch(
            "aicage.runtime.auth._exec.subprocess.run", side_effect=subprocess.CalledProcessError(1, ["cmd"])
        ):
            result = capture_stdout(["cmd"])
        self.assertIsNone(result)

        with mock.patch("aicage.runtime.auth._exec.subprocess.run", side_effect=FileNotFoundError):
            result = capture_stdout(["missing"])
        self.assertIsNone(result)
