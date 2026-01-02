from __future__ import annotations

from aicage.config.resources import find_packaged_path
from aicage.errors import CliError
from aicage.registry._agent_discovery import discover_agents

from .models import ImagesMetadata

__all__ = ["load_images_metadata"]


def load_images_metadata() -> ImagesMetadata:
    path = find_packaged_path("images-metadata.yaml")
    try:
        payload = path.read_text(encoding="utf-8")
    except OSError as exc:
        raise CliError(f"Failed to read images metadata from {path}: {exc}") from exc
    metadata = ImagesMetadata.from_yaml(payload)
    return discover_agents(metadata)
