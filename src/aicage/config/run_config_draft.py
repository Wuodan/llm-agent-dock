from dataclasses import dataclass
from pathlib import Path

from aicage.cli_types import ParsedArgs
from aicage.config.project_config import AgentConfig, _ProjectConfig
from aicage.registry.image_selection.models import ImageSelection
from aicage.runtime.mounts.shares import merge_share_values


@dataclass
class RunConfigDraft:
    project_path: Path
    agent: str
    project_cfg: _ProjectConfig
    parsed: ParsedArgs | None
    existing_project_docker_args: str
    initial_base: str | None
    initial_image_ref: str | None
    initial_extensions: list[str]

    @property
    def agent_cfg(self) -> AgentConfig:
        return self.project_cfg.agents.setdefault(self.agent, AgentConfig())

    def apply_selection(self, selection: ImageSelection) -> None:
        if self.agent_cfg.base is None:
            self.agent_cfg.base = selection.base

    def persist_docker_args(self) -> None:
        if self.parsed is None or not self.parsed.docker_args:
            return
        if self.agent_cfg.docker_args == self.parsed.docker_args:
            return
        self.agent_cfg.docker_args = self.parsed.docker_args

    def merge_shares(self) -> list[str]:
        if self.parsed is None:
            return []
        merged_shares, new_shares = merge_share_values(
            self.parsed.shares,
            self.agent_cfg.shares,
            self.project_path,
        )
        self.parsed.shares = merged_shares
        return new_shares

    def persist_shares(self, new_shares: list[str]) -> None:
        if not new_shares:
            return
        self.agent_cfg.shares = [*self.agent_cfg.shares, *new_shares]

    def prefill_for_overview(self) -> None:
        if self.parsed is None:
            return
        if self.parsed.docker_args:
            self.agent_cfg.docker_args = self.parsed.docker_args
        if self.parsed.docker_socket:
            self.agent_cfg.mounts.docker = True
        if self.parsed.shares:
            self.agent_cfg.shares = merge_share_values(
                self.parsed.shares,
                self.agent_cfg.shares,
                self.project_path,
            )[0]

    def consume_overview_prefill(self) -> None:
        if self.parsed is None:
            return
        self.parsed.docker_args = ""
        self.parsed.docker_socket = False
        self.parsed.shares = []

    def image_selection_changed(self) -> bool:
        return (
            self.agent_cfg.base != self.initial_base
            or self.agent_cfg.image_ref != self.initial_image_ref
            or self.agent_cfg.extensions != self.initial_extensions
        )

    def reset_extension_image(self) -> None:
        self.agent_cfg.image_ref = None
        self.agent_cfg.extension_mounts = {
            key: value
            for key, value in self.agent_cfg.extension_mounts.items()
            if key in self.agent_cfg.extensions
        }


def _create_run_config_draft(
    project_path: Path,
    agent: str,
    project_cfg: _ProjectConfig,
    parsed: ParsedArgs | None,
) -> RunConfigDraft:
    initial_agent_cfg = project_cfg.agents.get(agent, AgentConfig())
    return RunConfigDraft(
        project_path=project_path,
        agent=agent,
        project_cfg=project_cfg,
        parsed=parsed,
        existing_project_docker_args=initial_agent_cfg.docker_args,
        initial_base=initial_agent_cfg.base,
        initial_image_ref=initial_agent_cfg.image_ref,
        initial_extensions=list(initial_agent_cfg.extensions),
    )
