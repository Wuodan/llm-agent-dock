from aicage.config.run_config import RunConfig
from aicage.docker.query import local_image_exists
from aicage.registry._layers import base_layer_missing

from ._store import BuildRecord


def should_rebuild(
    run_config: RunConfig,
    record: BuildRecord | None,
    agent_version: str,
    base_image_ref: str,
) -> bool:
    image_ref = run_config.selection.agent_image_ref
    if not local_image_exists(image_ref):
        return True
    if record is None:
        return True
    if record.agent_version != agent_version:
        return True
    return base_layer_missing(base_image_ref, image_ref)
