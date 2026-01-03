from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

_PROJECT_PATH_KEY: str = "path"
_PROJECT_AGENTS_KEY: str = "agents"
_DOCKER_ARGS_KEY: str = "docker_args"

AGENT_BASE_KEY: str = "base"
_AGENT_ENTRYPOINT_KEY: str = "entrypoint"
_AGENT_MOUNTS_KEY: str = "mounts"

_MOUNT_GITCONFIG_KEY: str = "gitconfig"
_MOUNT_GNUPG_KEY: str = "gnupg"
_MOUNT_SSH_KEY: str = "ssh"
_MOUNT_DOCKER_KEY: str = "docker"


@dataclass
class AgentMounts:
    gitconfig: bool | None = None
    gnupg: bool | None = None
    ssh: bool | None = None
    docker: bool | None = None

    @classmethod
    def from_mapping(cls, data: dict[str, Any]) -> "AgentMounts":
        return cls(
            gitconfig=data.get(_MOUNT_GITCONFIG_KEY),
            gnupg=data.get(_MOUNT_GNUPG_KEY),
            ssh=data.get(_MOUNT_SSH_KEY),
            docker=data.get(_MOUNT_DOCKER_KEY),
        )

    def to_mapping(self) -> dict[str, bool]:
        payload: dict[str, bool] = {}
        if self.gitconfig is not None:
            payload[_MOUNT_GITCONFIG_KEY] = self.gitconfig
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
    entrypoint: str | None = None
    mounts: AgentMounts = field(default_factory=AgentMounts)

    @classmethod
    def from_mapping(cls, data: dict[str, Any]) -> "AgentConfig":
        mounts = AgentMounts.from_mapping(data.get(_AGENT_MOUNTS_KEY, {}) or {})
        return cls(
            base=data.get(AGENT_BASE_KEY),
            docker_args=data.get(_DOCKER_ARGS_KEY, "") or "",
            entrypoint=data.get(_AGENT_ENTRYPOINT_KEY),
            mounts=mounts,
        )

    def to_mapping(self) -> dict[str, Any]:
        payload: dict[str, Any] = {}
        if self.base:
            payload[AGENT_BASE_KEY] = self.base
        if self.docker_args:
            payload[_DOCKER_ARGS_KEY] = self.docker_args
        if self.entrypoint:
            payload[_AGENT_ENTRYPOINT_KEY] = self.entrypoint
        mounts = self.mounts.to_mapping()
        if mounts:
            payload[_AGENT_MOUNTS_KEY] = mounts
        return payload


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
