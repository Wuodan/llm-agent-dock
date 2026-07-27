from unittest import TestCase, mock

from aicage.runtime.menu.textual import _execution_app
from aicage.runtime.menu.textual.services.execution_reporting import ExecutionReporter

from ._test_support import _call_work


class ExecutionAppTests(TestCase):
    def test_compose_yields_execution_screen(self) -> None:
        app = _execution_app.ExecutionApp(mock.Mock(), False, ExecutionReporter())

        widgets = list(app.compose())

        self.assertEqual(1, len(widgets))
        self.assertIsInstance(widgets[0], _execution_app.ExecutionScreen)

    def test_init_sets_container_setup_subtitle(self) -> None:
        app = _execution_app.ExecutionApp(mock.Mock(), False, ExecutionReporter())

        self.assertEqual("container setup", app.sub_title)

    def test_format_title_bolds_app_name_and_dims_subtitle(self) -> None:
        app = _execution_app.ExecutionApp(mock.Mock(), False, ExecutionReporter())

        title = app.format_title("aicage", "container setup")

        self.assertEqual("aicage — container setup", str(title))

    def test_on_mount_starts_execution(self) -> None:
        app = _execution_app.ExecutionApp(mock.Mock(), False, ExecutionReporter())

        with mock.patch.object(app, "_run_execution") as run_mock:
            app.on_mount()

        run_mock.assert_called_once_with()

    def test_action_cancel_cancels_current_execution_cleanup_and_exits(self) -> None:
        app = _execution_app.ExecutionApp(mock.Mock(), False, ExecutionReporter())
        screen = mock.Mock()

        with (
            mock.patch.object(app, "query_one", return_value=screen) as query_mock,
            mock.patch(
                "aicage.runtime.menu.textual._execution_app.cancel_current_execution_cleanup"
            ) as cancel_mock,
            mock.patch.object(app, "exit") as exit_mock,
        ):
            app.action_cancel()

        query_mock.assert_called_once_with(_execution_app.ExecutionScreen)
        screen.mark_cancelled.assert_called_once_with()
        cancel_mock.assert_called_once_with()
        exit_mock.assert_called_once()
        self.assertIsInstance(exit_mock.call_args.args[0], KeyboardInterrupt)

    def test_run_execution_exits_with_error(self) -> None:
        run_config = mock.Mock()
        reporter = ExecutionReporter()
        app = _execution_app.ExecutionApp(run_config, True, reporter)
        screen = mock.Mock()

        with (
            mock.patch.object(app, "query_one", return_value=screen),
            mock.patch.object(app, "call_from_thread") as call_from_thread_mock,
            mock.patch(
                "aicage.runtime.menu.textual._execution_app.ensure_image",
                side_effect=RuntimeError("boom"),
            ),
            mock.patch(
                "aicage.runtime.menu.textual._execution_app.current_execution_cleanup"
            ) as cleanup_mock,
        ):
            _call_work(app, "_run_execution")

        call_from_thread_mock.assert_called_once()
        self.assertIsInstance(call_from_thread_mock.call_args.args[1], RuntimeError)
        cleanup_mock.assert_called_once_with()
        self.assertIs(screen, reporter._screen)

    def test_run_execution_exits_with_none_on_success(self) -> None:
        run_config = mock.Mock()
        reporter = ExecutionReporter()
        app = _execution_app.ExecutionApp(run_config, False, reporter)
        screen = mock.Mock()

        with (
            mock.patch.object(app, "query_one", return_value=screen),
            mock.patch.object(app, "call_from_thread") as call_from_thread_mock,
            mock.patch(
                "aicage.runtime.menu.textual._execution_app.ensure_image"
            ) as ensure_image_mock,
            mock.patch(
                "aicage.runtime.menu.textual._execution_app.current_execution_cleanup"
            ) as cleanup_mock,
        ):
            _call_work(app, "_run_execution")

        call_from_thread_mock.assert_called_once_with(app.exit, None)
        ensure_image_mock.assert_called_once_with(
            run_config,
            update_approved=False,
            reporter=reporter,
        )
        cleanup_mock.assert_called_once_with()
        self.assertIs(screen, reporter._screen)
