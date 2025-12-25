from __future__ import annotations

import json
import subprocess

from aicage.config.runtime_config import RunConfig


def get_local_repo_digest(run_config: RunConfig) -> str | None:
    repository = f"{run_config.global_cfg.image_registry}/{run_config.global_cfg.image_repository}"
    inspect = subprocess.run(
        ["docker", "image", "inspect", run_config.image_ref, "--format", "{{json .RepoDigests}}"],
        check=False,
        capture_output=True,
        text=True,
    )
    if inspect.returncode != 0:
        return None

    try:
        digests = json.loads(inspect.stdout)
    except json.JSONDecodeError:
        return None

    if not isinstance(digests, list):
        return None

    for entry in digests:
        if not isinstance(entry, str):
            continue
        repo, sep, digest = entry.partition("@")
        if sep and repo == repository and digest:
            return digest

    return None
