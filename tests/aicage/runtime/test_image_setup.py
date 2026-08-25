from unittest import TestCase, mock

from aicage.registry.ensure_image import ImageSetupAction, ImageSetupPlan
from aicage.runtime import image_setup


class PrepareImageTests(TestCase):
    def test_prepare_image_skips_execution_when_setup_not_needed(self) -> None:
        run_config = mock.Mock()
        interaction = mock.Mock()

        with (
            mock.patch(
                "aicage.runtime.image_setup.image_setup_plan",
                return_value=ImageSetupPlan(
                    action=ImageSetupAction.SKIP,
                    image_ref="repo:tag",
                ),
            ),
        ):
            image_setup.prepare_image(run_config, interaction)

        interaction.execute_image_setup.assert_not_called()

    def test_prepare_image_runs_execution_when_setup_is_needed(self) -> None:
        run_config = mock.Mock()
        interaction = mock.Mock()

        with (
            mock.patch(
                "aicage.runtime.image_setup.image_setup_plan",
                return_value=ImageSetupPlan(
                    action=ImageSetupAction.SETUP,
                    image_ref="repo:tag",
                ),
            ),
        ):
            image_setup.prepare_image(run_config, interaction)

        interaction.execute_image_setup.assert_called_once()

    def test_prepare_image_confirms_update_through_interaction(self) -> None:
        run_config = mock.Mock()
        run_config.selection.base_image_ref = "wrong-repo:tag"
        interaction = mock.Mock(confirm_image_update=mock.Mock(return_value=True))

        with (
            mock.patch(
                "aicage.runtime.image_setup.image_setup_plan",
                return_value=ImageSetupPlan(
                    action=ImageSetupAction.CONFIRM_UPDATE_AND_DO_SETUP,
                    image_ref="repo:tag",
                ),
            ),
        ):
            image_setup.prepare_image(run_config, interaction)

        interaction.confirm_image_update.assert_called_once_with("repo:tag")
        interaction.execute_image_setup.assert_called_once_with(run_config, True)

    def test_prepare_image_passes_rejected_update_to_ensure_image(self) -> None:
        run_config = mock.Mock()
        run_config.selection.base_image_ref = "repo:tag"
        interaction = mock.Mock(confirm_image_update=mock.Mock(return_value=False))

        with (
            mock.patch(
                "aicage.runtime.image_setup.image_setup_plan",
                return_value=ImageSetupPlan(
                    action=ImageSetupAction.CONFIRM_UPDATE_AND_DO_SETUP,
                    image_ref="repo:tag",
                ),
            ),
        ):
            image_setup.prepare_image(run_config, interaction)

        interaction.confirm_image_update.assert_called_once_with("repo:tag")
        interaction.execute_image_setup.assert_called_once_with(run_config, False)

    def test_prepare_image_skips_execution_when_only_confirmation_declined(
        self,
    ) -> None:
        run_config = mock.Mock()
        run_config.selection.base_image_ref = "repo:tag"
        interaction = mock.Mock(confirm_image_update=mock.Mock(return_value=False))

        with (
            mock.patch(
                "aicage.runtime.image_setup.image_setup_plan",
                return_value=ImageSetupPlan(
                    action=ImageSetupAction.CONFIRM_UPDATE,
                    image_ref="repo:tag",
                ),
            ),
        ):
            image_setup.prepare_image(run_config, interaction)

        interaction.confirm_image_update.assert_called_once_with("repo:tag")
        interaction.execute_image_setup.assert_not_called()
