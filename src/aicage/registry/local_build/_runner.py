from __future__ import annotations

import subprocess
from pathlib import Path

from aicage._logging import get_logger
from aicage.config.resources import find_packaged_path
from aicage.config.runtime_config import RunConfig
from aicage.errors import CliError


def run_build(
    run_config: RunConfig,
    base_image_ref: str,
    log_path: Path,
) -> None:
    logger = get_logger()
    log_path.parent.mkdir(parents=True, exist_ok=True)
    print(f"[aicage] Building local image {run_config.image_ref} (logs: {log_path})...")
    logger.info("Building local image %s (logs: %s)", run_config.image_ref, log_path)

    dockerfile_path = find_packaged_path("agent-build/Dockerfile")
    build_root = _build_context_dir(run_config, dockerfile_path)
    command = [
        "docker",
        "build",
        "--no-cache",
        "--file",
        str(dockerfile_path),
        "--build-arg",
        f"BASE_IMAGE={base_image_ref}",
        "--build-arg",
        f"AGENT={run_config.agent}",
        "--tag",
        run_config.image_ref,
        str(build_root),
    ]
    with log_path.open("w", encoding="utf-8") as log_handle:
        result = subprocess.run(command, check=False, stdout=log_handle, stderr=subprocess.STDOUT)
    if result.returncode != 0:
        logger.error("Local image build failed for %s (logs: %s)", run_config.image_ref, log_path)
        raise CliError(
            f"Local image build failed for {run_config.image_ref}. See log at {log_path}."
        )

    logger.info("Local image build succeeded for %s", run_config.image_ref)


def local_image_exists(image_ref: str) -> bool:
    result = subprocess.run(
        ["docker", "image", "inspect", image_ref],
        check=False,
        capture_output=True,
        text=True,
    )
    return result.returncode == 0


def _build_context_dir(run_config: RunConfig, dockerfile_path: Path) -> Path:
    agent_metadata = run_config.images_metadata.agents[run_config.agent]
    local_definition_dir = agent_metadata.local_definition_dir
    if local_definition_dir is None:
        return dockerfile_path.parent
    if local_definition_dir.is_relative_to(dockerfile_path.parent):
        return dockerfile_path.parent
    return local_definition_dir.parent.parent
