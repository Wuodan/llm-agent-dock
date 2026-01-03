import tempfile
from pathlib import Path
from unittest import TestCase

from aicage.errors import CliError
from aicage.registry.images_metadata.models import ImagesMetadata
from aicage.runtime.agent_config import resolve_agent_config


class AgentConfigTests(TestCase):
    def test_resolve_agent_config_reads_metadata_and_creates_dir(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            agent_dir = Path(tmp_dir) / ".codex"
            metadata = ImagesMetadata.from_mapping(
                {
                    "aicage-image": {"version": "0.3.3"},
                    "aicage-image-base": {"version": "0.3.3"},
                    "bases": {
                        "ubuntu": {
                            "root_image": "ubuntu:latest",
                            "base_image_distro": "Ubuntu",
                            "base_image_description": "Default",
                            "os_installer": "distro/debian/install.sh",
                            "test_suite": "default",
                        }
                    },
                    "agent": {
                        "codex": {
                            "agent_path": str(agent_dir),
                            "agent_full_name": "Codex CLI",
                            "agent_homepage": "https://example.com",
                            "build_local": False,
                            "valid_bases": {"ubuntu": "ghcr.io/aicage/aicage:codex-ubuntu"},
                        }
                    },
                }
            )
            config = resolve_agent_config("codex", metadata)
            self.assertEqual(str(agent_dir), config.agent_path)
            self.assertTrue(config.agent_config_host.exists())

    def test_resolve_agent_config_missing_agent_raises(self) -> None:
        metadata = ImagesMetadata.from_mapping(
            {
                "aicage-image": {"version": "0.3.3"},
                "aicage-image-base": {"version": "0.3.3"},
                "bases": {},
                "agent": {},
            }
        )
        with self.assertRaises(CliError):
            resolve_agent_config("codex", metadata)
