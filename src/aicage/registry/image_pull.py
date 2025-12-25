from __future__ import annotations

import subprocess
import sys
from dataclasses import dataclass

from aicage.config.runtime_config import RunConfig
from aicage.errors import CliError
from aicage.registry import _local_query, _remote_query

__all__ = ["pull_image"]


@dataclass(frozen=True)
class _PullDecision:
    should_pull: bool


def pull_image(run_config: RunConfig) -> None:
    decision = _decide_pull(run_config)
    if not decision.should_pull:
        return

    _run_pull(run_config.image_ref)


def _decide_pull(run_config: RunConfig) -> _PullDecision:
    local_digest = _local_query.get_local_repo_digest(run_config)
    if local_digest is None:
        return _PullDecision(should_pull=True)

    remote_digest = _remote_query.get_remote_repo_digest(run_config)
    if remote_digest is None:
        return _PullDecision(should_pull=False)

    return _PullDecision(should_pull=local_digest != remote_digest)


def _run_pull(image_ref: str) -> None:
    print(f"[aicage] Pulling image {image_ref}...")

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
        return

    detail = last_nonempty_line or f"docker pull failed for {image_ref}"
    raise CliError(detail)
