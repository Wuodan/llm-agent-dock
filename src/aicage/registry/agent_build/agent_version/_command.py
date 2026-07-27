import os
import shutil
import subprocess  # nosec B404 -- subprocess is required for host-side version script execution.
from dataclasses import dataclass
from pathlib import Path

from aicage._logging import get_logger
from aicage.constants import HOST_VERSION_CHECK_TIMEOUT_SECONDS
from aicage.docker.run import run_builder_version_check
from aicage.reporting import OperationReporter

from ._images import ensure_version_check_image

_VERSION_CHECK_TIMEOUT_MESSAGE: str = "Version check timed out."


@dataclass(frozen=True)
class _CommandResult:
    success: bool
    output: str
    error: str


def run_version_check_image(
    image_ref: str,
    definition_dir: Path,
    reporter: OperationReporter,
) -> _CommandResult:
    try:
        ensure_version_check_image(image_ref, reporter=reporter)
    except Exception as exc:
        get_logger().warning("Version check image preparation failed: %s", exc)
        return _CommandResult(success=False, output="", error=str(exc))
    process = run_builder_version_check(image_ref, definition_dir)
    return _from_process(process, "version check image")


def run_host(script_path: Path) -> _CommandResult:
    if not os.access(script_path, os.X_OK):
        get_logger().warning(
            "version.sh at %s is not executable; running with /bin/bash.",
            script_path,
        )
    bash_path = shutil.which("bash")
    if bash_path is None:
        message = "bash is not available on the host."
        get_logger().warning("Version check failed in host: %s", message)
        return _CommandResult(success=False, output="", error=message)
    try:
        process = subprocess.run(  # nosec B603 -- resolved bash path plus local script path, no shell usage.
            [bash_path, str(script_path)],
            check=False,
            capture_output=True,
            text=True,
            timeout=HOST_VERSION_CHECK_TIMEOUT_SECONDS,
        )
    except subprocess.TimeoutExpired:
        return _CommandResult(
            success=False, output="", error=_VERSION_CHECK_TIMEOUT_MESSAGE
        )
    except Exception as exc:
        get_logger().warning("Version check failed in host: %s", exc)
        return _CommandResult(success=False, output="", error=str(exc))
    return _from_process(process, "host")


def _from_process(
    process: subprocess.CompletedProcess[str], context: str
) -> _CommandResult:
    output = process.stdout.strip() if process.stdout else ""
    if process.returncode == 0 and output:
        return _CommandResult(success=True, output=output, error="")

    stderr = process.stderr.strip() if process.stderr else ""
    error = stderr or output or f"Version check failed in {context}."
    return _CommandResult(success=False, output=output, error=error)
