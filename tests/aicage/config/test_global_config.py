from unittest import TestCase

from aicage.config.errors import ConfigError
from aicage.config.global_config import (
    _DEFAULT_IMAGE_BASE_KEY,
    _GLOBAL_AGENTS_KEY,
    _IMAGE_BASE_REPOSITORY_KEY,
    _IMAGE_REGISTRY_API_TOKEN_URL_KEY,
    _IMAGE_REGISTRY_API_URL_KEY,
    _IMAGE_REGISTRY_KEY,
    _IMAGE_REPOSITORY_KEY,
    _LOCAL_IMAGE_REPOSITORY_KEY,
    _VERSION_CHECK_IMAGE_KEY,
    GlobalConfig,
)
from aicage.config.project_config import AGENT_BASE_KEY


class GlobalConfigTests(TestCase):
    def test_from_mapping_requires_fields(self) -> None:
        with self.assertRaises(ConfigError):
            GlobalConfig.from_mapping({_IMAGE_REGISTRY_KEY: "ghcr.io"})

    def test_round_trip_mapping(self) -> None:
        data = {
            _IMAGE_REGISTRY_KEY: "ghcr.io",
            _IMAGE_REGISTRY_API_URL_KEY: "https://ghcr.io/v2",
            _IMAGE_REGISTRY_API_TOKEN_URL_KEY: "https://ghcr.io/token",
            _IMAGE_REPOSITORY_KEY: "aicage/aicage",
            _IMAGE_BASE_REPOSITORY_KEY: "aicage/aicage-image-base",
            _DEFAULT_IMAGE_BASE_KEY: "ubuntu",
            _VERSION_CHECK_IMAGE_KEY: "ghcr.io/aicage/aicage-image-util:agent-version",
            _LOCAL_IMAGE_REPOSITORY_KEY: "aicage",
            _GLOBAL_AGENTS_KEY: {"codex": {AGENT_BASE_KEY: "ubuntu"}},
        }
        cfg = GlobalConfig.from_mapping(data)
        self.assertEqual(data, cfg.to_mapping())
