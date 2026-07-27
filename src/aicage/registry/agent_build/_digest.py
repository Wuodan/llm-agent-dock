from aicage._logging import get_logger
from aicage.docker.pull import run_pull
from aicage.docker.query import cleanup_old_digest, get_local_repo_digest_for_repo
from aicage.registry._errors import RegistryError
from aicage.registry._logs import pull_log_path
from aicage.registry._signature import resolve_verified_digest
from aicage.reporting import OperationReporter


def resolve_base_digest(
    base_image_ref: str,
    base_repository: str,
    reporter: OperationReporter,
) -> str:
    logger = get_logger()
    local_digest = get_local_repo_digest_for_repo(base_image_ref, base_repository)
    try:
        digest_ref = resolve_verified_digest(base_image_ref, reporter=reporter)
    except RegistryError:
        if not local_digest:
            raise
        logger.warning("Base image digest check failed; using local base image.")
        return f"{base_repository}@{local_digest}"
    remote_digest = digest_ref.split("@", 1)[1]
    if remote_digest == local_digest:
        return digest_ref

    log_path = pull_log_path(base_image_ref)
    try:
        run_pull(base_image_ref, log_path, reporter=reporter)
    except RegistryError:
        if local_digest:
            logger.warning(
                "Base image pull failed; using local base image (logs: %s).", log_path
            )
            return f"{base_repository}@{local_digest}"
        raise

    cleanup_old_digest(base_repository, local_digest, base_image_ref)
    return digest_ref
