from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path

from aicage.config.extensions.loader import ExtensionMetadata
from aicage.config.project_config import AgentConfig
from aicage.runtime.mounts.shares import ShareSpec, resolve_share_specs
from aicage.runtime.prompts.confirm import prompt_mount_git_support

from ._git_support import git_support_prompt_items


@dataclass(frozen=True)
class _ExtensionMountPromptItem:
    extension_id: str
    description: str


@dataclass(frozen=True)
class _MountPromptPrefs:
    git_mounts: set[str]
    extension_mounts: dict[str, bool]


def resolve_mount_prompt_prefs(
    project_path: Path,
    agent_cfg: AgentConfig,
    available_extensions: dict[str, ExtensionMetadata],
) -> _MountPromptPrefs | None:
    git_items = git_support_prompt_items(project_path, agent_cfg.mounts)
    extension_items = _extension_mount_prompt_items(
        project_path,
        agent_cfg.extensions,
        agent_cfg.extension_mounts,
        available_extensions,
    )
    if not git_items and not extension_items:
        return None

    selected = set(
        prompt_mount_git_support(
            list(git_items),
            _format_extension_prompt_items(extension_items),
        )
    )
    return _MountPromptPrefs(
        git_mounts={key for key, _description in git_items if key in selected},
        extension_mounts={
            item.extension_id: item.extension_id in selected
            for item in extension_items
        },
    )


def _format_extension_prompt_items(
    extension_items: Iterable[_ExtensionMountPromptItem],
) -> list[tuple[str, str]]:
    return [(item.extension_id, item.description) for item in extension_items]


def _extension_mount_prompt_items(
    project_path: Path,
    selected_extensions: list[str],
    extension_mounts: dict[str, bool],
    available_extensions: dict[str, ExtensionMetadata],
) -> list[_ExtensionMountPromptItem]:
    items: list[_ExtensionMountPromptItem] = []
    for extension_id in selected_extensions:
        if extension_id in extension_mounts:
            continue
        extension = available_extensions.get(extension_id)
        if extension is None or not extension.shares:
            continue
        share_specs = resolve_share_specs(extension.shares, project_path)
        share_values = ", ".join(_format_share_value(spec) for spec in share_specs)
        items.append(
            _ExtensionMountPromptItem(
                extension_id=extension_id,
                description=f"Extension {extension_id} shares: {share_values}",
            )
        )
    return items


def _format_share_value(spec: ShareSpec) -> str:
    host_value = str(spec.host_path)
    return f"{host_value}:ro" if spec.read_only else host_value
