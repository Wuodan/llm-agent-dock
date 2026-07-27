import tempfile
from pathlib import Path
from unittest import TestCase, mock

from aicage.config.agent._custom_loader import load_custom_agents
from aicage.config.agent.models import (
    _AGENT_FULL_NAME_KEY,
    _AGENT_HOMEPAGE_KEY,
    _AGENT_PATH_KEY,
    _BASE_DISTRO_EXCLUDE_KEY,
    _BASE_EXCLUDE_KEY,
)
from aicage.config.base.models import BaseMetadata
from aicage.config.errors import ConfigError
from aicage.config.image_refs import local_image_ref
from aicage.constants import LOCAL_IMAGE_REPOSITORY
from aicage.paths import CUSTOM_AGENT_DEFINITION_FILES


class CustomAgentLoaderTests(TestCase):
    def test_load_custom_agents_returns_empty_when_missing_dir(self) -> None:
        bases = self._bases(["ubuntu"])
        with tempfile.TemporaryDirectory() as tmp_dir:
            missing = Path(tmp_dir) / "missing-custom-agents"
            with mock.patch(
                "aicage.config.agent._custom_loader.CUSTOM_AGENTS_DIR",
                missing,
            ):
                custom_agents = load_custom_agents(bases)
        self.assertEqual({}, custom_agents)

    def test_load_custom_agents_builds_bases(self) -> None:
        bases = self._bases(["ubuntu", "fedora", "alpine"])
        with tempfile.TemporaryDirectory() as tmp_dir:
            custom_dir = Path(tmp_dir)
            agent_dir = custom_dir / "custom"
            agent_dir.mkdir()
            (agent_dir / CUSTOM_AGENT_DEFINITION_FILES[0]).write_text(
                "\n".join(
                    [
                        f"{_AGENT_PATH_KEY}:",
                        "  directories:",
                        "    - ~/.custom",
                        f"{_AGENT_FULL_NAME_KEY}: Custom",
                        f"{_AGENT_HOMEPAGE_KEY}: https://example.com",
                        f"{_BASE_EXCLUDE_KEY}:",
                        "  - alpine",
                        f"{_BASE_DISTRO_EXCLUDE_KEY}:",
                        "  - Fedora",
                    ]
                ),
                encoding="utf-8",
            )
            (agent_dir / "install.sh").write_text(
                "#!/usr/bin/env bash\n", encoding="utf-8"
            )
            (agent_dir / "version.sh").write_text("echo 1.0.0\n", encoding="utf-8")
            with mock.patch(
                "aicage.config.agent._custom_loader.CUSTOM_AGENTS_DIR",
                custom_dir,
            ):
                custom_agents = load_custom_agents(bases)

        agent = custom_agents["custom"]
        self.assertEqual(custom_dir / "custom", agent.local_definition_dir)
        self.assertEqual(
            {"ubuntu": local_image_ref(LOCAL_IMAGE_REPOSITORY, "custom", "ubuntu")},
            agent.valid_bases,
        )

    def test_load_custom_agents_requires_install_and_version(self) -> None:
        bases = self._bases(["ubuntu"])
        with tempfile.TemporaryDirectory() as tmp_dir:
            custom_dir = Path(tmp_dir)
            agent_dir = custom_dir / "custom"
            agent_dir.mkdir()
            (agent_dir / CUSTOM_AGENT_DEFINITION_FILES[0]).write_text(
                "\n".join(
                    [
                        f"{_AGENT_PATH_KEY}:",
                        "  directories:",
                        "    - ~/.custom",
                        f"{_AGENT_FULL_NAME_KEY}: Custom",
                        f"{_AGENT_HOMEPAGE_KEY}: https://example.com",
                    ]
                ),
                encoding="utf-8",
            )
            with mock.patch(
                "aicage.config.agent._custom_loader.CUSTOM_AGENTS_DIR",
                custom_dir,
            ):
                with self.assertRaises(ConfigError):
                    load_custom_agents(bases)

    @staticmethod
    def _bases(bases: list[str]) -> dict[str, BaseMetadata]:
        return {
            name: BaseMetadata(
                from_image="ubuntu:latest",
                base_image_distro=name.capitalize(),
                base_image_description="Default",
                architectures=["amd64", "arm64"],
                build_local=False,
                local_definition_dir=Path(f"/test-tmp/{name}"),
            )
            for name in bases
        }
