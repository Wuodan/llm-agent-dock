import argparse
import sys
from collections.abc import Sequence

from aicage import __version__
from aicage._logging import get_logger
from aicage.cli._errors import CliError
from aicage.cli_types import ParsedArgs
from aicage.config.agent.loader import load_agents
from aicage.config.base.loader import load_bases
from aicage.config.errors import ConfigError

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
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print docker run command without executing.",
    )
    parser.add_argument(
        "--menu",
        choices=["ui", "simple", "none"],
        default="ui",
        help="Select menu mode: ui, simple, or none.",
    )
    parser.add_argument(
        "--stdio",
        action="store_true",
        help="Run without Docker TTY allocation for SDK/protocol use.",
    )
    parser.add_argument(
        "--docker",
        action="store_true",
        help="Mount the host Docker socket into the container.",
    )
    parser.add_argument(
        "--share",
        action="append",
        default=[],
        help="Mount a host directory into the container (repeatable).",
    )
    parser.add_argument(
        "--config",
        nargs="*",
        help="Perform config actions such as the default info or 'remove [agent]'.",
    )
    parser.add_argument(
        "-h", "--help", action="store_true", help="Show help message and exit."
    )
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
            "  aicage [--menu <mode>] [--dry-run] [--docker] [--share <path>...] <agent> [<agent-args>]\n"
            "  aicage [--stdio] [--menu <mode>] [--dry-run] [--docker] [--share <path>...] <agent> [<agent-args>]\n"
            "  aicage [--menu <mode>] [--dry-run] [--docker] [--share <path>...] <docker-args> -- <agent>"
            " [<agent-args>]\n"
            "  aicage --config\n"
            "  aicage --config info\n"
            "  aicage --config remove [<agent>]\n"
            "  aicage --version\n\n"
            "Arguments:\n"
            "  --dry-run        Print the generated docker run command and exit.\n"
            "  --menu <mode>    Choose menu mode: ui (default), simple, or none.\n"
            "  --stdio          Disable Docker TTY allocation for SDK/protocol use.\n"
            "  --docker         Mount /run/docker.sock into the container.\n"
            "  --share <path>   Mount a host path into the container. Repeatable.\n"
            "  --config [<cmd>] Run config command: default info, or remove [agent].\n"
            "  -v, --version    Print aicage version and exit.\n"
            "  -h, --help       Show this help and exit.\n\n"
            "Behavior:\n"
            "  - '--menu ui' uses the default config overview.\n"
            "  - '--menu simple' uses the line-based setup prompts.\n"
            "  - '--menu none' skips menus and uses defaults.\n"
            "  - '--stdio' uses 'docker run -i' instead of 'docker run -it'.\n"
            "  - <docker-args> are forwarded verbatim to docker run.\n"
            "  - If docker args are present, use '--' before <agent>.\n"
            "  - <agent-args> are forwarded verbatim to the agent.\n"
        )
        print(usage)
        get_logger().info("Displayed CLI usage help.")
        sys.exit(0)

    if opts.config is not None:
        config_tokens: list[str] = opts.config
        config_action, config_agent = _validate_config_action(
            config_tokens, opts, remaining, post_argv
        )
        return ParsedArgs(
            opts.dry_run,
            "",
            "",
            [],
            opts.docker,
            opts.share,
            config_action,
            config_agent,
            opts.menu,
            opts.stdio,
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
        opts.menu,
        opts.stdio,
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
    if not config_tokens:
        config_tokens = ["info"]
    if len(config_tokens) > _MAX_CONFIG_TOKENS:
        raise CliError("Too many values for --config. Use '--config remove [agent]'.")
    raw_action = config_tokens[0]
    config_action = _normalize_config_action(raw_action)
    if config_action not in _VALID_CONFIG_ACTIONS:
        raise CliError(f"Unknown config action: {raw_action}")
    config_agent = (
        config_tokens[1] if len(config_tokens) == _MAX_CONFIG_TOKENS else None
    )
    if config_action == "info" and config_agent is not None:
        raise CliError("No agent value is allowed with '--config info'.")
    if (
        remaining
        or post_argv
        or opts.docker
        or opts.dry_run
        or opts.share
        or opts.menu != "ui"
        or opts.stdio
    ):
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
        raise CliError(_missing_agent_message())
    first: str = remaining[0]
    if first.startswith("-") or "=" in first:
        raise CliError("Docker args require '--' before the agent.")
    return "", first, remaining[1:]


def _missing_agent_message() -> str:
    message = "Missing argument. Provide an agent name."
    available_agents = _available_agents()
    if not available_agents:
        return message
    agent_list = ", ".join(available_agents)
    return f"{message} Available agents: {agent_list}."


def _available_agents() -> list[str]:
    try:
        return sorted(load_agents(load_bases()))
    except ConfigError:
        return []
