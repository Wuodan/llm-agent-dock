import json
from collections.abc import Callable
from functools import lru_cache
from typing import Any

from jsonschema import Draft202012Validator
from jsonschema.exceptions import ValidationError

from aicage.config.errors import ConfigError
from aicage.config.resources import find_packaged_path

_Normalizer = Callable[[dict[str, Any]], dict[str, Any]]


@lru_cache(maxsize=1)
def load_schema(path: str) -> dict[str, Any]:
    payload = find_packaged_path(path).read_text(encoding="utf-8")
    return json.loads(payload)


def validate_schema_mapping(
    mapping: dict[str, Any],
    schema: dict[str, Any],
    context: str,
    *,
    normalizer: _Normalizer | None = None,
) -> dict[str, Any]:
    if not isinstance(mapping, dict):
        raise ConfigError(f"{context} must be a mapping.")

    normalized = dict(mapping)
    if normalizer is not None:
        normalized = normalizer(normalized)

    validator = Draft202012Validator(schema)
    errors = sorted(validator.iter_errors(normalized), key=lambda error: list(error.path))
    if errors:
        raise ConfigError(_error_message(context, errors[0]))
    return normalized


def _error_message(context: str, error: ValidationError) -> str:
    if error.path:
        path = ".".join(str(token) for token in error.path)
        return f"{context}.{path} {error.message}"
    return f"{context} {error.message}"
