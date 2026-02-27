import os
import shutil
from functools import lru_cache
from pathlib import Path

from aicage.docker.errors import DockerError
from aicage.paths import HOST_DOCKER_SOCKET_PATH

_PODMAN_ROOTFUL_SOCKET_PATH: Path = Path("/run/podman/podman.sock")


@lru_cache(maxsize=1)
def get_container_runtime() -> str:
    for executable_name in ("docker", "podman"):
        if shutil.which(executable_name):
            return executable_name
    raise DockerError("Container runtime CLI not found. Install Docker or Podman and ensure it is on PATH.")


def get_container_runtime_socket_path() -> Path:
    runtime = get_container_runtime()
    if runtime == "docker":
        return HOST_DOCKER_SOCKET_PATH
    return _get_podman_socket_path()


def _get_podman_socket_path() -> Path:
    candidates: list[Path] = []
    xdg_runtime_dir = os.environ.get("XDG_RUNTIME_DIR")
    if xdg_runtime_dir:
        candidates.append(Path(xdg_runtime_dir) / "podman" / "podman.sock")
    if hasattr(os, "getuid"):
        candidates.append(Path(f"/run/user/{os.getuid()}/podman/podman.sock"))
    candidates.append(_PODMAN_ROOTFUL_SOCKET_PATH)
    for candidate in candidates:
        if candidate.exists():
            return candidate
    return candidates[0]
