import io
from unittest import TestCase, mock

from aicage.docker.image.progress import PullProgress


class PullProgressTests(TestCase):
    def test_consume_event_renders_aggregate_download_bar(self) -> None:
        stdout = io.StringIO()
        events = [
            {"status": "Pulling fs layer", "id": "layer-a", "progressDetail": {}},
            {
                "status": "Downloading",
                "id": "layer-a",
                "progressDetail": {"current": 25, "total": 100},
            },
            {
                "status": "Downloading",
                "id": "layer-b",
                "progressDetail": {"current": 50, "total": 100},
            },
            {
                "status": "Download complete",
                "id": "layer-a",
                "progressDetail": {"hidecounts": True},
            },
            {
                "status": "Extracting",
                "id": "layer-a",
                "progressDetail": {"current": 1, "units": "s"},
            },
            {
                "status": "Pull complete",
                "id": "layer-b",
                "progressDetail": {"hidecounts": True},
            },
        ]

        with (
            mock.patch("sys.stdout", stdout),
            mock.patch.object(stdout, "isatty", return_value=True),
            mock.patch(
                "aicage.docker.image.progress.shutil.get_terminal_size",
                return_value=mock.Mock(columns=200),
            ),
        ):
            progress = PullProgress()
            for offset, event in enumerate(events, start=1):
                progress.consume_event(event, float(offset))
            progress.finish()

        rendered = stdout.getvalue()
        self.assertIn("[aicage] Pulling", rendered)
        self.assertIn("75%", rendered)
        self.assertIn("100%", rendered)
        self.assertIn("layers 2/2", rendered)
        self.assertIn("extracting 1", rendered)
        self.assertTrue(rendered.endswith("\n"))

    def test_progress_details_reports_aggregate_summary_without_tty(self) -> None:
        with (
            mock.patch("sys.stdout", io.StringIO()),
            mock.patch("sys.stderr", io.StringIO()),
            mock.patch("sys.stdout.isatty", return_value=False),
            mock.patch("sys.stderr.isatty", return_value=False),
        ):
            progress = PullProgress()
            progress.consume_event(
                {"status": "Pulling fs layer", "id": "layer-a", "progressDetail": {}},
                1.0,
            )
            self.assertEqual(
                "[waiting for layer sizes...]", progress.progress_details()
            )
            self.assertIsNone(progress.progress_current())
            self.assertIsNone(progress.progress_total())

            progress.consume_event(
                {
                    "status": "Downloading",
                    "id": "layer-a",
                    "progressDetail": {"current": 25, "total": 100},
                },
                2.0,
            )

        self.assertEqual(
            "25 B/100 B layers 0/1 downloading 1",
            progress.progress_details(),
        )

    def test_progress_current_returns_aggregate_downloaded_bytes(self) -> None:
        progress = PullProgress()

        progress.consume_event(
            {"status": "Pulling fs layer", "id": "layer-a", "progressDetail": {}}, 1.0
        )
        self.assertIsNone(progress.progress_current())

        progress.consume_event(
            {
                "status": "Downloading",
                "id": "layer-a",
                "progressDetail": {"current": 25, "total": 100},
            },
            2.0,
        )

        self.assertEqual(25, progress.progress_current())

    def test_progress_status_returns_console_summary(self) -> None:
        progress = PullProgress()

        progress.consume_event(
            {
                "status": "Downloading",
                "id": "layer-a",
                "progressDetail": {"current": 25, "total": 100},
            },
            1.0,
        )

        self.assertEqual(
            "[######..................]  25% 25 B/100 B layers 0/1 downloading 1",
            progress.progress_status(),
        )

    def test_progress_total_returns_aggregate_total_bytes(self) -> None:
        progress = PullProgress()

        progress.consume_event(
            {"status": "Pulling fs layer", "id": "layer-a", "progressDetail": {}}, 1.0
        )
        self.assertIsNone(progress.progress_total())

        progress.consume_event(
            {
                "status": "Downloading",
                "id": "layer-a",
                "progressDetail": {"current": 25, "total": 100},
            },
            2.0,
        )

        self.assertEqual(100, progress.progress_total())

    def test_finish_prints_trailing_newline_after_render(self) -> None:
        stdout = io.StringIO()
        with (
            mock.patch("sys.stdout", stdout),
            mock.patch.object(stdout, "isatty", return_value=True),
            mock.patch(
                "aicage.docker.image.progress.shutil.get_terminal_size",
                return_value=mock.Mock(columns=200),
            ),
        ):
            progress = PullProgress()
            progress.consume_event(
                {
                    "status": "Downloading",
                    "id": "layer-a",
                    "progressDetail": {"current": 25, "total": 100},
                },
                1.0,
            )
            progress.finish()

        self.assertTrue(stdout.getvalue().endswith("\n"))

    def test_consume_event_skips_non_tty_output(self) -> None:
        stdout = io.StringIO()
        stderr = io.StringIO()

        with (
            mock.patch("sys.stdout", stdout),
            mock.patch("sys.stderr", stderr),
            mock.patch.object(stdout, "isatty", return_value=False),
            mock.patch.object(stderr, "isatty", return_value=False),
        ):
            progress = PullProgress()
            progress.consume_event(
                {
                    "status": "Downloading",
                    "id": "layer-a",
                    "progressDetail": {"current": 25, "total": 100},
                },
                1.0,
            )
            progress.finish()

        self.assertEqual("", stdout.getvalue())
        self.assertEqual("", stderr.getvalue())

    def test_consume_event_falls_back_to_stderr_when_stdout_is_not_tty(self) -> None:
        stdout = io.StringIO()
        stderr = io.StringIO()
        with (
            mock.patch("sys.stdout", stdout),
            mock.patch("sys.stderr", stderr),
            mock.patch.object(stdout, "isatty", return_value=False),
            mock.patch.object(stderr, "isatty", return_value=True),
            mock.patch(
                "aicage.docker.image.progress.shutil.get_terminal_size",
                return_value=mock.Mock(columns=200),
            ),
        ):
            progress = PullProgress()
            progress.consume_event(
                {
                    "status": "Downloading",
                    "id": "layer-a",
                    "progressDetail": {"current": 25, "total": 100},
                },
                1.0,
            )
            progress.finish()

        self.assertEqual("", stdout.getvalue())
        self.assertIn("[aicage] Pulling", stderr.getvalue())
