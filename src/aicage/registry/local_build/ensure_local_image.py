from __future__ import annotations

from aicage.config.runtime_config import RunConfig
from aicage.errors import CliError
from aicage.registry import _local_query

from ._digest import refresh_base_digest
from ._logs import build_log_path
from ._plan import base_image_ref, base_repository, now_iso, should_build
from ._runner import run_build
from ._store import BuildRecord, BuildStore


def ensure_local_image(run_config: RunConfig) -> None:
    agent_metadata = run_config.images_metadata.agents[run_config.agent]
    if agent_metadata.local_definition_dir is None:
        raise CliError(f"Missing local definition for '{run_config.agent}'.")

    if run_config.agent_version is None:
        raise CliError(f"Missing agent version for '{run_config.agent}'.")

    base_image = base_image_ref(run_config)
    base_repo = base_repository(run_config)
    base_digest = refresh_base_digest(
        base_image_ref=base_image,
        base_repository=base_repo,
        global_cfg=run_config.global_cfg,
    )

    store = BuildStore()
    record = store.load(run_config.agent, run_config.base)

    needs_build = should_build(
        run_config=run_config,
        record=record,
        base_digest=base_digest,
    )
    if not needs_build:
        return

    log_path = build_log_path(run_config.agent, run_config.base)
    run_build(
        run_config=run_config,
        base_image_ref=base_image,
        log_path=log_path,
    )

    updated_base_digest = _local_query.get_local_repo_digest_for_repo(base_image, base_repo)
    store.save(
        BuildRecord(
            agent=run_config.agent,
            base=run_config.base,
            agent_version=run_config.agent_version,
            base_image=base_image,
            base_digest=updated_base_digest,
            image_ref=run_config.image_ref,
            built_at=now_iso(),
        )
    )
