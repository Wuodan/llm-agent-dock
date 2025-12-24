import io
import subprocess
from datetime import datetime, timezone
from unittest import TestCase, mock

from aicage.errors import CliError
from aicage.registry import image_selection
from aicage.registry.discovery import _local as registry_local


class FakeCompleted:
    def __init__(self, stdout: str = "", stderr: str = "", returncode: int = 0):
        self.stdout = stdout
        self.stderr = stderr
        self.returncode = returncode


class FakeProcess:
    def __init__(self, output: str = "", returncode: int = 0) -> None:
        self.stdout = io.StringIO(output)
        self.returncode = returncode

    def wait(self) -> int:
        return self.returncode


class DockerInvocationTests(TestCase):
    def test_pull_image_success_and_warning(self) -> None:
        pull_ok = FakeProcess(returncode=0)
        with (
            mock.patch("aicage.registry.image_selection.Path.open", mock.mock_open()),
            mock.patch("aicage.registry.image_selection.subprocess.Popen", return_value=pull_ok) as popen_mock,
            mock.patch("aicage.registry.image_selection.subprocess.run") as run_mock,
            mock.patch("sys.stdout", new_callable=io.StringIO),
        ):
            image_selection.pull_image("repo:tag")
        popen_mock.assert_called_once()
        run_mock.assert_not_called()

        pull_fail = FakeProcess(output="timeout\n", returncode=1)
        inspect_ok = FakeCompleted(returncode=0)
        fixed_time = datetime(2025, 12, 24, 15, 42, 0, tzinfo=timezone.utc)
        with (
            mock.patch("aicage.registry.image_selection.datetime") as datetime_mock,
            mock.patch("aicage.registry.image_selection.Path.open", mock.mock_open()),
            mock.patch("aicage.registry.image_selection.subprocess.Popen", return_value=pull_fail),
            mock.patch("aicage.registry.image_selection.subprocess.run", return_value=inspect_ok),
            mock.patch("sys.stderr", new_callable=io.StringIO) as stderr,
            mock.patch("sys.stdout", new_callable=io.StringIO),
        ):
            datetime_mock.now.return_value = fixed_time
            image_selection.pull_image("repo:tag")
        self.assertIn("Warning", stderr.getvalue())

    def test_pull_image_raises_on_missing_local(self) -> None:
        pull_fail = FakeProcess(output="network down\n", returncode=1)
        inspect_fail = FakeCompleted(returncode=1, stderr="missing", stdout="")
        fixed_time = datetime(2025, 12, 24, 15, 42, 0, tzinfo=timezone.utc)
        with (
            mock.patch("aicage.registry.image_selection.datetime") as datetime_mock,
            mock.patch("aicage.registry.image_selection.Path.open", mock.mock_open()),
            mock.patch("aicage.registry.image_selection.subprocess.Popen", return_value=pull_fail),
            mock.patch("aicage.registry.image_selection.subprocess.run", return_value=inspect_fail),
            mock.patch("sys.stdout", new_callable=io.StringIO),
        ):
            datetime_mock.now.return_value = fixed_time
            with self.assertRaises(CliError):
                image_selection.pull_image("repo:tag")

    def test_discover_local_bases_and_errors(self) -> None:
        list_output = "\n".join(
            [
                "repo:codex-ubuntu-latest",
                "repo:codex-debian-latest",
                "repo:codex-ubuntu-1.0",
                "other:codex-ubuntu-latest",
                "repo:codex-<none>",
            ]
        )
        with mock.patch(
            "aicage.registry.discovery._local.subprocess.run",
            return_value=FakeCompleted(stdout=list_output, returncode=0),
        ):
            aliases = registry_local.discover_local_bases("repo", "codex")
        self.assertEqual(["debian", "ubuntu"], aliases)

        with mock.patch(
            "aicage.registry.discovery._local.subprocess.run",
            side_effect=subprocess.CalledProcessError(1, "docker image ls", stderr="boom"),
        ):
            with self.assertRaises(CliError):
                registry_local.discover_local_bases("repo", "codex")
