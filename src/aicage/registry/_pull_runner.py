from __future__ import annotations

import subprocess
import sys

from aicage._logging import get_logger
from aicage.errors import CliError


def run_pull(image_ref: str) -> None:
    logger = get_logger()
    print(f"[aicage] Pulling image {image_ref}...")
    logger.info("Pulling image %s", image_ref)

    last_nonempty_line = ""
    pull_process = subprocess.Popen(
        ["docker", "pull", image_ref],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
    )
    if pull_process.stdout is not None:
        for line in pull_process.stdout:
            sys.stdout.write(line)
            sys.stdout.flush()
            stripped = line.strip()
            if stripped:
                last_nonempty_line = stripped

    pull_process.wait()

    if pull_process.returncode == 0:
        logger.info("Image pull succeeded for %s", image_ref)
        return

    inspect = subprocess.run(
        ["docker", "image", "inspect", image_ref],
        check=False,
        capture_output=True,
        text=True,
    )
    if inspect.returncode == 0:
        msg = last_nonempty_line or f"docker pull failed for {image_ref}"
        print(f"[aicage] Warning: {msg}. Using local image.", file=sys.stderr)
        logger.warning("Pull failed for %s, using local image: %s", image_ref, msg)
        return

    detail = last_nonempty_line or f"docker pull failed for {image_ref}"
    logger.error("Pull failed for %s: %s", image_ref, detail)
    raise CliError(detail)
