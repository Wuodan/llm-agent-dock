from pathlib import Path
from typing import Any

from aicage.config._schema_validation import load_schema, validate_schema_mapping
from aicage.config.agent.models import (
    AGENT_PATH_DIRECTORIES_KEY,
    AGENT_PATH_FILES_KEY,
    AGENT_PATH_KEY,
    BUILD_LOCAL_KEY,
)
from aicage.config.errors import ConfigError

_AGENT_SCHEMA_PATH = "validation/agent.schema.json"
_AGENT_CONTEXT = "agent metadata"


def validate_agent_mapping(mapping: dict[str, Any]) -> dict[str, Any]:
    schema = load_schema(_AGENT_SCHEMA_PATH)
    return validate_schema_mapping(
        mapping,
        schema,
        _AGENT_CONTEXT,
        normalizer=_apply_defaults,
    )


def ensure_required_files(agent_name: str, agent_dir: Path) -> None:
    missing = [name for name in ("install.sh", "version.sh") if not (agent_dir / name).is_file()]
    if missing:
        raise ConfigError(f"Agent '{agent_name}' is missing {', '.join(missing)}.")


def _apply_defaults(mapping: dict[str, Any]) -> dict[str, Any]:
    normalized = dict(mapping)
    normalized.setdefault(BUILD_LOCAL_KEY, True)
    agent_path = normalized.get(AGENT_PATH_KEY)
    if isinstance(agent_path, dict):
        agent_path = dict(agent_path)
        agent_path.setdefault(AGENT_PATH_FILES_KEY, [])
        agent_path.setdefault(AGENT_PATH_DIRECTORIES_KEY, [])
        normalized[AGENT_PATH_KEY] = agent_path
    return normalized
