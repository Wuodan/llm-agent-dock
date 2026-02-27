import json
import subprocess

from aicage._logging import get_logger

from .cli import run_docker_command, run_docker_command_capture
from .runtime import get_container_runtime
from .types import ImageRefRepository


def local_image_exists(image_ref: str) -> bool:
    return _inspect_local_image(image_ref) is not None


def get_local_repo_digest(image: ImageRefRepository) -> str | None:
    return get_local_repo_digest_for_repo(image.image_ref, image.repository)


def get_local_repo_digest_for_repo(image_ref: str, repository: str) -> str | None:
    image = _inspect_local_image(image_ref)
    if image is None:
        return None

    repo_digests = image.get("RepoDigests")
    if not isinstance(repo_digests, list):
        return None

    for entry in repo_digests:
        if not isinstance(entry, str):
            continue
        repo, sep, digest = entry.partition("@")
        if sep and repo == repository and digest:
            return digest

    return None


def get_local_rootfs_layers(image_ref: str) -> list[str] | None:
    image = _inspect_local_image(image_ref)
    if image is None:
        return None

    rootfs = image.get("RootFS")
    if not isinstance(rootfs, dict):
        return None
    layers = rootfs.get("Layers")
    if not isinstance(layers, list):
        return None
    filtered = [layer for layer in layers if isinstance(layer, str)]
    if not filtered:
        return None
    return filtered


def _remove_image_ref(image_ref: str, target_label: str) -> None:
    logger = get_logger()
    runtime = get_container_runtime()
    result = run_docker_command(
        [runtime, "image", "rm", image_ref],
        check=False,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    if result.returncode != 0:
        logger.warning("Failed to remove %s %s", target_label, image_ref)
        return
    logger.info("Removed %s %s", target_label, image_ref)


def _remove_old_image_digest(repository: str, old_digest: str) -> None:
    _remove_image_ref(f"{repository}@{old_digest}", "old image digest")


def cleanup_old_digest(
    repository: str,
    local_digest: str | None,
    image_ref: str,
) -> None:
    if local_digest is None:
        return
    updated_digest = get_local_repo_digest_for_repo(image_ref, repository)
    if updated_digest and updated_digest != local_digest:
        _remove_old_image_digest(repository, local_digest)


def _inspect_local_image(image_ref: str) -> dict[str, object] | None:
    runtime = get_container_runtime()
    result = run_docker_command_capture(
        [runtime, "image", "inspect", image_ref],
        check=False,
        text=True,
    )
    if result.returncode != 0:
        return None
    try:
        payload = json.loads(result.stdout)
    except json.JSONDecodeError:
        return None
    if not isinstance(payload, list) or not payload:
        return None
    image = payload[0]
    if not isinstance(image, dict):
        return None
    return image
