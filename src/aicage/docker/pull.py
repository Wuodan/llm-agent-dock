import subprocess
from pathlib import Path

from aicage._logging import get_logger
from aicage.docker.cli import run_docker_command
from aicage.docker.errors import DockerError
from aicage.docker.runtime import get_container_runtime


def run_pull(image_ref: str, log_path: Path) -> None:
    logger = get_logger()
    log_path.parent.mkdir(parents=True, exist_ok=True)
    print(f"[aicage] Pulling image {image_ref} (logs: {log_path})...")
    logger.info("Pulling image %s (logs: %s)", image_ref, log_path)

    runtime = get_container_runtime()
    with log_path.open("w", encoding="utf-8") as log_handle:
        result = run_docker_command(
            [runtime, "pull", image_ref],
            check=False,
            stdout=log_handle,
            stderr=subprocess.STDOUT,
        )
    if result.returncode != 0:
        raise DockerError(f"Image pull failed for {image_ref}. See log at {log_path}.")

    logger.info("Image pull succeeded for %s", image_ref)
