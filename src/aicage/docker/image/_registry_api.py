import json
import urllib.error
import urllib.request
from collections.abc import Mapping
from typing import Any

from aicage._network import classify_network_failure, host_from_url, require_http_url
from aicage.constants import DOCKER_REGISTRY_REQUEST_TIMEOUT_SECONDS
from aicage.docker.errors import _RegistryDiscoveryError
from aicage.docker.types import _RegistryApiConfig


def _fetch_pull_token_for_repository(
    api_config: _RegistryApiConfig, repository: str
) -> str:
    url = f"{api_config.registry_api_token_url}:{repository}:pull"
    data, _ = _fetch_json(url, None)
    token = data.get("token")
    if not token:
        raise _RegistryDiscoveryError(
            f"Missing token while querying registry for {repository}."
        )
    return token


def _fetch_json(
    url: str, headers: dict[str, str] | None
) -> tuple[dict[str, Any], Mapping[str, str]]:
    try:
        request = urllib.request.Request(require_http_url(url), headers=headers or {})
        with urllib.request.urlopen(  # nosec B310 -- request URL is restricted to HTTP(S) by require_http_url().
            request, timeout=DOCKER_REGISTRY_REQUEST_TIMEOUT_SECONDS
        ) as response:
            payload = response.read().decode("utf-8")
            response_headers = response.headers
    except urllib.error.HTTPError as exc:
        category = classify_network_failure(exc)
        host = host_from_url(url)
        message = f"Failed to query registry endpoint {url} (host={host}, category={category}): {exc}"
        raise _RegistryDiscoveryError(message) from exc
    except urllib.error.URLError as exc:
        category = classify_network_failure(exc)
        host = host_from_url(url)
        message = f"Failed to query registry endpoint {url} (host={host}, category={category}): {exc}"
        raise _RegistryDiscoveryError(message) from exc

    try:
        data = json.loads(payload)
    except json.JSONDecodeError as exc:
        raise _RegistryDiscoveryError(
            f"Invalid JSON from registry endpoint {url}: {exc}"
        ) from exc
    return data, response_headers
