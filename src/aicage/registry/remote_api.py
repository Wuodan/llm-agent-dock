from __future__ import annotations

import json
import urllib.request
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from aicage.config.global_config import GlobalConfig


class RegistryDiscoveryError(Exception):
    """Raised when registry discovery fails."""


def fetch_pull_token(global_cfg: GlobalConfig) -> str:
    url = f"{global_cfg.image_registry_api_token_url}:{global_cfg.image_repository}:pull"
    data, _ = fetch_json(url, None)
    token = data.get("token")
    if not token:
        raise RegistryDiscoveryError(
            f"Missing token while querying registry for {global_cfg.image_repository}."
        )
    return token


def fetch_json(url: str, headers: dict[str, str] | None) -> tuple[dict[str, Any], Mapping[str, str]]:
    request = urllib.request.Request(url, headers=headers or {})
    try:
        with urllib.request.urlopen(request) as response:
            payload = response.read().decode("utf-8")
            response_headers = response.headers
    except Exception as exc:  # pylint: disable=broad-except
        raise RegistryDiscoveryError(f"Failed to query registry endpoint {url}: {exc}") from exc

    try:
        data = json.loads(payload)
    except json.JSONDecodeError as exc:
        raise RegistryDiscoveryError(f"Invalid JSON from registry endpoint {url}: {exc}") from exc
    return data, response_headers
