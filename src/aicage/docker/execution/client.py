from functools import lru_cache

import docker
from docker.client import DockerClient
from docker.errors import DockerException

from aicage.constants import (
    DOCKER_LOCAL_METADATA_TIMEOUT_SECONDS,
    DOCKER_PULL_REQUEST_TIMEOUT_SECONDS,
)
from aicage.docker.errors import DockerError
from aicage.docker.runtime import get_active_docker_host


@lru_cache(maxsize=1)
def get_docker_client() -> DockerClient:
    try:
        return _build_client(DOCKER_LOCAL_METADATA_TIMEOUT_SECONDS)
    except DockerException as exc:
        raise DockerError(
            "Docker is not running or not reachable. Start Docker and retry."
        ) from exc


@lru_cache(maxsize=1)
def get_docker_pull_client() -> DockerClient:
    try:
        return _build_client(DOCKER_PULL_REQUEST_TIMEOUT_SECONDS)
    except DockerException as exc:
        raise DockerError(
            "Docker is not running or not reachable. Start Docker and retry."
        ) from exc


def _build_client(timeout: int) -> DockerClient:
    docker_host = get_active_docker_host()
    return docker.DockerClient(base_url=docker_host.host, timeout=timeout)
