from dataclasses import dataclass

from aicage.registry.image_selection.models import ImageSelection


@dataclass(frozen=True)
class ConfigSelectionResult:
    selection: ImageSelection
    project_docker_args: str
