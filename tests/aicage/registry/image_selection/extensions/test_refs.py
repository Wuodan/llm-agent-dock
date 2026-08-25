from pathlib import Path
from unittest import TestCase, mock

from aicage.config.agent.models import AgentMetadata
from aicage.config.base.models import BaseMetadata
from aicage.config.context import ConfigContext
from aicage.config.project_config import _ProjectConfig
from aicage.constants import IMAGE_REGISTRY, IMAGE_REPOSITORY, LOCAL_IMAGE_REPOSITORY
from aicage.paths import CUSTOM_BASES_DIR
from aicage.registry.image_selection.extensions.refs import agent_image_ref


class ExtensionRefsTests(TestCase):
    def test_agent_image_ref_uses_local_repo_for_custom_agent(self) -> None:
        context = self._context()
        agent_metadata = AgentMetadata(
            agent_path_files=[],
            agent_path_directories=["~/.codex"],
            agent_full_name="Codex",
            agent_homepage="https://example.com",
            build_local=True,
            valid_bases={"ubuntu": f"{IMAGE_REGISTRY}/{IMAGE_REPOSITORY}:codex-ubuntu"},
            local_definition_dir=Path("/test-tmp/def"),
        )

        result = agent_image_ref(agent_metadata, "codex", "ubuntu", context)

        self.assertEqual(f"{LOCAL_IMAGE_REPOSITORY}:codex-ubuntu", result)

    def test_agent_image_ref_uses_remote_for_builtin_agent(self) -> None:
        context = self._context()
        agent_metadata = AgentMetadata(
            agent_path_files=[],
            agent_path_directories=["~/.codex"],
            agent_full_name="Codex",
            agent_homepage="https://example.com",
            build_local=False,
            valid_bases={"ubuntu": f"{IMAGE_REGISTRY}/{IMAGE_REPOSITORY}:codex-ubuntu"},
            local_definition_dir=Path("/test-tmp/def"),
        )

        result = agent_image_ref(agent_metadata, "codex", "ubuntu", context)

        self.assertEqual(f"{IMAGE_REGISTRY}/{IMAGE_REPOSITORY}:codex-ubuntu", result)

    def test_agent_image_ref_uses_local_for_custom_base(self) -> None:
        context = self._context()
        agent_metadata = AgentMetadata(
            agent_path_files=[],
            agent_path_directories=["~/.codex"],
            agent_full_name="Codex",
            agent_homepage="https://example.com",
            build_local=False,
            valid_bases={"custom": f"{IMAGE_REGISTRY}/{IMAGE_REPOSITORY}:codex-custom"},
            local_definition_dir=Path("/test-tmp/def"),
        )
        context.bases["custom"] = BaseMetadata(
            from_image="ubuntu:latest",
            base_image_distro="Ubuntu",
            base_image_description="Custom",
            architectures=["amd64", "arm64"],
            build_local=True,
            local_definition_dir=CUSTOM_BASES_DIR / "custom",
        )
        result = agent_image_ref(agent_metadata, "codex", "custom", context)

        self.assertEqual(f"{LOCAL_IMAGE_REPOSITORY}:codex-custom", result)

    @staticmethod
    def _context() -> ConfigContext:
        bases = {
            "ubuntu": BaseMetadata(
                from_image="ubuntu:latest",
                base_image_distro="Ubuntu",
                base_image_description="Default",
                architectures=["amd64", "arm64"],
                build_local=False,
                local_definition_dir=Path("/test-tmp/ubuntu"),
            )
        }
        return ConfigContext(
            store=mock.Mock(),
            project_cfg=_ProjectConfig(path="/test-tmp/project", agents={}),
            agents={},
            bases=bases,
            extensions={},
        )
