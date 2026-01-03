from dataclasses import dataclass, field
from typing import Any

from .errors import ConfigError

_IMAGE_REGISTRY_KEY: str = "image_registry"
_IMAGE_REGISTRY_API_URL_KEY: str = "image_registry_api_url"
_IMAGE_REGISTRY_API_TOKEN_URL_KEY: str = "image_registry_api_token_url"
_IMAGE_REPOSITORY_KEY: str = "image_repository"
_IMAGE_BASE_REPOSITORY_KEY: str = "image_base_repository"
_DEFAULT_IMAGE_BASE_KEY: str = "default_image_base"
_VERSION_CHECK_IMAGE_KEY: str = "version_check_image"
_LOCAL_IMAGE_REPOSITORY_KEY: str = "local_image_repository"
_GLOBAL_AGENTS_KEY: str = "agents"


@dataclass
class GlobalConfig:
    image_registry: str
    image_registry_api_url: str
    image_registry_api_token_url: str
    image_repository: str
    image_base_repository: str
    default_image_base: str
    version_check_image: str
    local_image_repository: str
    agents: dict[str, dict[str, Any]] = field(default_factory=dict)

    @classmethod
    def from_mapping(cls, data: dict[str, Any]) -> "GlobalConfig":
        required = (
            _IMAGE_REGISTRY_KEY,
            _IMAGE_REGISTRY_API_URL_KEY,
            _IMAGE_REGISTRY_API_TOKEN_URL_KEY,
            _IMAGE_REPOSITORY_KEY,
            _IMAGE_BASE_REPOSITORY_KEY,
            _DEFAULT_IMAGE_BASE_KEY,
            _VERSION_CHECK_IMAGE_KEY,
            _LOCAL_IMAGE_REPOSITORY_KEY,
        )
        missing = [key for key in required if key not in data]
        if missing:
            raise ConfigError(f"Missing required config values: {', '.join(missing)}.")
        return cls(
            image_registry=data[_IMAGE_REGISTRY_KEY],
            image_registry_api_url=data[_IMAGE_REGISTRY_API_URL_KEY],
            image_registry_api_token_url=data[_IMAGE_REGISTRY_API_TOKEN_URL_KEY],
            image_repository=data[_IMAGE_REPOSITORY_KEY],
            image_base_repository=data[_IMAGE_BASE_REPOSITORY_KEY],
            default_image_base=data[_DEFAULT_IMAGE_BASE_KEY],
            version_check_image=data[_VERSION_CHECK_IMAGE_KEY],
            local_image_repository=data[_LOCAL_IMAGE_REPOSITORY_KEY],
            agents=data.get(_GLOBAL_AGENTS_KEY, {}) or {},
        )

    def to_mapping(self) -> dict[str, Any]:
        return {
            _IMAGE_REGISTRY_KEY: self.image_registry,
            _IMAGE_REGISTRY_API_URL_KEY: self.image_registry_api_url,
            _IMAGE_REGISTRY_API_TOKEN_URL_KEY: self.image_registry_api_token_url,
            _IMAGE_REPOSITORY_KEY: self.image_repository,
            _IMAGE_BASE_REPOSITORY_KEY: self.image_base_repository,
            _DEFAULT_IMAGE_BASE_KEY: self.default_image_base,
            _VERSION_CHECK_IMAGE_KEY: self.version_check_image,
            _LOCAL_IMAGE_REPOSITORY_KEY: self.local_image_repository,
            _GLOBAL_AGENTS_KEY: self.agents,
        }
