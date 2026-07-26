import subprocess
from unittest import TestCase, mock

from aicage import _execution_cleanup


class ExecutionCleanupTests(TestCase):
    def test_add_cleanup_runs_immediately_after_cancel(self) -> None:
        registry = _execution_cleanup._CleanupRegistry()
        cleanup = mock.Mock()

        registry.cancel()
        registry.add_cleanup(cleanup)

        cleanup.assert_called_once_with()

    def test_cancel_runs_registered_cleanups_in_reverse_order(self) -> None:
        registry = _execution_cleanup._CleanupRegistry()
        calls: list[str] = []

        registry.add_cleanup(lambda: calls.append("first"))
        registry.add_cleanup(lambda: calls.append("second"))

        registry.cancel()

        self.assertEqual(["second", "first"], calls)

    def test_current_execution_cleanup_registers_current_scope(self) -> None:
        cleanup = mock.Mock()

        with _execution_cleanup.current_execution_cleanup():
            _execution_cleanup.register_cleanup(cleanup)

        cleanup.assert_not_called()

    def test_cancel_current_execution_cleanup_runs_registered_cleanup(self) -> None:
        cleanup = mock.Mock()

        with _execution_cleanup.current_execution_cleanup():
            _execution_cleanup.register_cleanup(cleanup)
            _execution_cleanup.cancel_current_execution_cleanup()

        cleanup.assert_called_once_with()

    def test_register_cleanup_runs_on_cancel(self) -> None:
        cleanup = mock.Mock()

        with _execution_cleanup.current_execution_cleanup():
            _execution_cleanup.register_cleanup(cleanup)
            _execution_cleanup.cancel_current_execution_cleanup()

        cleanup.assert_called_once_with()

    def test_register_cleanup_outside_scope_does_nothing(self) -> None:
        cleanup = mock.Mock()

        _execution_cleanup.register_cleanup(cleanup)

        cleanup.assert_not_called()

    def test_register_process_terminates_active_process_on_cancel(self) -> None:
        process = mock.Mock(spec=subprocess.Popen)
        process.poll.return_value = None

        with _execution_cleanup.current_execution_cleanup():
            _execution_cleanup.register_process(process)
            _execution_cleanup.cancel_current_execution_cleanup()

        process.terminate.assert_called_once_with()
        process.wait.assert_called_once_with(timeout=1.0)
