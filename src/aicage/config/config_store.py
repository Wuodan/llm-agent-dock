import hashlib
import os
import shutil
from importlib import resources
from pathlib import Path
from typing import Any, Dict

import yaml

from .errors import ConfigError
from .global_config import GlobalConfig
from .project_config import ProjectConfig

_CONFIG_FILENAME = "config.yaml"
_DEFAULT_BASE_DIR = "~/.aicage"
_PROJECTS_SUBDIR = "projects"


class SettingsStore:
    """
    Persists global and per-project configuration under ~/.aicage.
    """

    def __init__(self, base_dir: Path | None = None) -> None:
        self.base_dir = base_dir or Path(os.path.expanduser(_DEFAULT_BASE_DIR))
        self.projects_dir = self.base_dir / _PROJECTS_SUBDIR
        self.base_dir.mkdir(parents=True, exist_ok=True)
        self.projects_dir.mkdir(parents=True, exist_ok=True)
        self.global_config_path = self.base_dir / _CONFIG_FILENAME
        self._ensure_global_config()

    def _load_yaml(self, path: Path) -> Dict[str, Any]:
        if not path.exists():
            return {}
        try:
            with path.open("r", encoding="utf-8") as handle:
                data = yaml.safe_load(handle)
                return data or {}
        except yaml.YAMLError as exc:
            raise ConfigError(f"Failed to parse YAML config at {path}: {exc}") from exc

    def _save_yaml(self, path: Path, data: Dict[str, Any]) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", encoding="utf-8") as handle:
            yaml.safe_dump(data, handle, sort_keys=True)

    def load_global(self) -> GlobalConfig:
        data = self._load_yaml(self.global_config_path)
        return GlobalConfig.from_mapping(data)

    def save_global(self, config: GlobalConfig) -> None:
        self._save_yaml(self.global_config_path, config.to_mapping())

    def _project_path(self, project_realpath: Path) -> Path:
        digest = hashlib.sha256(str(project_realpath).encode("utf-8")).hexdigest()
        return self.projects_dir / f"{digest}.yaml"

    def load_project(self, project_realpath: Path) -> ProjectConfig:
        data = self._load_yaml(self._project_path(project_realpath))
        return ProjectConfig.from_mapping(project_realpath, data)

    def save_project(self, project_realpath: Path, config: ProjectConfig) -> None:
        self._save_yaml(self._project_path(project_realpath), config.to_mapping())

    def _ensure_global_config(self) -> None:
        """
        Create the global config file with defaults if it does not exist.
        """
        if not self.global_config_path.exists():
            packaged = self._packaged_config_path()
            shutil.copyfile(packaged, self.global_config_path)

    def global_config(self) -> Path:
        """
        Returns the path to the global config file under the base directory.
        """
        return self.global_config_path

    def _packaged_config_path(self) -> Path:
        """
        Locate the packaged default config.yaml.
        """
        try:
            resource = resources.files("aicage.config").joinpath(_CONFIG_FILENAME)
        except Exception as exc:  # pragma: no cover - unexpected packaging issue
            raise ConfigError(f"Failed to locate packaged config.yaml: {exc}") from exc
        if not resource.exists():  # pragma: no cover - unexpected packaging issue
            raise ConfigError("Packaged config.yaml is missing.")
        return Path(resource)
