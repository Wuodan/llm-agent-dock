import argparse
import sys
from collections.abc import Sequence

from aicage import __version__
from aicage._logging import get_logger
from aicage.cli._errors import CliError
from aicage.cli_types import ParsedArgs

_MIN_REMAINING_WITH_AGENT = 2
_MAX_CONFIG_TOKENS = 2
_CONFIG_ACTION_ALIASES: dict[str, str] = {
    "print": "info",
}
_VALID_CONFIG_ACTIONS: set[str] = {"info", "remove"}


def parse_cli(argv: Sequence[str]) -> ParsedArgs:
    """
    Returns parsed CLI args.
    Docker args are captured as an opaque string; precedence is resolved later.
    """
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("--dry-run", action="store_true", help="Print container run command without executing.")
    parser.add_argument("-y", "--yes", action="store_true", help="Use defaults for all prompts.")
    parser.add_argument("--docker", action="store_true", help="Mount the host container runtime socket.")
    parser.add_argument(
        "--share",
        action="append",
        default=[],
        help="Mount a host directory into the container (repeatable).",
    )
    parser.add_argument(
        "--config",
        nargs="+",
        help="Perform config actions such as 'info' or 'remove [agent]'.",
    )
    parser.add_argument("-h", "--help", action="store_true", help="Show help message and exit.")
    pre_argv, post_argv = _split_argv(argv)

    opts: argparse.Namespace
    remaining: list[str]
    if len(pre_argv) == 1 and pre_argv[0] in ("-v", "--version") and post_argv is None:
        print(__version__)
        get_logger().info("Displayed CLI version.")
        sys.exit(0)

    opts, remaining = parser.parse_known_args(pre_argv)

    if opts.help:
        usage: str = (
            "Usage:\n"
            "  aicage <agent>\n"
            "  aicage [--dry-run] [--docker] [--share <path>...] <agent> [<agent-args>]\n"
            "  aicage [--dry-run] [--docker] [--share <path>...] <docker-args> -- <agent> [<agent-args>]\n"
            "  aicage -y [--dry-run] [--docker] [--share <path>...] <agent> [<agent-args>]\n"
            "  aicage --config info\n"
            "  aicage --config remove [<agent>]\n"
            "  aicage --version\n\n"
            "Arguments:\n"
            "  --dry-run        Print the generated container run command and exit.\n"
            "  -y, --yes        Use default answers for all prompts.\n"
            "  --docker         Mount the host container runtime socket into the container.\n"
            "  --share <path>   Mount a host path into the container. Repeatable.\n"
            "  --config <cmd>   Run config command: info, remove [agent].\n"
            "  -v, --version    Print aicage version and exit.\n"
            "  -h, --help       Show this help and exit.\n\n"
            "Behavior:\n"
            "  - <docker-args> are forwarded verbatim to the selected container runtime.\n"
            "  - If docker args are present, use '--' before <agent>.\n"
            "  - <agent-args> are forwarded verbatim to the agent.\n"
        )
        print(usage)
        get_logger().info("Displayed CLI usage help.")
        sys.exit(0)

    if opts.config:
        config_tokens: list[str] = opts.config
        config_action, config_agent = _validate_config_action(config_tokens, opts, remaining, post_argv)
        return ParsedArgs(
            opts.dry_run,
            "",
            "",
            [],
            opts.docker,
            opts.share,
            config_action,
            config_agent,
            opts.yes,
        )

    docker_args, agent, agent_args = _parse_agent_section(remaining, post_argv)

    if not agent:
        raise CliError("Agent name is required.")

    return ParsedArgs(
        opts.dry_run,
        docker_args,
        agent,
        agent_args,
        opts.docker,
        opts.share,
        None,
        None,
        opts.yes,
    )


def _split_argv(argv: Sequence[str]) -> tuple[list[str], list[str] | None]:
    if "--" not in argv:
        return list(argv), None
    sep_index = argv.index("--")
    pre_argv = list(argv[:sep_index])
    post_argv = list(argv[sep_index + 1 :])
    return pre_argv, post_argv


def _normalize_config_action(action: str) -> str:
    return _CONFIG_ACTION_ALIASES.get(action, action)


def _validate_config_action(
    config_tokens: list[str],
    opts: argparse.Namespace,
    remaining: list[str],
    post_argv: list[str] | None,
) -> tuple[str, str | None]:
    if len(config_tokens) > _MAX_CONFIG_TOKENS:
        raise CliError("Too many values for --config. Use '--config remove [agent]'.")
    raw_action = config_tokens[0]
    config_action = _normalize_config_action(raw_action)
    if config_action not in _VALID_CONFIG_ACTIONS:
        raise CliError(f"Unknown config action: {raw_action}")
    config_agent = config_tokens[1] if len(config_tokens) == _MAX_CONFIG_TOKENS else None
    if config_action == "info" and config_agent is not None:
        raise CliError("No agent value is allowed with '--config info'.")
    if remaining or post_argv or opts.docker or opts.dry_run or opts.share or opts.yes:
        raise CliError("No additional arguments are allowed with --config.")
    return config_action, config_agent


def _parse_agent_section(
    remaining: list[str],
    post_argv: list[str] | None,
) -> tuple[str, str, list[str]]:
    if post_argv is not None:
        if not post_argv:
            raise CliError("Missing agent after '--'.")
        docker_args = " ".join(remaining).strip()
        return docker_args, post_argv[0], post_argv[1:]
    if not remaining:
        raise CliError("Missing arguments. Provide an agent name (and optional docker args).")
    first: str = remaining[0]
    if first.startswith("-") or "=" in first:
        raise CliError("Docker args require '--' before the agent.")
    return "", first, remaining[1:]
