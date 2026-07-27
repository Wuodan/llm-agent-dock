from textual import work
from textual.app import ComposeResult

from aicage._execution_cleanup import (
    cancel_current_execution_cleanup,
    current_execution_cleanup,
)
from aicage.runtime.menu._interaction_types import ImageSetupOperation

from ._textual_app import TextualApp
from .services.execution_reporting import ExecutionReporter
from .views.execution_screen import ExecutionScreen


class ExecutionApp(TextualApp[BaseException | None]):
    def __init__(self, operation: ImageSetupOperation) -> None:
        super().__init__("container setup")
        self._operation = operation

    def compose(self) -> ComposeResult:
        yield ExecutionScreen()

    def on_mount(self) -> None:
        self._run_execution()

    def action_cancel(self) -> None:
        self.query_one(ExecutionScreen).mark_cancelled()
        cancel_current_execution_cleanup()
        self.exit(KeyboardInterrupt())

    @work(thread=True, exclusive=True)
    def _run_execution(self) -> None:
        reporter = ExecutionReporter(self.query_one(ExecutionScreen))
        error: BaseException | None = None
        try:
            with current_execution_cleanup():
                self._operation(reporter)
        except BaseException as exc:
            error = exc
        self.call_from_thread(self.exit, error)
