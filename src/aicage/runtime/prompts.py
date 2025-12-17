import curses
import os
import sys
from dataclasses import dataclass
from typing import Any, List, Sequence

from aicage.errors import CliError

__all__ = ["BaseSelectionRequest", "ensure_tty_for_prompt", "prompt_yes_no", "prompt_for_base"]


@dataclass
class BaseSelectionRequest:
    tool: str
    default_base: str
    available: List[str]


def ensure_tty_for_prompt() -> None:
    if not sys.stdin.isatty():
        raise CliError("Interactive input required but stdin is not a TTY.")


def prompt_yes_no(question: str, default: bool = False) -> bool:
    ensure_tty_for_prompt()
    suffix = "[Y/n]" if default else "[y/N]"
    response = input(f"{question} {suffix} ").strip().lower()
    if not response:
        return default
    return response in {"y", "yes"}


def _supports_arrow_prompt() -> bool:
    return sys.stdin.isatty() and sys.stdout.isatty() and os.environ.get("TERM") not in {None, "", "dumb"}


def _arrow_select(options: Sequence[str], default: str) -> str:
    default_idx = options.index(default) if default in options else 0

    def _ui(stdscr: Any) -> str:
        curses.curs_set(0)
        selected = default_idx
        typed: List[str] = []
        instructions = "Use arrow keys to choose, type to enter a name, Enter to confirm."
        while True:
            stdscr.clear()
            stdscr.addstr(0, 0, instructions)
            for idx, option in enumerate(options):
                prefix = ">" if idx == selected else " "
                suffix = " (default)" if option == default else ""
                stdscr.addstr(idx + 2, 0, f"{prefix} {option}{suffix}")
            manual = "".join(typed)
            stdscr.addstr(len(options) + 3, 0, f"Manual entry: {manual}")
            key = stdscr.get_wch()
            if isinstance(key, str):
                if key in {"\n", "\r"}:
                    return manual.strip() if manual else options[selected]
                if key in {"\b", "\x7f"}:
                    if typed:
                        typed.pop()
                    continue
                if key == "\x1b":  # escape clears typed input and returns default
                    typed.clear()
                    selected = default_idx
                    continue
                if key.isprintable():
                    typed.append(key)
                    continue
            if key == curses.KEY_UP:
                selected = (selected - 1) % len(options)
            elif key == curses.KEY_DOWN:
                selected = (selected + 1) % len(options)

        return default

    return curses.wrapper(_ui)


def prompt_for_base(request: BaseSelectionRequest) -> str:
    ensure_tty_for_prompt()
    if request.available:
        title = f"Select base image for '{request.tool}' (runtime to use inside the container):"
        print(title)
        for idx, base in enumerate(request.available, start=1):
            suffix = " (default)" if base == request.default_base else ""
            print(f"  {idx}) {base}{suffix}")

        if _supports_arrow_prompt():
            try:
                return _arrow_select(request.available, request.default_base)
            except Exception:
                # Fall back to numeric/text input on any terminal/curses issue.
                pass

        prompt = f"Enter number or name [{request.default_base}]: "
    else:
        prompt = (
            f"Select base image for '{request.tool}' (runtime to use inside the container) "
            f"[{request.default_base}]: "
        )

    response = input(prompt).strip()
    if not response:
        choice = request.default_base
    elif response.isdigit() and request.available:
        idx = int(response)
        if idx < 1 or idx > len(request.available):
            raise CliError(f"Invalid choice '{response}'. Pick a number between 1 and {len(request.available)}.")
        choice = request.available[idx - 1]
    else:
        choice = response

    if request.available and choice not in request.available:
        options = ", ".join(request.available)
        raise CliError(f"Invalid base '{choice}'. Valid options: {options}")
    return choice
