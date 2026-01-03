from unittest import TestCase

from aicage.errors import CliError
from aicage.registry.images_metadata.models import ImagesMetadata


class ImagesMetadataModelTests(TestCase):
    def test_from_yaml_parses_valid_payload(self) -> None:
        payload = """
aicage-image:
  version: 0.3.3
aicage-image-base:
  version: 0.3.3
bases:
  ubuntu:
    root_image: ubuntu:latest
    base_image_distro: Ubuntu
    base_image_description: Good default
    os_installer: distro/debian/install.sh
    test_suite: default
agent:
  codex:
    agent_path: ~/.codex
    agent_full_name: Codex CLI
    agent_homepage: https://example.com
    build_local: false
    valid_bases:
      ubuntu: ghcr.io/aicage/aicage:codex-ubuntu
        """
        metadata = ImagesMetadata.from_yaml(payload)
        self.assertEqual("0.3.3", metadata.aicage_image.version)
        self.assertEqual("0.3.3", metadata.aicage_image_base.version)
        self.assertIn("ubuntu", metadata.bases)
        self.assertIn("codex", metadata.agents)
        self.assertEqual(
            {"ubuntu": "ghcr.io/aicage/aicage:codex-ubuntu"},
            metadata.agents["codex"].valid_bases,
        )

    def test_from_yaml_rejects_invalid_payload(self) -> None:
        with self.assertRaises(CliError):
            ImagesMetadata.from_yaml("aicage-image: [")

    def test_from_yaml_requires_mapping(self) -> None:
        with self.assertRaises(CliError):
            ImagesMetadata.from_yaml("- item")

    def test_from_mapping_rejects_unknown_top_level_keys(self) -> None:
        data = {
            "aicage-image": {"version": "0.3.3"},
            "aicage-image-base": {"version": "0.3.3"},
            "bases": {},
            "agent": {},
            "extra": {},
        }
        with self.assertRaises(CliError):
            ImagesMetadata.from_mapping(data)

    def test_from_mapping_rejects_unknown_agent_keys(self) -> None:
        data = {
            "aicage-image": {"version": "0.3.3"},
            "aicage-image-base": {"version": "0.3.3"},
            "bases": {},
            "agent": {
                "codex": {
                    "agent_path": "~/.codex",
                    "agent_full_name": "Codex CLI",
                    "agent_homepage": "https://example.com",
                    "build_local": False,
                    "valid_bases": {"ubuntu": "ghcr.io/aicage/aicage:codex-ubuntu"},
                    "extra": "nope",
                }
            },
        }
        with self.assertRaises(CliError):
            ImagesMetadata.from_mapping(data)

    def test_from_mapping_rejects_missing_required_keys(self) -> None:
        with self.assertRaises(CliError):
            ImagesMetadata.from_mapping({})

    def test_from_mapping_rejects_missing_agent_required_keys(self) -> None:
        data = {
            "aicage-image": {"version": "0.3.3"},
            "aicage-image-base": {"version": "0.3.3"},
            "bases": {},
            "agent": {
                "codex": {
                    "agent_path": "~/.codex",
                    "agent_full_name": "Codex CLI",
                    "agent_homepage": "https://example.com",
                    "valid_bases": {"ubuntu": "ghcr.io/aicage/aicage:codex-ubuntu"},
                }
            },
        }
        with self.assertRaises(CliError):
            ImagesMetadata.from_mapping(data)

    def test_from_mapping_rejects_non_string_base_key(self) -> None:
        data = {
            "aicage-image": {"version": "0.3.3"},
            "aicage-image-base": {"version": "0.3.3"},
            "bases": {
                1: {
                    "root_image": "ubuntu:latest",
                    "base_image_distro": "Ubuntu",
                    "base_image_description": "Default",
                    "os_installer": "distro/debian/install.sh",
                    "test_suite": "default",
                }
            },
            "agent": {},
        }
        with self.assertRaises(CliError):
            ImagesMetadata.from_mapping(data)

    def test_from_mapping_rejects_non_string_agent_key(self) -> None:
        data = {
            "aicage-image": {"version": "0.3.3"},
            "aicage-image-base": {"version": "0.3.3"},
            "bases": {},
            "agent": {
                1: {
                    "agent_path": "~/.codex",
                    "agent_full_name": "Codex CLI",
                    "agent_homepage": "https://example.com",
                    "build_local": False,
                    "valid_bases": {"ubuntu": "ghcr.io/aicage/aicage:codex-ubuntu"},
                }
            },
        }
        with self.assertRaises(CliError):
            ImagesMetadata.from_mapping(data)

    def test_from_mapping_rejects_invalid_valid_bases_keys(self) -> None:
        data = {
            "aicage-image": {"version": "0.3.3"},
            "aicage-image-base": {"version": "0.3.3"},
            "bases": {},
            "agent": {
                "codex": {
                    "agent_path": "~/.codex",
                    "agent_full_name": "Codex CLI",
                    "agent_homepage": "https://example.com",
                    "build_local": False,
                    "valid_bases": {1: "ghcr.io/aicage/aicage:codex-ubuntu"},
                }
            },
        }
        with self.assertRaises(CliError):
            ImagesMetadata.from_mapping(data)

    def test_from_mapping_rejects_invalid_valid_bases_values(self) -> None:
        data = {
            "aicage-image": {"version": "0.3.3"},
            "aicage-image-base": {"version": "0.3.3"},
            "bases": {},
            "agent": {
                "codex": {
                    "agent_path": "~/.codex",
                    "agent_full_name": "Codex CLI",
                    "agent_homepage": "https://example.com",
                    "build_local": False,
                    "valid_bases": {"ubuntu": ""},
                }
            },
        }
        with self.assertRaises(CliError):
            ImagesMetadata.from_mapping(data)

    def test_from_mapping_rejects_invalid_agent_bool(self) -> None:
        data = {
            "aicage-image": {"version": "0.3.3"},
            "aicage-image-base": {"version": "0.3.3"},
            "bases": {},
            "agent": {
                "codex": {
                    "agent_path": "~/.codex",
                    "agent_full_name": "Codex CLI",
                    "agent_homepage": "https://example.com",
                    "build_local": "yes",
                    "valid_bases": {"ubuntu": "ghcr.io/aicage/aicage:codex-ubuntu"},
                }
            },
        }
        with self.assertRaises(CliError):
            ImagesMetadata.from_mapping(data)

    def test_from_mapping_rejects_invalid_agent_list(self) -> None:
        data = {
            "aicage-image": {"version": "0.3.3"},
            "aicage-image-base": {"version": "0.3.3"},
            "bases": {},
            "agent": {
                "codex": {
                    "agent_path": "~/.codex",
                    "agent_full_name": "Codex CLI",
                    "agent_homepage": "https://example.com",
                    "build_local": False,
                    "valid_bases": {"ubuntu": "ghcr.io/aicage/aicage:codex-ubuntu"},
                    "base_exclude": [1],
                }
            },
        }
        with self.assertRaises(CliError):
            ImagesMetadata.from_mapping(data)

    def test_from_mapping_rejects_invalid_agent_list_type(self) -> None:
        data = {
            "aicage-image": {"version": "0.3.3"},
            "aicage-image-base": {"version": "0.3.3"},
            "bases": {},
            "agent": {
                "codex": {
                    "agent_path": "~/.codex",
                    "agent_full_name": "Codex CLI",
                    "agent_homepage": "https://example.com",
                    "build_local": False,
                    "valid_bases": {"ubuntu": "ghcr.io/aicage/aicage:codex-ubuntu"},
                    "base_exclude": "ubuntu",
                }
            },
        }
        with self.assertRaises(CliError):
            ImagesMetadata.from_mapping(data)

    def test_from_mapping_rejects_empty_agent_fields(self) -> None:
        data = {
            "aicage-image": {"version": "0.3.3"},
            "aicage-image-base": {"version": "0.3.3"},
            "bases": {},
            "agent": {
                "codex": {
                    "agent_path": " ",
                    "agent_full_name": "Codex CLI",
                    "agent_homepage": "https://example.com",
                    "build_local": False,
                    "valid_bases": {"ubuntu": "ghcr.io/aicage/aicage:codex-ubuntu"},
                }
            },
        }
        with self.assertRaises(CliError):
            ImagesMetadata.from_mapping(data)

    def test_from_mapping_accepts_valid_exclude_list(self) -> None:
        data = {
            "aicage-image": {"version": "0.3.3"},
            "aicage-image-base": {"version": "0.3.3"},
            "bases": {},
            "agent": {
                "codex": {
                    "agent_path": "~/.codex",
                    "agent_full_name": "Codex CLI",
                    "agent_homepage": "https://example.com",
                    "build_local": False,
                    "valid_bases": {"ubuntu": "ghcr.io/aicage/aicage:codex-ubuntu"},
                    "base_exclude": ["ubuntu"],
                }
            },
        }
        metadata = ImagesMetadata.from_mapping(data)
        self.assertEqual(["ubuntu"], metadata.agents["codex"].base_exclude)

    def test_from_mapping_rejects_invalid_bases_mapping(self) -> None:
        data = {
            "aicage-image": {"version": "0.3.3"},
            "aicage-image-base": {"version": "0.3.3"},
            "bases": [],
            "agent": {},
        }
        with self.assertRaises(CliError):
            ImagesMetadata.from_mapping(data)
