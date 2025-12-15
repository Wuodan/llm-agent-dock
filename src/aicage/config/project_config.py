from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict


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
