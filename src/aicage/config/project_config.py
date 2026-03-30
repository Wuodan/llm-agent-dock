from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from aicage._lists import read_str_list_or_empty

_PROJECT_PATH_KEY: str = "path"
_PROJECT_AGENTS_KEY: str = "agents"
_DOCKER_ARGS_KEY: str = "docker_args"

_AGENT_BASE_KEY: str = "base"
_AGENT_MOUNTS_KEY: str = "mounts"
_AGENT_IMAGE_REF_KEY: str = "image_ref"
_AGENT_EXTENSIONS_KEY: str = "extensions"
_AGENT_SHARES_KEY: str = "shares"
_AGENT_EXTENSION_MOUNTS_KEY: str = "extension_mounts"

_MOUNT_GITCONFIG_KEY: str = "gitconfig"
_MOUNT_GITROOT_KEY: str = "gitroot"
_MOUNT_GNUPG_KEY: str = "gnupg"
_MOUNT_SSH_KEY: str = "ssh"
_MOUNT_DOCKER_KEY: str = "docker"


@dataclass
class _AgentMounts:
    gitconfig: bool | None = None
    gitroot: bool | None = None
    gnupg: bool | None = None
    ssh: bool | None = None
    docker: bool | None = None

    @classmethod
    def from_mapping(cls, data: dict[str, Any]) -> "_AgentMounts":
        return cls(
            gitconfig=data.get(_MOUNT_GITCONFIG_KEY),
            gitroot=data.get(_MOUNT_GITROOT_KEY),
            gnupg=data.get(_MOUNT_GNUPG_KEY),
            ssh=data.get(_MOUNT_SSH_KEY),
            docker=data.get(_MOUNT_DOCKER_KEY),
        )

    def to_mapping(self) -> dict[str, bool]:
        payload: dict[str, bool] = {}
        if self.gitconfig is not None:
            payload[_MOUNT_GITCONFIG_KEY] = self.gitconfig
        if self.gitroot is not None:
            payload[_MOUNT_GITROOT_KEY] = self.gitroot
        if self.gnupg is not None:
            payload[_MOUNT_GNUPG_KEY] = self.gnupg
        if self.ssh is not None:
            payload[_MOUNT_SSH_KEY] = self.ssh
        if self.docker is not None:
            payload[_MOUNT_DOCKER_KEY] = self.docker
        return payload


@dataclass
class AgentConfig:
    base: str | None = None
    docker_args: str = ""
    mounts: _AgentMounts = field(default_factory=_AgentMounts)
    image_ref: str | None = None
    extensions: list[str] = field(default_factory=list)
    shares: list[str] = field(default_factory=list)
    extension_mounts: dict[str, bool] = field(default_factory=dict)

    @classmethod
    def from_mapping(cls, data: dict[str, Any]) -> "AgentConfig":
        mounts = _AgentMounts.from_mapping(data.get(_AGENT_MOUNTS_KEY, {}) or {})
        return cls(
            base=data.get(_AGENT_BASE_KEY),
            docker_args=data.get(_DOCKER_ARGS_KEY, "") or "",
            mounts=mounts,
            image_ref=data.get(_AGENT_IMAGE_REF_KEY),
            extensions=read_str_list_or_empty(data.get(_AGENT_EXTENSIONS_KEY)),
            shares=read_str_list_or_empty(data.get(_AGENT_SHARES_KEY)),
            extension_mounts=_read_bool_dict_or_empty(data.get(_AGENT_EXTENSION_MOUNTS_KEY)),
        )

    def to_mapping(self) -> dict[str, Any]:
        payload: dict[str, Any] = {}
        if self.base:
            payload[_AGENT_BASE_KEY] = self.base
        if self.docker_args:
            payload[_DOCKER_ARGS_KEY] = self.docker_args
        mounts = self.mounts.to_mapping()
        if mounts:
            payload[_AGENT_MOUNTS_KEY] = mounts
        if self.image_ref:
            payload[_AGENT_IMAGE_REF_KEY] = self.image_ref
        if self.extensions:
            payload[_AGENT_EXTENSIONS_KEY] = list(self.extensions)
        if self.shares:
            payload[_AGENT_SHARES_KEY] = list(self.shares)
        if self.extension_mounts:
            payload[_AGENT_EXTENSION_MOUNTS_KEY] = dict(self.extension_mounts)
        return payload


def _read_bool_dict_or_empty(value: Any) -> dict[str, bool]:
    if not isinstance(value, dict):
        return {}
    return {
        key: item
        for key, item in value.items()
        if isinstance(key, str) and key and isinstance(item, bool)
    }


@dataclass
class ProjectConfig:
    path: str
    agents: dict[str, AgentConfig] = field(default_factory=dict)

    @classmethod
    def from_mapping(cls, project_path: Path, data: dict[str, Any]) -> "ProjectConfig":
        raw_agents = data.get(_PROJECT_AGENTS_KEY, {}) or {}
        agents = {name: AgentConfig.from_mapping(cfg) for name, cfg in raw_agents.items()}
        legacy_docker_args = data.get(_DOCKER_ARGS_KEY, "")
        if legacy_docker_args:
            for agent_cfg in agents.values():
                if not agent_cfg.docker_args:
                    agent_cfg.docker_args = legacy_docker_args
        return cls(
            path=data.get(_PROJECT_PATH_KEY, str(project_path)),
            agents=agents,
        )

    def to_mapping(self) -> dict[str, Any]:
        agents_payload = {name: cfg.to_mapping() for name, cfg in self.agents.items()}
        return {_PROJECT_PATH_KEY: self.path, _PROJECT_AGENTS_KEY: agents_payload}
