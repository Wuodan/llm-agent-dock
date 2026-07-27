import io
import tempfile
from pathlib import Path
from unittest import TestCase, mock

from aicage.docker.pull import run_pull


class DockerPullTests(TestCase):
    def test_run_pull_writes_logs(self) -> None:
        client = mock.Mock()
        client.api.pull.return_value = [{"status": "downloaded"}, b"done\n"]
        with tempfile.TemporaryDirectory() as tmp_dir:
            log_path = Path(tmp_dir) / "pull.log"
            with (
                mock.patch(
                    "aicage.docker.execution.client.get_docker_pull_client",
                    return_value=client,
                ),
                mock.patch("aicage.docker.pull.register_cleanup") as register_mock,
            ):
                run_pull("ghcr.io/aicage/aicage:latest", log_path)

            payload = log_path.read_text(encoding="utf-8")
        self.assertIn('"status": "downloaded"', payload)
        self.assertIn("done", payload)
        register_mock.assert_called_once_with(client.close)

    def test_run_pull_renders_progress_and_writes_logs(self) -> None:
        client = mock.Mock()
        client.api.pull.return_value = [
            {"status": "Pulling fs layer", "id": "layer-a", "progressDetail": {}},
            {
                "status": "Downloading",
                "id": "layer-a",
                "progressDetail": {"current": 50, "total": 100},
            },
            {
                "status": "Pull complete",
                "id": "layer-a",
                "progressDetail": {"hidecounts": True},
            },
        ]
        stdout = io.StringIO()
        with tempfile.TemporaryDirectory() as tmp_dir:
            log_path = Path(tmp_dir) / "pull.log"
            with (
                mock.patch(
                    "aicage.docker.execution.client.get_docker_pull_client",
                    return_value=client,
                ),
                mock.patch("sys.stdout", stdout),
                mock.patch.object(stdout, "isatty", return_value=True),
                mock.patch(
                    "aicage.docker.image.progress.shutil.get_terminal_size",
                    return_value=mock.Mock(columns=200),
                ),
                mock.patch(
                    "aicage.docker.pull.time.monotonic", side_effect=[1.0, 2.0, 3.0]
                ),
            ):
                run_pull("ghcr.io/aicage/aicage:latest", log_path)

            payload = log_path.read_text(encoding="utf-8")

        self.assertIn('"status": "Downloading"', payload)
        rendered = stdout.getvalue()
        self.assertIn("Pulling image ghcr.io/aicage/aicage:latest", rendered)
        self.assertIn("100%", rendered)
        self.assertTrue(rendered.endswith("\n"))

    def test_run_pull_reports_started_progress_logs_and_finished(self) -> None:
        client = mock.Mock()
        client.api.pull.return_value = [
            {
                "status": "Downloading",
                "id": "layer-a",
                "progressDetail": {"current": 50, "total": 100},
            },
            {"status": "Pull complete", "id": "layer-a"},
        ]
        reporter = mock.Mock()

        with tempfile.TemporaryDirectory() as tmp_dir:
            log_path = Path(tmp_dir) / "pull.log"
            with mock.patch(
                "aicage.docker.execution.client.get_docker_pull_client",
                return_value=client,
            ):
                run_pull("ghcr.io/aicage/aicage:latest", log_path, reporter=reporter)

        reporter.on_phase_started.assert_called_once()
        reporter.on_phase_log.assert_any_call(
            "pull",
            '{"status": "Downloading", "id": "layer-a", "progressDetail": {"current": 50, "total": 100}}',
        )
        reporter.on_phase_progress.assert_any_call(
            "pull",
            "100 B/100 B layers 1/1",
            100,
            100,
        )
        reporter.on_phase_finished.assert_called_once_with(
            "pull",
            "Pull finished for ghcr.io/aicage/aicage:latest",
        )

    def test_run_pull_without_reporter_skips_reporting_seam(self) -> None:
        client = mock.Mock()
        client.api.pull.return_value = [
            {"status": "Pulling fs layer", "id": "layer-a", "progressDetail": {}}
        ]

        with tempfile.TemporaryDirectory() as tmp_dir:
            log_path = Path(tmp_dir) / "pull.log"
            with (
                mock.patch(
                    "aicage.docker.execution.client.get_docker_pull_client",
                    return_value=client,
                ),
                mock.patch(
                    "aicage.docker.pull._report_progress"
                ) as report_progress_mock,
            ):
                run_pull("ghcr.io/aicage/aicage:latest", log_path)

        report_progress_mock.assert_not_called()
