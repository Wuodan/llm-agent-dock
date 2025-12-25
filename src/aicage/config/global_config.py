from dataclasses import dataclass, field
from typing import Any

from .errors import ConfigError

__all__ = ["GlobalConfig"]


@dataclass
class GlobalConfig:
    image_registry: str
    image_registry_api_url: str
    image_registry_api_token_url: str
    image_repository: str
    default_image_base: str
    tools: dict[str, dict[str, Any]] = field(default_factory=dict)

    @classmethod
    def from_mapping(cls, data: dict[str, Any]) -> "GlobalConfig":
        required = (
            "image_registry",
            "image_registry_api_url",
            "image_registry_api_token_url",
            "image_repository",
            "default_image_base",
        )
        missing = [key for key in required if key not in data]
        if missing:
            raise ConfigError(f"Missing required config values: {', '.join(missing)}.")
        return cls(
            image_registry=data["image_registry"],
            image_registry_api_url=data["image_registry_api_url"],
            image_registry_api_token_url=data["image_registry_api_token_url"],
            image_repository=data["image_repository"],
            default_image_base=data["default_image_base"],
            tools=data.get("tools", {}) or {},
        )

    def to_mapping(self) -> dict[str, Any]:
        return {
            "image_registry": self.image_registry,
            "image_registry_api_url": self.image_registry_api_url,
            "image_registry_api_token_url": self.image_registry_api_token_url,
            "image_repository": self.image_repository,
            "default_image_base": self.default_image_base,
            "tools": self.tools,
        }
