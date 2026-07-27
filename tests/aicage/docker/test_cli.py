import subprocess
from unittest import TestCase, mock

from aicage.docker.cli import _run_docker_command, run_docker_command_capture
from aicage.docker.errors import DockerError


class DockerCliTests(TestCase):
    @staticmethod
    def test_run_docker_command_passes_through() -> None:
        process = mock.Mock()
        process.returncode = 0
        process.wait.return_value = 0
        process_context = mock.Mock()
        process_context.__enter__ = mock.Mock(return_value=process)
        process_context.__exit__ = mock.Mock(return_value=None)
        with (
            mock.patch(
                "aicage.docker.cli.subprocess.Popen", return_value=process_context
            ) as run_mock,
            mock.patch("aicage.docker.cli.register_process") as register_mock,
        ):
            result = _run_docker_command(["docker", "run"], check=True)

        run_mock.assert_called_once_with(["docker", "run"], stdout=None, stderr=None)
        register_mock.assert_called_once_with(process)
        assert result.returncode == 0

    @staticmethod
    def test_run_docker_command_raises_clean_error_on_missing_docker() -> None:
        with mock.patch(
            "aicage.docker.cli.subprocess.Popen", side_effect=FileNotFoundError
        ):
            try:
                _run_docker_command(["docker", "run"], check=True)
            except DockerError as exc:
                assert "Docker CLI not found" in str(exc)
            else:
                raise AssertionError("Expected DockerError")

    @staticmethod
    def test_run_docker_command_raises_clean_error_on_non_zero_exit() -> None:
        process = mock.Mock()
        process.returncode = 2
        process.wait.return_value = 2
        process_context = mock.Mock()
        process_context.__enter__ = mock.Mock(return_value=process)
        process_context.__exit__ = mock.Mock(return_value=None)
        with mock.patch(
            "aicage.docker.cli.subprocess.Popen", return_value=process_context
        ):
            with TestCase().assertRaises(DockerError) as raised:
                _run_docker_command(["docker", "run"], check=True)

        assert "exit code 2" in str(raised.exception)

    @staticmethod
    def test_run_docker_command_capture_returns_process() -> None:
        process = mock.Mock()
        process.returncode = 0
        process.communicate.return_value = ("ok", "")
        process_context = mock.Mock()
        process_context.__enter__ = mock.Mock(return_value=process)
        process_context.__exit__ = mock.Mock(return_value=None)
        with (
            mock.patch(
                "aicage.docker.cli.subprocess.Popen", return_value=process_context
            ) as run_mock,
            mock.patch("aicage.docker.cli.register_process") as register_mock,
        ):
            result = run_docker_command_capture(
                ["docker", "run"], check=False, text=True
            )

        run_mock.assert_called_once_with(
            ["docker", "run"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        register_mock.assert_called_once_with(process)
        assert result.stdout == "ok"

    @staticmethod
    def test_run_docker_command_capture_raises_clean_error_on_missing_docker() -> None:
        with mock.patch(
            "aicage.docker.cli.subprocess.Popen", side_effect=FileNotFoundError
        ):
            try:
                run_docker_command_capture(["docker", "run"], check=True, text=True)
            except DockerError as exc:
                assert "Docker CLI not found" in str(exc)
            else:
                raise AssertionError("Expected DockerError")

    @staticmethod
    def test_run_docker_command_capture_raises_clean_error_on_non_zero_exit() -> None:
        process = mock.Mock()
        process.returncode = 3
        process.communicate.return_value = ("", "broken")
        process_context = mock.Mock()
        process_context.__enter__ = mock.Mock(return_value=process)
        process_context.__exit__ = mock.Mock(return_value=None)
        with mock.patch(
            "aicage.docker.cli.subprocess.Popen", return_value=process_context
        ):
            try:
                run_docker_command_capture(["docker", "run"], check=True, text=True)
            except DockerError as exc:
                assert "exit code 3" in str(exc)
            else:
                raise AssertionError("Expected DockerError")
