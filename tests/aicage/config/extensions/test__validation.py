from typing import Any, cast
from unittest import TestCase

from aicage.config.errors import ConfigError
from aicage.config.extensions import _validation


class ExtensionValidationTests(TestCase):
    def test_validate_extension_mapping_rejects_non_mapping(self) -> None:
        with self.assertRaises(ConfigError):
            _validation.validate_extension_mapping(cast(Any, ["name", "description"]))

    def test_validate_extension_mapping_rejects_missing_required(self) -> None:
        with self.assertRaises(ConfigError):
            _validation.validate_extension_mapping({"name": "Example"})

    def test_validate_extension_mapping_rejects_unknown_keys(self) -> None:
        with self.assertRaises(ConfigError):
            _validation.validate_extension_mapping(
                {"name": "Example", "description": "Demo", "extra": "nope"}
            )

    def test_validate_extension_mapping_rejects_empty_strings(self) -> None:
        with self.assertRaises(ConfigError):
            _validation.validate_extension_mapping({"name": " ", "description": "Demo"})

    def test_validate_extension_mapping_accepts_valid_payload(self) -> None:
        payload = _validation.validate_extension_mapping(
            {"name": "Example", "description": "Demo"}
        )
        self.assertEqual(payload, {"name": "Example", "description": "Demo"})

    def test_validate_extension_mapping_accepts_shares(self) -> None:
        payload = _validation.validate_extension_mapping(
            {"name": "Example", "description": "Demo", "shares": ["~/.m2", "~/.cache:ro"]}
        )
        self.assertEqual(
            payload,
            {"name": "Example", "description": "Demo", "shares": ["~/.m2", "~/.cache:ro"]},
        )

    def test_validate_extension_mapping_rejects_invalid_share_item(self) -> None:
        with self.assertRaises(ConfigError):
            _validation.validate_extension_mapping(
                {"name": "Example", "description": "Demo", "shares": ["~/.m2", " "]}
            )
