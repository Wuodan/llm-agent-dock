import json
import re
import urllib.request
from typing import Any, Dict, List, Mapping, Tuple

class RegistryDiscoveryError(Exception):
    """Raised when registry discovery fails."""


def discover_base_aliases(
    repository: str,
    registry_api_url: str,
    registry_token_url: str,
    tool: str,
) -> List[str]:
    aliases: set[str] = set()
    token = _fetch_pull_token(registry_token_url, repository)
    page_url = f"{registry_api_url}/{repository}/tags/list?n=1000"

    while page_url:
        data, headers = _fetch_json(page_url, {"Authorization": f"Bearer {token}"})
        for name in data.get("tags", []) or []:
            expected_prefix = f"{tool}-"
            if name.startswith(expected_prefix) and name.endswith("-latest"):
                base = name[len(expected_prefix) : -len("-latest")]
                if base:
                    aliases.add(base)
        page_url = _parse_next_link(headers.get("Link"))

    return sorted(aliases)


def _fetch_pull_token(registry_token_url: str, repository: str) -> str:
    url = f"{registry_token_url}:{repository}:pull"
    data, _ = _fetch_json(url, None)
    token = data.get("token")
    if not token:
        raise RegistryDiscoveryError(f"Missing token while querying registry for {repository}.")
    return token


def _fetch_json(url: str, headers: Dict[str, str] | None) -> Tuple[Dict[str, Any], Mapping[str, str]]:
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


def _parse_next_link(link_header: str | None) -> str:
    if not link_header:
        return ""
    for part in link_header.split(","):
        match = re.search(r'<([^>]+)>\s*;\s*rel="next"', part.strip(), re.IGNORECASE)
        if match:
            return match.group(1)
    return ""
