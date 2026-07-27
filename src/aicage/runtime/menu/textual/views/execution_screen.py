from pathlib import Path

from textual.app import ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.widgets import Button, Header, ProgressBar, RichLog, Static

from .. import _clipboard


class ExecutionScreen(Container):
    def __init__(self) -> None:
        super().__init__(id="execution_root")
        self._cancelled = False
        self._pull_status = ""
        self._build_log_path = ""

    def compose(self) -> ComposeResult:
        yield Container(
            Container(
                Header(show_clock=False, classes="app_header"),
                Static("Container Setup", classes="screen_title"),
                Static("", id="execution_status", classes="screen_hint"),
                ProgressBar(total=None, id="execution_progress"),
                Static("", id="execution_details", classes="screen_path"),
                Vertical(
                    Static(
                        "Target image:", classes="screen_path execution_image_ref_label"
                    ),
                    Static(
                        "",
                        id="execution_image_ref",
                        classes="screen_path execution_image_ref",
                    ),
                    Static("Log path:", classes="screen_path execution_log_path_label"),
                    Horizontal(
                        Button("Copy Log Path", id="copy_log_path", variant="warning"),
                        classes="execution_copy_actions",
                    ),
                    Static(
                        "",
                        id="execution_log_path",
                        classes="screen_path execution_log_path",
                    ),
                    id="execution_build_info",
                ),
                RichLog(
                    id="execution_log",
                    classes="field execution_log",
                    wrap=False,
                    highlight=False,
                ),
                classes="execution_shell",
            ),
            classes="execution_frame",
        )

    def show_phase_started(self, phase: str, message: str, log_path: Path) -> None:
        if self._cancelled:
            return
        if phase == "pull":
            self._pull_status = message
            self._status().update(self._pull_status)
            self._progress().display = True
            self._details().display = True
            self._build_info().display = False
        else:
            status, image_ref = _split_build_message(message)
            self._status().update(status)
            self._build_log_path = str(log_path)
            self._image_ref().update(image_ref)
            self._log_path().update(self._build_log_path)
            self._progress().display = False
            self._details().display = False
            self._build_info().display = True
        self._progress().update(total=None, progress=0)
        self._details().update("")
        self._log().display = phase == "build"
        self._write_log(phase, message)

    def show_phase_progress(
        self,
        phase: str,
        status: str,
        current: int | None,
        total: int | None,
    ) -> None:
        if self._cancelled:
            return
        if phase == "pull":
            self._status().update(self._pull_status)
            self._details().update(status)
        else:
            self._status().update(status)
        self._write_log(phase, status)
        if phase != "pull":
            return
        if total is None:
            self._progress().update(total=None, progress=0)
            return
        self._progress().update(total=total, progress=current or 0)

    def show_phase_log(self, phase: str, line: str) -> None:
        if self._cancelled:
            return
        self._write_log(phase, line)

    def show_phase_finished(self, phase: str, message: str) -> None:
        if self._cancelled:
            return
        self._status().update(f"{_phase_label(phase)}: {message}")
        if phase == "pull":
            self._progress().update(total=1, progress=1)
            self._details().update("")
        self._write_log(phase, message)

    def show_phase_failed(self, phase: str, message: str, log_path: Path) -> None:
        if self._cancelled:
            return
        if phase == "pull":
            self._status().update(
                f"{_phase_label(phase)}: {message} (logs: {log_path})"
            )
            self._details().update("")
        else:
            self._status().update(message)
            self._build_log_path = str(log_path)
            self._log_path().update(self._build_log_path)
            self._build_info().display = True
        self._write_log(phase, message)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        event.stop()
        if event.button.id != "copy_log_path" or not self._build_log_path:
            return
        _clipboard.copy_to_clipboard(self._build_log_path, self.app.copy_to_clipboard)

    def mark_cancelled(self) -> None:
        self._cancelled = True

    def _status(self) -> Static:
        return self.query_one("#execution_status", Static)

    def _progress(self) -> ProgressBar:
        return self.query_one("#execution_progress", ProgressBar)

    def _details(self) -> Static:
        return self.query_one("#execution_details", Static)

    def _build_info(self) -> Vertical:
        return self.query_one("#execution_build_info", Vertical)

    def _image_ref(self) -> Static:
        return self.query_one("#execution_image_ref", Static)

    def _log_path(self) -> Static:
        return self.query_one("#execution_log_path", Static)

    def _log(self) -> RichLog:
        return self.query_one("#execution_log", RichLog)

    def _write_log(self, phase: str, line: str) -> None:
        if phase != "build":
            return
        self._log().write(f"[{phase}] {line}")


def _phase_label(phase: str) -> str:
    return phase.capitalize()


def _split_build_message(message: str) -> tuple[str, str]:
    prefix, separator, image_ref = message.partition(" image ")
    if not separator or not image_ref:
        return message, ""
    return f"{prefix} image", image_ref
