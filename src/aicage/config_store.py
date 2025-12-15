import hashlib
import json
import os
import shutil
from importlib import resources
from pathlib import Path
from typing import Any, Dict


class ConfigError(Exception):
    """Raised when configuration cannot be loaded or saved."""


def load_central_config(config_path: Path) -> Dict[str, str]:
    """
    Parse the top-level config.yaml (simple KEY: value file) into a dict.
    This intentionally avoids external dependencies.
    """
    if not config_path.exists():
        raise ConfigError(f"Config file not found: {config_path}")

    values: Dict[str, str] = {}
    for raw_line in config_path.read_text().splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if ":" not in line:
            continue
        key, raw_value = line.split(":", 1)
        values[key.strip()] = raw_value.strip()
    return values


class SettingsStore:
    """
    Persists global and per-project settings under ~/.aicage.
    """

    def __init__(self, base_dir: Path | None = None) -> None:
        self.base_dir = base_dir or Path(os.path.expanduser("~/.aicage"))
        self.projects_dir = self.base_dir / "projects"
        self.base_dir.mkdir(parents=True, exist_ok=True)
        self.projects_dir.mkdir(parents=True, exist_ok=True)
        self.global_path = self.base_dir / "config.json"
        self.central_config_path = self.base_dir / "config.yaml"
        self._ensure_central_config()

    def _load_json(self, path: Path) -> Dict[str, Any]:
        if not path.exists():
            return {}
        try:
            with path.open("r", encoding="utf-8") as handle:
                return json.load(handle)
        except json.JSONDecodeError as exc:
            raise ConfigError(f"Failed to parse JSON config at {path}: {exc}") from exc

    def _save_json(self, path: Path, data: Dict[str, Any]) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", encoding="utf-8") as handle:
            json.dump(data, handle, indent=2, sort_keys=True)
            handle.write("\n")

    def load_global(self) -> Dict[str, Any]:
        data = self._load_json(self.global_path)
        return {
            "docker_args": data.get("docker_args", ""),
            "tools": data.get("tools", {}),
        }

    def save_global(self, data: Dict[str, Any]) -> None:
        self._save_json(
            self.global_path,
            {"docker_args": data.get("docker_args", ""), "tools": data.get("tools", {})},
        )

    def _project_path(self, project_realpath: Path) -> Path:
        digest = hashlib.sha256(str(project_realpath).encode("utf-8")).hexdigest()
        return self.projects_dir / f"{digest}.json"

    def load_project(self, project_realpath: Path) -> Dict[str, Any]:
        data = self._load_json(self._project_path(project_realpath))
        return {
            "path": data.get("path", str(project_realpath)),
            "docker_args": data.get("docker_args", ""),
            "tools": data.get("tools", {}),
        }

    def save_project(self, project_realpath: Path, data: Dict[str, Any]) -> None:
        payload = {
            "path": str(project_realpath),
            "docker_args": data.get("docker_args", ""),
            "tools": data.get("tools", {}),
        }
        self._save_json(self._project_path(project_realpath), payload)

    def _ensure_central_config(self) -> None:
        """
        Create the central config file with defaults if it does not exist.
        """
        if not self.central_config_path.exists():
            packaged = self._packaged_config_path()
            shutil.copyfile(packaged, self.central_config_path)

    def central_config(self) -> Path:
        """
        Returns the path to the central config file under the base directory.
        """
        return self.central_config_path

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
