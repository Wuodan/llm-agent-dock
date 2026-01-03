import tempfile
from pathlib import Path
from unittest import TestCase, mock

from aicage.registry._agent_discovery import discover_agents
from aicage.registry.images_metadata.models import ImagesMetadata


class AgentDiscoveryTests(TestCase):
    def test_discover_agents_returns_release_metadata_when_missing_custom_dir(self) -> None:
        metadata = self._metadata_with_bases(["ubuntu"])
        with tempfile.TemporaryDirectory() as tmp_dir:
            missing = Path(tmp_dir) / "missing-custom-agents"
            with mock.patch(
                "aicage.registry.custom_agent.loader.DEFAULT_CUSTOM_AGENTS_DIR",
                str(missing),
            ):
                discovered = discover_agents(metadata, "aicage")
        self.assertIs(discovered, metadata)

    def test_discover_agents_overrides_release_agent(self) -> None:
        metadata = self._metadata_with_bases(["ubuntu"])
        with tempfile.TemporaryDirectory() as tmp_dir:
            custom_dir = Path(tmp_dir)
            agent_dir = custom_dir / "codex"
            agent_dir.mkdir()
            (agent_dir / "agent.yml").write_text(
                "\n".join(
                    [
                        "agent_path: ~/.custom-codex",
                        "agent_full_name: Custom Codex",
                        "agent_homepage: https://example.com",
                    ]
                ),
                encoding="utf-8",
            )
            (agent_dir / "install.sh").write_text("#!/usr/bin/env bash\n", encoding="utf-8")
            (agent_dir / "version.sh").write_text("echo 1.0.0\n", encoding="utf-8")
            with mock.patch(
                "aicage.registry.custom_agent.loader.DEFAULT_CUSTOM_AGENTS_DIR",
                str(custom_dir),
            ):
                discovered = discover_agents(metadata, "aicage")

        agent = discovered.agents["codex"]
        self.assertEqual(custom_dir / "codex", agent.local_definition_dir)
        self.assertEqual({"ubuntu": "aicage:codex-ubuntu"}, agent.valid_bases)

    def test_discover_agents_filters_bases(self) -> None:
        metadata = self._metadata_with_bases(["ubuntu", "fedora", "alpine"])
        with tempfile.TemporaryDirectory() as tmp_dir:
            custom_dir = Path(tmp_dir)
            agent_dir = custom_dir / "custom"
            agent_dir.mkdir()
            (agent_dir / "agent.yml").write_text(
                "\n".join(
                    [
                        "agent_path: ~/.custom",
                        "agent_full_name: Custom",
                        "agent_homepage: https://example.com",
                        "base_exclude:",
                        "  - alpine",
                        "base_distro_exclude:",
                        "  - Fedora",
                    ]
                ),
                encoding="utf-8",
            )
            (agent_dir / "install.sh").write_text("#!/usr/bin/env bash\n", encoding="utf-8")
            (agent_dir / "version.sh").write_text("echo 1.0.0\n", encoding="utf-8")
            with mock.patch(
                "aicage.registry.custom_agent.loader.DEFAULT_CUSTOM_AGENTS_DIR",
                str(custom_dir),
            ):
                discovered = discover_agents(metadata, "aicage")

        agent = discovered.agents["custom"]
        self.assertEqual(custom_dir / "custom", agent.local_definition_dir)
        self.assertEqual({"ubuntu": "aicage:custom-ubuntu"}, agent.valid_bases)

    @staticmethod
    def _metadata_with_bases(bases: list[str]) -> ImagesMetadata:
        return ImagesMetadata.from_mapping(
            {
                "aicage-image": {"version": "0.3.3"},
                "aicage-image-base": {"version": "0.3.3"},
                "bases": {
                    name: {
                        "root_image": "ubuntu:latest",
                        "base_image_distro": name.capitalize(),
                        "base_image_description": "Default",
                        "os_installer": "distro/debian/install.sh",
                        "test_suite": "default",
                    }
                    for name in bases
                },
                "agent": {
                    "codex": {
                        "agent_path": "~/.codex",
                        "agent_full_name": "Codex CLI",
                        "agent_homepage": "https://example.com",
                        "build_local": False,
                        "valid_bases": {
                            name: f"ghcr.io/aicage/aicage:codex-{name}" for name in bases
                        },
                    }
                },
            }
        )
