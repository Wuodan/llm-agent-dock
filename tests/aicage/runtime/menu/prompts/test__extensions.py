from unittest import TestCase, mock

from aicage.runtime._errors import RuntimeExecutionError
from aicage.runtime.menu.prompts._extensions import (
    ExtensionOption,
    prompt_for_extensions,
)


class PromptExtensionsTests(TestCase):
    def test_prompt_for_extensions_returns_empty_for_no_options(self) -> None:
        self.assertEqual([], prompt_for_extensions([]))

    def test_prompt_for_extensions_accepts_numbers_and_names(self) -> None:
        options = [
            ExtensionOption(name="one", description="First"),
            ExtensionOption(name="two", description="Second"),
        ]
        with (
            mock.patch("aicage.runtime.menu.prompts._extensions.ensure_tty_for_prompt"),
            mock.patch("builtins.input", return_value="2,one"),
        ):
            selection = prompt_for_extensions(options)
        self.assertEqual(["one", "two"], selection)

    def test_prompt_for_extensions_returns_prompt_order_for_custom_input_order(
        self,
    ) -> None:
        options = [
            ExtensionOption(name="act", description="Act"),
            ExtensionOption(name="cosign", description="Cosign"),
            ExtensionOption(name="gh", description="GitHub CLI"),
            ExtensionOption(name="regctl", description="regctl"),
        ]
        with (
            mock.patch("aicage.runtime.menu.prompts._extensions.ensure_tty_for_prompt"),
            mock.patch("builtins.input", return_value="4,3,2,1"),
        ):
            selection = prompt_for_extensions(options)
        self.assertEqual(["act", "cosign", "gh", "regctl"], selection)

    def test_prompt_for_extensions_returns_empty_on_blank_input(self) -> None:
        options = [
            ExtensionOption(name="one", description="First"),
            ExtensionOption(name="two", description="Second"),
        ]
        with (
            mock.patch("aicage.runtime.menu.prompts._extensions.ensure_tty_for_prompt"),
            mock.patch("builtins.input", return_value=""),
        ):
            selection = prompt_for_extensions(options)
        self.assertEqual([], selection)

    def test_prompt_for_extensions_rejects_duplicates(self) -> None:
        options = [
            ExtensionOption(name="one", description="First"),
            ExtensionOption(name="two", description="Second"),
        ]
        with (
            mock.patch("aicage.runtime.menu.prompts._extensions.ensure_tty_for_prompt"),
            mock.patch("builtins.input", return_value="1,one"),
        ):
            with self.assertRaises(RuntimeExecutionError):
                prompt_for_extensions(options)

    def test_prompt_for_extensions_rejects_invalid_choice(self) -> None:
        options = [
            ExtensionOption(name="one", description="First"),
            ExtensionOption(name="two", description="Second"),
        ]
        with (
            mock.patch("aicage.runtime.menu.prompts._extensions.ensure_tty_for_prompt"),
            mock.patch("builtins.input", return_value="3"),
        ):
            with self.assertRaises(RuntimeExecutionError):
                prompt_for_extensions(options)

    def test_prompt_for_extensions_rejects_invalid_name(self) -> None:
        options = [
            ExtensionOption(name="one", description="First"),
            ExtensionOption(name="two", description="Second"),
        ]
        with (
            mock.patch("aicage.runtime.menu.prompts._extensions.ensure_tty_for_prompt"),
            mock.patch("builtins.input", return_value="unknown"),
        ):
            with self.assertRaises(RuntimeExecutionError):
                prompt_for_extensions(options)

    def test_prompt_for_extensions_prints_heading_before_dockerfile_extensions(
        self,
    ) -> None:
        options = [
            ExtensionOption(name="one", description="First"),
            ExtensionOption(
                name="two",
                description="Second",
                has_dockerfile=True,
            ),
        ]
        with (
            mock.patch("aicage.runtime.menu.prompts._extensions.ensure_tty_for_prompt"),
            mock.patch("builtins.input", return_value=""),
            mock.patch("builtins.print") as print_mock,
        ):
            prompt_for_extensions(options)

        self.assertEqual(
            [
                mock.call(
                    "Select extensions to add (comma-separated numbers or names, empty for none):"
                ),
                mock.call("  1) one: First"),
                mock.call("  Extensions with custom Dockerfiles:"),
                mock.call("  2) two: Second"),
            ],
            print_mock.call_args_list,
        )
