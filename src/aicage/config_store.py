import hashlib
import os
import shutil
from dataclasses import dataclass, field
from importlib import resources
from pathlib import Path
from typing import Any, Dict

import yaml


class ConfigError(Exception):
    """Raised when configuration cannot be loaded or saved."""


@dataclass
class GlobalConfig:
    repository: str
    default_base: str
    docker_args: str = ""
    tools: Dict[str, Dict[str, Any]] = field(default_factory=dict)

    @classmethod
    def from_mapping(cls, data: Dict[str, Any]) -> "GlobalConfig":
        if "AICAGE_REPOSITORY" not in data or "AICAGE_DEFAULT_BASE" not in data:
            raise ConfigError("AICAGE_REPOSITORY and AICAGE_DEFAULT_BASE are required in config.yaml.")
        return cls(
            repository=data["AICAGE_REPOSITORY"],
            default_base=data["AICAGE_DEFAULT_BASE"],
            docker_args=data.get("docker_args", ""),
            tools=data.get("tools", {}) or {},
        )

    def to_mapping(self) -> Dict[str, Any]:
        return {
            "AICAGE_REPOSITORY": self.repository,
            "AICAGE_DEFAULT_BASE": self.default_base,
            "docker_args": self.docker_args,
            "tools": self.tools,
        }


@dataclass
class ProjectConfig:
    path: str
    docker_args: str = ""
    tools: Dict[str, Dict[str, Any]] = field(default_factory=dict)

    @classmethod
    def from_mapping(cls, project_path: Path, data: Dict[str, Any]) -> "ProjectConfig":
        return cls(
            path=data.get("path", str(project_path)),
            docker_args=data.get("docker_args", ""),
            tools=data.get("tools", {}) or {},
        )

    def to_mapping(self) -> Dict[str, Any]:
        return {"path": self.path, "docker_args": self.docker_args, "tools": self.tools}


class SettingsStore:
    """
    Persists global and per-project settings under ~/.aicage.
    """

    def __init__(self, base_dir: Path | None = None) -> None:
        self.base_dir = base_dir or Path(os.path.expanduser("~/.aicage"))
        self.projects_dir = self.base_dir / "projects"
        self.base_dir.mkdir(parents=True, exist_ok=True)
        self.projects_dir.mkdir(parents=True, exist_ok=True)
        self.global_config_path = self.base_dir / "config.yaml"
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
            resource = resources.files("aicage").joinpath("config.yaml")
        except Exception as exc:  # pragma: no cover - unexpected packaging issue
            raise ConfigError(f"Failed to locate packaged config.yaml: {exc}") from exc
        if not resource.exists():  # pragma: no cover - unexpected packaging issue
            raise ConfigError("Packaged config.yaml is missing.")
        return Path(resource)
