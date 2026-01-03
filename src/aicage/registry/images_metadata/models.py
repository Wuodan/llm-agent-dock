from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

from aicage.config.resources import find_packaged_path
from aicage.errors import CliError


@dataclass(frozen=True)
class ImageReleaseInfo:
    version: str


@dataclass(frozen=True)
class BaseMetadata:
    root_image: str
    base_image_distro: str
    base_image_description: str
    os_installer: str
    test_suite: str


@dataclass(frozen=True)
class AgentMetadata:
    agent_path: str
    agent_full_name: str
    agent_homepage: str
    valid_bases: dict[str, str]
    base_exclude: list[str] | None = None
    base_distro_exclude: list[str] | None = None
    local_definition_dir: Path | None = None


@dataclass(frozen=True)
class ImagesMetadata:
    aicage_image: ImageReleaseInfo
    aicage_image_base: ImageReleaseInfo
    bases: dict[str, BaseMetadata]
    agents: dict[str, AgentMetadata]

    @classmethod
    def from_yaml(cls, payload: str) -> ImagesMetadata:
        try:
            data = yaml.safe_load(payload) or {}
        except yaml.YAMLError as exc:
            raise CliError(f"Invalid images metadata YAML: {exc}") from exc
        if not isinstance(data, dict):
            raise CliError("Images metadata YAML must be a mapping at the top level.")
        return cls.from_mapping(data)

    @classmethod
    def from_mapping(cls, data: dict[str, Any]) -> ImagesMetadata:
        _expect_keys(
            data,
            required={"aicage-image", "aicage-image-base", "bases", "agent"},
            optional=set(),
            context="images metadata",
        )
        aicage_image = _parse_release_info(data["aicage-image"], "aicage-image")
        aicage_image_base = _parse_release_info(data["aicage-image-base"], "aicage-image-base")
        bases = _parse_bases(data["bases"])
        agents = _parse_agents(data["agent"])
        return cls(
            aicage_image=aicage_image,
            aicage_image_base=aicage_image_base,
            bases=bases,
            agents=agents,
        )


def _parse_release_info(value: Any, context: str) -> ImageReleaseInfo:
    mapping = _expect_mapping(value, context)
    _expect_keys(mapping, required={"version"}, optional=set(), context=context)
    return ImageReleaseInfo(version=_expect_string(mapping.get("version"), f"{context}.version"))


def _parse_bases(value: Any) -> dict[str, BaseMetadata]:
    mapping = _expect_mapping(value, "bases")
    bases: dict[str, BaseMetadata] = {}
    for name, base_value in mapping.items():
        if not isinstance(name, str):
            raise CliError("Images metadata base keys must be strings.")
        base_mapping = _expect_mapping(base_value, f"bases.{name}")
        _expect_keys(
            base_mapping,
            required={
                "root_image",
                "base_image_distro",
                "base_image_description",
                "os_installer",
                "test_suite",
            },
            optional=set(),
            context=f"bases.{name}",
        )
        bases[name] = BaseMetadata(
            root_image=_expect_string(base_mapping.get("root_image"), f"bases.{name}.root_image"),
            base_image_distro=_expect_string(
                base_mapping.get("base_image_distro"), f"bases.{name}.base_image_distro"
            ),
            base_image_description=_expect_string(
                base_mapping.get("base_image_description"),
                f"bases.{name}.base_image_description",
            ),
            os_installer=_expect_string(base_mapping.get("os_installer"), f"bases.{name}.os_installer"),
            test_suite=_expect_string(base_mapping.get("test_suite"), f"bases.{name}.test_suite"),
        )
    return bases


def _parse_agents(value: Any) -> dict[str, AgentMetadata]:
    mapping = _expect_mapping(value, "agent")
    agents: dict[str, AgentMetadata] = {}
    for name, agent_value in mapping.items():
        if not isinstance(name, str):
            raise CliError("Images metadata agent keys must be strings.")
        agent_mapping = _expect_mapping(agent_value, f"agent.{name}")
        _expect_keys(
            agent_mapping,
            required={
                "agent_path",
                "agent_full_name",
                "agent_homepage",
                "build_local",
                "valid_bases",
            },
            optional={"base_exclude", "base_distro_exclude"},
            context=f"agent.{name}",
        )
        agents[name] = AgentMetadata(
            agent_path=_expect_string(agent_mapping.get("agent_path"), f"agent.{name}.agent_path"),
            agent_full_name=_expect_string(
                agent_mapping.get("agent_full_name"), f"agent.{name}.agent_full_name"
            ),
            agent_homepage=_expect_string(
                agent_mapping.get("agent_homepage"), f"agent.{name}.agent_homepage"
            ),
            local_definition_dir=_local_definition_dir(
                name,
                _expect_bool(agent_mapping.get("build_local"), f"agent.{name}.build_local"),
            ),
            valid_bases=_expect_str_mapping(
                agent_mapping.get("valid_bases"), f"agent.{name}.valid_bases"
            ),
            base_exclude=_maybe_str_list(
                agent_mapping.get("base_exclude"), f"agent.{name}.base_exclude"
            ),
            base_distro_exclude=_maybe_str_list(
                agent_mapping.get("base_distro_exclude"), f"agent.{name}.base_distro_exclude"
            ),
        )
    return agents


def _local_definition_dir(agent_name: str, build_local: bool) -> Path | None:
    if not build_local:
        return None
    dockerfile = find_packaged_path("agent-build/Dockerfile")
    return dockerfile.parent / "agents" / agent_name


def _expect_mapping(value: Any, context: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise CliError(f"{context} must be a mapping.")
    return value


def _expect_string(value: Any, context: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise CliError(f"{context} must be a non-empty string.")
    return value


def _expect_bool(value: Any, context: str) -> bool:
    if not isinstance(value, bool):
        raise CliError(f"{context} must be a boolean.")
    return value


def _expect_str_list(value: Any, context: str) -> list[str]:
    if not isinstance(value, list):
        raise CliError(f"{context} must be a list.")
    items: list[str] = []
    for item in value:
        if not isinstance(item, str) or not item.strip():
            raise CliError(f"{context} must contain non-empty strings.")
        items.append(item)
    return items


def _expect_str_mapping(value: Any, context: str) -> dict[str, str]:
    mapping = _expect_mapping(value, context)
    items: dict[str, str] = {}
    for key, item in mapping.items():
        if not isinstance(key, str) or not key.strip():
            raise CliError(f"{context} must contain non-empty string keys.")
        if not isinstance(item, str) or not item.strip():
            raise CliError(f"{context} must contain non-empty string values.")
        items[key] = item
    return items


def _maybe_str_list(value: Any, context: str) -> list[str] | None:
    if value is None:
        return None
    return _expect_str_list(value, context)


def _expect_keys(
    mapping: dict[str, Any],
    required: set[str],
    optional: set[str],
    context: str,
) -> None:
    missing = sorted(required - set(mapping))
    if missing:
        raise CliError(f"{context} missing required keys: {', '.join(missing)}.")
    unknown = sorted(set(mapping) - required - optional)
    if unknown:
        raise CliError(f"{context} contains unsupported keys: {', '.join(unknown)}.")
