from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Container, Horizontal
from textual.widgets import Button, Header, Static

from ._cancelable_screen import CancelableScreen


class ImageUpdateConfirmScreen(CancelableScreen[bool | None]):
    BINDINGS = [
        Binding("escape", "cancel", "Cancel"),
    ]

    def __init__(self, image_ref: str) -> None:
        super().__init__()
        self._image_ref = image_ref

    def compose(self) -> ComposeResult:
        yield Container(
            Container(
                Header(show_clock=False, classes="app_header"),
                Static("Update Image", classes="screen_title"),
                Static(
                    f"A newer version of Docker image '{self._image_ref}' is available.",
                    classes="screen_hint",
                ),
                Static(
                    "Choose whether to pull the newer image or keep the local image.",
                    classes="screen_hint",
                ),
                Horizontal(
                    Button("Keep local", id="keep_local", variant="default"),
                    Button("Pull newer", id="pull_newer", variant="primary"),
                    classes="screen_actions",
                ),
                classes="confirm_shell",
            ),
            classes="screen_frame",
        )

    def on_mount(self) -> None:
        self.query_one("#pull_newer", Button).focus()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        event.stop()
        if event.button.id == "pull_newer":
            self.dismiss(True)
        elif event.button.id == "keep_local":
            self.dismiss(False)
