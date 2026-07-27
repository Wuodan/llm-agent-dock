import subprocess
from unittest import TestCase, mock

from textual.widgets import Button, Checkbox, Static, TextArea

from aicage.registry.image_selection.interaction import ExtensionChoiceOption
from aicage.runtime.menu.textual.views import extensions_screen as screen_module


class ExtensionsScreenTests(TestCase):
    def test_compose_builds_screen_widgets(self) -> None:
        option = _option("gh", "GitHub CLI", "Desc")
        screen = screen_module.ExtensionsScreen([option], ["gh"])

        widgets = list(screen.compose())

        self.assertEqual(1, len(widgets))

    def test_checkboxes_marks_selected_extensions(self) -> None:
        option = _option("gh", "GitHub CLI", "Desc")

        checkboxes = screen_module.ExtensionsScreen([option], ["gh"])._checkboxes()

        self.assertEqual(1, len(checkboxes))

    def test_on_mount_focuses_first_checkbox(self) -> None:
        option = _option("gh", "GitHub CLI", "Desc")
        screen = screen_module.ExtensionsScreen([option], ["gh"])

        with mock.patch.object(screen, "_focus_checkbox") as focus_checkbox_mock:
            screen.on_mount()

        focus_checkbox_mock.assert_called_once_with(0)

    def test_on_mount_without_options_focuses_command_box(self) -> None:
        screen = screen_module.ExtensionsScreen([], [])
        command_box = mock.Mock(spec=TextArea)

        with mock.patch.object(screen, "query_one", return_value=command_box):
            screen.on_mount()

        command_box.focus.assert_called_once_with()

    def test_content_widgets_without_options_returns_empty_state_message(self) -> None:
        screen = screen_module.ExtensionsScreen([], [])

        widgets = screen._content_widgets()

        self.assertEqual(3, len(widgets))
        self.assertIsInstance(widgets[0], Static)
        self.assertIsInstance(widgets[1], Static)
        self.assertIsInstance(widgets[2], TextArea)
        command_box = widgets[2]
        assert isinstance(command_box, TextArea)
        self.assertEqual("No optional extensions available.", widgets[0].render())
        self.assertEqual("Get samples with:", widgets[1].render())
        self.assertEqual(
            "git clone https://github.com/aicage/aicage-custom-samples.git $HOME/.aicage-custom",
            command_box.text,
        )

    def test_content_widgets_adds_heading_before_dockerfile_extensions(self) -> None:
        widgets = screen_module.ExtensionsScreen(
            [
                _option("gh", "GitHub CLI", "Desc"),
                _option(
                    "marker-dockerfile",
                    "Marker Dockerfile",
                    "Desc",
                    has_dockerfile=True,
                ),
            ],
            [],
        )._content_widgets()

        self.assertEqual(3, len(widgets))
        self.assertIsInstance(widgets[0], Checkbox)
        self.assertIsInstance(widgets[1], Static)
        self.assertIsInstance(widgets[2], Checkbox)
        self.assertEqual(
            "Extensions with custom Dockerfiles:",
            widgets[1].render(),
        )

    def test_action_buttons_without_options_uses_copy_command_instead_of_clear(
        self,
    ) -> None:
        screen = screen_module.ExtensionsScreen([], [])

        buttons = screen._action_buttons()

        self.assertEqual(["copy_command", "cancel"], [button.id for button in buttons])

    def test_hint_text_without_options_mentions_custom_extensions_dir(self) -> None:
        screen = screen_module.ExtensionsScreen([], [])

        hint = screen._hint_text()

        self.assertEqual(
            "Optional extensions are loaded from $HOME/.aicage-custom.", hint
        )

    def test_action_accept_saves_selected_extensions(self) -> None:
        option = _option("gh", "GitHub CLI", "Desc")
        screen = screen_module.ExtensionsScreen([option], [])
        checkbox = mock.Mock()
        checkbox.value = True

        with (
            mock.patch.object(screen, "query_one", return_value=checkbox),
            mock.patch.object(screen, "dismiss") as dismiss_mock,
        ):
            screen.action_accept()

        dismiss_mock.assert_called_once_with(["gh"])

    def test_on_button_pressed_dispatches_ok(self) -> None:
        option = _option("gh", "GitHub CLI", "Desc")
        screen = screen_module.ExtensionsScreen([option], [])
        event = mock.Mock()
        event.button.id = "ok"

        with mock.patch.object(screen, "action_accept") as accept_mock:
            screen.on_button_pressed(event)

        event.stop.assert_called_once_with()
        accept_mock.assert_called_once_with()

    def test_on_button_pressed_copy_command_copies_samples_command(self) -> None:
        screen = screen_module.ExtensionsScreen([], [])
        event = mock.Mock()
        event.button.id = "copy_command"

        with mock.patch.object(screen, "_copy_samples_command") as copy_mock:
            screen.on_button_pressed(event)

        event.stop.assert_called_once_with()
        copy_mock.assert_called_once_with()

    def test_copy_samples_command_copies_to_system_clipboard_when_available(
        self,
    ) -> None:
        screen = screen_module.ExtensionsScreen([], [])
        app = mock.Mock()

        with (
            mock.patch.object(
                type(screen), "app", new_callable=mock.PropertyMock, return_value=app
            ),
            mock.patch(
                "aicage.runtime.menu.textual.views.extensions_screen._clipboard.copy_to_clipboard"
            ) as copy_mock,
        ):
            screen._copy_samples_command()

        copy_mock.assert_called_once()
        self.assertEqual(
            "git clone https://github.com/aicage/aicage-custom-samples.git $HOME/.aicage-custom",
            copy_mock.call_args.args[0],
        )

    def test_copy_to_system_clipboard_returns_true_when_process_stays_alive(
        self,
    ) -> None:
        process = mock.Mock()
        process.stdin = mock.Mock()
        process.wait.side_effect = subprocess.TimeoutExpired(cmd="xclip", timeout=0.2)

        with (
            mock.patch(
                "aicage.runtime.menu.textual._clipboard.clipboard_command",
                return_value=["xclip"],
            ),
            mock.patch(
                "aicage.runtime.menu.textual._clipboard.subprocess.Popen",
                return_value=process,
            ),
        ):
            copied = screen_module.ExtensionsScreen._copy_to_system_clipboard("echo hi")

        self.assertTrue(copied)
        process.stdin.write.assert_called_once_with("echo hi")
        process.stdin.close.assert_called_once_with()

    def test_clipboard_command_prefers_wl_copy_on_linux(self) -> None:
        with (
            mock.patch(
                "aicage.runtime.menu.textual._clipboard.platform.system",
                return_value="Linux",
            ),
            mock.patch(
                "aicage.runtime.menu.textual._clipboard.shutil.which"
            ) as which_mock,
        ):
            which_mock.side_effect = lambda name: (
                "/usr/bin/wl-copy" if name == "wl-copy" else None
            )

            command = screen_module.ExtensionsScreen._clipboard_command()

        self.assertEqual(["wl-copy"], command)

    def test_action_focus_next_option_moves_checkbox_focus(self) -> None:
        options = [
            _option("gh", "GitHub CLI", "Desc"),
            _option("act", "act", "Desc"),
        ]
        screen = screen_module.ExtensionsScreen(options, [])
        screen.focused = mock.Mock(id="ext-gh")
        checkbox = mock.Mock()

        with mock.patch.object(screen, "query_one", return_value=checkbox):
            screen.action_focus_next_option()

        checkbox.focus.assert_called_once_with()

    def test_action_focus_previous_option_moves_checkbox_focus(self) -> None:
        options = [
            _option("gh", "GitHub CLI", "Desc"),
            _option("act", "act", "Desc"),
        ]
        screen = screen_module.ExtensionsScreen(options, [])

        with mock.patch.object(screen, "_move_checkbox_focus") as move_focus_mock:
            screen.action_focus_previous_option()

        move_focus_mock.assert_called_once_with(-1)

    def test_action_focus_next_field_moves_from_checkbox_to_buttons(self) -> None:
        option = _option("gh", "GitHub CLI", "Desc")
        screen = screen_module.ExtensionsScreen([option], [])
        screen.focused = mock.Mock(spec=Checkbox)
        cancel_button = mock.Mock(spec=Button)

        with mock.patch.object(screen, "query_one", return_value=cancel_button):
            screen.action_focus_next_field()

        cancel_button.focus.assert_called_once_with()

    def test_action_focus_next_field_uses_default_navigation_outside_checkbox(
        self,
    ) -> None:
        option = _option("gh", "GitHub CLI", "Desc")
        screen = screen_module.ExtensionsScreen([option], [])

        with mock.patch.object(screen, "focus_next") as focus_next_mock:
            screen.action_focus_next_field()

        focus_next_mock.assert_called_once_with()

    def test_action_focus_previous_field_moves_from_buttons_to_checkbox(
        self,
    ) -> None:
        options = [
            _option("gh", "GitHub CLI", "Desc"),
            _option("act", "act", "Desc"),
        ]
        screen = screen_module.ExtensionsScreen(options, [])
        screen.focused = mock.Mock(spec=Button)

        with mock.patch.object(screen, "_focus_checkbox") as focus_checkbox_mock:
            screen.action_focus_previous_field()

        focus_checkbox_mock.assert_called_once_with(1)

    def test_action_focus_previous_field_moves_from_checkbox_to_buttons(
        self,
    ) -> None:
        option = _option("gh", "GitHub CLI", "Desc")
        screen = screen_module.ExtensionsScreen([option], [])
        screen.focused = mock.Mock(spec=Checkbox)
        ok_button = mock.Mock(spec=Button)

        with mock.patch.object(screen, "query_one", return_value=ok_button):
            screen.action_focus_previous_field()

        ok_button.focus.assert_called_once_with()

    def test_on_button_pressed_clear_unchecks_visible_checkboxes(self) -> None:
        options = [
            _option("gh", "GitHub CLI", "Desc"),
            _option("act", "act", "Desc"),
        ]
        screen = screen_module.ExtensionsScreen(options, ["gh", "act"])
        event = mock.Mock()
        event.button.id = "clear"
        checkboxes = {"#ext-gh": mock.Mock(), "#ext-act": mock.Mock()}

        def query_one_side_effect(selector: str, _expected_type: object) -> mock.Mock:
            return checkboxes[selector]

        with mock.patch.object(screen, "query_one", side_effect=query_one_side_effect):
            screen.on_button_pressed(event)

        event.stop.assert_called_once_with()
        self.assertFalse(checkboxes["#ext-gh"].value)
        self.assertFalse(checkboxes["#ext-act"].value)

    def test_focused_checkbox_index_returns_matching_checkbox_index(self) -> None:
        options = [
            _option("gh", "GitHub CLI", "Desc"),
            _option("act", "act", "Desc"),
        ]
        screen = screen_module.ExtensionsScreen(options, [])
        focused = mock.Mock(spec=Checkbox)
        focused.id = "ext-act"
        screen.focused = focused

        value = screen._focused_checkbox_index()

        self.assertEqual(1, value)

    def test_focused_checkbox_index_returns_zero_for_unknown_checkbox_id(self) -> None:
        option = _option("gh", "GitHub CLI", "Desc")
        screen = screen_module.ExtensionsScreen([option], [])
        focused = mock.Mock(spec=Checkbox)
        focused.id = "ext-missing"
        screen.focused = focused

        value = screen._focused_checkbox_index()

        self.assertEqual(0, value)


def _option(
    name: str,
    label: str,
    description: str,
    *,
    has_dockerfile: bool = False,
) -> ExtensionChoiceOption:
    return ExtensionChoiceOption(
        name=name,
        description=f"{label} - {description}",
        has_dockerfile=has_dockerfile,
    )
