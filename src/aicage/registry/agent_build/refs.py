from aicage.config.run_config import RunConfig
from aicage.constants import IMAGE_BASE_REPOSITORY, IMAGE_REGISTRY
from aicage.paths import CUSTOM_BASES_DIR

from ..base_build.ensure import image_ref as base_build_image_ref


def get_base_image_ref(run_config: RunConfig) -> str:
    base_metadata = run_config.context.bases[run_config.selection.base]
    if base_metadata.local_definition_dir.is_relative_to(CUSTOM_BASES_DIR):
        return base_build_image_ref(run_config.selection.base)
    repository = _base_repository(run_config)
    return f"{repository}:{run_config.selection.base}"


def _base_repository(_run_config: RunConfig) -> str:
    return f"{IMAGE_REGISTRY}/{IMAGE_BASE_REPOSITORY}"
