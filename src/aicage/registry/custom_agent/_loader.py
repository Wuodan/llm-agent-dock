from __future__ import annotations

import os
from pathlib import Path
from typing import Any

import yaml

from aicage.errors import CliError
from aicage.registry.images_metadata.models import AgentMetadata, ImagesMetadata

from ._validation import expect_bool, expect_keys, expect_string, maybe_str_list

DEFAULT_CUSTOM_AGENTS_DIR = "~/.aicage/custom/agent"
_AGENT_DEFINITION_FILES = ("agent.yml", "agent.yaml")


def load_custom_agents(images_metadata: ImagesMetadata) -> dict[str, AgentMetadata]:
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
        custom_agents[agent_name] = _build_custom_agent(
            agent_name=agent_name,
            agent_mapping=agent_mapping,
            images_metadata=images_metadata,
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
) -> AgentMetadata:
    expect_keys(
        agent_mapping,
        required={"agent_path", "agent_full_name", "agent_homepage", "redistributable"},
        optional={"base_exclude", "base_distro_exclude"},
        context=f"custom agent '{agent_name}'",
    )
    base_exclude = maybe_str_list(agent_mapping.get("base_exclude"), "base_exclude")
    base_distro_exclude = maybe_str_list(agent_mapping.get("base_distro_exclude"), "base_distro_exclude")
    valid_bases = _build_valid_bases(
        agent_name=agent_name,
        images_metadata=images_metadata,
        base_exclude=base_exclude,
        base_distro_exclude=base_distro_exclude,
    )
    return AgentMetadata(
        agent_path=expect_string(agent_mapping.get("agent_path"), "agent_path"),
        agent_full_name=expect_string(agent_mapping.get("agent_full_name"), "agent_full_name"),
        agent_homepage=expect_string(agent_mapping.get("agent_homepage"), "agent_homepage"),
        redistributable=expect_bool(agent_mapping.get("redistributable"), "redistributable"),
        valid_bases=valid_bases,
        base_exclude=base_exclude,
        base_distro_exclude=base_distro_exclude,
        is_custom=True,
    )


def _build_valid_bases(
    agent_name: str,
    images_metadata: ImagesMetadata,
    base_exclude: list[str] | None,
    base_distro_exclude: list[str] | None,
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
        valid_bases[base_name] = _custom_image_ref(agent_name, base_name)
    return valid_bases


def _custom_image_ref(agent_name: str, base_name: str) -> str:
    tag = f"{agent_name}-{base_name}".lower().replace("/", "-")
    return f"aicage-local:{tag}"


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
