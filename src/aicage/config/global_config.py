from dataclasses import dataclass, field
from typing import Any, Dict

from .errors import ConfigError


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
