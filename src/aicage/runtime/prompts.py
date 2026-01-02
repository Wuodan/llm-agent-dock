import sys
from dataclasses import dataclass

from aicage._logging import get_logger
from aicage.config.context import ConfigContext
from aicage.errors import CliError
from aicage.registry.images_metadata.models import AgentMetadata

__all__ = ["BaseSelectionRequest", "ensure_tty_for_prompt", "prompt_yes_no", "prompt_for_base"]

@dataclass(frozen=True)
class BaseSelectionRequest:
    agent: str
    context: ConfigContext
    agent_metadata: AgentMetadata


def ensure_tty_for_prompt() -> None:
    if not sys.stdin.isatty():
        raise CliError("Interactive input required but stdin is not a TTY.")


def prompt_yes_no(question: str, default: bool = False) -> bool:
    ensure_tty_for_prompt()
    suffix = "[Y/n]" if default else "[y/N]"
    response = input(f"{question} {suffix} ").strip().lower()
    if not response:
        choice = default
    else:
        choice = response in {"y", "yes"}
    get_logger().info("Prompt yes/no '%s' -> %s", question, choice)
    return choice


def prompt_for_base(request: BaseSelectionRequest) -> str:
    ensure_tty_for_prompt()
    logger = get_logger()
    title = f"Select base image for '{request.agent}' (runtime to use inside the container):"
    bases = _base_options(request.context, request.agent_metadata)

    if bases:
        print(title)
        for idx, option in enumerate(bases, start=1):
            suffix = " (default)" if option.base == request.context.global_cfg.default_image_base else ""
            print(f"  {idx}) {option.base}: {option.description}{suffix}")
        prompt = f"Enter number or name [{request.context.global_cfg.default_image_base}]: "
    else:
        prompt = f"{title} [{request.context.global_cfg.default_image_base}]: "

    response = input(prompt).strip()
    if not response:
        choice = request.context.global_cfg.default_image_base
    elif response.isdigit() and bases:
        idx = int(response)
        if idx < 1 or idx > len(bases):
            raise CliError(f"Invalid choice '{response}'. Pick a number between 1 and {len(bases)}.")
        choice = bases[idx - 1].base
    else:
        choice = response

    if bases and choice not in _available_bases(bases):
        options = ", ".join(_available_bases(bases))
        raise CliError(f"Invalid base '{choice}'. Valid options: {options}")
    logger.info("Selected base '%s' for agent '%s'", choice, request.agent)
    return choice


@dataclass(frozen=True)
class _BaseOption:
    base: str
    description: str


def _base_options(context: ConfigContext, agent_metadata: AgentMetadata) -> list[_BaseOption]:
    return [
        _BaseOption(
            base=base,
            description=context.images_metadata.bases[base].base_image_description,
        )
        for base in sorted(agent_metadata.valid_bases)
    ]


def _available_bases(options: list[_BaseOption]) -> list[str]:
    return [option.base for option in options]
