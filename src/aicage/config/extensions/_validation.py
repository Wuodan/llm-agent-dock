from aicage.config._schema_validation import load_schema, validate_schema_mapping

_EXTENSION_SCHEMA_PATH = "validation/extension.schema.json"
_EXTENSION_CONTEXT = "extension metadata"


def validate_extension_mapping(mapping: dict[str, object]) -> dict[str, object]:
    schema = load_schema(_EXTENSION_SCHEMA_PATH)
    return validate_schema_mapping(mapping, schema, _EXTENSION_CONTEXT)
