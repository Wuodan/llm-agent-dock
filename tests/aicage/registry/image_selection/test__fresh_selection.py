from pathlib import Path
from unittest import TestCase, mock

from aicage.config.config_store import SettingsStore
from aicage.registry._errors import RegistryError
from aicage.registry.image_selection import _fresh_selection
from aicage.registry.image_selection.models import ImageSelection

from ._fixtures import build_context


class ImageSelectionFreshTests(TestCase):
    def test_fresh_selection_prompts_for_base(self) -> None:
        context = build_context(
            mock.Mock(spec=SettingsStore), Path("/test-tmp/project"), bases=["ubuntu"]
        )
        with (
            mock.patch(
                "aicage.registry.image_selection._fresh_selection.handle_extension_selection",
                return_value=ImageSelection(
                    image_ref="aicage:codex-ubuntu",
                    base="ubuntu",
                    extensions=[],
                    agent_image_ref="ghcr.io/aicage/aicage:codex-ubuntu",
                ),
            ) as handle_mock,
        ):
            selection = _fresh_selection.fresh_selection(
                agent="codex",
                context=context,
                extensions={},
                selection_interaction=_selection_interaction(),
            )
        self.assertEqual("aicage:codex-ubuntu", selection.image_ref)
        handle_mock.assert_called_once()

    def test_fresh_selection_raises_on_empty_bases(self) -> None:
        context = build_context(
            mock.Mock(spec=SettingsStore), Path("/test-tmp/project"), bases=["ubuntu"]
        )
        with mock.patch(
            "aicage.registry.image_selection._fresh_selection.available_bases",
            return_value=[],
        ):
            with self.assertRaises(RegistryError):
                _fresh_selection.fresh_selection(
                    agent="codex",
                    context=context,
                    extensions={},
                    selection_interaction=mock.Mock(),
                )


def _selection_interaction() -> mock.Mock:
    interaction = mock.Mock()
    interaction.choose_base.return_value = "ubuntu"
    return interaction
