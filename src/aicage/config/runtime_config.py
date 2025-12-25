from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from aicage.cli_types import ParsedArgs
from aicage.config.config_store import SettingsStore
from aicage.config.context import ConfigContext
from aicage.config.file_locking import lock_config_files
from aicage.config.global_config import GlobalConfig
from aicage.registry.image_selection import select_tool_image
from aicage.runtime.auth.mounts import (
    MountPreferences,
    build_auth_mounts,
    load_mount_preferences,
    store_mount_preferences,
)
from aicage.runtime.extra_mounts import (
    _build_extra_mounts,
    _ExtraMountPreferences,
    _load_extra_mount_preferences,
    _store_extra_mount_preferences,
)
from aicage.runtime.prompts import prompt_yes_no
from aicage.runtime.run_args import MountSpec

__all__ = ["MountPreferencesSnapshot", "RunConfig", "load_run_config"]


@dataclass(frozen=True)
class MountPreferencesSnapshot:
    gitconfig: bool | None
    gnupg: bool | None
    ssh: bool | None


@dataclass(frozen=True)
class RunConfig:
    project_path: Path
    tool: str
    image_ref: str
    global_cfg: GlobalConfig
    project_docker_args: str
    mounts: list[MountSpec]
    mount_preferences: MountPreferencesSnapshot


def load_run_config(tool: str, parsed: ParsedArgs | None = None) -> RunConfig:
    store = SettingsStore(ensure_global_config=False)
    project_path = Path.cwd().resolve()
    global_config_path = store.global_config()
    project_config_path = store.project_config_path(project_path)

    with lock_config_files(global_config_path, project_config_path):
        store.ensure_global_config()
        global_cfg = store.load_global()
        project_cfg = store.load_project(project_path)
        context = ConfigContext(
            store=store,
            project_path=project_path,
            project_cfg=project_cfg,
            global_cfg=global_cfg,
        )
        image_ref = select_tool_image(tool, context)
        tool_cfg = project_cfg.tools.setdefault(tool, {})

        existing_project_docker_args: str = tool_cfg.get("docker_args", "")

        prefs = load_mount_preferences(tool_cfg)
        mounts, auth_prefs_updated = build_auth_mounts(project_path, prefs)

        extra_prefs: _ExtraMountPreferences = _load_extra_mount_preferences(tool_cfg)
        cli_entrypoint = parsed.entrypoint if parsed else None
        cli_docker_socket = parsed.docker_socket if parsed else False
        extra_mounts, extra_prefs_updated = _build_extra_mounts(cli_entrypoint, cli_docker_socket, extra_prefs)
        mounts.extend(extra_mounts)

        docker_args_updated = _persist_docker_args(tool_cfg, parsed)

        if auth_prefs_updated:
            store_mount_preferences(tool_cfg, prefs)
        if extra_prefs_updated:
            _store_extra_mount_preferences(tool_cfg, extra_prefs)
        if auth_prefs_updated or extra_prefs_updated or docker_args_updated:
            store.save_project(project_path, project_cfg)

        return RunConfig(
            project_path=project_path,
            tool=tool,
            image_ref=image_ref,
            global_cfg=global_cfg,
            project_docker_args=existing_project_docker_args,
            mounts=mounts,
            mount_preferences=_freeze_mount_preferences(prefs),
        )


def _freeze_mount_preferences(prefs: MountPreferences) -> MountPreferencesSnapshot:
    return MountPreferencesSnapshot(
        gitconfig=prefs.gitconfig,
        gnupg=prefs.gnupg,
        ssh=prefs.ssh,
    )


def _persist_docker_args(tool_cfg: dict[str, Any], parsed: ParsedArgs | None) -> bool:
    if parsed is None or not parsed.docker_args:
        return False
    existing = tool_cfg.get("docker_args", "")
    if existing == parsed.docker_args:
        return False

    if existing:
        question = (
            f"Persist docker run args '{parsed.docker_args}' for this project "
            f"(replacing '{existing}')?"
        )
    else:
        question = f"Persist docker run args '{parsed.docker_args}' for this project?"

    if prompt_yes_no(question, default=True):
        tool_cfg["docker_args"] = parsed.docker_args
        return True
    return False
