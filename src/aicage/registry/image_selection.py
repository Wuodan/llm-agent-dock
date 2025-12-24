from aicage.config.context import ConfigContext
from aicage.errors import CliError
from aicage.runtime.prompts import BaseSelectionRequest, prompt_for_base

from .discovery.catalog import discover_tool_bases

__all__ = ["select_tool_image"]


def select_tool_image(tool: str, context: ConfigContext) -> str:
    tool_cfg = context.project_cfg.tools.setdefault(tool, {})
    base = tool_cfg.get("base") or context.global_cfg.tools.get(tool, {}).get("base")
    repository_ref = context.image_repository_ref()

    if not base:
        available_bases = discover_tool_bases(context, tool)
        if not available_bases:
            raise CliError(f"No base images found for tool '{tool}' (repository={repository_ref}).")

        request = BaseSelectionRequest(
            tool=tool,
            default_base=context.global_cfg.default_image_base,
            available=available_bases,
        )
        base = prompt_for_base(request)
        tool_cfg["base"] = base
        context.store.save_project(context.project_path, context.project_cfg)

    image_tag = f"{tool}-{base}-latest"
    image_ref = f"{repository_ref}:{image_tag}"
    return image_ref
