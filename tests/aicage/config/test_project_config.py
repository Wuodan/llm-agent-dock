from pathlib import Path
from unittest import TestCase

from aicage.config.project_config import (
    _DOCKER_ARGS_KEY,
    _PROJECT_AGENTS_KEY,
    _PROJECT_PATH_KEY,
    AGENT_BASE_KEY,
    AgentConfig,
    ProjectConfig,
)


class ProjectConfigTests(TestCase):
    def test_from_mapping_applies_legacy_docker_args(self) -> None:
        data = {_PROJECT_AGENTS_KEY: {"codex": {}}, _DOCKER_ARGS_KEY: "--net=host"}
        cfg = ProjectConfig.from_mapping(Path("/repo"), data)
        self.assertEqual("--net=host", cfg.agents["codex"].docker_args)

    def test_round_trip_mapping(self) -> None:
        cfg = ProjectConfig(path="/repo", agents={"codex": AgentConfig(base="ubuntu")})
        self.assertEqual(
            {_PROJECT_PATH_KEY: "/repo", _PROJECT_AGENTS_KEY: {"codex": {AGENT_BASE_KEY: "ubuntu"}}},
            cfg.to_mapping(),
        )
