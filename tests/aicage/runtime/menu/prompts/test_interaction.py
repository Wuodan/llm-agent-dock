from unittest import TestCase, mock

from aicage.cli_types import ParsedArgs
from aicage.config.project_config import AgentConfig
from aicage.registry.image_selection.interaction import (
    BaseChoiceRequest,
    ExtensionChoiceOption,
)
from aicage.runtime.menu.prompts import interaction

from .._test_support import _build_context, _build_draft


class ConfigureRunTests(TestCase):
    def test_configure_run(self) -> None:
        resolved = interaction.SimpleInteraction(mock.Mock())
        draft = _build_draft(
            AgentConfig(base="ubuntu"),
            ParsedArgs(
                False,
                "--cli",
                "codex",
                [],
                False,
                ["logs"],
                None,
                menu="simple",
            ),
        )
        selection = mock.Mock()
        selection.base = "ubuntu"

        with (
            mock.patch(
                "aicage.runtime.menu.prompts.interaction.select_agent_image",
                return_value=selection,
            ),
            mock.patch(
                "aicage.runtime.menu.prompts.interaction.prompt_persist_docker_args",
                return_value=True,
            ),
            mock.patch(
                "aicage.runtime.menu.prompts.interaction.prompt_persist_shares",
                return_value=True,
            ),
            mock.patch(
                "aicage.runtime.menu.prompts.interaction.apply_mount_preferences"
            ),
        ):
            result = resolved.configure_run(draft, _build_context(), "codex")

        self.assertIs(selection, result.selection)


class ExecuteImageSetupTests(TestCase):
    def test_execute_image_setup(self) -> None:
        reporter = mock.Mock()
        resolved = interaction.SimpleInteraction(reporter)
        run_config = mock.Mock()

        with mock.patch(
            "aicage.runtime.menu.prompts.interaction.ensure_image"
        ) as ensure:
            resolved.execute_image_setup(run_config, update_approved=False)

        ensure.assert_called_once_with(
            run_config,
            update_approved=False,
            reporter=reporter,
        )


class SimpleSelectionInteractionTests(TestCase):
    def test_choose_base(self) -> None:
        request = BaseChoiceRequest(
            agent="codex",
            context=_build_context(),
            agent_metadata=mock.Mock(),
            default_base="ubuntu",
        )

        with mock.patch(
            "aicage.runtime.menu.prompts.interaction.prompt_for_base",
            return_value="ubuntu",
        ) as prompt_mock:
            choice = interaction._SimpleSelectionInteraction().choose_base(request)

        self.assertEqual("ubuntu", choice)
        prompt_mock.assert_called_once()

    def test_choose_extensions(self) -> None:
        with mock.patch(
            "aicage.runtime.menu.prompts.interaction.prompt_for_extensions",
            return_value=["gh"],
        ) as prompt_mock:
            choice = interaction._SimpleSelectionInteraction().choose_extensions(
                [
                    ExtensionChoiceOption(
                        name="gh",
                        description="GitHub CLI",
                        has_dockerfile=True,
                    )
                ]
            )

        self.assertEqual(["gh"], choice)
        prompt_mock.assert_called_once_with(
            [
                interaction.ExtensionOption(
                    name="gh",
                    description="GitHub CLI",
                    has_dockerfile=True,
                )
            ]
        )

    def test_choose_image_ref(self) -> None:
        with mock.patch(
            "aicage.runtime.menu.prompts.interaction.prompt_for_image_ref",
            return_value="repo:tag",
        ) as prompt_mock:
            choice = interaction._SimpleSelectionInteraction().choose_image_ref(
                "repo:default"
            )

        self.assertEqual("repo:tag", choice)
        prompt_mock.assert_called_once_with("repo:default")


class RuntimeUpdateInteractionTests(TestCase):
    def test_confirm_aicage_update(self) -> None:
        with mock.patch(
            "aicage.runtime.menu.prompts.interaction.prompt_update_aicage",
            return_value=True,
        ) as prompt_mock:
            confirmed = interaction.SimpleInteraction(
                mock.Mock()
            ).confirm_aicage_update(
                "1.0.0",
                "1.1.0",
            )

        self.assertTrue(confirmed)
        prompt_mock.assert_called_once_with("1.0.0", "1.1.0")

    def test_confirm_image_update(self) -> None:
        with mock.patch(
            "aicage.runtime.menu.prompts.interaction.prompt_update_image",
            return_value=True,
        ) as prompt_mock:
            confirmed = interaction.SimpleInteraction(mock.Mock()).confirm_image_update(
                "repo:tag"
            )

        self.assertTrue(confirmed)
        prompt_mock.assert_called_once_with("repo:tag")
