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
from typing import List

DEFAULT_AGENT_CMDS = {
    "cline": "cline",
    "codex": "codex",
    "factory_ai_droid": "factory_ai_droid",
}


def detect_repo_root() -> pathlib.Path:
    return pathlib.Path(__file__).resolve().parents[2]


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("tool", choices=sorted(DEFAULT_AGENT_CMDS.keys()), help="Tool name")
    parser.add_argument("base", choices=["ubuntu", "act", "universal"], help="Base alias")
    parser.add_argument(
        "--image",
        help=(
            "Override image tag (default ghcr.io/wuodan/llm-agent-dock:<tool>-<base>-latest). "
            "If provided, overrides --repository/--registry/--version"
        ),
    )
    parser.add_argument("--registry", default="ghcr.io", help="Registry host when deriving tag")
    parser.add_argument("--repository", default="wuodan/llm-agent-dock", help="Registry namespace/image")
    parser.add_argument("--version", default="latest", help="Tag suffix in <tool>-<base>-<version>")
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
    return f"{args.registry.rstrip('/')}/{args.repository.strip('/')}:" f"{args.tool}-{args.base}-{args.version}"


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
        fp.write(f"# Agent startup capture\n")
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
    repo_root = detect_repo_root()
    log_dir = args.log_dir or repo_root / "doc/ai/tasks/T003_intensive-startup-tests/plan/logs"
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
