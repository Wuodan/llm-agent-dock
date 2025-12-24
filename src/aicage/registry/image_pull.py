import json
import subprocess
import sys
from dataclasses import dataclass
from typing import Any

from aicage.errors import CliError

__all__ = ["pull_image"]


@dataclass(frozen=True)
class _PullDecision:
    should_pull: bool


def pull_image(image_ref: str) -> None:
    decision = _decide_pull(image_ref)
    if not decision.should_pull:
        return

    _run_pull(image_ref)


def _decide_pull(image_ref: str) -> _PullDecision:
    local_digest = _get_local_repo_digest(image_ref)
    if local_digest is None:
        return _PullDecision(should_pull=True)

    remote_digests = _get_remote_manifest_digests(image_ref)
    if remote_digests is None:
        return _PullDecision(should_pull=False)

    return _PullDecision(should_pull=local_digest not in remote_digests)


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


def _get_local_repo_digest(image_ref: str) -> str | None:
    repository = _repository_from_ref(image_ref)
    inspect = subprocess.run(
        ["docker", "image", "inspect", image_ref, "--format", "{{json .RepoDigests}}"],
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


def _repository_from_ref(image_ref: str) -> str:
    if "@" in image_ref:
        return image_ref.split("@", 1)[0]
    last_colon = image_ref.rfind(":")
    if last_colon > image_ref.rfind("/"):
        return image_ref[:last_colon]
    return image_ref


def _get_remote_manifest_digests(image_ref: str) -> set[str] | None:
    inspect = subprocess.run(
        ["docker", "manifest", "inspect", "--verbose", image_ref],
        check=False,
        capture_output=True,
        text=True,
    )
    if inspect.returncode != 0:
        return None

    try:
        payload: Any = json.loads(inspect.stdout)
    except json.JSONDecodeError:
        return None

    digests: set[str] = set()
    _collect_manifest_digests(payload, digests)
    return digests or None


def _collect_manifest_digests(payload: Any, digests: set[str]) -> None:
    if isinstance(payload, list):
        for item in payload:
            _collect_manifest_digests(item, digests)
        return

    if not isinstance(payload, dict):
        return

    descriptor = payload.get("Descriptor")
    if isinstance(descriptor, dict):
        digest = descriptor.get("digest")
        if isinstance(digest, str) and digest:
            digests.add(digest)

    manifest_digest = payload.get("digest")
    if isinstance(manifest_digest, str) and manifest_digest:
        digests.add(manifest_digest)

    config = payload.get("config")
    if isinstance(config, dict):
        config_digest = config.get("digest")
        if isinstance(config_digest, str) and config_digest:
            digests.add(config_digest)

    manifests = payload.get("manifests")
    if isinstance(manifests, list):
        for manifest in manifests:
            _collect_manifest_digests(manifest, digests)
