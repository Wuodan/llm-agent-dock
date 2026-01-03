from unittest import TestCase

from aicage.errors import CliError
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
    BASE_EXCLUDE_KEY,
    BUILD_LOCAL_KEY,
    ImagesMetadata,
)


class ImagesMetadataModelTests(TestCase):
    def test_from_yaml_parses_valid_payload(self) -> None:
        payload = f"""
{_AICAGE_IMAGE_KEY}:
  {_VERSION_KEY}: 0.3.3
{_AICAGE_IMAGE_BASE_KEY}:
  {_VERSION_KEY}: 0.3.3
{_BASES_KEY}:
  ubuntu:
    {_ROOT_IMAGE_KEY}: ubuntu:latest
    {_BASE_IMAGE_DISTRO_KEY}: Ubuntu
    {_BASE_IMAGE_DESCRIPTION_KEY}: Good default
    {_OS_INSTALLER_KEY}: distro/debian/install.sh
    {_TEST_SUITE_KEY}: default
{_AGENT_KEY}:
  codex:
    {AGENT_PATH_KEY}: ~/.codex
    {AGENT_FULL_NAME_KEY}: Codex CLI
    {AGENT_HOMEPAGE_KEY}: https://example.com
    {BUILD_LOCAL_KEY}: false
    {_VALID_BASES_KEY}:
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
            ImagesMetadata.from_yaml(f"{_AICAGE_IMAGE_KEY}: [")

    def test_from_yaml_requires_mapping(self) -> None:
        with self.assertRaises(CliError):
            ImagesMetadata.from_yaml("- item")

    def test_from_mapping_rejects_unknown_top_level_keys(self) -> None:
        data = {
            _AICAGE_IMAGE_KEY: {_VERSION_KEY: "0.3.3"},
            _AICAGE_IMAGE_BASE_KEY: {_VERSION_KEY: "0.3.3"},
            _BASES_KEY: {},
            _AGENT_KEY: {},
            "extra": {},
        }
        with self.assertRaises(CliError):
            ImagesMetadata.from_mapping(data)

    def test_from_mapping_rejects_unknown_agent_keys(self) -> None:
        data = {
            _AICAGE_IMAGE_KEY: {_VERSION_KEY: "0.3.3"},
            _AICAGE_IMAGE_BASE_KEY: {_VERSION_KEY: "0.3.3"},
            _BASES_KEY: {},
            _AGENT_KEY: {
                "codex": {
                    AGENT_PATH_KEY: "~/.codex",
                    AGENT_FULL_NAME_KEY: "Codex CLI",
                    AGENT_HOMEPAGE_KEY: "https://example.com",
                    BUILD_LOCAL_KEY: False,
                    _VALID_BASES_KEY: {"ubuntu": "ghcr.io/aicage/aicage:codex-ubuntu"},
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
            _AICAGE_IMAGE_KEY: {_VERSION_KEY: "0.3.3"},
            _AICAGE_IMAGE_BASE_KEY: {_VERSION_KEY: "0.3.3"},
            _BASES_KEY: {},
            _AGENT_KEY: {
                "codex": {
                    AGENT_PATH_KEY: "~/.codex",
                    AGENT_FULL_NAME_KEY: "Codex CLI",
                    AGENT_HOMEPAGE_KEY: "https://example.com",
                    _VALID_BASES_KEY: {"ubuntu": "ghcr.io/aicage/aicage:codex-ubuntu"},
                }
            },
        }
        with self.assertRaises(CliError):
            ImagesMetadata.from_mapping(data)

    def test_from_mapping_rejects_non_string_base_key(self) -> None:
        data = {
            _AICAGE_IMAGE_KEY: {_VERSION_KEY: "0.3.3"},
            _AICAGE_IMAGE_BASE_KEY: {_VERSION_KEY: "0.3.3"},
            _BASES_KEY: {
                1: {
                    _ROOT_IMAGE_KEY: "ubuntu:latest",
                    _BASE_IMAGE_DISTRO_KEY: "Ubuntu",
                    _BASE_IMAGE_DESCRIPTION_KEY: "Default",
                    _OS_INSTALLER_KEY: "distro/debian/install.sh",
                    _TEST_SUITE_KEY: "default",
                }
            },
            _AGENT_KEY: {},
        }
        with self.assertRaises(CliError):
            ImagesMetadata.from_mapping(data)

    def test_from_mapping_rejects_non_string_agent_key(self) -> None:
        data = {
            _AICAGE_IMAGE_KEY: {_VERSION_KEY: "0.3.3"},
            _AICAGE_IMAGE_BASE_KEY: {_VERSION_KEY: "0.3.3"},
            _BASES_KEY: {},
            _AGENT_KEY: {
                1: {
                    AGENT_PATH_KEY: "~/.codex",
                    AGENT_FULL_NAME_KEY: "Codex CLI",
                    AGENT_HOMEPAGE_KEY: "https://example.com",
                    BUILD_LOCAL_KEY: False,
                    _VALID_BASES_KEY: {"ubuntu": "ghcr.io/aicage/aicage:codex-ubuntu"},
                }
            },
        }
        with self.assertRaises(CliError):
            ImagesMetadata.from_mapping(data)

    def test_from_mapping_rejects_invalid_valid_bases_keys(self) -> None:
        data = {
            _AICAGE_IMAGE_KEY: {_VERSION_KEY: "0.3.3"},
            _AICAGE_IMAGE_BASE_KEY: {_VERSION_KEY: "0.3.3"},
            _BASES_KEY: {},
            _AGENT_KEY: {
                "codex": {
                    AGENT_PATH_KEY: "~/.codex",
                    AGENT_FULL_NAME_KEY: "Codex CLI",
                    AGENT_HOMEPAGE_KEY: "https://example.com",
                    BUILD_LOCAL_KEY: False,
                    _VALID_BASES_KEY: {1: "ghcr.io/aicage/aicage:codex-ubuntu"},
                }
            },
        }
        with self.assertRaises(CliError):
            ImagesMetadata.from_mapping(data)

    def test_from_mapping_rejects_invalid_valid_bases_values(self) -> None:
        data = {
            _AICAGE_IMAGE_KEY: {_VERSION_KEY: "0.3.3"},
            _AICAGE_IMAGE_BASE_KEY: {_VERSION_KEY: "0.3.3"},
            _BASES_KEY: {},
            _AGENT_KEY: {
                "codex": {
                    AGENT_PATH_KEY: "~/.codex",
                    AGENT_FULL_NAME_KEY: "Codex CLI",
                    AGENT_HOMEPAGE_KEY: "https://example.com",
                    BUILD_LOCAL_KEY: False,
                    _VALID_BASES_KEY: {"ubuntu": ""},
                }
            },
        }
        with self.assertRaises(CliError):
            ImagesMetadata.from_mapping(data)

    def test_from_mapping_rejects_invalid_agent_bool(self) -> None:
        data = {
            _AICAGE_IMAGE_KEY: {_VERSION_KEY: "0.3.3"},
            _AICAGE_IMAGE_BASE_KEY: {_VERSION_KEY: "0.3.3"},
            _BASES_KEY: {},
            _AGENT_KEY: {
                "codex": {
                    AGENT_PATH_KEY: "~/.codex",
                    AGENT_FULL_NAME_KEY: "Codex CLI",
                    AGENT_HOMEPAGE_KEY: "https://example.com",
                    BUILD_LOCAL_KEY: "yes",
                    _VALID_BASES_KEY: {"ubuntu": "ghcr.io/aicage/aicage:codex-ubuntu"},
                }
            },
        }
        with self.assertRaises(CliError):
            ImagesMetadata.from_mapping(data)

    def test_from_mapping_rejects_invalid_agent_list(self) -> None:
        data = {
            _AICAGE_IMAGE_KEY: {_VERSION_KEY: "0.3.3"},
            _AICAGE_IMAGE_BASE_KEY: {_VERSION_KEY: "0.3.3"},
            _BASES_KEY: {},
            _AGENT_KEY: {
                "codex": {
                    AGENT_PATH_KEY: "~/.codex",
                    AGENT_FULL_NAME_KEY: "Codex CLI",
                    AGENT_HOMEPAGE_KEY: "https://example.com",
                    BUILD_LOCAL_KEY: False,
                    _VALID_BASES_KEY: {"ubuntu": "ghcr.io/aicage/aicage:codex-ubuntu"},
                    BASE_EXCLUDE_KEY: [1],
                }
            },
        }
        with self.assertRaises(CliError):
            ImagesMetadata.from_mapping(data)

    def test_from_mapping_rejects_invalid_agent_list_type(self) -> None:
        data = {
            _AICAGE_IMAGE_KEY: {_VERSION_KEY: "0.3.3"},
            _AICAGE_IMAGE_BASE_KEY: {_VERSION_KEY: "0.3.3"},
            _BASES_KEY: {},
            _AGENT_KEY: {
                "codex": {
                    AGENT_PATH_KEY: "~/.codex",
                    AGENT_FULL_NAME_KEY: "Codex CLI",
                    AGENT_HOMEPAGE_KEY: "https://example.com",
                    BUILD_LOCAL_KEY: False,
                    _VALID_BASES_KEY: {"ubuntu": "ghcr.io/aicage/aicage:codex-ubuntu"},
                    BASE_EXCLUDE_KEY: "ubuntu",
                }
            },
        }
        with self.assertRaises(CliError):
            ImagesMetadata.from_mapping(data)

    def test_from_mapping_rejects_empty_agent_fields(self) -> None:
        data = {
            _AICAGE_IMAGE_KEY: {_VERSION_KEY: "0.3.3"},
            _AICAGE_IMAGE_BASE_KEY: {_VERSION_KEY: "0.3.3"},
            _BASES_KEY: {},
            _AGENT_KEY: {
                "codex": {
                    AGENT_PATH_KEY: " ",
                    AGENT_FULL_NAME_KEY: "Codex CLI",
                    AGENT_HOMEPAGE_KEY: "https://example.com",
                    BUILD_LOCAL_KEY: False,
                    _VALID_BASES_KEY: {"ubuntu": "ghcr.io/aicage/aicage:codex-ubuntu"},
                }
            },
        }
        with self.assertRaises(CliError):
            ImagesMetadata.from_mapping(data)

    def test_from_mapping_accepts_valid_exclude_list(self) -> None:
        data = {
            _AICAGE_IMAGE_KEY: {_VERSION_KEY: "0.3.3"},
            _AICAGE_IMAGE_BASE_KEY: {_VERSION_KEY: "0.3.3"},
            _BASES_KEY: {},
            _AGENT_KEY: {
                "codex": {
                    AGENT_PATH_KEY: "~/.codex",
                    AGENT_FULL_NAME_KEY: "Codex CLI",
                    AGENT_HOMEPAGE_KEY: "https://example.com",
                    BUILD_LOCAL_KEY: False,
                    _VALID_BASES_KEY: {"ubuntu": "ghcr.io/aicage/aicage:codex-ubuntu"},
                    BASE_EXCLUDE_KEY: ["ubuntu"],
                }
            },
        }
        metadata = ImagesMetadata.from_mapping(data)
        self.assertEqual(["ubuntu"], metadata.agents["codex"].base_exclude)

    def test_from_mapping_rejects_invalid_bases_mapping(self) -> None:
        data = {
            _AICAGE_IMAGE_KEY: {_VERSION_KEY: "0.3.3"},
            _AICAGE_IMAGE_BASE_KEY: {_VERSION_KEY: "0.3.3"},
            _BASES_KEY: [],
            _AGENT_KEY: {},
        }
        with self.assertRaises(CliError):
            ImagesMetadata.from_mapping(data)
