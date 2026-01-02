from __future__ import annotations

from datetime import datetime, timezone

from aicage.config.runtime_config import RunConfig
from aicage.errors import CliError
from aicage.registry import _local_query

from ._digest import refresh_base_digest
from ._logs import build_log_path, pull_log_path
from ._runner import local_image_exists, run_build
from ._store import BuildRecord, BuildStore

__all__ = ["ensure_local_image"]


def ensure_local_image(run_config: RunConfig) -> None:
    agent_metadata = run_config.images_metadata.agents[run_config.agent]
    if agent_metadata.redistributable:
        return

    if run_config.agent_version is None:
        raise CliError(f"Missing agent version for '{run_config.agent}'.")

    base_image_ref = _base_image_ref(run_config)
    base_repo = _base_repository(run_config)
    pull_log = pull_log_path(run_config.agent, run_config.base)
    base_digest = refresh_base_digest(
        base_image_ref=base_image_ref,
        base_repository=base_repo,
        global_cfg=run_config.global_cfg,
        pull_log_path=pull_log,
    )

    store = BuildStore()
    record = store.load(run_config.agent, run_config.base)

    should_build = _should_build(
        run_config=run_config,
        record=record,
        base_digest=base_digest,
    )
    if not should_build:
        return

    log_path = build_log_path(run_config.agent, run_config.base)
    run_build(
        run_config=run_config,
        base_image_ref=base_image_ref,
        log_path=log_path,
    )

    updated_base_digest = _local_query.get_local_repo_digest_for_repo(base_image_ref, base_repo)
    store.save(
        BuildRecord(
            agent=run_config.agent,
            base=run_config.base,
            agent_version=run_config.agent_version,
            base_image=base_image_ref,
            base_digest=updated_base_digest,
            image_ref=run_config.image_ref,
            built_at=_now_iso(),
        )
    )


def _should_build(
    run_config: RunConfig,
    record: BuildRecord | None,
    base_digest: str | None,
) -> bool:
    if not local_image_exists(run_config.image_ref):
        return True
    if record is None:
        return True
    if record.agent_version != run_config.agent_version:
        return True
    if record.base_digest is None:
        return True
    if base_digest and record.base_digest != base_digest:
        return True
    return False


def _base_repository(run_config: RunConfig) -> str:
    return f"{run_config.global_cfg.image_registry}/{run_config.global_cfg.image_base_repository}"


def _base_image_ref(run_config: RunConfig) -> str:
    repository = _base_repository(run_config)
    return f"{repository}:{run_config.base}"


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()
