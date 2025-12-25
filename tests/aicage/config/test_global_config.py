from unittest import TestCase

from aicage.config.errors import ConfigError
from aicage.config.global_config import GlobalConfig


class GlobalConfigTests(TestCase):
    def test_from_mapping_requires_fields(self) -> None:
        with self.assertRaises(ConfigError):
            GlobalConfig.from_mapping({"image_registry": "ghcr.io"})

    def test_round_trip_mapping(self) -> None:
        data = {
            "image_registry": "ghcr.io",
            "image_registry_api_url": "https://ghcr.io/v2",
            "image_registry_api_token_url": "https://ghcr.io/token",
            "image_repository": "aicage/aicage",
            "default_image_base": "ubuntu",
            "tools": {"codex": {"base": "ubuntu"}},
        }
        cfg = GlobalConfig.from_mapping(data)
        self.assertEqual(data, cfg.to_mapping())
