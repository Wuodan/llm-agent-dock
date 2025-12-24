import json
import subprocess
import sys
from typing import Any

from aicage.config.context import ConfigContext
from aicage.errors import CliError
from aicage.runtime.prompts import BaseSelectionRequest, prompt_for_base

from .discovery.catalog import discover_tool_bases

__all__ = ["pull_image", "select_tool_image"]


def _repository_from_ref(image_ref: str) -> str:
    if "@" in image_ref:
        return image_ref.split("@", 1)[0]
    last_colon = image_ref.rfind(":")
    if last_colon > image_ref.rfind("/"):
        return image_ref[:last_colon]
    return image_ref


def _get_local_digest(image_ref: str, repository: str) -> str | None:
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


def _get_remote_digests(image_ref: str) -> set[str] | None:
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

    def collect_digest(entry: Any) -> None:
        if not isinstance(entry, dict):
            return
        descriptor = entry.get("Descriptor")
        if isinstance(descriptor, dict):
            digest = descriptor.get("digest")
            if isinstance(digest, str) and digest:
                digests.add(digest)
        manifest_digest = entry.get("digest")
        if isinstance(manifest_digest, str) and manifest_digest:
            digests.add(manifest_digest)
        config = entry.get("config")
        if isinstance(config, dict):
            config_digest = config.get("digest")
            if isinstance(config_digest, str) and config_digest:
                digests.add(config_digest)
        manifests = entry.get("manifests")
        if isinstance(manifests, list):
            for manifest in manifests:
                collect_digest(manifest)

    if isinstance(payload, list):
        for item in payload:
            collect_digest(item)
    else:
        collect_digest(payload)

    return digests or None


def pull_image(image_ref: str) -> None:
    repository = _repository_from_ref(image_ref)
    local_digest = _get_local_digest(image_ref, repository)
    if local_digest is not None:
        remote_digests = _get_remote_digests(image_ref)
        if remote_digests is not None and local_digest in remote_digests:
            print(f"[aicage] Image {image_ref} is up to date.")
            return

    print(f"[aicage] Pulling image {image_ref}...")

    last_nonempty_line = ""
    line_buffer = ""
    pull_process = subprocess.Popen(
        ["docker", "pull", image_ref],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
    )

    if pull_process.stdout is not None:
        while True:
            chunk = pull_process.stdout.read(1)
            if chunk == "":
                break
            sys.stdout.write(chunk)
            sys.stdout.flush()

            if chunk in ("\n", "\r"):
                stripped = line_buffer.strip()
                if stripped:
                    last_nonempty_line = stripped
                line_buffer = ""
            else:
                line_buffer += chunk

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


def select_tool_image(tool: str, context: ConfigContext) -> str:
    tool_cfg = context.project_cfg.tools.setdefault(tool, {})
    base = tool_cfg.get("base") or context.global_cfg.tools.get(tool, {}).get("base")
    repository_ref = context.image_repository_ref()

    if not base:
        available_bases = discover_tool_bases(context, tool)
        if not available_bases:
            raise CliError(f"No base images found for tool '{tool}' (repository={repository_ref}).")

        request = BaseSelectionRequest(
            tool=tool,
            default_base=context.global_cfg.default_image_base,
            available=available_bases,
        )
        base = prompt_for_base(request)
        tool_cfg["base"] = base
        context.store.save_project(context.project_path, context.project_cfg)

    image_tag = f"{tool}-{base}-latest"
    image_ref = f"{repository_ref}:{image_tag}"
    return image_ref
