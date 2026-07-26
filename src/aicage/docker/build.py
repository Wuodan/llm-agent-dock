import subprocess  # nosec B404 -- subprocess is required to stream docker build output incrementally.
from pathlib import Path
from typing import TextIO

from aicage._execution_cleanup import register_process
from aicage._logging import get_logger
from aicage._proxy import proxy_build_args_from_host
from aicage.config.extensions.loader import ExtensionMetadata
from aicage.config.resources import find_packaged_path
from aicage.config.run_config import RunConfig
from aicage.docker.cli import _run_docker_command
from aicage.docker.errors import DockerError
from aicage.docker.reporting import OperationReporter, _default_operation_reporter


def run_build(
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
    build_root = _build_context_dir(run_config, dockerfile_path)
    # Docker SDK does not support BuildKit; keep CLI build for compatibility.
    # See: https://github.com/docker/docker-py/issues/2230
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
        returncode = _run_build_command(
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
            f"Local image build failed for {image_ref}. See log at {log_path}."
        )

    operation_reporter.on_phase_finished(
        "build", f"Local image build finished for {image_ref}"
    )
    logger.info("Local image build succeeded for %s", image_ref)


def run_extended_build(
    run_config: RunConfig,
    base_image_ref: str,
    extensions: list[ExtensionMetadata],
    log_path: Path,
    reporter: OperationReporter | None = None,
) -> None:
    logger = get_logger()
    operation_reporter = reporter or _default_operation_reporter()
    log_path.parent.mkdir(parents=True, exist_ok=True)
    operation_reporter.on_phase_started(
        "build",
        f"Building extended image {run_config.selection.image_ref}",
        log_path,
    )
    logger.info(
        "Building extended image %s (logs: %s)",
        run_config.selection.image_ref,
        log_path,
    )

    dockerfile_builtin = find_packaged_path("extension-build/Dockerfile")
    current_image_ref = base_image_ref
    intermediate_refs: list[str] = []
    proxy_build_args = proxy_build_args_from_host()
    with log_path.open("w", encoding="utf-8") as log_handle:
        for idx, extension in enumerate(extensions):
            target_ref = (
                run_config.selection.image_ref
                if idx == len(extensions) - 1
                else _intermediate_image_ref(run_config, extension, idx)
            )
            if target_ref != run_config.selection.image_ref:
                intermediate_refs.append(target_ref)
            dockerfile_path = extension.dockerfile_path or dockerfile_builtin
            # Docker SDK does not support BuildKit; keep CLI build for compatibility.
            # See: https://github.com/docker/docker-py/issues/2230
            command = [
                "docker",
                "build",
                "--no-cache",
                "--file",
                str(dockerfile_path),
                "--build-arg",
                f"BASE_IMAGE={current_image_ref}",
                "--build-arg",
                f"EXTENSION={extension.extension_id}",
                "--tag",
                target_ref,
                str(extension.directory),
            ]
            command.extend(proxy_build_args)
            returncode = _run_build_command(
                command,
                log_handle,
                operation_reporter,
            )
            if returncode != 0:
                logger.error(
                    "Extended image build failed for %s (logs: %s)",
                    run_config.selection.image_ref,
                    log_path,
                )
                operation_reporter.on_phase_failed(
                    "build",
                    f"Extended image build failed for {run_config.selection.image_ref}",
                    log_path,
                )
                raise DockerError(
                    f"Extended image build failed for {run_config.selection.image_ref}. See log at {log_path}."
                )
            current_image_ref = target_ref
    _cleanup_intermediate_images(intermediate_refs)
    operation_reporter.on_phase_finished(
        "build",
        f"Extended image build finished for {run_config.selection.image_ref}",
    )
    logger.info("Extended image build succeeded for %s", run_config.selection.image_ref)


def run_custom_base_build(
    build_root: Path,
    from_image: str,
    image_ref: str,
    log_path: Path,
    reporter: OperationReporter | None = None,
) -> None:
    logger = get_logger()
    operation_reporter = reporter or _default_operation_reporter()
    dockerfile_path = build_root / "Dockerfile"
    log_path.parent.mkdir(parents=True, exist_ok=True)
    operation_reporter.on_phase_started(
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
        returncode = _run_build_command(
            command,
            log_handle,
            operation_reporter,
        )
    if returncode != 0:
        logger.error(
            "Custom base image build failed for %s (logs: %s)", image_ref, log_path
        )
        operation_reporter.on_phase_failed(
            "build",
            f"Custom base image build failed for {image_ref}",
            log_path,
        )
        raise DockerError(
            f"Custom base image build failed for {image_ref}. See log at {log_path}."
        )

    operation_reporter.on_phase_finished(
        "build", f"Custom base image build finished for {image_ref}"
    )
    logger.info("Custom base image build succeeded for %s", image_ref)


def _build_context_dir(run_config: RunConfig, dockerfile_path: Path) -> Path:
    agent_metadata = run_config.context.agents[run_config.agent]
    local_definition_dir = agent_metadata.local_definition_dir
    if local_definition_dir.is_relative_to(dockerfile_path.parent):
        return dockerfile_path.parent
    return local_definition_dir.parent.parent


def _intermediate_image_ref(
    run_config: RunConfig, extension: ExtensionMetadata, idx: int
) -> str:
    repository, _ = _parse_image_ref(run_config.selection.image_ref)
    tag = f"tmp-{run_config.agent}-{run_config.selection.base}-{idx + 1}-{extension.extension_id}"
    tag = tag.lower().replace("/", "-")
    return f"{repository}:{tag}"


def _parse_image_ref(image_ref: str) -> tuple[str, str]:
    repository, sep, tag = image_ref.rpartition(":")
    if not sep:
        raise DockerError(f"Image ref '{image_ref}' is missing a tag.")
    return repository, tag


def _cleanup_intermediate_images(intermediate_refs: list[str]) -> None:
    logger = get_logger()
    for image_ref in intermediate_refs:
        result = _run_docker_command(
            ["docker", "image", "rm", "-f", image_ref],
            check=False,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        if result.returncode != 0:
            logger.warning("Failed to remove intermediate image %s", image_ref)


def _run_build_command(
    command: list[str],
    log_handle: TextIO,
    reporter: OperationReporter,
) -> int:
    try:
        with subprocess.Popen(  # nosec B603 -- command is an internal Docker CLI argument list without shell usage.
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding="utf-8",
        ) as process:
            register_process(process)
            if process.stdout is None:
                raise RuntimeError("Docker build process did not provide stdout.")
            for line in process.stdout:
                stripped = line.rstrip("\n")
                log_handle.write(line)
                log_handle.flush()
                reporter.on_phase_log("build", stripped)
            return process.wait()
    except FileNotFoundError as exc:
        raise DockerError(
            "Docker CLI not found. Install Docker and ensure it is on PATH."
        ) from exc
