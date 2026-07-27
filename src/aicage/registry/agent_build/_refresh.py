from dataclasses import dataclass
from enum import Enum

from aicage._logging import get_logger
from aicage.docker.query import get_local_repo_digest_for_repo
from aicage.registry._errors import RegistryError
from aicage.registry.digest.remote_digest import get_remote_digest
from aicage.reporting import OperationReporter

from ._digest import resolve_base_digest


class _BaseRefreshAction(Enum):
    USE_LOCAL = "use_local"
    PULL_NOW = "pull_now"
    CONFIRM_PULL = "confirm_pull"


@dataclass(frozen=True)
class _BaseRefreshPlan:
    image_ref: str
    action: _BaseRefreshAction


def refresh_base_image(
    base_image_ref: str,
    base_repository: str,
    update_approved: bool,
    reporter: OperationReporter,
) -> str:
    logger = get_logger()
    plan = refresh_base_image_plan(base_image_ref, base_repository)
    match plan.action:
        case _BaseRefreshAction.PULL_NOW:
            return resolve_base_digest(
                base_image_ref, base_repository, reporter=reporter
            )
        case _BaseRefreshAction.USE_LOCAL:
            return plan.image_ref
        case _BaseRefreshAction.CONFIRM_PULL:
            if not update_approved:
                logger.info("Base image pull not required for %s", base_image_ref)
                return plan.image_ref
            return resolve_base_digest(
                base_image_ref, base_repository, reporter=reporter
            )


def refresh_base_image_plan(
    base_image_ref: str,
    base_repository: str,
) -> _BaseRefreshPlan:
    logger = get_logger()
    local_digest = get_local_repo_digest_for_repo(base_image_ref, base_repository)
    local_ref = _local_base_image_ref(base_repository, local_digest)
    remote_digest = get_remote_digest(base_image_ref)
    if remote_digest is None:
        if local_ref is None:
            raise RegistryError(
                f"Failed to resolve remote digest for {base_image_ref}."
            )
        logger.warning("Base image digest check failed; using local base image.")
        return _BaseRefreshPlan(
            image_ref=local_ref,
            action=_BaseRefreshAction.USE_LOCAL,
        )

    digest_ref = f"{base_repository}@{remote_digest}"
    if remote_digest == local_digest:
        return _BaseRefreshPlan(
            image_ref=digest_ref,
            action=_BaseRefreshAction.USE_LOCAL,
        )
    if local_ref is None:
        return _BaseRefreshPlan(
            image_ref=digest_ref,
            action=_BaseRefreshAction.PULL_NOW,
        )
    # A local tag exists but points to an older digest; ask before pulling the update.
    return _BaseRefreshPlan(
        image_ref=local_ref,
        action=_BaseRefreshAction.CONFIRM_PULL,
    )


def _local_base_image_ref(base_repository: str, local_digest: str | None) -> str | None:
    if local_digest is None:
        return None
    return f"{base_repository}@{local_digest}"
