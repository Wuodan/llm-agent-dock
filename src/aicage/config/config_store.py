import hashlib
from pathlib import Path
from typing import Any

import yaml

from aicage.paths import PROJECTS_DIR

from ._yaml_loader import load_yaml
from .project_config import _ProjectConfig


class _IndentedSafeDumper(yaml.SafeDumper):
    def increase_indent(self, flow: bool = False, indentless: bool = False) -> None:
        super().increase_indent(flow, False)


class SettingsStore:
    """
    Persists per-project configuration under ~/.aicage.
    """

    def __init__(self) -> None:
        self.projects_dir = PROJECTS_DIR
        self.projects_dir.mkdir(parents=True, exist_ok=True)

    @staticmethod
    def _save_yaml(path: Path, data: dict[str, Any]) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", encoding="utf-8") as handle:
            yaml.dump(data, handle, Dumper=_IndentedSafeDumper, sort_keys=True)

    def _project_path(self, project_realpath: Path) -> Path:
        digest = hashlib.sha256(str(project_realpath).encode("utf-8")).hexdigest()
        return self.projects_dir / f"{digest}.yml"

    def load_project(self, project_realpath: Path) -> _ProjectConfig:
        path = self._project_path(project_realpath)
        if not path.exists():
            data = {}
        else:
            data = load_yaml(path)
        return _ProjectConfig.from_mapping(project_realpath, data)

    def save_project(self, project_realpath: Path, config: _ProjectConfig) -> None:
        self._save_yaml(self._project_path(project_realpath), config.to_mapping())

    def project_config_path(self, project_realpath: Path) -> Path:
        """
        Returns the path to a project's config file under the base directory.
        """
        return self._project_path(project_realpath)
