from __future__ import annotations

from docker.errors import DockerException, ImageNotFound

from aicage.config.runtime_config import RunConfig
from aicage.docker_client import get_docker_client


def get_local_repo_digest(run_config: RunConfig) -> str | None:
    repository = f"{run_config.global_cfg.image_registry}/{run_config.global_cfg.image_repository}"
    return get_local_repo_digest_for_repo(run_config.image_ref, repository)


def get_local_repo_digest_for_repo(image_ref: str, repository: str) -> str | None:
    try:
        client = get_docker_client()
        image = client.images.get(image_ref)
    except (ImageNotFound, DockerException):
        return None

    repo_digests = image.attrs.get("RepoDigests")
    if not isinstance(repo_digests, list):
        return None

    for entry in repo_digests:
        if not isinstance(entry, str):
            continue
        repo, sep, digest = entry.partition("@")
        if sep and repo == repository and digest:
            return digest

    return None
