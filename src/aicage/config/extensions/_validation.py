from typing import Any

from aicage.config._schema_validation import load_schema, validate_schema_mapping
from aicage.config._yaml import expect_string
from aicage.config.errors import ConfigError

_EXTENSION_SCHEMA_PATH = "validation/extension.schema.json"
_EXTENSION_CONTEXT = "extension metadata"


def validate_extension_mapping(mapping: dict[str, Any]) -> dict[str, Any]:
    context = _EXTENSION_CONTEXT
    schema = load_schema(_EXTENSION_SCHEMA_PATH)
    return validate_schema_mapping(mapping, schema, context, value_validator=_validate_value)


def _validate_value(value: Any, schema_entry: dict[str, Any], context: str) -> None:
    schema_type = schema_entry.get("type")
    if schema_type == "string":
        expect_string(value, context)
        return
    if schema_type == "array":
        if not isinstance(value, list):
            raise ConfigError(f"{context} must be a list.")
        items = schema_entry.get("items", {})
        item_type = items.get("type")
        if item_type != "string":
            raise ConfigError(f"{context} has unsupported item type '{item_type}'.")
        for index, item in enumerate(value):
            expect_string(item, f"{context}[{index}]")
        return
    raise ConfigError(f"{context} has unsupported schema type '{schema_type}'.")
