import os

from aicage._logging import get_logger
from aicage.runtime._errors import RuntimeExecutionError

from ._tty import ensure_tty_for_prompt
from .mode import assume_yes_enabled


def _prompt_yes_no(question: str, default: bool = False) -> bool:
    if assume_yes_enabled():
        get_logger().info("Prompt yes/no '%s' -> %s (assume-yes)", question, default)
        return default
    ensure_tty_for_prompt()
    suffix = "[Y/n]" if default else "[y/N]"
    response = input(f"{question} {suffix} ").strip().lower()
    if not response:
        choice = default
    else:
        choice = response in {"y", "yes"}
    get_logger().info("Prompt yes/no '%s' -> %s", question, choice)
    return choice


def prompt_persist_docker_socket() -> bool:
    if os.name == "nt":
        print(
            "Info: You must enable 'Expose daemon on tcp://localhost:2375 without TLS' "
            "in Docker Desktop settings to use --docker on Windows."
    )
    return _prompt_yes_no("Persist mounting the Docker socket for this project?", default=True)


def prompt_mount_git_support(
    git_items: list[tuple[str, str]],
    extension_items: list[tuple[str, str]],
) -> list[str]:
    items = [*git_items, *extension_items]
    if assume_yes_enabled():
        selected_keys = [item[0] for item in items]
        get_logger().info("Prompt git support mounts selected -> %s (assume-yes)", selected_keys)
        return selected_keys
    ensure_tty_for_prompt()
    logger = get_logger()
    if git_items:
        print("Enable Git support in the container by mounting:")
        for idx, (_, description) in enumerate(git_items, start=1):
            print(f"  {idx}) {description}")
    if extension_items:
        print("Mounts from extensions:")
        for idx, (_, description) in enumerate(extension_items, start=len(git_items) + 1):
            print(f"  {idx}) {description}")
    response = input("Select mounts (comma-separated numbers) [all, default on Enter]: ").strip()
    if not response:
        selected = set(range(1, len(items) + 1))
    else:
        selected = _parse_number_selection(response, len(items))
    selected_keys = [items[idx - 1][0] for idx in sorted(selected)]
    logger.info("Prompt git support mounts selected -> %s", selected_keys)
    return selected_keys


def _parse_number_selection(response: str, max_value: int) -> set[int]:
    selected: set[int] = set()
    tokens = [item.strip() for item in response.split(",") if item.strip()]
    if not tokens:
        raise RuntimeExecutionError("Invalid selection ''. Provide comma-separated numbers, e.g. 1,2.")
    for token in tokens:
        if not token.isdigit():
            raise RuntimeExecutionError(f"Invalid selection '{token}'. Use numbers between 1 and {max_value}.")
        value = int(token)
        if value < 1 or value > max_value:
            raise RuntimeExecutionError(
                f"Invalid selection '{token}'. Pick a number between 1 and {max_value}."
            )
        if value in selected:
            raise RuntimeExecutionError(f"Duplicate selection '{token}' is not allowed.")
        selected.add(value)
    return selected


def prompt_persist_docker_args(new_args: str, existing_args: str | None) -> bool:
    if existing_args:
        question = f"Persist docker run args '{new_args}' for this project (replacing '{existing_args}')?"
    else:
        question = f"Persist docker run args '{new_args}' for this project?"
    return _prompt_yes_no(question, default=True)


def prompt_persist_shares(new_shares: list[str], existing_shares: list[str]) -> bool:
    new_values = ", ".join(new_shares)
    if existing_shares:
        question = (
            "Persist share mounts "
            f"'{new_values}' for this project (adding to {len(existing_shares)} existing share(s))?"
        )
    else:
        question = f"Persist share mounts '{new_values}' for this project?"
    return _prompt_yes_no(question, default=True)


def prompt_update_aicage(installed_version: str, latest_version: str) -> bool:
    question = (
        "A newer version of aicage is available "
        f"(installed: {installed_version}, latest: {latest_version}). "
        "Update now?"
    )
    return _prompt_yes_no(question, default=True)
