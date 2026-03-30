import tempfile
from pathlib import Path
from typing import cast
from unittest import TestCase, mock

from aicage.config.agent.models import AgentMetadata
from aicage.config.base.models import BaseMetadata
from aicage.config.context import ConfigContext
from aicage.config.extensions.loader import ExtensionMetadata
from aicage.config.project_config import AgentConfig, ProjectConfig
from aicage.constants import DEFAULT_EXTENDED_IMAGE_NAME
from aicage.registry.image_selection.extensions.context import ExtensionSelectionContext
from aicage.registry.image_selection.extensions.handler import handle_extension_selection


class ExtensionHandlerTests(TestCase):
    def test_handle_extension_selection_uses_base_when_none_selected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            context = self._context(tmp_dir)
            agent_cfg = AgentConfig()
            selection = ExtensionSelectionContext(
                agent="codex",
                base="ubuntu",
                agent_cfg=agent_cfg,
                agent_metadata=self._agent_metadata(local=False),
                extensions={},
                context=context,
            )
            with mock.patch(
                "aicage.registry.image_selection.extensions.handler.prompt_for_extensions",
                return_value=[],
            ):
                result = handle_extension_selection(selection)

            self.assertEqual("ghcr.io/aicage/aicage:codex-ubuntu", result.image_ref)
            self.assertEqual([], agent_cfg.extensions)
            save_project_mock = cast(mock.Mock, context.store.save_project)
            save_project_mock.assert_called_once()

    def test_handle_extension_selection_persists_selection(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            context = self._context(tmp_dir)
            agent_cfg = AgentConfig()
            extension = self._extension(tmp_dir, "extra")
            selection = ExtensionSelectionContext(
                agent="codex",
                base="ubuntu",
                agent_cfg=agent_cfg,
                agent_metadata=self._agent_metadata(local=False),
                extensions={"extra": extension},
                context=context,
            )
            with (
                mock.patch(
                    "aicage.registry.image_selection.extensions.handler.prompt_for_extensions",
                    return_value=["extra"],
                ),
                mock.patch(
                    "aicage.registry.image_selection.extensions.handler.prompt_for_image_ref",
                    return_value=f"{DEFAULT_EXTENDED_IMAGE_NAME}:custom",
                ),
                mock.patch(
                    "aicage.registry.image_selection.extensions.handler.write_extended_image_config"
                ) as write_mock,
            ):
                result = handle_extension_selection(selection)

            self.assertEqual(f"{DEFAULT_EXTENDED_IMAGE_NAME}:custom", result.image_ref)
            self.assertEqual(["extra"], agent_cfg.extensions)
            write_mock.assert_called_once()
            save_project_mock = cast(mock.Mock, context.store.save_project)
            save_project_mock.assert_called_once()

    @staticmethod
    def _extension(tmp_dir: str, extension_id: str) -> ExtensionMetadata:
        base = Path(tmp_dir)
        return ExtensionMetadata(
            extension_id=extension_id,
            name=extension_id,
            description="desc",
            shares=[],
            directory=base,
            scripts_dir=base,
            dockerfile_path=None,
        )

    @staticmethod
    def _agent_metadata(local: bool) -> AgentMetadata:
        return AgentMetadata(
            agent_path_files=[],
            agent_path_directories=["~/.codex"],
            agent_full_name="Codex",
            agent_homepage="https://example.com",
            build_local=local,
            valid_bases={"ubuntu": "ghcr.io/aicage/aicage:codex-ubuntu"},
            local_definition_dir=Path("/tmp/def"),
        )

    @staticmethod
    def _context(tmp_dir: str) -> ConfigContext:
        bases = {
            "ubuntu": BaseMetadata(
                from_image="ubuntu:latest",
                base_image_distro="Ubuntu",
                base_image_description="Default",
                build_local=False,
                local_definition_dir=Path("/tmp/ubuntu"),
            )
        }
        return ConfigContext(
            store=mock.Mock(),
            project_cfg=ProjectConfig(path=str(Path(tmp_dir) / "project"), agents={}),
            agents={},
            bases=bases,
            extensions={},
        )
