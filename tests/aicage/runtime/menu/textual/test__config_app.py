import asyncio
from pathlib import Path
from unittest import TestCase, mock

from aicage.cli_types import ParsedArgs
from aicage.config.project_config import AgentConfig
from aicage.runtime.menu._interaction_types import ConfigSelectionResult
from aicage.runtime.menu.textual import _config_app
from aicage.runtime.menu.textual._models import (
    BuiltInShareValue,
    CustomShareValue,
    DockerOptionValue,
    HostAccessConfirmValues,
    ShareEditorResult,
)
from aicage.runtime.menu.textual.views.overview.view import Overview

from .._test_support import _build_context, _build_draft
from ._test_support import _call_work_async


class ConfigAppTests(TestCase):
    def test_command_palette_is_disabled(self) -> None:
        self.assertFalse(_config_app.ConfigApp.ENABLE_COMMAND_PALETTE)

    def test_inline_padding_is_disabled(self) -> None:
        self.assertEqual(0, _config_app.ConfigApp.INLINE_PADDING)

    def test_compose_builds_overview(self) -> None:
        app = _build_app()

        widgets = list(app.compose())

        self.assertEqual(1, len(widgets))
        self.assertIsInstance(widgets[0], Overview)

    def test_init_sets_container_config_subtitle(self) -> None:
        app = _build_app()

        self.assertEqual("container config", app.sub_title)

    def test_format_title_bolds_app_name_and_dims_subtitle(self) -> None:
        app = _build_app()

        title = app.format_title("aicage", "container config")

        self.assertEqual("aicage — container config", str(title))

    def test_on_mount_populates_table(self) -> None:
        app = _build_app()
        overview = mock.Mock()

        with (
            mock.patch.object(app, "_overview", return_value=overview),
            mock.patch.object(app, "_apply_shell_width") as apply_shell_width_mock,
            mock.patch.object(app, "_refresh_sections") as refresh_sections_mock,
        ):
            app.on_mount()

        apply_shell_width_mock.assert_called_once_with()
        refresh_sections_mock.assert_called_once_with()
        overview.focus_default.assert_called_once_with()

    def test_on_mount_uses_default_base_resolution_when_base_missing(self) -> None:
        app = _build_app(agent_cfg=AgentConfig())

        with (
            mock.patch.object(app, "_overview", return_value=mock.Mock()),
            mock.patch.object(app, "_apply_shell_width"),
            mock.patch.object(app, "_refresh_sections"),
            mock.patch(
                "aicage.runtime.menu.textual.services.base_support.resolve_default_base",
                return_value="ubuntu",
            ),
        ):
            app.on_mount()

        self.assertEqual("ubuntu", app._draft.agent_cfg.base)

    def test_action_accept_dispatches_async_accept(self) -> None:
        app = _build_app()

        with mock.patch.object(app, "_accept") as accept_mock:
            app.action_accept()

        accept_mock.assert_called_once_with()

    def test_action_cancel_exits_none(self) -> None:
        app = _build_app()

        with mock.patch.object(app, "_finish") as finish_mock:
            app.action_cancel()

        finish_mock.assert_called_once_with(None)

    def test_accept_finishes_when_host_access_confirmed(self) -> None:
        app = _build_app()

        with (
            mock.patch.object(
                app,
                "_confirm_undecided_built_in_shares",
                new=mock.AsyncMock(return_value=True),
            ),
            mock.patch.object(app, "_finish") as finish_mock,
        ):
            _call_work_async(app, "_accept")

        finish_mock.assert_called_once()

    def test_accept_stops_when_host_access_rejected(self) -> None:
        app = _build_app()

        with (
            mock.patch.object(
                app,
                "_confirm_undecided_built_in_shares",
                new=mock.AsyncMock(return_value=False),
            ),
            mock.patch.object(app, "_finish") as finish_mock,
        ):
            _call_work_async(app, "_accept")

        finish_mock.assert_not_called()

    def test_on_overview_accept_requested_dispatches_ok(self) -> None:
        app = _build_app()

        with mock.patch.object(app, "action_accept") as accept_mock:
            app.on_overview_accept_requested(Overview.AcceptRequested())

        accept_mock.assert_called_once_with()

    def test_on_overview_cancel_requested_dispatches_cancel(self) -> None:
        app = _build_app()

        with mock.patch.object(app, "action_cancel") as cancel_mock:
            app.on_overview_cancel_requested(Overview.CancelRequested())

        cancel_mock.assert_called_once_with()

    def test_on_overview_add_share_requested_dispatches_add_share(self) -> None:
        app = _build_app()

        with mock.patch.object(app, "_add_share") as add_share_mock:
            app.on_overview_add_share_requested(Overview.AddShareRequested())

        add_share_mock.assert_called_once_with()

    def test_on_overview_edit_section_requested_dispatches_section_edit(self) -> None:
        app = _build_app()

        with mock.patch.object(app, "_edit_section") as edit_mock:
            app.on_overview_edit_section_requested(
                Overview.EditSectionRequested("base")
            )

        edit_mock.assert_called_once_with("base")

    def test_on_overview_edit_custom_share_requested_opens_custom_share_editor(
        self,
    ) -> None:
        app = _build_app(
            agent_cfg=AgentConfig(base="ubuntu", shares=["/test-tmp/project/logs"])
        )

        with mock.patch.object(app, "_edit_custom_share") as edit_mock:
            app.on_overview_edit_custom_share_requested(
                Overview.EditCustomShareRequested("/test-tmp/project/logs")
            )

        edit_mock.assert_called_once_with("/test-tmp/project/logs")

    def test_add_share_updates_custom_shares(self) -> None:
        app = _build_app()

        with (
            mock.patch.object(
                app,
                "_push_view",
                new=mock.AsyncMock(return_value=ShareEditorResult("logs", False)),
            ),
            mock.patch.object(app, "_apply_shell_width") as apply_shell_width_mock,
            mock.patch.object(app, "_refresh_sections") as refresh_mock,
        ):
            _call_work_async(app, "_add_share")

        self.assertEqual(
            [CustomShareValue("/test-tmp/project/logs")], app._state.custom_shares
        )
        apply_shell_width_mock.assert_called_once_with()
        refresh_mock.assert_called_once_with()

    def test_confirm_undecided_built_in_shares_persists_enabled_mount_and_custom_shares(
        self,
    ) -> None:
        built_in_share = BuiltInShareValue(
            "git_support", "gitconfig", "Git config", "/test-tmp/gitconfig", None, True
        )
        app = _build_app(built_in_shares=[built_in_share])
        overview = mock.Mock()
        overview.current_built_in_shares.return_value = [built_in_share]
        overview.current_custom_shares.return_value = [
            CustomShareValue("/test-tmp/project/logs"),
            CustomShareValue("/test-tmp/project/data"),
        ]
        overview.current_host_options.return_value = [
            DockerOptionValue("docker", "Docker socket", None, None, True)
        ]

        with (
            mock.patch.object(app, "_overview", return_value=overview),
            mock.patch.object(
                app,
                "_push_view",
                new=mock.AsyncMock(
                    return_value=HostAccessConfirmValues(
                        docker_options=[
                            DockerOptionValue(
                                "docker", "Docker socket", None, None, True
                            )
                        ],
                        git_support_shares=[built_in_share],
                        extension_shares=[],
                    )
                ),
            ),
        ):
            accepted = asyncio.run(app._confirm_undecided_built_in_shares())

        self.assertTrue(accepted)
        self.assertTrue(app._draft.agent_cfg.mounts.gitconfig)
        self.assertTrue(app._draft.agent_cfg.mounts.docker)
        self.assertEqual(
            ["/test-tmp/project/logs", "/test-tmp/project/data"],
            app._draft.agent_cfg.shares,
        )

    def test_confirm_undecided_built_in_shares_persists_deselected_docker_socket_from_popup(
        self,
    ) -> None:
        app = _build_app()
        overview = mock.Mock()
        overview.current_built_in_shares.return_value = []
        overview.current_custom_shares.return_value = []
        overview.current_host_options.return_value = [
            DockerOptionValue("docker", "Docker socket", None, None, True)
        ]

        with (
            mock.patch.object(app, "_overview", return_value=overview),
            mock.patch.object(
                app,
                "_push_view",
                new=mock.AsyncMock(
                    return_value=HostAccessConfirmValues(
                        docker_options=[
                            DockerOptionValue(
                                "docker", "Docker socket", None, None, False
                            )
                        ],
                        git_support_shares=[],
                        extension_shares=[],
                    )
                ),
            ),
        ):
            accepted = asyncio.run(app._confirm_undecided_built_in_shares())

        self.assertTrue(accepted)
        self.assertFalse(app._draft.agent_cfg.mounts.docker)

    def test_confirm_undecided_built_in_shares_returns_false_when_confirmation_cancels(
        self,
    ) -> None:
        built_in_share = BuiltInShareValue(
            "git_support", "gitconfig", "Git config", "/test-tmp/gitconfig", None, True
        )
        app = _build_app(built_in_shares=[built_in_share])
        overview = mock.Mock()
        overview.current_built_in_shares.return_value = [built_in_share]
        overview.current_custom_shares.return_value = []
        overview.current_host_options.return_value = [
            DockerOptionValue("docker", "Docker socket", None, None, False)
        ]

        with (
            mock.patch.object(app, "_overview", return_value=overview),
            mock.patch.object(app, "_push_view", new=mock.AsyncMock(return_value=None)),
        ):
            accepted = asyncio.run(app._confirm_undecided_built_in_shares())

        self.assertFalse(accepted)

    def test_confirm_undecided_built_in_shares_persists_extension_share_selection(
        self,
    ) -> None:
        extension_share = BuiltInShareValue(
            "extension",
            "gh",
            "Extension gh",
            str(Path.home().resolve() / ".config/gh"),
            None,
            True,
        )
        app = _build_app(
            agent_cfg=AgentConfig(base="ubuntu", extensions=["gh"]),
            built_in_shares=[extension_share],
        )
        overview = mock.Mock()
        overview.current_built_in_shares.return_value = [extension_share]
        overview.current_custom_shares.return_value = []
        overview.current_host_options.return_value = [
            DockerOptionValue("docker", "Docker socket", None, None, False)
        ]

        with (
            mock.patch.object(app, "_overview", return_value=overview),
            mock.patch.object(
                app,
                "_push_view",
                new=mock.AsyncMock(
                    return_value=HostAccessConfirmValues(
                        docker_options=[],
                        git_support_shares=[],
                        extension_shares=[extension_share],
                    )
                ),
            ),
        ):
            accepted = asyncio.run(app._confirm_undecided_built_in_shares())

        self.assertTrue(accepted)
        self.assertEqual({"gh": True}, app._draft.agent_cfg.extension_mounts)

    def test_edit_custom_share_removes_share(self) -> None:
        app = _build_app(
            agent_cfg=AgentConfig(
                base="ubuntu",
                shares=["/test-tmp/project/logs", "/test-tmp/project/data"],
            )
        )

        with (
            mock.patch.object(
                app,
                "_push_view",
                new=mock.AsyncMock(
                    return_value=ShareEditorResult("/test-tmp/project/logs", True)
                ),
            ),
            mock.patch.object(app, "_apply_shell_width") as apply_shell_width_mock,
            mock.patch.object(app, "_refresh_sections") as refresh_mock,
        ):
            _call_work_async(app, "_edit_custom_share", "/test-tmp/project/logs")

        self.assertEqual(
            [CustomShareValue("/test-tmp/project/data")], app._state.custom_shares
        )
        apply_shell_width_mock.assert_called_once_with()
        refresh_mock.assert_called_once_with()

    def test_edit_custom_share_replaces_share(self) -> None:
        app = _build_app(
            agent_cfg=AgentConfig(base="ubuntu", shares=["/test-tmp/project/logs"])
        )

        with (
            mock.patch.object(
                app,
                "_push_view",
                new=mock.AsyncMock(return_value=ShareEditorResult("data", False)),
            ),
            mock.patch.object(app, "_apply_shell_width") as apply_shell_width_mock,
            mock.patch.object(app, "_refresh_sections") as refresh_mock,
        ):
            _call_work_async(app, "_edit_custom_share", "/test-tmp/project/logs")

        self.assertEqual(
            [CustomShareValue("/test-tmp/project/data")], app._state.custom_shares
        )
        apply_shell_width_mock.assert_called_once_with()
        refresh_mock.assert_called_once_with()

    def test_push_view_restores_focus_to_launching_section(self) -> None:
        app = _build_app()
        app._state.last_section_id = "base"
        overview = mock.Mock()

        with (
            mock.patch.object(app, "_overview", return_value=overview),
            mock.patch.object(app, "_focus_last_section") as focus_last_section_mock,
            mock.patch.object(
                app, "push_screen_wait", new=mock.AsyncMock(return_value=None)
            ),
        ):
            asyncio.run(app._push_view(mock.Mock()))

        overview.hide_shell.assert_called_once_with()
        overview.show_shell.assert_called_once_with()
        focus_last_section_mock.assert_called_once_with()

    def test_finish_exits_with_result(self) -> None:
        app = _build_app()
        result = ConfigSelectionResult(
            selection=mock.Mock(),
            project_docker_args="--project",
        )

        with mock.patch.object(app, "exit") as exit_mock:
            app._finish(result)

        exit_mock.assert_called_once_with(result)

    def test_focus_last_section_focuses_default_when_no_last_section(self) -> None:
        app = _build_app()
        app._state.last_section_id = None
        overview = mock.Mock()

        with mock.patch.object(app, "_overview", return_value=overview):
            app._focus_last_section()

        overview.focus_default.assert_called_once_with()
        overview.focus_section.assert_not_called()

    def test_focus_last_section_focuses_last_section_when_present(self) -> None:
        app = _build_app()
        app._state.last_section_id = "extensions"
        overview = mock.Mock()

        with mock.patch.object(app, "_overview", return_value=overview):
            app._focus_last_section()

        overview.focus_default.assert_not_called()
        overview.focus_section.assert_called_once_with("extensions")


def _build_app(
    agent_cfg: AgentConfig | None = None,
    built_in_shares: list[BuiltInShareValue] | None = None,
) -> _config_app.ConfigApp:
    with mock.patch(
        "aicage.runtime.menu.textual.services.summary.built_in_share_values",
        return_value=built_in_shares or [],
    ):
        return _config_app.ConfigApp(
            _build_draft(
                agent_cfg or AgentConfig(base="ubuntu"),
                ParsedArgs(False, "", "codex", [], False, [], None),
                project_path=Path("/test-tmp/project"),
            ),
            _build_context(),
        )
