from __future__ import annotations

import re
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from aicage.config.context import ConfigContext
from aicage.registry.remote_api import fetch_json, fetch_pull_token


def discover_base_aliases(context: ConfigContext, tool: str) -> list[str]:
    aliases: set[str] = set()
    token = fetch_pull_token(context.global_cfg)
    page_url = f"{context.global_cfg.image_registry_api_url}/{context.global_cfg.image_repository}/tags/list?n=1000"

    while page_url:
        data, headers = fetch_json(page_url, {"Authorization": f"Bearer {token}"})
        for name in data.get("tags", []) or []:
            if name.endswith(("-amd64-latest", "-arm64-latest", "-arch64-latest")):
                continue
            expected_prefix = f"{tool}-"
            if name.startswith(expected_prefix) and name.endswith("-latest"):
                base = name[len(expected_prefix) : -len("-latest")]
                if base:
                    aliases.add(base)
        page_url = _parse_next_link(headers.get("Link"))

    return sorted(aliases)


def _parse_next_link(link_header: str | None) -> str:
    if not link_header:
        return ""
    for part in link_header.split(","):
        match = re.search(r'<([^>]+)>\s*;\s*rel="next"', part.strip(), re.IGNORECASE)
        if match:
            return match.group(1)
    return ""
