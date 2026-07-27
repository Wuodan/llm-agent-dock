from dataclasses import dataclass

from aicage.runtime._errors import RuntimeExecutionError

from ._tty import ensure_tty_for_prompt


@dataclass(frozen=True)
class ExtensionOption:
    name: str
    description: str
    has_dockerfile: bool = False


def prompt_for_extensions(options: list[ExtensionOption]) -> list[str]:
    if not options:
        return []
    ensure_tty_for_prompt()
    print(
        "Select extensions to add (comma-separated numbers or names, empty for none):"
    )
    shown_dockerfile_heading = False
    for idx, option in enumerate(options, start=1):
        if option.has_dockerfile and not shown_dockerfile_heading:
            print("  Extensions with custom Dockerfiles:")
            shown_dockerfile_heading = True
        print(f"  {idx}) {option.name}: {option.description}")
    response = input("Enter selection: ").strip()
    if not response:
        return []
    requested = [item.strip() for item in response.split(",") if item.strip()]
    seen: set[str] = set()
    for item in requested:
        extension_id = _resolve_extension_choice(item, options)
        if extension_id in seen:
            raise RuntimeExecutionError(
                f"Duplicate extension '{extension_id}' selected."
            )
        seen.add(extension_id)
    return [option.name for option in options if option.name in seen]


def _resolve_extension_choice(response: str, options: list[ExtensionOption]) -> str:
    if response.isdigit():
        idx = int(response)
        if idx < 1 or idx > len(options):
            raise RuntimeExecutionError(
                f"Invalid selection '{response}'. Pick a number between 1 and {len(options)}."
            )
        return options[idx - 1].name
    for option in options:
        if option.name == response:
            return option.name
    valid = ", ".join(option.name for option in options)
    raise RuntimeExecutionError(
        f"Invalid extension '{response}'. Valid options: {valid}"
    )
