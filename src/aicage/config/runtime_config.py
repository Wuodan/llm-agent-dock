from __future__ import annotations

from contextlib import ExitStack, contextmanager
from dataclasses import dataclass
from pathlib import Path
from typing import Iterator, List

import portalocker

from aicage.config.config_store import SettingsStore
from aicage.config.context import ConfigContext
from aicage.config.errors import ConfigError
from aicage.registry import select_tool_image
from aicage.runtime.auth.mounts import (
    MountPreferences,
    build_auth_mounts,
    load_mount_preferences,
    store_mount_preferences,
)
from aicage.runtime.run_args import MountSpec

__all__ = ["MountPreferencesSnapshot", "RunConfig", "load_run_config"]

_LOCK_TIMEOUT_SECONDS = 30


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
    global_docker_args: str
    project_docker_args: str
    mounts: List[MountSpec]
    mount_preferences: MountPreferencesSnapshot


def load_run_config(tool: str) -> RunConfig:
    store = SettingsStore(ensure_global_config=False)
    project_path = Path.cwd().resolve()
    global_config_path = store.global_config()
    project_config_path = store.project_config_path(project_path)

    with _lock_config_files(global_config_path, project_config_path):
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

        prefs = load_mount_preferences(tool_cfg)
        mounts, prefs_updated = build_auth_mounts(project_path, prefs)
        if prefs_updated:
            store_mount_preferences(tool_cfg, prefs)
            store.save_project(project_path, project_cfg)

        return RunConfig(
            project_path=project_path,
            tool=tool,
            image_ref=image_ref,
            global_docker_args=global_cfg.docker_args,
            project_docker_args=tool_cfg.get("docker_args", ""),
            mounts=mounts,
            mount_preferences=_freeze_mount_preferences(prefs),
        )


@contextmanager
def _lock_config_files(global_config_path: Path, project_config_path: Path) -> Iterator[None]:
    try:
        with ExitStack() as stack:
            stack.enter_context(_lock_file(global_config_path))
            stack.enter_context(_lock_file(project_config_path))
            yield
    except portalocker.exceptions.LockException as exc:  # pragma: no cover - rare file lock failure
        raise ConfigError(f"Failed to lock configuration files: {exc}") from exc


def _lock_file(path: Path) -> portalocker.Lock:
    path.parent.mkdir(parents=True, exist_ok=True)
    return portalocker.Lock(str(path), timeout=_LOCK_TIMEOUT_SECONDS, mode="a+")


def _freeze_mount_preferences(prefs: MountPreferences) -> MountPreferencesSnapshot:
    return MountPreferencesSnapshot(
        gitconfig=prefs.gitconfig,
        gnupg=prefs.gnupg,
        ssh=prefs.ssh,
    )
