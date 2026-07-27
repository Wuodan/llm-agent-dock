from pathlib import Path
from unittest import TestCase, mock

from aicage.runtime.menu.textual.services import execution_reporting


class ExecutionReporterTests(TestCase):
    def test_on_phase_started_raises_when_screen_not_attached(self) -> None:
        reporter = execution_reporting.ExecutionReporter()

        with self.assertRaises(RuntimeError):
            reporter.on_phase_started(
                "pull", "Pulling image repo:tag", Path("/test-tmp/pull.log")
            )

    def test_attach_screen(self) -> None:
        screen = mock.Mock()
        reporter = execution_reporting.ExecutionReporter()

        reporter.attach_screen(screen)

        self.assertIs(screen, reporter._screen)

    def test_on_phase_started_calls_screen_directly_without_app(self) -> None:
        screen = mock.Mock()
        del screen.app
        reporter = execution_reporting.ExecutionReporter()
        reporter.attach_screen(screen)

        reporter.on_phase_started(
            "pull", "Pulling image repo:tag", Path("/test-tmp/pull.log")
        )

        screen.show_phase_started.assert_called_once_with(
            "pull", "Pulling image repo:tag", Path("/test-tmp/pull.log")
        )

    def test_on_phase_started_dispatches_via_app_thread_bridge(self) -> None:
        screen = mock.Mock()
        screen.app = mock.Mock()
        reporter = execution_reporting.ExecutionReporter()
        reporter.attach_screen(screen)

        reporter.on_phase_started(
            "pull", "Pulling image repo:tag", Path("/test-tmp/pull.log")
        )

        screen.app.call_from_thread.assert_called_once_with(
            screen.show_phase_started,
            "pull",
            "Pulling image repo:tag",
            Path("/test-tmp/pull.log"),
        )

    def test_on_phase_started_falls_back_to_direct_call_on_runtime_error(self) -> None:
        screen = mock.Mock()
        screen.app = mock.Mock()
        screen.app.call_from_thread.side_effect = RuntimeError("same thread")
        reporter = execution_reporting.ExecutionReporter()
        reporter.attach_screen(screen)

        reporter.on_phase_started(
            "pull", "Pulling image repo:tag", Path("/test-tmp/pull.log")
        )

        screen.show_phase_started.assert_called_once_with(
            "pull", "Pulling image repo:tag", Path("/test-tmp/pull.log")
        )

    def test_on_phase_progress_dispatches_expected_values(self) -> None:
        screen = mock.Mock()
        del screen.app
        reporter = execution_reporting.ExecutionReporter()
        reporter.attach_screen(screen)

        reporter.on_phase_progress("pull", "Downloading", 1, 2)

        screen.show_phase_progress.assert_called_once_with("pull", "Downloading", 1, 2)

    def test_on_phase_log_dispatches_expected_values(self) -> None:
        screen = mock.Mock()
        del screen.app
        reporter = execution_reporting.ExecutionReporter()
        reporter.attach_screen(screen)

        reporter.on_phase_log("build", "step 1")

        screen.show_phase_log.assert_called_once_with("build", "step 1")

    def test_on_phase_finished_dispatches_expected_values(self) -> None:
        screen = mock.Mock()
        del screen.app
        reporter = execution_reporting.ExecutionReporter()
        reporter.attach_screen(screen)

        reporter.on_phase_finished("build", "done")

        screen.show_phase_finished.assert_called_once_with("build", "done")

    def test_on_phase_failed_dispatches_expected_values(self) -> None:
        screen = mock.Mock()
        del screen.app
        reporter = execution_reporting.ExecutionReporter()
        reporter.attach_screen(screen)

        reporter.on_phase_failed("build", "failed", Path("/test-tmp/build.log"))

        screen.show_phase_failed.assert_called_once_with(
            "build", "failed", Path("/test-tmp/build.log")
        )
