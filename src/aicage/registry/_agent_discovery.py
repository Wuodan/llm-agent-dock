from __future__ import annotations

from aicage.registry._custom_agent_loader import load_custom_agents
from aicage.registry.images_metadata.models import ImagesMetadata

__all__ = ["discover_agents"]


def discover_agents(
    images_metadata: ImagesMetadata,
) -> ImagesMetadata:
    custom_agents = load_custom_agents(images_metadata)
    if not custom_agents:
        return images_metadata

    merged_agents = dict(images_metadata.agents)
    merged_agents.update(custom_agents)
    return ImagesMetadata(
        aicage_image=images_metadata.aicage_image,
        aicage_image_base=images_metadata.aicage_image_base,
        bases=images_metadata.bases,
        agents=merged_agents,
    )
