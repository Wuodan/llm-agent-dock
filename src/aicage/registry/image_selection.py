from __future__ import annotations

from pathlib import Path

from aicage.config.context import ConfigContext
from aicage.config.project_config import ToolConfig
from aicage.errors import CliError
from aicage.registry.images_metadata.models import ImagesMetadata, ToolMetadata
from aicage.runtime.prompts import BaseSelectionRequest, prompt_for_base

__all__ = ["select_tool_image"]


def select_tool_image(tool: str, context: ConfigContext) -> str:
    tool_cfg = context.project_cfg.tools.setdefault(tool, ToolConfig())
    tool_metadata = _require_tool_metadata(tool, context.images_metadata)
    base = tool_cfg.base or context.global_cfg.tools.get(tool, {}).get("base")

    if not base:
        available_bases = _available_bases(tool, tool_metadata, context.images_metadata)
        if not available_bases:
            raise CliError(f"No base images found for tool '{tool}' in metadata.")

        request = BaseSelectionRequest(
            tool=tool,
            context=context,
            tool_metadata=tool_metadata,
        )
        base = prompt_for_base(request)
        tool_cfg.base = base
        context.store.save_project(Path(context.project_cfg.path), context.project_cfg)
    else:
        _validate_base(tool, base, tool_metadata, context.images_metadata)

    image_tag = f"{tool}-{base}-latest"
    image_ref = f"{context.image_repository_ref()}:{image_tag}"
    return image_ref


def _require_tool_metadata(tool: str, images_metadata: ImagesMetadata) -> ToolMetadata:
    tool_metadata = images_metadata.tools.get(tool)
    if not tool_metadata:
        raise CliError(f"Tool '{tool}' is missing from images metadata.")
    return tool_metadata


def _available_bases(
    tool: str,
    tool_metadata: ToolMetadata,
    images_metadata: ImagesMetadata,
) -> list[str]:
    invalid = [base for base in tool_metadata.valid_bases if base not in images_metadata.bases]
    if invalid:
        raise CliError(
            f"Tool '{tool}' references unknown base(s) in metadata: {', '.join(invalid)}."
        )
    return sorted(set(tool_metadata.valid_bases))


def _validate_base(
    tool: str,
    base: str,
    tool_metadata: ToolMetadata,
    images_metadata: ImagesMetadata,
) -> None:
    if base not in tool_metadata.valid_bases:
        raise CliError(f"Base '{base}' is not valid for tool '{tool}'.")
    if base not in images_metadata.bases:
        raise CliError(f"Base '{base}' is missing from images metadata.")

