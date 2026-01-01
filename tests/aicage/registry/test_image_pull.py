import io
from pathlib import Path
from unittest import TestCase, mock

from aicage.config.global_config import GlobalConfig
from aicage.config.runtime_config import RunConfig
from aicage.errors import CliError
from aicage.registry import image_pull
from aicage.registry.images_metadata.models import ImagesMetadata


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
    def _build_run_config(self, image_ref: str) -> RunConfig:
        return RunConfig(
            project_path=Path("/tmp/project"),
            agent="codex",
            image_ref=image_ref,
            global_cfg=GlobalConfig(
                image_registry="ghcr.io",
                image_registry_api_url="https://ghcr.io/v2",
                image_registry_api_token_url="https://ghcr.io/token?service=ghcr.io&scope=repository",
                image_repository="aicage/aicage",
                default_image_base="ubuntu",
            ),
            images_metadata=self._get_images_metadata(),
            project_docker_args="",
            mounts=[],
        )

    @staticmethod
    def _get_images_metadata() -> ImagesMetadata:
        return ImagesMetadata.from_mapping(
            {
                "aicage-image": {"version": "0.3.3"},
                "aicage-image-base": {"version": "0.3.3"},
                "bases": {
                    "ubuntu": {
                        "root_image": "ubuntu:latest",
                        "base_image_distro": "Ubuntu",
                        "base_image_description": "Default",
                        "os_installer": "distro/debian/install.sh",
                        "test_suite": "default",
                    }
                },
                "agent": {
                    "codex": {
                        "agent_path": "~/.codex",
                        "agent_full_name": "Codex CLI",
                        "agent_homepage": "https://example.com",
                        "redistributable": True,
                        "valid_bases": {"ubuntu": "ghcr.io/aicage/aicage:codex-ubuntu"},
                    }
                },
            }
        )

    def test_pull_image_success_and_warning(self) -> None:
        run_config = self._build_run_config("repo:tag")
        pull_ok = FakeProcess(
            output="repo:tag\n",
            returncode=0,
        )
        with (
            mock.patch("aicage.registry.image_pull._local_query.get_local_repo_digest", return_value=None),
            mock.patch("aicage.registry.image_pull._remote_query.get_remote_repo_digest") as remote_mock,
            mock.patch("aicage.registry.image_pull.subprocess.Popen", return_value=pull_ok) as popen_mock,
            mock.patch("aicage.registry.image_pull.subprocess.run") as run_mock,
            mock.patch("sys.stdout", new_callable=io.StringIO) as stdout,
        ):
            image_pull.pull_image(run_config)
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
            mock.patch("aicage.registry.image_pull._local_query.get_local_repo_digest", return_value=None),
            mock.patch("aicage.registry.image_pull._remote_query.get_remote_repo_digest") as remote_mock,
            mock.patch("aicage.registry.image_pull.subprocess.Popen", return_value=pull_download) as popen_mock,
            mock.patch("aicage.registry.image_pull.subprocess.run") as run_mock,
            mock.patch("sys.stdout", new_callable=io.StringIO) as stdout,
        ):
            image_pull.pull_image(run_config)
        remote_mock.assert_not_called()
        popen_mock.assert_called_once()
        run_mock.assert_not_called()
        output = stdout.getvalue()
        self.assertIn("Pulling image repo:tag", output)
        self.assertIn("Pulling fs layer", output)

        pull_fail = FakeProcess(output="timeout\n", returncode=1)
        inspect_ok = FakeCompleted(returncode=0)
        with (
            mock.patch("aicage.registry.image_pull._local_query.get_local_repo_digest", return_value=None),
            mock.patch("aicage.registry.image_pull._remote_query.get_remote_repo_digest") as remote_mock,
            mock.patch("aicage.registry.image_pull.subprocess.Popen", return_value=pull_fail),
            mock.patch("aicage.registry.image_pull.subprocess.run", return_value=inspect_ok),
            mock.patch("sys.stderr", new_callable=io.StringIO) as stderr,
            mock.patch("sys.stdout", new_callable=io.StringIO),
        ):
            image_pull.pull_image(run_config)
        remote_mock.assert_not_called()
        self.assertIn("Warning", stderr.getvalue())

    def test_pull_image_raises_on_missing_local(self) -> None:
        run_config = self._build_run_config("repo:tag")
        pull_fail = FakeProcess(output="network down\n", returncode=1)
        inspect_fail = FakeCompleted(returncode=1, stderr="missing", stdout="")
        with (
            mock.patch("aicage.registry.image_pull._local_query.get_local_repo_digest", return_value=None),
            mock.patch("aicage.registry.image_pull._remote_query.get_remote_repo_digest") as remote_mock,
            mock.patch("aicage.registry.image_pull.subprocess.Popen", return_value=pull_fail),
            mock.patch("aicage.registry.image_pull.subprocess.run", return_value=inspect_fail),
            mock.patch("sys.stdout", new_callable=io.StringIO),
        ):
            with self.assertRaises(CliError):
                image_pull.pull_image(run_config)
        remote_mock.assert_not_called()

    def test_pull_image_skips_when_up_to_date(self) -> None:
        run_config = self._build_run_config("repo:tag")
        with (
            mock.patch("aicage.registry.image_pull._local_query.get_local_repo_digest", return_value="same"),
            mock.patch("aicage.registry.image_pull._remote_query.get_remote_repo_digest", return_value="same"),
            mock.patch("aicage.registry.image_pull.subprocess.Popen") as popen_mock,
            mock.patch("sys.stdout", new_callable=io.StringIO) as stdout,
        ):
            image_pull.pull_image(run_config)
        popen_mock.assert_not_called()
        self.assertEqual("", stdout.getvalue())

    def test_pull_image_skips_when_remote_unknown(self) -> None:
        run_config = self._build_run_config("repo:tag")
        with (
            mock.patch("aicage.registry.image_pull._local_query.get_local_repo_digest", return_value="local"),
            mock.patch("aicage.registry.image_pull._remote_query.get_remote_repo_digest", return_value=None),
            mock.patch("aicage.registry.image_pull.subprocess.Popen") as popen_mock,
            mock.patch("sys.stdout", new_callable=io.StringIO) as stdout,
        ):
            image_pull.pull_image(run_config)
        popen_mock.assert_not_called()
        self.assertEqual("", stdout.getvalue())
