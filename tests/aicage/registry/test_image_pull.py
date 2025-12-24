import io
import subprocess
from unittest import TestCase, mock

from aicage.errors import CliError
from aicage.registry import image_pull
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
        pull_ok = FakeProcess(
            output="repo:tag\n",
            returncode=0,
        )
        with (
            mock.patch("aicage.registry.image_pull._get_local_repo_digest", return_value=None),
            mock.patch("aicage.registry.image_pull._get_remote_manifest_digests") as remote_mock,
            mock.patch("aicage.registry.image_pull.subprocess.Popen", return_value=pull_ok) as popen_mock,
            mock.patch("aicage.registry.image_pull.subprocess.run") as run_mock,
            mock.patch("sys.stdout", new_callable=io.StringIO) as stdout,
        ):
            image_pull.pull_image("repo:tag")
        remote_mock.assert_not_called()
        popen_mock.assert_called_once()
        run_mock.assert_not_called()
        self.assertIn("Pulling image repo:tag", stdout.getvalue())

        pull_download = FakeProcess(
            output=(
                "repo:tag: Pulling from org/repo\n"
                "abc123: Pulling fs layer\n"
                "abc123: Downloading\n"
                "Status: Downloaded newer image for repo:tag\n"
            ),
            returncode=0,
        )
        with (
            mock.patch("aicage.registry.image_pull._get_local_repo_digest", return_value=None),
            mock.patch("aicage.registry.image_pull._get_remote_manifest_digests") as remote_mock,
            mock.patch("aicage.registry.image_pull.subprocess.Popen", return_value=pull_download) as popen_mock,
            mock.patch("aicage.registry.image_pull.subprocess.run") as run_mock,
            mock.patch("sys.stdout", new_callable=io.StringIO) as stdout,
        ):
            image_pull.pull_image("repo:tag")
        remote_mock.assert_not_called()
        popen_mock.assert_called_once()
        run_mock.assert_not_called()
        output = stdout.getvalue()
        self.assertIn("Pulling image repo:tag", output)
        self.assertIn("Pulling fs layer", output)

        pull_fail = FakeProcess(output="timeout\n", returncode=1)
        inspect_ok = FakeCompleted(returncode=0)
        with (
            mock.patch("aicage.registry.image_pull._get_local_repo_digest", return_value=None),
            mock.patch("aicage.registry.image_pull._get_remote_manifest_digests") as remote_mock,
            mock.patch("aicage.registry.image_pull.subprocess.Popen", return_value=pull_fail),
            mock.patch("aicage.registry.image_pull.subprocess.run", return_value=inspect_ok),
            mock.patch("sys.stderr", new_callable=io.StringIO) as stderr,
            mock.patch("sys.stdout", new_callable=io.StringIO),
        ):
            image_pull.pull_image("repo:tag")
        remote_mock.assert_not_called()
        self.assertIn("Warning", stderr.getvalue())

    def test_pull_image_raises_on_missing_local(self) -> None:
        pull_fail = FakeProcess(output="network down\n", returncode=1)
        inspect_fail = FakeCompleted(returncode=1, stderr="missing", stdout="")
        with (
            mock.patch("aicage.registry.image_pull._get_local_repo_digest", return_value=None),
            mock.patch("aicage.registry.image_pull._get_remote_manifest_digests") as remote_mock,
            mock.patch("aicage.registry.image_pull.subprocess.Popen", return_value=pull_fail),
            mock.patch("aicage.registry.image_pull.subprocess.run", return_value=inspect_fail),
            mock.patch("sys.stdout", new_callable=io.StringIO),
        ):
            with self.assertRaises(CliError):
                image_pull.pull_image("repo:tag")
        remote_mock.assert_not_called()

    def test_pull_image_skips_when_up_to_date(self) -> None:
        with (
            mock.patch("aicage.registry.image_pull._get_local_repo_digest", return_value="same"),
            mock.patch("aicage.registry.image_pull._get_remote_manifest_digests", return_value={"same"}),
            mock.patch("aicage.registry.image_pull.subprocess.Popen") as popen_mock,
            mock.patch("sys.stdout", new_callable=io.StringIO) as stdout,
        ):
            image_pull.pull_image("repo:tag")
        popen_mock.assert_not_called()
        self.assertEqual("", stdout.getvalue())

    def test_pull_image_skips_when_remote_unknown(self) -> None:
        with (
            mock.patch("aicage.registry.image_pull._get_local_repo_digest", return_value="local"),
            mock.patch("aicage.registry.image_pull._get_remote_manifest_digests", return_value=None),
            mock.patch("aicage.registry.image_pull.subprocess.Popen") as popen_mock,
            mock.patch("sys.stdout", new_callable=io.StringIO) as stdout,
        ):
            image_pull.pull_image("repo:tag")
        popen_mock.assert_not_called()
        self.assertEqual("", stdout.getvalue())

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
