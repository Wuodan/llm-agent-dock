from __future__ import annotations

import urllib.error
import urllib.request
from collections.abc import Mapping

from aicage.config.runtime_config import RunConfig
from aicage.registry.remote_api import RegistryDiscoveryError, fetch_pull_token


def get_remote_repo_digest(run_config: RunConfig) -> str | None:
    reference = _parse_reference(run_config.image_ref)
    try:
        token = fetch_pull_token(run_config.global_cfg)
    except RegistryDiscoveryError:
        return None
    url = (
        f"{run_config.global_cfg.image_registry_api_url}"
        f"/{run_config.global_cfg.image_repository}"
        f"/manifests/{reference}"
    )
    headers: dict[str, str] = {
        "Accept": ",".join(
            [
                "application/vnd.oci.image.index.v1+json",
                "application/vnd.docker.distribution.manifest.list.v2+json",
                "application/vnd.oci.image.manifest.v1+json",
                "application/vnd.docker.distribution.manifest.v2+json",
            ]
        ),
        "Authorization": f"Bearer {token}",
    }
    response_headers = _head_request(url, headers)
    if response_headers is None:
        return None
    return response_headers.get("Docker-Content-Digest")


def _parse_reference(image_ref: str) -> str:
    reference = "latest"
    if "@" in image_ref:
        _, reference = image_ref.split("@", 1)
    else:
        last_colon = image_ref.rfind(":")
        if last_colon > image_ref.rfind("/"):
            reference = image_ref[last_colon + 1 :]
    return reference or "latest"


def _head_request(url: str, headers: Mapping[str, str]) -> Mapping[str, str] | None:
    request = urllib.request.Request(url, headers=dict(headers), method="HEAD")
    try:
        with urllib.request.urlopen(request) as response:
            return response.headers
    except urllib.error.HTTPError as exc:
        if exc.code in {401, 403}:
            return exc.headers
        return None
    except urllib.error.URLError:
        return None
