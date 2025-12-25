from __future__ import annotations

import importlib
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from aicage.config.context import ConfigContext
    from aicage.config.runtime_config import RunConfig

__all__ = ["pull_image", "select_tool_image"]


def pull_image(run_config: RunConfig) -> None:
    module = importlib.import_module("aicage.registry.image_pull")
    module.pull_image(run_config)


def select_tool_image(tool: str, context: ConfigContext) -> str:
    module = importlib.import_module("aicage.registry.image_selection")
    return module.select_tool_image(tool, context)
