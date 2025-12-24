import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

from aicage.config.context import ConfigContext
from aicage.errors import CliError
from aicage.runtime.prompts import BaseSelectionRequest, prompt_for_base

from .discovery.catalog import discover_tool_bases

__all__ = ["pull_image", "select_tool_image"]


def pull_image(image_ref: str) -> None:
    log_dir = Path("/tmp/aicage/log/image-pull")
    log_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
    safe_ref = image_ref.replace("/", "_").replace(":", "_").replace("@", "_")
    log_path = log_dir / f"{safe_ref}-{timestamp}.log"

    print(f"[aicage] Pulling image {image_ref}...")
    print(f"[aicage] Writing docker pull output to {log_path}")

    last_nonempty_line = ""
    line_buffer = ""

    with log_path.open("w", encoding="utf-8") as log_file:
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
                log_file.write(chunk)
                log_file.flush()

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
        print(f"[aicage] Docker pull output saved to {log_path}", file=sys.stderr)
        return

    detail = last_nonempty_line or f"docker pull failed for {image_ref}"
    raise CliError(f"{detail}. See {log_path}")


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
