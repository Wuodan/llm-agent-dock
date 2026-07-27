from collections.abc import Sequence

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Container, Horizontal, Vertical
from textual.widgets import Button, Checkbox, Header, Static, TextArea

from aicage.registry.image_selection.interaction import ExtensionChoiceOption

from .. import _clipboard
from ._cancelable_screen import CancelableScreen


class ExtensionsScreen(CancelableScreen[list[str] | None]):
    _SAMPLES_CLONE_COMMAND = "git clone https://github.com/aicage/aicage-custom-samples.git $HOME/.aicage-custom"

    BINDINGS = [
        Binding("tab", "focus_next_field", show=False, priority=True),
        Binding("shift+tab", "focus_previous_field", show=False, priority=True),
        Binding("up", "focus_previous_option", "Previous", show=False),
        Binding("down", "focus_next_option", "Next", show=False),
        Binding("enter", "accept", "OK"),
        *CancelableScreen.BINDINGS,
    ]

    def __init__(
        self, options: list[ExtensionChoiceOption], selected: list[str]
    ) -> None:
        super().__init__()
        self._options = options
        self._selected = set(selected)

    def on_mount(self) -> None:
        if not self._options:
            self.query_one("#samples_clone_command", TextArea).focus()
            return
        self._focus_checkbox(0)

    def compose(self) -> ComposeResult:
        yield Container(
            Container(
                Header(show_clock=False, classes="app_header"),
                Static("Choose Extensions", classes="screen_title"),
                Static(self._hint_text(), classes="screen_hint"),
                Vertical(*self._content_widgets(), classes="checkbox_group"),
                Horizontal(*self._action_buttons(), classes="screen_actions"),
                classes="screen_shell",
            ),
            classes="screen_frame",
        )

    def action_accept(self) -> None:
        if not self._options:
            self.action_cancel()
            return
        selected = [
            option.name
            for option in self._options
            if self.query_one(f"#ext-{option.name}", Checkbox).value
        ]
        self.dismiss(selected)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        event.stop()
        if event.button.id == "ok":
            self.action_accept()
        elif event.button.id == "copy_command":
            self._copy_samples_command()
        elif event.button.id == "clear":
            self._clear_checkboxes()
        elif event.button.id == "cancel":
            self.action_cancel()

    def action_focus_previous_option(self) -> None:
        self._move_checkbox_focus(-1)

    def action_focus_next_option(self) -> None:
        self._move_checkbox_focus(1)

    def action_focus_next_field(self) -> None:
        if self._options and isinstance(self.focused, Checkbox):
            self.query_one("#cancel", Button).focus()
            return
        self.focus_next()

    def action_focus_previous_field(self) -> None:
        if self._options and isinstance(self.focused, Checkbox):
            self.query_one("#ok", Button).focus()
            return
        if self._options and isinstance(self.focused, Button):
            self._focus_checkbox(len(self._options) - 1)
            return
        self.focus_previous()

    def _checkboxes(self) -> list[Checkbox]:
        return [
            Checkbox(
                f"{option.name}: {option.description}",
                value=option.name in self._selected,
                id=f"ext-{option.name}",
            )
            for option in self._options
        ]

    def _content_widgets(self) -> Sequence[Checkbox | Static | TextArea]:
        if not self._options:
            return [
                Static("No optional extensions available.", classes="screen_subtitle"),
                Static("Get samples with:", classes="screen_path"),
                TextArea(
                    self._SAMPLES_CLONE_COMMAND,
                    language="bash",
                    soft_wrap=False,
                    read_only=True,
                    show_cursor=False,
                    id="samples_clone_command",
                    classes="command_box",
                ),
            ]
        return self._extension_widgets()

    def _extension_widgets(self) -> list[Checkbox | Static]:
        widgets: list[Checkbox | Static] = []
        shown_dockerfile_heading = False
        for option, checkbox in zip(self._options, self._checkboxes(), strict=False):
            if option.has_dockerfile and not shown_dockerfile_heading:
                widgets.append(
                    Static(
                        "Extensions with custom Dockerfiles:",
                        classes="screen_subtitle",
                    )
                )
                shown_dockerfile_heading = True
            widgets.append(checkbox)
        return widgets

    def _action_buttons(self) -> list[Button]:
        if not self._options:
            return [
                Button("Copy Command", id="copy_command", variant="warning"),
                Button("Back", id="cancel", variant="primary"),
            ]
        return [
            Button("Cancel", id="cancel", variant="default"),
            Button("Clear", id="clear", variant="warning"),
            Button("OK", id="ok", variant="primary"),
        ]

    def _hint_text(self) -> str:
        if not self._options:
            return "Optional extensions are loaded from $HOME/.aicage-custom."
        return "Toggle the optional extensions to include."

    def _copy_samples_command(self) -> None:
        _clipboard.copy_to_clipboard(
            self._SAMPLES_CLONE_COMMAND, self.app.copy_to_clipboard
        )

    @classmethod
    def _copy_to_system_clipboard(cls, text: str) -> bool:
        return _clipboard.copy_to_system_clipboard(text)

    @staticmethod
    def _clipboard_command() -> list[str] | None:
        return _clipboard.clipboard_command()

    def _move_checkbox_focus(self, delta: int) -> None:
        if not self._options:
            return
        current_index = self._focused_checkbox_index()
        next_index = min(max(current_index + delta, 0), len(self._options) - 1)
        self._focus_checkbox(next_index)

    def _clear_checkboxes(self) -> None:
        for option in self._options:
            self.query_one(f"#ext-{option.name}", Checkbox).value = False

    def _focused_checkbox_index(self) -> int:
        focused = self.focused
        if not isinstance(focused, Checkbox):
            return 0
        for index, option in enumerate(self._options):
            if focused.id == f"ext-{option.name}":
                return index
        return 0

    def _focus_checkbox(self, index: int) -> None:
        option = self._options[index]
        self.query_one(f"#ext-{option.name}", Checkbox).focus()
