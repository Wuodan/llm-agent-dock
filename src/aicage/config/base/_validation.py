from typing import Any

from aicage.config._schema_validation import load_schema, validate_schema_mapping
from aicage.config.base.models import BUILD_LOCAL_KEY

_BASE_SCHEMA_PATH: str = "validation/base.schema.json"
_BASE_CONTEXT: str = "base metadata"


def validate_base_mapping(mapping: dict[str, Any]) -> dict[str, Any]:
    schema = load_schema(_BASE_SCHEMA_PATH)
    return validate_schema_mapping(
        mapping,
        schema,
        _BASE_CONTEXT,
        normalizer=_apply_defaults,
    )


def _apply_defaults(mapping: dict[str, Any]) -> dict[str, Any]:
    normalized = dict(mapping)
    normalized.setdefault(BUILD_LOCAL_KEY, False)
    return normalized
