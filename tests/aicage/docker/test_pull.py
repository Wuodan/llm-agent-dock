import subprocess
import tempfile
from pathlib import Path
from unittest import TestCase, mock

from aicage.docker.errors import DockerError
from aicage.docker.pull import run_pull


class DockerPullTests(TestCase):
    @staticmethod
    def test_run_pull_writes_logs() -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            log_path = Path(tmp_dir) / "pull.log"
            with (
                mock.patch("aicage.docker.pull.get_container_runtime", return_value="podman"),
                mock.patch(
                    "aicage.docker.pull.run_docker_command",
                    return_value=subprocess.CompletedProcess(["podman", "pull"], 0),
                ) as run_mock,
            ):
                run_pull("ghcr.io/aicage/aicage:latest", log_path)
        run_mock.assert_called_once_with(
            ["podman", "pull", "ghcr.io/aicage/aicage:latest"],
            check=False,
            stdout=mock.ANY,
            stderr=mock.ANY,
        )

    def test_run_pull_raises_on_failure(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            log_path = Path(tmp_dir) / "pull.log"
            with (
                mock.patch("aicage.docker.pull.get_container_runtime", return_value="podman"),
                mock.patch(
                    "aicage.docker.pull.run_docker_command",
                    return_value=subprocess.CompletedProcess(["podman", "pull"], 1),
                ),
            ):
                with self.assertRaises(DockerError) as raised:
                    run_pull("ghcr.io/aicage/aicage:latest", log_path)
        self.assertIn("Image pull failed for ghcr.io/aicage/aicage:latest.", str(raised.exception))
