from aicage.config.run_config import RunConfig
from aicage.docker.query import local_image_exists
from aicage.registry._layers import base_layer_missing

from ._store import BuildRecord


def should_rebuild(
    run_config: RunConfig,
    record: BuildRecord | None,
    agent_image_ref: str,
    extension_hash: str,
) -> bool:
    needs_rebuild = (
        not local_image_exists(run_config.selection.image_ref)
        or record is None
        or record.image_ref != run_config.selection.image_ref
        or record.extensions != run_config.selection.extensions
        or record.extension_hash != extension_hash
        or record.base_image != agent_image_ref
    )
    if needs_rebuild:
        return True
    return base_layer_missing(agent_image_ref, run_config.selection.image_ref)
