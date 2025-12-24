import io
import subprocess
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
            mock.patch("aicage.registry.image_selection._get_local_digest", return_value=None) as local_mock,
            mock.patch("aicage.registry.image_selection._get_remote_digests") as remote_mock,
            mock.patch("aicage.registry.image_selection.subprocess.Popen", return_value=pull_ok) as popen_mock,
            mock.patch("aicage.registry.image_selection.subprocess.run") as run_mock,
            mock.patch("sys.stdout", new_callable=io.StringIO),
        ):
            image_selection.pull_image("repo:tag")
        local_mock.assert_called_once()
        remote_mock.assert_not_called()
        popen_mock.assert_called_once()
        run_mock.assert_not_called()

        pull_fail = FakeProcess(output="timeout\n", returncode=1)
        inspect_ok = FakeCompleted(returncode=0)
        with (
            mock.patch("aicage.registry.image_selection._get_local_digest", return_value="local") as local_mock,
            mock.patch("aicage.registry.image_selection._get_remote_digests", return_value={"remote"}) as remote_mock,
            mock.patch("aicage.registry.image_selection.subprocess.Popen", return_value=pull_fail),
            mock.patch("aicage.registry.image_selection.subprocess.run", return_value=inspect_ok),
            mock.patch("sys.stderr", new_callable=io.StringIO) as stderr,
            mock.patch("sys.stdout", new_callable=io.StringIO),
        ):
            image_selection.pull_image("repo:tag")
        local_mock.assert_called_once()
        remote_mock.assert_called_once()
        self.assertIn("Warning", stderr.getvalue())

    def test_pull_image_raises_on_missing_local(self) -> None:
        pull_fail = FakeProcess(output="network down\n", returncode=1)
        inspect_fail = FakeCompleted(returncode=1, stderr="missing", stdout="")
        with (
            mock.patch("aicage.registry.image_selection._get_local_digest", return_value="local") as local_mock,
            mock.patch("aicage.registry.image_selection._get_remote_digests", return_value={"remote"}) as remote_mock,
            mock.patch("aicage.registry.image_selection.subprocess.Popen", return_value=pull_fail),
            mock.patch("aicage.registry.image_selection.subprocess.run", return_value=inspect_fail),
            mock.patch("sys.stdout", new_callable=io.StringIO),
        ):
            with self.assertRaises(CliError):
                image_selection.pull_image("repo:tag")
        local_mock.assert_called_once()
        remote_mock.assert_called_once()

    def test_pull_image_skips_when_up_to_date(self) -> None:
        with (
            mock.patch("aicage.registry.image_selection._get_local_digest", return_value="same") as local_mock,
            mock.patch("aicage.registry.image_selection._get_remote_digests", return_value={"same"}) as remote_mock,
            mock.patch("aicage.registry.image_selection.subprocess.Popen") as popen_mock,
            mock.patch("sys.stdout", new_callable=io.StringIO) as stdout,
        ):
            image_selection.pull_image("repo:tag")
        local_mock.assert_called_once()
        remote_mock.assert_called_once()
        popen_mock.assert_not_called()
        self.assertIn("up to date", stdout.getvalue())

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
