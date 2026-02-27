import io
import subprocess
import tempfile
from pathlib import Path
from unittest import TestCase, mock

from aicage.docker.errors import DockerError
from aicage.registry import _image_pull as image_pull


class DockerInvocationTests(TestCase):
    def test_pull_image_success_writes_log(self) -> None:
        image_ref = "repo:tag"
        with tempfile.TemporaryDirectory() as tmp_dir:
            log_path = Path(tmp_dir) / "pull.log"

            def _pull_side_effect(
                command: list[str],
                *,
                check: bool,
                stdout: object = None,
                stderr: object = None,
            ) -> subprocess.CompletedProcess[str]:
                del check, stderr
                assert command == ["podman", "pull", image_ref]
                assert stdout is not None
                stdout.write("Pulling from org/repo\nDownloaded newer image\n")
                return subprocess.CompletedProcess(command, 0)

            with (
                mock.patch(
                    "aicage.registry._pull_decision.get_local_repo_digest",
                    return_value=None,
                ),
                mock.patch(
                    "aicage.registry._image_pull.get_local_repo_digest_for_repo",
                    side_effect=["sha256:old", "sha256:new"],
                ),
                mock.patch(
                    "aicage.registry._pull_decision.get_remote_digest"
                ) as remote_mock,
                mock.patch(
                    "aicage.registry._image_pull.resolve_verified_digest",
                    return_value="repo@sha256:verified",
                ) as verify_mock,
                mock.patch("aicage.docker.pull.get_container_runtime", return_value="podman"),
                mock.patch(
                    "aicage.docker.pull.run_docker_command",
                    side_effect=_pull_side_effect,
                ) as pull_mock,
                mock.patch("aicage.registry._image_pull.cleanup_old_digest") as cleanup_mock,
                mock.patch("aicage.registry._image_pull.pull_log_path", return_value=log_path),
                mock.patch("sys.stdout", new_callable=io.StringIO) as stdout,
            ):
                image_pull.pull_image(image_ref)
            remote_mock.assert_not_called()
            verify_mock.assert_called_once_with(image_ref)
            cleanup_mock.assert_called_once_with(
                "ghcr.io/aicage/aicage",
                "sha256:old",
                image_ref,
            )
            pull_mock.assert_called_once()
            self.assertIn("Pulling image repo:tag", stdout.getvalue())
            self.assertIn("Pulling from org/repo", log_path.read_text(encoding="utf-8"))

    def test_pull_image_raises_on_pull_error(self) -> None:
        image_ref = "repo:tag"
        with tempfile.TemporaryDirectory() as tmp_dir:
            log_path = Path(tmp_dir) / "pull.log"
            with (
                mock.patch(
                    "aicage.registry._pull_decision.get_local_repo_digest",
                    return_value=None,
                ),
                mock.patch(
                    "aicage.registry._image_pull.get_local_repo_digest_for_repo",
                    side_effect=["sha256:old", "sha256:new"],
                ),
                mock.patch(
                    "aicage.registry._pull_decision.get_remote_digest"
                ) as remote_mock,
                mock.patch(
                    "aicage.registry._image_pull.resolve_verified_digest",
                    return_value="repo@sha256:verified",
                ) as verify_mock,
                mock.patch("aicage.docker.pull.get_container_runtime", return_value="podman"),
                mock.patch(
                    "aicage.docker.pull.run_docker_command",
                    return_value=subprocess.CompletedProcess(["podman", "pull"], 1),
                ),
                mock.patch("aicage.registry._image_pull.cleanup_old_digest") as cleanup_mock,
                mock.patch("aicage.registry._image_pull.pull_log_path", return_value=log_path),
                mock.patch("sys.stdout", new_callable=io.StringIO),
            ):
                with self.assertRaisesRegex(DockerError, "Image pull failed"):
                    image_pull.pull_image(image_ref)
            remote_mock.assert_not_called()
            verify_mock.assert_called_once_with(image_ref)
            cleanup_mock.assert_not_called()

    def test_pull_image_skips_when_up_to_date(self) -> None:
        image_ref = "repo:tag"
        with tempfile.TemporaryDirectory() as tmp_dir:
            log_path = Path(tmp_dir) / "pull.log"
            with (
                mock.patch(
                    "aicage.registry._pull_decision.get_local_repo_digest",
                    return_value="same",
                ),
                mock.patch(
                    "aicage.registry._image_pull.get_local_repo_digest_for_repo"
                ) as local_repo_mock,
                mock.patch(
                    "aicage.registry._pull_decision.get_remote_digest",
                    return_value="same",
                ),
                mock.patch(
                    "aicage.registry._image_pull.resolve_verified_digest"
                ) as verify_mock,
                mock.patch("aicage.docker.pull.run_docker_command") as pull_mock,
                mock.patch("aicage.registry._image_pull.cleanup_old_digest") as cleanup_mock,
                mock.patch("aicage.registry._image_pull.pull_log_path", return_value=log_path),
                mock.patch("sys.stdout", new_callable=io.StringIO) as stdout,
            ):
                image_pull.pull_image(image_ref)
            pull_mock.assert_not_called()
            verify_mock.assert_not_called()
            local_repo_mock.assert_called_once()
            cleanup_mock.assert_not_called()
            self.assertEqual("", stdout.getvalue())

    def test_pull_image_skips_when_remote_unknown(self) -> None:
        image_ref = "repo:tag"
        with tempfile.TemporaryDirectory() as tmp_dir:
            log_path = Path(tmp_dir) / "pull.log"
            with (
                mock.patch(
                    "aicage.registry._pull_decision.get_local_repo_digest",
                    return_value="local",
                ),
                mock.patch(
                    "aicage.registry._image_pull.get_local_repo_digest_for_repo"
                ) as local_repo_mock,
                mock.patch(
                    "aicage.registry._pull_decision.get_remote_digest",
                    return_value=None,
                ),
                mock.patch(
                    "aicage.registry._image_pull.resolve_verified_digest"
                ) as verify_mock,
                mock.patch("aicage.docker.pull.run_docker_command") as pull_mock,
                mock.patch("aicage.registry._image_pull.cleanup_old_digest") as cleanup_mock,
                mock.patch("aicage.registry._image_pull.pull_log_path", return_value=log_path),
                mock.patch("sys.stdout", new_callable=io.StringIO) as stdout,
            ):
                image_pull.pull_image(image_ref)
            pull_mock.assert_not_called()
            verify_mock.assert_not_called()
            local_repo_mock.assert_called_once()
            cleanup_mock.assert_not_called()
            self.assertEqual("", stdout.getvalue())
