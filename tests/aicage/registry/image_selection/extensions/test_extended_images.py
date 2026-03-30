from pathlib import Path
from typing import cast
from unittest import TestCase, mock

from aicage.config.agent.models import AgentMetadata
from aicage.config.base.models import BaseMetadata
from aicage.config.context import ConfigContext
from aicage.config.extended_images import ExtendedImageConfig
from aicage.config.extensions.loader import ExtensionMetadata
from aicage.config.project_config import AgentConfig, ProjectConfig
from aicage.constants import DEFAULT_EXTENDED_IMAGE_NAME
from aicage.registry._errors import RegistryError
from aicage.registry.image_selection.extensions.extended_images import (
    apply_extended_selection,
    load_extended_image_options,
    resolve_extended_image,
)
from aicage.runtime.prompts.image_choice import ExtendedImageOption


class ExtendedImageSelectionTests(TestCase):
    def test_load_extended_image_options_filters_agent(self) -> None:
        config = ExtendedImageConfig(
            name="custom",
            agent="codex",
            base="ubuntu",
            extensions=["ext"],
            image_ref=f"{DEFAULT_EXTENDED_IMAGE_NAME}:custom",
            path=Path("/tmp/custom/image-extended.yml"),
        )
        wrong_base = ExtendedImageConfig(
            name="wrong-base",
            agent="codex",
            base="debian",
            extensions=["ext"],
            image_ref=f"{DEFAULT_EXTENDED_IMAGE_NAME}:wrong-base",
            path=Path("/tmp/wrong/image-extended.yml"),
        )
        other = ExtendedImageConfig(
            name="other",
            agent="claude",
            base="ubuntu",
            extensions=["ext"],
            image_ref=f"{DEFAULT_EXTENDED_IMAGE_NAME}:other",
            path=Path("/tmp/other/image-extended.yml"),
        )
        with mock.patch(
            "aicage.registry.image_selection.extensions.extended_images.load_extended_images",
            return_value={"custom": config, "wrong": wrong_base, "other": other},
        ):
            options = load_extended_image_options(
                agent="codex",
                context=self._context(),
            )
        self.assertEqual(["custom", "wrong-base"], [option.name for option in options])

    def test_resolve_extended_image(self) -> None:
        option = ExtendedImageOption(
            name="custom",
            base="ubuntu",
            description="Custom",
            extensions=["ext"],
            image_ref=f"{DEFAULT_EXTENDED_IMAGE_NAME}:custom",
        )
        self.assertEqual(option, resolve_extended_image("custom", [option]))
        with self.assertRaises(RegistryError):
            resolve_extended_image("missing", [option])

    def test_apply_extended_selection_updates_config(self) -> None:
        context = self._context()
        agent_cfg = AgentConfig()
        option = ExtendedImageOption(
            name="custom",
            base="ubuntu",
            description="Custom",
            extensions=["ext"],
            image_ref=f"{DEFAULT_EXTENDED_IMAGE_NAME}:custom",
        )
        selection = apply_extended_selection(
            agent="codex",
            agent_cfg=agent_cfg,
            selected=option,
            agent_metadata=self._agent_metadata(),
            context=context,
        )
        self.assertEqual("ubuntu", agent_cfg.base)
        self.assertEqual(["ext"], agent_cfg.extensions)
        self.assertEqual(f"{DEFAULT_EXTENDED_IMAGE_NAME}:custom", agent_cfg.image_ref)
        save_project_mock = cast(mock.Mock, context.store.save_project)
        save_project_mock.assert_called_once_with(
            Path(context.project_cfg.path),
            context.project_cfg,
        )
        self.assertEqual(f"{DEFAULT_EXTENDED_IMAGE_NAME}:custom", selection.image_ref)

    @staticmethod
    def _extension() -> ExtensionMetadata:
        return ExtensionMetadata(
            extension_id="ext",
            name="Ext",
            description="Desc",
            shares=[],
            directory=Path("/tmp/ext"),
            scripts_dir=Path("/tmp/ext/scripts"),
            dockerfile_path=None,
        )

    @staticmethod
    def _agent_metadata() -> AgentMetadata:
        return AgentMetadata(
            agent_path_files=[],
            agent_path_directories=["~/.codex"],
            agent_full_name="Codex",
            agent_homepage="https://example.com",
            build_local=False,
            valid_bases={"ubuntu": "ghcr.io/aicage/aicage:codex-ubuntu"},
            local_definition_dir=Path("/tmp/def"),
        )

    @staticmethod
    def _context() -> ConfigContext:
        bases = {
            "ubuntu": BaseMetadata(
                from_image="ubuntu:latest",
                base_image_distro="Ubuntu",
                base_image_description="Default",
                build_local=False,
                local_definition_dir=Path("/tmp/ubuntu"),
            )
        }
        extensions = {"ext": ExtendedImageSelectionTests._extension()}
        agents = {"codex": ExtendedImageSelectionTests._agent_metadata()}
        return ConfigContext(
            store=mock.Mock(),
            project_cfg=ProjectConfig(path="/tmp/project", agents={}),
            agents=agents,
            bases=bases,
            extensions=extensions,
        )
