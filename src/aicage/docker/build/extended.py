import os
from pathlib import Path

from aicage._logging import get_logger
from aicage.config.extensions.loader import ExtensionMetadata
from aicage.config.run_config import RunConfig
from aicage.docker.errors import DockerError
from aicage.docker.execution import cli as _docker_cli
from aicage.reporting import OperationReporter

from ._dockerfile_extensions import build_dockerfile_extensions
from ._shell_extensions import build_shell_extensions


def run(
    run_config: RunConfig,
    base_image_ref: str,
    extensions: list[ExtensionMetadata],
    log_path: Path,
    reporter: OperationReporter,
) -> None:
    logger = get_logger()
    log_path.parent.mkdir(parents=True, exist_ok=True)
    reporter.on_phase_started(
        "build",
        f"Building extended image {run_config.selection.image_ref}",
        log_path,
    )
    logger.info(
        "Building extended image %s (logs: %s)",
        run_config.selection.image_ref,
        log_path,
    )

    shell_extensions = [
        extension for extension in extensions if extension.dockerfile_path is None
    ]
    dockerfile_extensions = [
        extension for extension in extensions if extension.dockerfile_path is not None
    ]
    current_image_ref = base_image_ref
    intermediate_refs: list[str] = []
    with log_path.open("w", encoding="utf-8") as log_handle:
        if shell_extensions:
            target_ref = (
                run_config.selection.image_ref
                if not dockerfile_extensions
                else _shell_batch_image_ref(run_config)
            )
            if target_ref != run_config.selection.image_ref:
                intermediate_refs.append(target_ref)
            returncode = build_shell_extensions(
                base_image_ref=current_image_ref,
                target_ref=target_ref,
                shell_extensions=shell_extensions,
                log_handle=log_handle,
                operation_reporter=reporter,
            )
            if returncode != 0:
                logger.error(
                    "Extended image build failed for %s (logs: %s)",
                    run_config.selection.image_ref,
                    log_path,
                )
                reporter.on_phase_failed(
                    "build",
                    f"Extended image build failed for {run_config.selection.image_ref}",
                    log_path,
                )
                raise DockerError(
                    f"Extended image build failed for {run_config.selection.image_ref}. See log at: {log_path}"
                )
            current_image_ref = target_ref
        if dockerfile_extensions:
            current_image_ref, dockerfile_intermediate_refs, returncode = (
                build_dockerfile_extensions(
                    dockerfile_extensions=dockerfile_extensions,
                    run_config=run_config,
                    current_image_ref=current_image_ref,
                    log_handle=log_handle,
                    operation_reporter=reporter,
                )
            )
            intermediate_refs.extend(dockerfile_intermediate_refs)
            if returncode != 0:
                logger.error(
                    "Extended image build failed for %s (logs: %s)",
                    run_config.selection.image_ref,
                    log_path,
                )
                reporter.on_phase_failed(
                    "build",
                    f"Extended image build failed for {run_config.selection.image_ref}",
                    log_path,
                )
                raise DockerError(
                    f"Extended image build failed for {run_config.selection.image_ref}. See log at: {log_path}"
                )
    _cleanup_intermediate_images(intermediate_refs)
    reporter.on_phase_finished(
        "build",
        f"Extended image build finished for {run_config.selection.image_ref}",
    )
    logger.info("Extended image build succeeded for %s", run_config.selection.image_ref)


def _shell_batch_image_ref(run_config: RunConfig) -> str:
    repository, _ = _parse_image_ref(run_config.selection.image_ref)
    tag = f"tmp-{run_config.agent}-{run_config.selection.base}-shell-extensions"
    tag = tag.lower().replace("/", "-")
    return f"{repository}:{tag}"


def _cleanup_intermediate_images(intermediate_refs: list[str]) -> None:
    logger = get_logger()
    with Path(os.devnull).open("w", encoding="utf-8") as null_handle:
        for image_ref in intermediate_refs:
            result = _docker_cli.run_docker_command(
                ["docker", "image", "rm", "-f", image_ref],
                check=False,
                stdout=null_handle,
                stderr=null_handle,
            )
            if result.returncode != 0:
                logger.warning("Failed to remove intermediate image %s", image_ref)


def _parse_image_ref(image_ref: str) -> tuple[str, str]:
    repository, sep, tag = image_ref.rpartition(":")
    if not sep:
        raise DockerError(f"Image ref '{image_ref}' is missing a tag.")
    return repository, tag
