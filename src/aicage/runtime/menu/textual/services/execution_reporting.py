from collections.abc import Callable
from pathlib import Path

from aicage.reporting import OperationReporter
from aicage.runtime.menu.textual.views.execution_screen import ExecutionScreen


class ExecutionReporter(OperationReporter):
    def __init__(self) -> None:
        self._screen: ExecutionScreen | None = None

    def attach_screen(self, screen: ExecutionScreen) -> None:
        self._screen = screen

    def on_phase_started(self, phase: str, message: str, log_path: Path) -> None:
        screen = self._screen_or_raise()
        self._dispatch(screen.show_phase_started, phase, message, log_path)

    def on_phase_progress(
        self,
        phase: str,
        status: str,
        current: int | None,
        total: int | None,
    ) -> None:
        screen = self._screen_or_raise()
        self._dispatch(screen.show_phase_progress, phase, status, current, total)

    def on_phase_log(self, phase: str, line: str) -> None:
        screen = self._screen_or_raise()
        self._dispatch(screen.show_phase_log, phase, line)

    def on_phase_finished(self, phase: str, message: str) -> None:
        screen = self._screen_or_raise()
        self._dispatch(screen.show_phase_finished, phase, message)

    def on_phase_failed(self, phase: str, message: str, log_path: Path) -> None:
        screen = self._screen_or_raise()
        self._dispatch(screen.show_phase_failed, phase, message, log_path)

    def _dispatch(self, callback: Callable[..., None], *args: object) -> None:
        screen = self._screen_or_raise()
        try:
            app = screen.app
        except AttributeError:
            callback(*args)
            return
        try:
            app.call_from_thread(callback, *args)
        except RuntimeError:
            callback(*args)

    def _screen_or_raise(self) -> ExecutionScreen:
        if self._screen is None:
            raise RuntimeError("ExecutionReporter used before attach_screen().")
        return self._screen
