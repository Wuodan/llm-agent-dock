from typing import TextIO

from aicage._proxy import proxy_build_args_from_host
from aicage.config.extensions.loader import ExtensionMetadata
from aicage.config.resources import find_packaged_path
from aicage.config.run_config import RunConfig
from aicage.docker.errors import DockerError
from aicage.docker.reporting import OperationReporter

from . import _common


def build_dockerfile_extensions(
    dockerfile_extensions: list[ExtensionMetadata],
    run_config: RunConfig,
    current_image_ref: str,
    log_handle: TextIO,
    operation_reporter: OperationReporter,
) -> tuple[str, list[str], int]:
    intermediate_refs: list[str] = []
    dockerfile_builtin = find_packaged_path("extension-build/Dockerfile")
    proxy_build_args = proxy_build_args_from_host()
    for idx, extension in enumerate(dockerfile_extensions):
        target_ref = (
            run_config.selection.image_ref
            if idx == len(dockerfile_extensions) - 1
            else _intermediate_image_ref(run_config, extension.extension_id, idx)
        )
        if target_ref != run_config.selection.image_ref:
            intermediate_refs.append(target_ref)
        dockerfile_path = extension.dockerfile_path or dockerfile_builtin
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
        returncode = _common.run_build_command(
            command,
            log_handle,
            operation_reporter,
        )
        if returncode != 0:
            return current_image_ref, intermediate_refs, returncode
        current_image_ref = target_ref
    return current_image_ref, intermediate_refs, 0


def _intermediate_image_ref(run_config: RunConfig, extension_id: str, idx: int) -> str:
    repository, sep, _ = run_config.selection.image_ref.rpartition(":")
    if not sep:
        raise DockerError(
            f"Image ref '{run_config.selection.image_ref}' is missing a tag."
        )
    tag = f"tmp-{run_config.agent}-{run_config.selection.base}-{idx + 1}-{extension_id}"
    return f"{repository}:{tag.lower().replace('/', '-')}"
