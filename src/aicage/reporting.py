import sys
from pathlib import Path
from typing import Protocol


class OperationReporter(Protocol):
    def on_phase_started(self, phase: str, message: str, log_path: Path) -> None: ...

    def on_phase_progress(
        self,
        phase: str,
        status: str,
        current: int | None,
        total: int | None,
    ) -> None: ...

    def on_phase_log(self, phase: str, line: str) -> None: ...

    def on_phase_finished(self, phase: str, message: str) -> None: ...

    def on_phase_failed(self, phase: str, message: str, log_path: Path) -> None: ...


class ConsoleOperationReporter(OperationReporter):
    def on_phase_started(self, phase: str, message: str, log_path: Path) -> None:
        del self, phase
        print(f"[aicage] {message} (logs: {log_path})...", file=sys.stderr)

    def on_phase_progress(
        self,
        phase: str,
        status: str,
        current: int | None,
        total: int | None,
    ) -> None:
        del self, phase, status, current, total

    def on_phase_log(self, phase: str, line: str) -> None:
        del self, phase, line

    def on_phase_finished(self, phase: str, message: str) -> None:
        del self, phase, message

    def on_phase_failed(self, phase: str, message: str, log_path: Path) -> None:
        del self, phase, message, log_path
