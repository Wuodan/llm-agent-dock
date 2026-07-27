from aicage._logging import get_logger
from aicage.constants import IMAGE_REGISTRY
from aicage.docker.pull import run_pull
from aicage.docker.query import cleanup_old_digest, get_local_repo_digest_for_repo
from aicage.registry._errors import RegistryError
from aicage.registry._logs import pull_log_path
from aicage.registry._signature import resolve_verified_digest
from aicage.registry.digest.remote_digest import get_remote_digest
from aicage.reporting import OperationReporter


def ensure_version_check_image(image_ref: str, reporter: OperationReporter) -> None:
    repository = _local_repository(image_ref, IMAGE_REGISTRY)
    local_digest = get_local_repo_digest_for_repo(
        image_ref,
        repository,
    )
    if local_digest is None:
        _pull_version_check_image(image_ref, repository, local_digest, reporter)
        return

    remote_digest = get_remote_digest(image_ref)
    if remote_digest is None or remote_digest == local_digest:
        return

    _pull_version_check_image(image_ref, repository, local_digest, reporter)


def _pull_version_check_image(
    image_ref: str,
    repository: str,
    local_digest: str | None,
    reporter: OperationReporter,
) -> None:
    logger = get_logger()
    log_path = pull_log_path(image_ref)
    try:
        resolve_verified_digest(image_ref, reporter=reporter)
        run_pull(image_ref, log_path, reporter=reporter)
    except RegistryError:
        logger.warning(
            "Version check image pull failed; using local image (logs: %s).", log_path
        )
        return
    cleanup_old_digest(repository, local_digest, image_ref)


def _local_repository(image_ref: str, default_registry: str) -> str:
    name = _strip_reference(image_ref)
    parts = name.split("/", 1)
    if len(parts) == 1:
        return f"{default_registry}/{name}"
    registry, remainder = parts
    if "." in registry or ":" in registry or registry == "localhost":
        return f"{registry}/{remainder}"
    return f"{default_registry}/{name}"


def _strip_reference(image_ref: str) -> str:
    if "@" in image_ref:
        return image_ref.split("@", 1)[0]
    last_colon = image_ref.rfind(":")
    if last_colon > image_ref.rfind("/"):
        return image_ref[:last_colon]
    return image_ref
