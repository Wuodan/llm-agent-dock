from aicage._logging import get_logger
from aicage.constants import IMAGE_REGISTRY, IMAGE_REPOSITORY
from aicage.docker.pull import run_pull
from aicage.docker.query import cleanup_old_digest, get_local_repo_digest_for_repo
from aicage.registry._logs import pull_log_path
from aicage.registry._pull_decision import decide_pull
from aicage.registry._signature import resolve_verified_digest
from aicage.reporting import OperationReporter


def pull_image(
    image_ref: str,
    update_approved: bool,
    reporter: OperationReporter,
) -> None:
    logger = get_logger()
    repository = f"{IMAGE_REGISTRY}/{IMAGE_REPOSITORY}"
    should_pull = decide_pull(image_ref, update_approved)
    if not should_pull:
        logger.info("Image pull not required for %s", image_ref)
        return

    local_digest = get_local_repo_digest_for_repo(image_ref, repository)
    log_path = pull_log_path(image_ref)
    reporter.on_phase_started("pull", f"Preparing image {image_ref}", log_path)
    reporter.on_phase_progress(
        "pull",
        "Resolving digest and verifying image signature",
        None,
        None,
    )
    resolve_verified_digest(image_ref, reporter=reporter)
    run_pull(image_ref, log_path, reporter=reporter)
    cleanup_old_digest(repository, local_digest, image_ref)
