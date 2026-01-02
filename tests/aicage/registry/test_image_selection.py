import tempfile
from pathlib import Path
from unittest import TestCase, mock

from aicage.config import GlobalConfig, ProjectConfig
from aicage.config.context import ConfigContext
from aicage.config.project_config import AgentConfig
from aicage.errors import CliError
from aicage.registry import image_selection
from aicage.registry.images_metadata.models import ImagesMetadata


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

    def test_resolve_non_redistributable_uses_local_tag(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            project_path = Path(tmp_dir) / "project"
            project_path.mkdir()
            store = mock.Mock()
            context = self._build_context(
                store,
                project_path,
                bases=["ubuntu"],
                agent_name="claude",
                redistributable=False,
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
        agent_name: str = "codex",
        redistributable: bool = True,
    ) -> ConfigContext:
        return ConfigContext(
            store=store,
            project_cfg=ProjectConfig(path=str(project_path), agents=agents or {}),
            global_cfg=ImageSelectionTests._global_config(),
            images_metadata=ImageSelectionTests._metadata_with_bases(
                bases,
                agent_name=agent_name,
                redistributable=redistributable,
            ),
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
            version_check_image="ghcr.io/aicage/aicage-image-util:latest",
            agents={},
        )

    @staticmethod
    def _metadata_with_bases(
        bases: list[str],
        agent_name: str = "codex",
        redistributable: bool = True,
    ) -> ImagesMetadata:
        return ImagesMetadata.from_mapping(
            {
                "aicage-image": {"version": "0.3.3"},
                "aicage-image-base": {"version": "0.3.3"},
                "bases": {
                    name: {
                        "root_image": "ubuntu:latest",
                        "base_image_distro": "Ubuntu",
                        "base_image_description": "Default",
                        "os_installer": "distro/debian/install.sh",
                        "test_suite": "default",
                    }
                    for name in bases
                },
                "agent": {
                    agent_name: {
                        "agent_path": "~/.codex",
                        "agent_full_name": "Codex CLI",
                        "agent_homepage": "https://example.com",
                        "redistributable": redistributable,
                        "valid_bases": {
                            name: f"ghcr.io/aicage/aicage:{agent_name}-{name}"
                            for name in bases
                        },
                    }
                },
            }
        )
