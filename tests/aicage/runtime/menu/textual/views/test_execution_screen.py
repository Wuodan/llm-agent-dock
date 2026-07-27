from pathlib import Path
from unittest import TestCase, mock

from aicage.runtime.menu.textual.views import execution_screen


class ExecutionScreenTests(TestCase):
    def test_compose_builds_execution_widgets(self) -> None:
        screen = execution_screen.ExecutionScreen()

        widgets = list(screen.compose())

        self.assertEqual(1, len(widgets))

    def test_show_phase_started_updates_status_progress_without_pull_log(self) -> None:
        screen = execution_screen.ExecutionScreen()
        status = mock.Mock()
        progress = mock.Mock()
        details = mock.Mock()
        build_info = mock.Mock()
        log = mock.Mock()

        with mock.patch.object(
            screen,
            "query_one",
            side_effect=[status, progress, details, build_info, progress, details, log],
        ):
            screen.show_phase_started(
                "pull", "Pulling image repo:tag", Path("/test-tmp/pull.log")
            )

        status.update.assert_called_once_with("Pulling image repo:tag")
        progress.update.assert_called_once_with(total=None, progress=0)
        details.update.assert_called_once_with("")
        self.assertFalse(build_info.display)
        self.assertFalse(log.display)

    def test_show_phase_started_formats_build_image_and_log_path(self) -> None:
        screen = execution_screen.ExecutionScreen()
        status = mock.Mock()
        image_ref = mock.Mock()
        log_path = mock.Mock()
        progress = mock.Mock()
        details = mock.Mock()
        build_info = mock.Mock()
        log = mock.Mock()

        with mock.patch.object(
            screen,
            "query_one",
            side_effect=[
                status,
                image_ref,
                log_path,
                progress,
                details,
                build_info,
                progress,
                details,
                log,
                log,
            ],
        ):
            screen.show_phase_started(
                "build",
                "Building extended image repo:tag",
                Path("/test-tmp/build.log"),
            )

        status.update.assert_called_once_with("Building extended image")
        image_ref.update.assert_called_once_with("repo:tag")
        log_path.update.assert_called_once_with("/test-tmp/build.log")
        self.assertFalse(progress.display)
        self.assertFalse(details.display)
        self.assertTrue(build_info.display)
        self.assertTrue(log.display)

    def test_show_phase_progress_updates_known_progress(self) -> None:
        screen = execution_screen.ExecutionScreen()
        status = mock.Mock()
        progress = mock.Mock()
        details = mock.Mock()
        build_info = mock.Mock()
        log = mock.Mock()

        with mock.patch.object(
            screen,
            "query_one",
            side_effect=[
                status,
                progress,
                details,
                build_info,
                progress,
                details,
                log,
                status,
                details,
                progress,
            ],
        ):
            screen.show_phase_started(
                "pull", "Pulling image repo:tag", Path("/test-tmp/pull.log")
            )
            screen.show_phase_progress(
                "pull",
                "5 B/10 B layers 0/1 downloading 1",
                5,
                10,
            )

        self.assertEqual(
            [mock.call("Pulling image repo:tag"), mock.call("Pulling image repo:tag")],
            status.update.call_args_list,
        )
        self.assertEqual(
            [mock.call(""), mock.call("5 B/10 B layers 0/1 downloading 1")],
            details.update.call_args_list,
        )
        self.assertEqual(
            [mock.call(total=None, progress=0), mock.call(total=10, progress=5)],
            progress.update.call_args_list,
        )

    def test_show_phase_progress_handles_unknown_total(self) -> None:
        screen = execution_screen.ExecutionScreen()
        status = mock.Mock()
        progress = mock.Mock()
        details = mock.Mock()

        with mock.patch.object(
            screen, "query_one", side_effect=[status, details, progress]
        ):
            screen.show_phase_progress(
                "pull", "[waiting for layer sizes...]", None, None
            )

        details.update.assert_called_once_with("[waiting for layer sizes...]")
        progress.update.assert_called_once_with(total=None, progress=0)

    def test_show_phase_log_writes_build_log_line(self) -> None:
        screen = execution_screen.ExecutionScreen()
        log = mock.Mock()

        with mock.patch.object(screen, "query_one", return_value=log):
            screen.show_phase_log("build", "step 1")

        log.write.assert_called_once_with("[build] step 1")

    def test_show_phase_log_skips_pull_log_line(self) -> None:
        screen = execution_screen.ExecutionScreen()
        log = mock.Mock()

        with mock.patch.object(screen, "query_one", return_value=log):
            screen.show_phase_log("pull", "step 1")

        log.write.assert_not_called()

    def test_show_phase_finished_marks_complete(self) -> None:
        screen = execution_screen.ExecutionScreen()
        status = mock.Mock()
        log = mock.Mock()

        with mock.patch.object(screen, "query_one", side_effect=[status, log]):
            screen.show_phase_finished("build", "Build finished")

        status.update.assert_called_once_with("Build: Build finished")
        log.write.assert_called_once_with("[build] Build finished")

    def test_show_phase_failed_updates_status_and_log(self) -> None:
        screen = execution_screen.ExecutionScreen()
        status = mock.Mock()
        log_path = mock.Mock()
        build_info = mock.Mock()
        log = mock.Mock()

        with mock.patch.object(
            screen, "query_one", side_effect=[status, log_path, build_info, log]
        ):
            screen.show_phase_failed(
                "build", "Build failed", Path("/test-tmp/build.log")
            )

        status.update.assert_called_once_with("Build failed")
        log_path.update.assert_called_once_with("/test-tmp/build.log")
        self.assertTrue(build_info.display)
        log.write.assert_called_once_with("[build] Build failed")

    def test_on_button_pressed_copies_log_path(self) -> None:
        screen = execution_screen.ExecutionScreen()
        event = mock.Mock()
        event.button.id = "copy_log_path"
        screen._build_log_path = "/test-tmp/build.log"
        app = mock.Mock()

        with (
            mock.patch.object(
                type(screen), "app", new_callable=mock.PropertyMock, return_value=app
            ),
            mock.patch(
                "aicage.runtime.menu.textual.views.execution_screen._clipboard.copy_to_clipboard"
            ) as copy_mock,
        ):
            screen.on_button_pressed(event)

        event.stop.assert_called_once_with()
        copy_mock.assert_called_once_with("/test-tmp/build.log", app.copy_to_clipboard)

    def test_show_phase_progress_skips_updates_after_cancel(self) -> None:
        screen = execution_screen.ExecutionScreen()
        screen.mark_cancelled()

        with mock.patch.object(screen, "query_one") as query_mock:
            screen.show_phase_progress("pull", "Downloading", 1, 2)

        query_mock.assert_not_called()

    def test_mark_cancelled_sets_cancelled_flag(self) -> None:
        screen = execution_screen.ExecutionScreen()

        screen.mark_cancelled()

        self.assertTrue(screen._cancelled)
