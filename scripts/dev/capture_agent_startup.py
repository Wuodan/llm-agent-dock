#!/usr/bin/env python3
"""Capture agent CLI startup output via docker run with async stdout/stderr taps."""
from __future__ import annotations

import argparse
import asyncio
import datetime as dt
import os
import pathlib
import pty
import select
import shlex
import signal
import subprocess
import sys
import time
from typing import Dict, List, Tuple

def detect_repo_root() -> pathlib.Path:
    return pathlib.Path(__file__).resolve().parents[2]


def load_dotenv(env_path: pathlib.Path) -> Dict[str, str]:
    if not env_path.exists():
        return {}
    env: Dict[str, str] = {}
    for raw_line in env_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        env[key.strip()] = value.strip()
    return env


REPO_ROOT = detect_repo_root()
DOTENV_VALUES = load_dotenv(REPO_ROOT / ".env")


def split_list(raw: str) -> List[str]:
    return raw.split()


def load_matrix_settings() -> Tuple[List[str], List[str]]:
    tool_str = DOTENV_VALUES.get("AICAGE_TOOLS") or os.environ.get("AICAGE_TOOLS")
    base_str = DOTENV_VALUES.get("AICAGE_BASES") or os.environ.get("AICAGE_BASES")
    base_alias_str = DOTENV_VALUES.get("AICAGE_BASE_ALIASES") or os.environ.get("AICAGE_BASE_ALIASES")
    if not tool_str or not base_str or not base_alias_str:
        raise RuntimeError("AICAGE_TOOLS, AICAGE_BASES, and AICAGE_BASE_ALIASES must be set in .env or the environment.")
    return split_list(tool_str), split_list(base_str), split_list(base_alias_str)


SUPPORTED_TOOLS, SUPPORTED_BASES, SUPPORTED_BASE_ALIASES = load_matrix_settings()
if len(SUPPORTED_BASES) != len(SUPPORTED_BASE_ALIASES):
    raise RuntimeError("AICAGE_BASES and AICAGE_BASE_ALIASES must have the same length.")
DEFAULT_AGENT_CMDS = {tool: tool for tool in SUPPORTED_TOOLS}


def build_parser() -> argparse.ArgumentParser:
    repository_default = DOTENV_VALUES.get("AICAGE_REPOSITORY") or os.environ.get("AICAGE_REPOSITORY") or "wuodan/aicage"
    version_default = DOTENV_VALUES.get("AICAGE_VERSION") or os.environ.get("AICAGE_VERSION") or "dev"
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("tool", choices=sorted(SUPPORTED_TOOLS), help="Tool name")
    parser.add_argument("base", choices=sorted(SUPPORTED_BASES), help="Base alias")
    parser.add_argument(
        "--image",
        help="Override image tag (default <repo>:<tool>-<base>-<version> from .env). "
        "If provided, overrides --repository/--registry/--version",
    )
    parser.add_argument("--registry", default="", help="Registry host when deriving tag")
    parser.add_argument("--repository", default=repository_default, help="Registry namespace/image")
    parser.add_argument("--version", default=version_default, help="Tag suffix in <tool>-<base>-<version>")
    parser.add_argument("--timeout", type=float, default=20.0, help="Seconds before docker run is terminated")
    parser.add_argument("--log-dir", type=pathlib.Path, help="Directory to store logs (default task plan logs folder)")
    parser.add_argument("--agent-cmd", help="Override command executed inside the container")
    parser.add_argument(
        "--env",
        action="append",
        default=[],
        help="Additional KEY=VALUE env pairs passed to docker run (can be repeated)",
    )
    parser.add_argument(
        "--pty",
        action="store_true",
        help="Allocate a pseudo-TTY for docker run (merges stdout/stderr)",
    )
    parser.add_argument(
        "--script-tty",
        dest="script_tty",
        action="store_true",
        help="Wrap agent command with 'script -q -c', emulating a tty inside the container",
    )
    parser.add_argument(
        "--no-script-tty",
        dest="script_tty",
        action="store_false",
        help="Disable script-based tty shim (default)",
    )
    parser.set_defaults(script_tty=False)
    return parser


def derive_image(args: argparse.Namespace) -> str:
    if args.image:
        return args.image
    registry = args.registry.rstrip("/")
    repo = args.repository.strip("/")
    try:
        base_index = SUPPORTED_BASES.index(args.base)
    except ValueError as exc:
        raise ValueError(f"Base '{args.base}' not found in AICAGE_BASES") from exc
    base_alias = SUPPORTED_BASE_ALIASES[base_index]
    prefix = f"{registry}/" if registry else ""
    return f"{prefix}{repo}:{args.tool}-{base_alias}-{args.version}"


def build_container_command(agent_cmd: str, use_script: bool) -> str:
    if use_script:
        quoted = shlex.quote(agent_cmd)
        return f"script -q -c {quoted} /dev/null"
    return agent_cmd


def build_docker_cmd(args: argparse.Namespace, snippet: str) -> List[str]:
    docker_cmd: List[str] = ["docker", "run", "--rm"]
    if args.pty:
        docker_cmd.append("-t")
    for env_pair in args.env:
        docker_cmd.extend(["--env", sanitize_env(env_pair)])
    docker_cmd.extend([
        "-i",
        derive_image(args),
        "bash",
        "-lc",
        f"set -euo pipefail; {snippet}",
    ])
    return docker_cmd


def sanitize_env(env_pair: str) -> str:
    if "=" not in env_pair:
        raise ValueError(f"Env pair must be KEY=VALUE, got: {env_pair}")
    return env_pair


def log_banner(log_file: pathlib.Path, metadata: dict) -> None:
    log_file.parent.mkdir(parents=True, exist_ok=True)
    with log_file.open("w", encoding="utf-8") as fp:
        fp.write("# Agent startup capture\n")
        for key, value in metadata.items():
            fp.write(f"# {key}: {value}\n")
        fp.write("\n")


def append_line(log_file: pathlib.Path, label: str, data: bytes) -> None:
    text = data.decode(errors="replace")
    with log_file.open("a", encoding="utf-8") as fp:
        fp.write(f"[{label}] {text}")


async def stream_pipe(reader: asyncio.StreamReader, label: str, log_file: pathlib.Path) -> None:
    while True:
        chunk = await reader.readline()
        if not chunk:
            break
        append_line(log_file, label, chunk)
        sys.stdout.write(f"[{label}] {chunk.decode(errors='replace')}")
        sys.stdout.flush()


async def capture(args: argparse.Namespace) -> int:
    log_dir = args.log_dir or REPO_ROOT / "doc/ai/tasks/T003_intensive-startup-tests/plan/logs"
    timestamp = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    log_file = log_dir / f"startup_{args.tool}_{args.base}_{timestamp}.log"
    metadata = {
        "timestamp_utc": timestamp,
        "image": derive_image(args),
        "tool": args.tool,
        "base": args.base,
        "timeout_s": args.timeout,
        "pty": args.pty,
    }
    agent_cmd = args.agent_cmd or DEFAULT_AGENT_CMDS.get(args.tool, args.tool)
    container_snippet = build_container_command(agent_cmd, args.script_tty)
    docker_cmd = build_docker_cmd(args, container_snippet)
    metadata["docker_cmd"] = " ".join(shlex.quote(part) for part in docker_cmd)
    log_banner(log_file, metadata)

    if args.pty:
        exit_code = await asyncio.to_thread(run_with_pty, docker_cmd, log_file, args.timeout)
    else:
        exit_code = await capture_with_pipes(docker_cmd, log_file, args.timeout)

    append_line(log_file, "meta", f"process_exit={exit_code}\n".encode())
    print(f"[capture] Completed with exit code {exit_code}. Log: {log_file}")
    return exit_code


async def capture_with_pipes(docker_cmd: List[str], log_file: pathlib.Path, timeout: float) -> int:
    process = await asyncio.create_subprocess_exec(
        *docker_cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )

    tasks = [
        asyncio.create_task(stream_pipe(process.stdout, "stdout", log_file)),
        asyncio.create_task(stream_pipe(process.stderr, "stderr", log_file)),
    ]

    try:
        await asyncio.wait_for(process.wait(), timeout=timeout)
    except asyncio.TimeoutError:
        sys.stderr.write("[capture] timeout reached; sending SIGINT to docker process\n")
        process.send_signal(signal.SIGINT)
        try:
            await asyncio.wait_for(process.wait(), timeout=5)
        except asyncio.TimeoutError:
            sys.stderr.write("[capture] SIGINT failed, terminating\n")
            process.kill()
            await process.wait()
    finally:
        await asyncio.gather(*tasks, return_exceptions=True)

    return process.returncode


def run_with_pty(docker_cmd: List[str], log_file: pathlib.Path, timeout: float) -> int:
    master_fd, slave_fd = pty.openpty()
    try:
        process = subprocess.Popen(
            docker_cmd,
            stdin=slave_fd,
            stdout=slave_fd,
            stderr=slave_fd,
            close_fds=True,
        )
    finally:
        os.close(slave_fd)

    start = time.monotonic()
    exit_code = None
    try:
        while True:
            if timeout and (time.monotonic() - start) > timeout:
                sys.stderr.write("[capture] timeout reached in PTY mode; sending SIGINT\n")
                process.send_signal(signal.SIGINT)
                timeout = 0
            rlist, _, _ = select.select([master_fd], [], [], 0.1)
            if master_fd in rlist:
                try:
                    data = os.read(master_fd, 1024)
                except OSError:
                    break
                if not data:
                    break
                if b"\x1b[6n" in data:
                    # Respond to Device Status Report requests with home position.
                    os.write(master_fd, b"\x1b[1;1R")
                append_line(log_file, "pty", data)
                sys.stdout.buffer.write(b"[pty] " + data)
                sys.stdout.flush()
            if process.poll() is not None:
                exit_code = process.returncode
                break
        if exit_code is None:
            exit_code = process.wait()
    finally:
        os.close(master_fd)
    return exit_code


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    try:
        return asyncio.run(capture(args))
    except KeyboardInterrupt:
        return 130


if __name__ == "__main__":
    sys.exit(main())
