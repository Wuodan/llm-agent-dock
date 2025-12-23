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
    pre_argv, post_argv = _split_argv(argv)

    opts: argparse.Namespace
    remaining: list[str]
    opts, remaining = parser.parse_known_args(pre_argv)

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
        _validate_config_action(opts, remaining, post_argv)
        return ParsedArgs(
            opts.dry_run,
            "",
            "",
            [],
            opts.entrypoint,
            opts.docker,
            opts.config,
        )

    docker_args, tool, tool_args = _parse_tool_section(remaining, post_argv)

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


def _split_argv(argv: Sequence[str]) -> tuple[list[str], list[str] | None]:
    if "--" not in argv:
        return list(argv), None
    sep_index = argv.index("--")
    pre_argv = list(argv[:sep_index])
    post_argv = list(argv[sep_index + 1 :])
    return pre_argv, post_argv


def _validate_config_action(
    opts: argparse.Namespace,
    remaining: list[str],
    post_argv: list[str] | None,
) -> None:
    if opts.config != "print":
        raise CliError(f"Unknown config action: {opts.config}")
    if remaining or post_argv or opts.entrypoint or opts.docker or opts.dry_run:
        raise CliError("No additional arguments are allowed with --config.")


def _parse_tool_section(
    remaining: list[str],
    post_argv: list[str] | None,
) -> tuple[str, str, list[str]]:
    if post_argv is not None:
        if not post_argv:
            raise CliError("Missing tool after '--'.")
        docker_args = " ".join(remaining).strip()
        return docker_args, post_argv[0], post_argv[1:]
    if not remaining:
        raise CliError("Missing arguments. Provide a tool name (and optional docker args).")
    first: str = remaining[0]
    if len(remaining) >= MIN_REMAINING_FOR_DOCKER_ARGS and (first.startswith("-") or "=" in first):
        return first, remaining[1], remaining[2:]
    return "", first, remaining[1:]
