import argparse
import sys
from collections.abc import Sequence

from aicage.cli_types import ParsedArgs
from aicage.errors import CliError

__all__ = ["parse_cli"]

MIN_REMAINING_FOR_DOCKER_ARGS = 2


def parse_cli(argv: Sequence[str]) -> ParsedArgs:
    """
    Returns parsed CLI args.
    Docker args are a single opaque string; precedence is resolved later.
    """
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("--dry-run", action="store_true", help="Print docker run command without executing.")
    parser.add_argument("--entrypoint", help="Override the container entrypoint with a host path.")
    parser.add_argument("--docker", action="store_true", help="Mount the host Docker socket into the container.")
    parser.add_argument("--config", help="Perform config actions such as 'print'.")
    parser.add_argument("-h", "--help", action="store_true", help="Show help message and exit.")
    opts: argparse.Namespace
    remaining: list[str]
    opts, remaining = parser.parse_known_args(argv)

    if opts.help:
        usage: str = (
            "Usage:\n"
            "  aicage [--dry-run] [--docker] [--entrypoint PATH] [<docker-args>] <tool> [-- <tool-args>]\n"
            "  aicage [--dry-run] [--docker] [--entrypoint PATH] [<docker-args>] -- <tool> <tool-args>\n"
            "  aicage --config print\n\n"
            "<docker-args> is a single string of docker run flags (optional).\n"
            "<tool-args> are passed verbatim to the tool.\n"
        )
        print(usage)
        sys.exit(0)

    if opts.config:
        if opts.config != "print":
            raise CliError(f"Unknown config action: {opts.config}")
        if remaining or opts.entrypoint or opts.docker or opts.dry_run:
            raise CliError("No additional arguments are allowed with --config.")
        return ParsedArgs(
            opts.dry_run,
            "",
            "",
            [],
            opts.entrypoint,
            opts.docker,
            opts.config,
        )

    if not remaining:
        raise CliError("Missing arguments. Provide a tool name (and optional docker args).")

    docker_args: str = ""

    if "--" in remaining:
        sep_index: int = remaining.index("--")
        pre: list[str] = remaining[:sep_index]
        post: list[str] = remaining[sep_index + 1 :]
        if not post:
            raise CliError("Missing tool after '--'.")
        docker_args = " ".join(pre).strip()
        tool: str = post[0]
        tool_args: list[str] = post[1:]
    else:
        first: str = remaining[0]
        if len(remaining) >= MIN_REMAINING_FOR_DOCKER_ARGS and (first.startswith("-") or "=" in first):
            docker_args = first
            tool = remaining[1]
            tool_args = remaining[2:]
        else:
            tool = first
            tool_args = remaining[1:]

    if not tool:
        raise CliError("Tool name is required.")

    return ParsedArgs(
        opts.dry_run,
        docker_args,
        tool,
        tool_args,
        opts.entrypoint,
        opts.docker,
        None,
    )
