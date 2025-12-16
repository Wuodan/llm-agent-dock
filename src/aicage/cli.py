import argparse
import os
import shlex
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Sequence, Tuple

from aicage.config import ConfigError, SettingsStore
from aicage.config.global_config import GlobalConfig
from aicage.config.project_config import ProjectConfig
from aicage.discovery import DiscoveryError, discover_base_aliases
from aicage.errors import CliError
from aicage.runtime.auth.mounts import (
    build_auth_mounts,
    load_mount_preferences,
    store_mount_preferences,
)
from aicage.runtime.auth.prompts import ensure_tty_for_prompt
from aicage.runtime.run_args import DockerRunArgs, assemble_docker_run, merge_docker_args

TOOL_MOUNT_CONTAINER = Path("/aicage/tool-config")


@dataclass
class ParsedArgs:
    dry_run: bool
    docker_args: str
    tool: str
    tool_args: List[str]


@dataclass
class ConfigContext:
    store: SettingsStore
    project_path: Path
    project_cfg: ProjectConfig
    global_cfg: GlobalConfig


def parse_cli(argv: Sequence[str]) -> ParsedArgs:
    """
    Returns parsed CLI args.
    Docker args are a single opaque string; precedence is resolved later.
    """
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("--dry-run", action="store_true", help="Print docker run command without executing.")
    parser.add_argument("-h", "--help", action="store_true", help="Show help message and exit.")
    opts, remaining = parser.parse_known_args(argv)

    if opts.help:
        usage = (
            "Usage:\n"
            "  aicage [--dry-run] [<docker-args>] <tool> [-- <tool-args>]\n"
            "  aicage [--dry-run] [<docker-args>] -- <tool> <tool-args>\n\n"
            "<docker-args> is a single string of docker run flags (optional).\n"
            "<tool-args> are passed verbatim to the tool.\n"
        )
        print(usage)
        sys.exit(0)

    if not remaining:
        raise CliError("Missing arguments. Provide a tool name (and optional docker args).")

    docker_args = ""

    if "--" in remaining:
        sep_index = remaining.index("--")
        pre = remaining[:sep_index]
        post = remaining[sep_index + 1 :]
        if not post:
            raise CliError("Missing tool after '--'.")
        docker_args = " ".join(pre).strip()
        tool = post[0]
        tool_args = post[1:]
    else:
        first = remaining[0]
        if len(remaining) >= 2 and (first.startswith("-") or "=" in first):
            docker_args = first
            tool = remaining[1]
            tool_args = remaining[2:]
        else:
            tool = first
            tool_args = remaining[1:]

    if not tool:
        raise CliError("Tool name is required.")

    return ParsedArgs(opts.dry_run, docker_args, tool, tool_args)


def prompt_for_base(tool: str, default_base: str, available: List[str]) -> str:
    ensure_tty_for_prompt()
    choices = ", ".join(available) if available else "none discovered"
    prompt = f"Select base image for '{tool}' [{default_base}] (options: {choices}): "
    response = input(prompt).strip()
    choice = response or default_base
    if available and choice not in available:
        raise CliError(f"Invalid base '{choice}'. Valid options: {choices}")
    return choice


def discover_available_bases(repository: str, tool: str) -> List[str]:
    remote_bases: List[str] = []
    local_bases: List[str] = []
    try:
        remote_bases = discover_base_aliases(repository, tool)
    except DiscoveryError as exc:
        print(f"[aicage] Warning: {exc}. Continuing with local images.", file=sys.stderr)
    try:
        local_bases = discover_local_bases(repository, tool)
    except CliError as exc:
        print(f"[aicage] Warning: {exc}", file=sys.stderr)
    return sorted(set(remote_bases) | set(local_bases))


def build_config_context() -> ConfigContext:
    store = SettingsStore()
    project_path = Path.cwd().resolve()
    global_cfg = store.load_global()
    project_cfg = store.load_project(project_path)
    return ConfigContext(store=store, project_path=project_path, project_cfg=project_cfg, global_cfg=global_cfg)


def resolve_base(tool: str, tool_cfg: Dict[str, Any], context: ConfigContext) -> Tuple[str, bool]:
    base = tool_cfg.get("base") or context.global_cfg.tools.get(tool, {}).get("base")
    if base:
        return base, False

    available_bases = discover_available_bases(context.global_cfg.repository, tool)
    if not available_bases:
        raise CliError(f"No base images found for tool '{tool}' (repository={context.global_cfg.repository}).")

    base = prompt_for_base(tool, context.global_cfg.default_base, available_bases)
    tool_cfg["base"] = base
    return base, True


def read_tool_label(image_ref: str, label: str) -> str:
    try:
        result = subprocess.run(
            ["docker", "inspect", image_ref, "--format", f'{{{{ index .Config.Labels "{label}" }}}}'],
            check=True,
            capture_output=True,
            text=True,
        )
    except subprocess.CalledProcessError as exc:
        raise CliError(f"Failed to inspect image {image_ref}: {exc.stderr.strip() or exc}") from exc
    value = result.stdout.strip()
    if not value:
        raise CliError(f"Label '{label}' not found on image {image_ref}.")
    return value


def pull_image(image_ref: str) -> None:
    pull_result = subprocess.run(["docker", "pull", image_ref], capture_output=True, text=True)
    if pull_result.returncode == 0:
        return

    inspect = subprocess.run(
        ["docker", "image", "inspect", image_ref],
        capture_output=True,
        text=True,
    )
    if inspect.returncode == 0:
        msg = pull_result.stderr.strip() or f"docker pull failed for {image_ref}"
        print(f"[aicage] Warning: {msg}. Using local image.", file=sys.stderr)
        return

    raise CliError(f"docker pull failed for {image_ref}: {pull_result.stderr.strip() or pull_result.stdout.strip()}")


def discover_local_bases(repository: str, tool: str) -> List[str]:
    """
    Fallback discovery using local images when Docker Hub is unavailable.
    """
    try:
        result = subprocess.run(
            ["docker", "image", "ls", repository, "--format", "{{.Repository}}:{{.Tag}}"],
            check=True,
            capture_output=True,
            text=True,
        )
    except subprocess.CalledProcessError as exc:
        raise CliError(f"Failed to list local images for {repository}: {exc.stderr or exc}") from exc

    aliases: set[str] = set()
    for line in result.stdout.splitlines():
        line = line.strip()
        if not line or line.endswith(":<none>"):
            continue
        if ":" not in line:
            continue
        repo, tag = line.split(":", 1)
        if repo != repository:
            continue
        prefix = f"{tool}-"
        suffix = "-latest"
        if tag.startswith(prefix) and tag.endswith(suffix):
            base = tag[len(prefix) : -len(suffix)]
            if base:
                aliases.add(base)

    return sorted(aliases)


def main(argv: Sequence[str] | None = None) -> int:
    argv = argv if argv is not None else sys.argv[1:]
    try:
        parsed = parse_cli(argv)
        context = build_config_context()
        tool_cfg = context.project_cfg.tools.setdefault(parsed.tool, {})

        base, project_dirty = resolve_base(parsed.tool, tool_cfg, context)
        image_tag = f"{parsed.tool}-{base}-latest"
        image_ref = f"{context.global_cfg.repository}:{image_tag}"

        pull_image(image_ref)
        tool_path_label = read_tool_label(image_ref, "tool_path")
        tool_config_host = Path(os.path.expanduser(tool_path_label)).resolve()
        tool_config_host.mkdir(parents=True, exist_ok=True)

        merged_docker_args = merge_docker_args(
            context.global_cfg.docker_args, context.project_cfg.docker_args, parsed.docker_args
        )

        prefs = load_mount_preferences(tool_cfg)
        auth_mounts, prefs_updated = build_auth_mounts(context.project_path, prefs)
        if prefs_updated:
            store_mount_preferences(tool_cfg, prefs)
        project_dirty = project_dirty or prefs_updated

        run_args = DockerRunArgs(
            image_ref=image_ref,
            project_path=context.project_path,
            tool_config_host=tool_config_host,
            tool_mount_container=TOOL_MOUNT_CONTAINER,
            merged_docker_args=merged_docker_args,
            tool_args=parsed.tool_args,
            tool_path_label=tool_path_label,
            mounts=auth_mounts,
        )

        if project_dirty:
            context.store.save_project(context.project_path, context.project_cfg)

        run_cmd = assemble_docker_run(run_args)

        if parsed.dry_run:
            print(shlex.join(run_cmd))
            return 0

        subprocess.run(run_cmd, check=True)
        return 0
    except KeyboardInterrupt:
        print()
        return 130
    except (CliError, ConfigError, DiscoveryError) as exc:
        print(f"[aicage] {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
