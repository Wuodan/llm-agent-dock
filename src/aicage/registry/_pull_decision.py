from __future__ import annotations

from dataclasses import dataclass

from aicage.config.runtime_config import RunConfig
from aicage.registry import _local_query, _remote_query


@dataclass(frozen=True)
class PullDecision:
    should_pull: bool


def decide_pull(run_config: RunConfig) -> PullDecision:
    local_digest = _local_query.get_local_repo_digest(run_config)
    if local_digest is None:
        return PullDecision(should_pull=True)

    remote_digest = _remote_query.get_remote_repo_digest_for_repo(
        run_config.image_ref,
        run_config.global_cfg.image_repository,
        run_config.global_cfg,
    )
    if remote_digest is None:
        return PullDecision(should_pull=False)

    return PullDecision(should_pull=local_digest != remote_digest)
