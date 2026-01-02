from __future__ import annotations

from aicage._logging import get_logger
from aicage.config.runtime_config import RunConfig
from aicage.registry._pull_decision import decide_pull
from aicage.registry._pull_runner import run_pull


def pull_image(run_config: RunConfig) -> None:
    logger = get_logger()
    decision = decide_pull(run_config)
    if not decision.should_pull:
        logger.info("Image pull not required for %s", run_config.image_ref)
        return

    run_pull(run_config.image_ref)
