from __future__ import annotations

import sys
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from aicage.config.context import ConfigContext

from aicage.errors import CliError
from aicage.registry.remote_api import RegistryDiscoveryError

from ._local import discover_local_bases
from ._remote import discover_base_aliases


def discover_tool_bases(context: ConfigContext, tool: str) -> list[str]:
    remote_bases: list[str] = []
    local_bases: list[str] = []
    try:
        remote_bases = discover_base_aliases(context, tool)
    except RegistryDiscoveryError as exc:
        print(f"[aicage] Warning: {exc}. Continuing with local images.", file=sys.stderr)
    try:
        local_bases = discover_local_bases(context.image_repository_ref(), tool)
    except CliError as exc:
        print(f"[aicage] Warning: {exc}", file=sys.stderr)
    return sorted(set(remote_bases) | set(local_bases))
