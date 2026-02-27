import subprocess
from typing import Literal, TextIO, overload

from aicage.docker.errors import DockerError
from aicage.docker.runtime import get_container_runtime


def run_docker_command(
    command: list[str],
    *,
    check: bool,
    stdout: TextIO | int | None = None,
    stderr: TextIO | int | None = None,
) -> subprocess.CompletedProcess[str] | subprocess.CompletedProcess[bytes]:
    try:
        return subprocess.run(
            command,
            check=check,
            stdout=stdout,
            stderr=stderr,
        )
    except FileNotFoundError as exc:
        runtime = command[0] if command else get_container_runtime()
        raise DockerError(f"{runtime.capitalize()} CLI not found. Ensure it is installed and on PATH.") from exc
    except subprocess.CalledProcessError as exc:
        runtime = command[0] if command else get_container_runtime()
        raise DockerError(f"{runtime.capitalize()} command failed with exit code {exc.returncode}.") from exc


@overload
def run_docker_command_capture(
    command: list[str],
    *,
    check: bool,
    text: Literal[True],
) -> subprocess.CompletedProcess[str]:
    ...


@overload
def run_docker_command_capture(
    command: list[str],
    *,
    check: bool,
    text: Literal[False],
) -> subprocess.CompletedProcess[bytes]:
    ...


def run_docker_command_capture(
    command: list[str],
    *,
    check: bool,
    text: bool,
) -> subprocess.CompletedProcess[str] | subprocess.CompletedProcess[bytes]:
    try:
        return subprocess.run(
            command,
            check=check,
            capture_output=True,
            text=text,
        )
    except FileNotFoundError as exc:
        runtime = command[0] if command else get_container_runtime()
        raise DockerError(f"{runtime.capitalize()} CLI not found. Ensure it is installed and on PATH.") from exc
    except subprocess.CalledProcessError as exc:
        runtime = command[0] if command else get_container_runtime()
        raise DockerError(f"{runtime.capitalize()} command failed with exit code {exc.returncode}.") from exc
