import tempfile
from pathlib import Path
from unittest import TestCase, mock

from aicage.errors import CliError
from aicage.registry.custom_agent.loader import load_custom_agents
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
    BASE_DISTRO_EXCLUDE_KEY,
    BASE_EXCLUDE_KEY,
    BUILD_LOCAL_KEY,
    ImagesMetadata,
)


class CustomAgentLoaderTests(TestCase):
    def test_load_custom_agents_returns_empty_when_missing_dir(self) -> None:
        metadata = self._metadata_with_bases(["ubuntu"])
        with tempfile.TemporaryDirectory() as tmp_dir:
            missing = Path(tmp_dir) / "missing-custom-agents"
            with mock.patch(
                "aicage.registry.custom_agent.loader.DEFAULT_CUSTOM_AGENTS_DIR",
                str(missing),
            ):
                custom_agents = load_custom_agents(metadata, "aicage")
        self.assertEqual({}, custom_agents)

    def test_load_custom_agents_builds_bases(self) -> None:
        metadata = self._metadata_with_bases(["ubuntu", "fedora", "alpine"])
        with tempfile.TemporaryDirectory() as tmp_dir:
            custom_dir = Path(tmp_dir)
            agent_dir = custom_dir / "custom"
            agent_dir.mkdir()
            (agent_dir / "agent.yml").write_text(
                "\n".join(
                    [
                        f"{AGENT_PATH_KEY}: ~/.custom",
                        f"{AGENT_FULL_NAME_KEY}: Custom",
                        f"{AGENT_HOMEPAGE_KEY}: https://example.com",
                        f"{BASE_EXCLUDE_KEY}:",
                        "  - alpine",
                        f"{BASE_DISTRO_EXCLUDE_KEY}:",
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
                custom_agents = load_custom_agents(metadata, "aicage")

        agent = custom_agents["custom"]
        self.assertEqual(custom_dir / "custom", agent.local_definition_dir)
        self.assertEqual({"ubuntu": "aicage:custom-ubuntu"}, agent.valid_bases)

    def test_load_custom_agents_requires_install_and_version(self) -> None:
        metadata = self._metadata_with_bases(["ubuntu"])
        with tempfile.TemporaryDirectory() as tmp_dir:
            custom_dir = Path(tmp_dir)
            agent_dir = custom_dir / "custom"
            agent_dir.mkdir()
            (agent_dir / "agent.yml").write_text(
                "\n".join(
                    [
                        f"{AGENT_PATH_KEY}: ~/.custom",
                        f"{AGENT_FULL_NAME_KEY}: Custom",
                        f"{AGENT_HOMEPAGE_KEY}: https://example.com",
                    ]
                ),
                encoding="utf-8",
            )
            with mock.patch(
                "aicage.registry.custom_agent.loader.DEFAULT_CUSTOM_AGENTS_DIR",
                str(custom_dir),
            ):
                with self.assertRaises(CliError):
                    load_custom_agents(metadata, "aicage")

    @staticmethod
    def _metadata_with_bases(bases: list[str]) -> ImagesMetadata:
        return ImagesMetadata.from_mapping(
            {
                _AICAGE_IMAGE_KEY: {_VERSION_KEY: "0.3.3"},
                _AICAGE_IMAGE_BASE_KEY: {_VERSION_KEY: "0.3.3"},
                _BASES_KEY: {
                    name: {
                        _ROOT_IMAGE_KEY: "ubuntu:latest",
                        _BASE_IMAGE_DISTRO_KEY: name.capitalize(),
                        _BASE_IMAGE_DESCRIPTION_KEY: "Default",
                        _OS_INSTALLER_KEY: "distro/debian/install.sh",
                        _TEST_SUITE_KEY: "default",
                    }
                    for name in bases
                },
                _AGENT_KEY: {
                    "codex": {
                        AGENT_PATH_KEY: "~/.codex",
                        AGENT_FULL_NAME_KEY: "Codex CLI",
                        AGENT_HOMEPAGE_KEY: "https://example.com",
                        BUILD_LOCAL_KEY: False,
                        _VALID_BASES_KEY: {
                            name: f"ghcr.io/aicage/aicage:codex-{name}" for name in bases
                        },
                    }
                },
            }
        )
