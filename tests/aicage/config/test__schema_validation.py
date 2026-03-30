from unittest import TestCase

from aicage.config._schema_validation import load_schema, validate_schema_mapping
from aicage.config.errors import ConfigError


class SchemaValidationTests(TestCase):
    def test_load_schema_reads_packaged_schema(self) -> None:
        payload = load_schema("validation/base.schema.json")

        self.assertIsInstance(payload.get("properties"), dict)

    def test_validate_schema_mapping_applies_normalizer(self) -> None:
        schema = {
            "properties": {"name": {"type": "string"}, "enabled": {"type": "boolean"}},
            "required": ["name"],
            "additionalProperties": False,
        }

        def normalizer(mapping: dict[str, object]) -> dict[str, object]:
            _payload = dict(mapping)
            _payload.setdefault("enabled", True)
            return _payload

        payload = validate_schema_mapping(
            {"name": "agent"},
            schema,
            "example",
            normalizer=normalizer,
        )

        self.assertEqual({"name": "agent", "enabled": True}, payload)

    def test_validate_schema_mapping_rejects_missing_keys(self) -> None:
        schema = {"properties": {"name": {"type": "string"}}, "required": ["name"]}
        with self.assertRaises(ConfigError):
            validate_schema_mapping({}, schema, "example")

    def test_validate_schema_mapping_rejects_unknown_keys(self) -> None:
        schema = {"properties": {"name": {"type": "string"}}, "required": [], "additionalProperties": False}
        with self.assertRaises(ConfigError):
            validate_schema_mapping({"name": "agent", "extra": "value"}, schema, "example")

    def test_validate_schema_mapping_rejects_nested_invalid_value(self) -> None:
        schema = {
            "properties": {
                "agent_path": {
                    "type": "object",
                    "properties": {
                        "files": {
                            "type": "array",
                            "items": {"type": "string", "pattern": ".*\\S.*"},
                        }
                    },
                    "additionalProperties": False,
                }
            },
            "required": [],
            "additionalProperties": False,
        }
        with self.assertRaises(ConfigError):
            validate_schema_mapping({"agent_path": {"files": [" "]}}, schema, "example")
