from __future__ import annotations

import os
from pathlib import Path
from typing import Any

import yaml

from aicage.errors import CliError
from aicage.registry._image_refs import local_image_ref
from aicage.registry.images_metadata.models import AgentMetadata, ImagesMetadata

from ._validation import ensure_required_files, expect_string, maybe_str_list, validate_agent_mapping

DEFAULT_CUSTOM_AGENTS_DIR = "~/.aicage/custom/agent"
_AGENT_DEFINITION_FILES = ("agent.yml", "agent.yaml")


def load_custom_agents(
    images_metadata: ImagesMetadata,
    local_image_repository: str,
) -> dict[str, AgentMetadata]:
    agents_dir = Path(os.path.expanduser(DEFAULT_CUSTOM_AGENTS_DIR))
    if not agents_dir.is_dir():
        return {}

    custom_agents: dict[str, AgentMetadata] = {}
    for entry in sorted(agents_dir.iterdir()):
        if not entry.is_dir():
            continue
        agent_name = entry.name
        agent_path = _find_agent_definition(entry)
        agent_mapping = _load_yaml(agent_path)
        ensure_required_files(agent_name, entry)
        custom_agents[agent_name] = _build_custom_agent(
            agent_name=agent_name,
            agent_mapping=agent_mapping,
            images_metadata=images_metadata,
            local_image_repository=local_image_repository,
        )
    return custom_agents


def _find_agent_definition(agent_dir: Path) -> Path:
    for filename in _AGENT_DEFINITION_FILES:
        candidate = agent_dir / filename
        if candidate.is_file():
            return candidate
    expected = ", ".join(_AGENT_DEFINITION_FILES)
    raise CliError(f"Custom agent '{agent_dir.name}' is missing {expected}.")


def _load_yaml(path: Path) -> dict[str, Any]:
    try:
        payload = path.read_text(encoding="utf-8")
        data = yaml.safe_load(payload) or {}
    except (OSError, yaml.YAMLError) as exc:
        raise CliError(f"Failed to read custom agent metadata from {path}: {exc}") from exc
    if not isinstance(data, dict):
        raise CliError(f"Custom agent metadata at {path} must be a mapping.")
    return data


def _build_custom_agent(
    agent_name: str,
    agent_mapping: dict[str, Any],
    images_metadata: ImagesMetadata,
    local_image_repository: str,
) -> AgentMetadata:
    normalized_mapping = validate_agent_mapping(agent_mapping)
    base_exclude = maybe_str_list(normalized_mapping.get("base_exclude"), "base_exclude")
    base_distro_exclude = maybe_str_list(
        normalized_mapping.get("base_distro_exclude"), "base_distro_exclude"
    )
    valid_bases = _build_valid_bases(
        agent_name=agent_name,
        images_metadata=images_metadata,
        base_exclude=base_exclude,
        base_distro_exclude=base_distro_exclude,
        local_image_repository=local_image_repository,
    )
    return AgentMetadata(
        agent_path=expect_string(normalized_mapping.get("agent_path"), "agent_path"),
        agent_full_name=expect_string(normalized_mapping.get("agent_full_name"), "agent_full_name"),
        agent_homepage=expect_string(normalized_mapping.get("agent_homepage"), "agent_homepage"),
        valid_bases=valid_bases,
        base_exclude=base_exclude,
        base_distro_exclude=base_distro_exclude,
        local_definition_dir=Path(os.path.expanduser(DEFAULT_CUSTOM_AGENTS_DIR)) / agent_name,
    )


def _build_valid_bases(
    agent_name: str,
    images_metadata: ImagesMetadata,
    base_exclude: list[str] | None,
    base_distro_exclude: list[str] | None,
    local_image_repository: str,
) -> dict[str, str]:
    valid_bases: dict[str, str] = {}
    base_exclude_set = _normalize_exclude(base_exclude)
    base_distro_exclude_set = _normalize_exclude(base_distro_exclude)
    for base_name in sorted(images_metadata.bases):
        base_metadata = images_metadata.bases[base_name]
        if _is_base_excluded(
            base_name,
            base_metadata.base_image_distro,
            base_exclude_set,
            base_distro_exclude_set,
        ):
            continue
        valid_bases[base_name] = local_image_ref(local_image_repository, agent_name, base_name)
    return valid_bases


def _is_base_excluded(
    base_name: str,
    base_distro: str,
    base_exclude: set[str],
    base_distro_exclude: set[str],
) -> bool:
    base_name_lc = base_name.lower()
    if base_name_lc in base_exclude:
        return True
    if base_distro.lower() in base_distro_exclude:
        return True
    return False


def _normalize_exclude(values: list[str] | None) -> set[str]:
    if not values:
        return set()
    return {value.lower() for value in values}
