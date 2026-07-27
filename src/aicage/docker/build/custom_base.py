from pathlib import Path

from aicage._logging import get_logger
from aicage._proxy import proxy_build_args_from_host
from aicage.docker.errors import DockerError
from aicage.reporting import OperationReporter

from . import _common


def run(
    build_root: Path,
    from_image: str,
    image_ref: str,
    log_path: Path,
    reporter: OperationReporter,
) -> None:
    logger = get_logger()
    dockerfile_path = build_root / "Dockerfile"
    log_path.parent.mkdir(parents=True, exist_ok=True)
    reporter.on_phase_started(
        "build", f"Building custom base image {image_ref}", log_path
    )
    logger.info("Building custom base image %s (logs: %s)", image_ref, log_path)

    command = [
        "docker",
        "build",
        "--no-cache",
        "--file",
        str(dockerfile_path),
        "--build-arg",
        f"FROM_IMAGE={from_image}",
        "--tag",
        image_ref,
        str(build_root),
    ]
    command.extend(proxy_build_args_from_host())
    with log_path.open("w", encoding="utf-8") as log_handle:
        returncode = _common.run_build_command(
            command,
            log_handle,
            reporter,
        )
    if returncode != 0:
        logger.error(
            "Custom base image build failed for %s (logs: %s)", image_ref, log_path
        )
        reporter.on_phase_failed(
            "build",
            f"Custom base image build failed for {image_ref}",
            log_path,
        )
        raise DockerError(
            f"Custom base image build failed for {image_ref}. See log at: {log_path}"
        )

    reporter.on_phase_finished(
        "build", f"Custom base image build finished for {image_ref}"
    )
    logger.info("Custom base image build succeeded for %s", image_ref)
