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
        if "image_repository" not in data or "default_image_base" not in data:
            raise ConfigError("image_repository and default_image_base are required in config.yaml.")
        return cls(
            repository=data["image_repository"],
            default_base=data["default_image_base"],
            docker_args=data.get("docker_args", ""),
            tools=data.get("tools", {}) or {},
        )

    def to_mapping(self) -> Dict[str, Any]:
        return {
            "image_repository": self.repository,
            "default_image_base": self.default_base,
            "docker_args": self.docker_args,
            "tools": self.tools,
        }
