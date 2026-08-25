import io
import tempfile
from pathlib import Path
from unittest import TestCase, mock

from aicage import reporting


class ConsoleOperationReporterTests(TestCase):
    def test_on_phase_started_prints_message_with_log_path(self) -> None:
        reporter = reporting.ConsoleOperationReporter()
        stdout = io.StringIO()
        stderr = io.StringIO()

        with tempfile.TemporaryDirectory() as tmp_dir:
            log_path = Path(tmp_dir) / "pull.log"
            with mock.patch("sys.stdout", stdout), mock.patch("sys.stderr", stderr):
                reporter.on_phase_started("pull", "Pulling image repo:tag", log_path)

        self.assertEqual("", stdout.getvalue())
        self.assertEqual(
            f"[aicage] Pulling image repo:tag (logs: {log_path})...\n",
            stderr.getvalue(),
        )

    def test_on_phase_progress_does_not_print(self) -> None:
        reporter = reporting.ConsoleOperationReporter()
        stdout = io.StringIO()

        with mock.patch("sys.stdout", stdout):
            reporter.on_phase_progress("pull", "Downloading", 1, 2)

        self.assertEqual("", stdout.getvalue())

    def test_on_phase_log_does_not_print(self) -> None:
        reporter = reporting.ConsoleOperationReporter()
        stdout = io.StringIO()

        with mock.patch("sys.stdout", stdout):
            reporter.on_phase_log("pull", "line")

        self.assertEqual("", stdout.getvalue())

    def test_on_phase_finished_does_not_print(self) -> None:
        reporter = reporting.ConsoleOperationReporter()
        stdout = io.StringIO()

        with mock.patch("sys.stdout", stdout):
            reporter.on_phase_finished("pull", "done")

        self.assertEqual("", stdout.getvalue())

    def test_on_phase_failed_does_not_print(self) -> None:
        reporter = reporting.ConsoleOperationReporter()
        stdout = io.StringIO()

        with tempfile.TemporaryDirectory() as tmp_dir:
            log_path = Path(tmp_dir) / "pull.log"
            with (
                mock.patch("sys.stdout", stdout),
                mock.patch("sys.stderr", io.StringIO()),
            ):
                reporter.on_phase_failed("pull", "failed", log_path)

        self.assertEqual("", stdout.getvalue())
