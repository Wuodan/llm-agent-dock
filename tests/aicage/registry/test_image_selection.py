import tempfile
from pathlib import Path
from unittest import TestCase, mock

from aicage.config import GlobalConfig, ProjectConfig
from aicage.config.context import ConfigContext
from aicage.config.project_config import AgentConfig
from aicage.errors import CliError
from aicage.registry import image_selection
from aicage.registry.images_metadata.models import (
    _AGENT_KEY,
    _AICAGE_IMAGE_BASE_KEY,
    _AICAGE_IMAGE_KEY,
    _BASE_IMAGE_DESCRIPTION_KEY,
    _BASE_IMAGE_DISTRO_KEY,
    _BASES_KEY,
    _OS_INSTALLER_KEY,
    _ROOT_IMAGE_KEY,
    _TEST_SUITE_KEY,
    _VALID_BASES_KEY,
    _VERSION_KEY,
    AGENT_FULL_NAME_KEY,
    AGENT_HOMEPAGE_KEY,
    AGENT_PATH_KEY,
    BUILD_LOCAL_KEY,
    ImagesMetadata,
)


class ImageSelectionTests(TestCase):
    def test_resolve_uses_existing_base(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            project_path = Path(tmp_dir) / "project"
            project_path.mkdir()
            store = mock.Mock()
            context = self._build_context(
                store,
                project_path,
                bases=["debian", "ubuntu"],
            )
            context.project_cfg.agents["codex"] = AgentConfig(base="debian")
            selection = image_selection.select_agent_image("codex", context)

            self.assertIsInstance(selection, str)
            self.assertEqual("ghcr.io/aicage/aicage:codex-debian", selection)
            store.save_project.assert_not_called()

    def test_resolve_prompts_and_marks_dirty(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            project_path = Path(tmp_dir) / "project"
            project_path.mkdir()
            store = mock.Mock()
            context = self._build_context(
                store,
                project_path,
                bases=["alpine", "ubuntu"],
            )
            with mock.patch(
                "aicage.registry.image_selection.prompt_for_base", return_value="alpine"
            ):
                image_selection.select_agent_image("codex", context)

            self.assertEqual("alpine", context.project_cfg.agents["codex"].base)
            store.save_project.assert_called_once_with(project_path, context.project_cfg)

    def test_resolve_raises_without_bases(self) -> None:
        context = self._build_context(
            mock.Mock(),
            Path("/tmp/project"),
            bases=[],
        )
        with self.assertRaises(CliError):
            image_selection.select_agent_image("codex", context)

    def test_resolve_raises_on_invalid_base(self) -> None:
        context = self._build_context(
            mock.Mock(),
            Path("/tmp/project"),
            bases=["ubuntu"],
            agents={"codex": AgentConfig(base="alpine")},
        )
        with self.assertRaises(CliError):
            image_selection.select_agent_image("codex", context)

    def test_resolve_build_local_uses_local_tag(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            project_path = Path(tmp_dir) / "project"
            project_path.mkdir()
            store = mock.Mock()
            context = ConfigContext(
                store=store,
                project_cfg=ProjectConfig(path=str(project_path), agents={}),
                global_cfg=self._global_config(),
                images_metadata=self._metadata_with_bases(
                    ["ubuntu"],
                    agent_name="claude",
                    build_local=True,
                ),
            )
            context.project_cfg.agents["claude"] = AgentConfig(base="ubuntu")
            selection = image_selection.select_agent_image("claude", context)

            self.assertEqual("aicage:claude-ubuntu", selection)
            store.save_project.assert_not_called()

    @staticmethod
    def _build_context(
        store: mock.Mock,
        project_path: Path,
        bases: list[str],
        agents: dict[str, AgentConfig] | None = None,
    ) -> ConfigContext:
        return ConfigContext(
            store=store,
            project_cfg=ProjectConfig(path=str(project_path), agents=agents or {}),
            global_cfg=ImageSelectionTests._global_config(),
            images_metadata=ImageSelectionTests._metadata_with_bases(bases),
        )

    @staticmethod
    def _global_config() -> GlobalConfig:
        return GlobalConfig(
            image_registry="ghcr.io",
            image_registry_api_url="https://ghcr.io/v2",
            image_registry_api_token_url="https://ghcr.io/token?service=ghcr.io&scope=repository",
            image_repository="aicage/aicage",
            image_base_repository="aicage/aicage-image-base",
            default_image_base="ubuntu",
            version_check_image="ghcr.io/aicage/aicage-image-util:agent-version",
            local_image_repository="aicage",
            agents={},
        )

    @staticmethod
    def _metadata_with_bases(
        bases: list[str],
        agent_name: str = "codex",
        build_local: bool = False,
    ) -> ImagesMetadata:
        return ImagesMetadata.from_mapping(
            {
                _AICAGE_IMAGE_KEY: {_VERSION_KEY: "0.3.3"},
                _AICAGE_IMAGE_BASE_KEY: {_VERSION_KEY: "0.3.3"},
                _BASES_KEY: {
                    name: {
                        _ROOT_IMAGE_KEY: "ubuntu:latest",
                        _BASE_IMAGE_DISTRO_KEY: "Ubuntu",
                        _BASE_IMAGE_DESCRIPTION_KEY: "Default",
                        _OS_INSTALLER_KEY: "distro/debian/install.sh",
                        _TEST_SUITE_KEY: "default",
                    }
                    for name in bases
                },
                _AGENT_KEY: {
                    agent_name: {
                        AGENT_PATH_KEY: "~/.codex",
                        AGENT_FULL_NAME_KEY: "Codex CLI",
                        AGENT_HOMEPAGE_KEY: "https://example.com",
                        BUILD_LOCAL_KEY: build_local,
                        _VALID_BASES_KEY: {
                            name: f"ghcr.io/aicage/aicage:{agent_name}-{name}"
                            for name in bases
                        },
                    }
                },
            }
        )
