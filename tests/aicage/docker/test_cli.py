import subprocess
from unittest import TestCase, mock

from aicage.docker.cli import run_docker_command, run_docker_command_capture
from aicage.docker.errors import DockerError


class DockerCliTests(TestCase):
    @staticmethod
    def test_run_docker_command_passes_through() -> None:
        process = subprocess.CompletedProcess(["docker", "run"], 0)
        with mock.patch("aicage.docker.cli.subprocess.run", return_value=process) as run_mock:
            result = run_docker_command(["docker", "run"], check=True)

        run_mock.assert_called_once_with(["docker", "run"], check=True, stdout=None, stderr=None)
        assert result is process

    @staticmethod
    def test_run_docker_command_raises_clean_error_on_missing_docker() -> None:
        with mock.patch("aicage.docker.cli.subprocess.run", side_effect=FileNotFoundError):
            try:
                run_docker_command(["docker", "run"], check=True)
            except DockerError as exc:
                assert "Docker CLI not found." in str(exc)
            else:
                raise AssertionError("Expected DockerError")

    @staticmethod
    def test_run_docker_command_raises_clean_error_on_missing_podman() -> None:
        with mock.patch("aicage.docker.cli.subprocess.run", side_effect=FileNotFoundError):
            try:
                run_docker_command(["podman", "run"], check=True)
            except DockerError as exc:
                assert "Podman CLI not found." in str(exc)
            else:
                raise AssertionError("Expected DockerError")

    @staticmethod
    def test_run_docker_command_capture_returns_process() -> None:
        process = subprocess.CompletedProcess(["docker", "run"], 0, stdout="ok", stderr="")
        with mock.patch("aicage.docker.cli.subprocess.run", return_value=process) as run_mock:
            result = run_docker_command_capture(["docker", "run"], check=False, text=True)

        run_mock.assert_called_once_with(
            ["docker", "run"],
            check=False,
            capture_output=True,
            text=True,
        )
        assert result is process
