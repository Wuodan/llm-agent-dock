from pathlib import Path

from aicage._logging import get_logger
from aicage._proxy import proxy_build_args_from_host
from aicage.config.resources import find_packaged_path
from aicage.config.run_config import RunConfig
from aicage.docker.errors import DockerError
from aicage.docker.reporting import OperationReporter, _default_operation_reporter

from . import _common


def run(
    run_config: RunConfig,
    base_image_ref: str,
    image_ref: str,
    log_path: Path,
    reporter: OperationReporter | None = None,
) -> None:
    logger = get_logger()
    operation_reporter = reporter or _default_operation_reporter()
    log_path.parent.mkdir(parents=True, exist_ok=True)
    operation_reporter.on_phase_started(
        "build", f"Building local image {image_ref}", log_path
    )
    logger.info("Building local image %s (logs: %s)", image_ref, log_path)

    dockerfile_path = find_packaged_path("agent-build/Dockerfile")
    build_root = _common.build_context_dir(run_config, dockerfile_path)
    command = [
        "docker",
        "build",
        "--no-cache",
        "--file",
        str(dockerfile_path),
        "--build-arg",
        f"BASE_IMAGE={base_image_ref}",
        "--build-arg",
        f"AGENT={run_config.agent}",
        "--tag",
        image_ref,
        str(build_root),
    ]
    command.extend(proxy_build_args_from_host())
    with log_path.open("w", encoding="utf-8") as log_handle:
        returncode = _common.run_build_command(
            command,
            log_handle,
            operation_reporter,
        )
    if returncode != 0:
        logger.error("Local image build failed for %s (logs: %s)", image_ref, log_path)
        operation_reporter.on_phase_failed(
            "build", f"Local image build failed for {image_ref}", log_path
        )
        raise DockerError(
            f"Local image build failed for {image_ref}. See log at: {log_path}"
        )

    operation_reporter.on_phase_finished(
        "build", f"Local image build finished for {image_ref}"
    )
    logger.info("Local image build succeeded for %s", image_ref)
