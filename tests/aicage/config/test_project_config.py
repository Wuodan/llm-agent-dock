from pathlib import Path
from unittest import TestCase

from aicage.config.project_config import (
    _AGENT_BASE_KEY,
    _AGENT_EXTENSION_MOUNTS_KEY,
    _AGENT_SHARES_KEY,
    _DOCKER_ARGS_KEY,
    _PROJECT_AGENTS_KEY,
    _PROJECT_PATH_KEY,
    AgentConfig,
    _ProjectConfig,
)


class _ProjectConfigTests(TestCase):
    def test_from_mapping_applies_legacy_docker_args(self) -> None:
        data = {_PROJECT_AGENTS_KEY: {"codex": {}}, _DOCKER_ARGS_KEY: "--net=host"}
        cfg = _ProjectConfig.from_mapping(Path("/repo"), data)
        self.assertEqual("--net=host", cfg.agents["codex"].docker_args)

    def test_to_mapping_round_trip(self) -> None:
        cfg = _ProjectConfig(path="/repo", agents={"codex": AgentConfig(base="ubuntu")})
        self.assertEqual(
            {
                _PROJECT_PATH_KEY: "/repo",
                _PROJECT_AGENTS_KEY: {"codex": {_AGENT_BASE_KEY: "ubuntu"}},
            },
            cfg.to_mapping(),
        )

    def test_to_mapping_includes_shares(self) -> None:
        cfg = _ProjectConfig(
            path="/repo",
            agents={
                "codex": AgentConfig(
                    base="ubuntu", shares=["/test-tmp/one", "/test-tmp/two:ro"]
                )
            },
        )
        self.assertEqual(
            {
                _PROJECT_PATH_KEY: "/repo",
                _PROJECT_AGENTS_KEY: {
                    "codex": {
                        _AGENT_BASE_KEY: "ubuntu",
                        _AGENT_SHARES_KEY: ["/test-tmp/one", "/test-tmp/two:ro"],
                    }
                },
            },
            cfg.to_mapping(),
        )

    def test_to_mapping_includes_extension_mounts(self) -> None:
        cfg = _ProjectConfig(
            path="/repo",
            agents={
                "codex": AgentConfig(
                    base="ubuntu", extension_mounts={"gh": True, "maven": False}
                )
            },
        )
        self.assertEqual(
            {
                _PROJECT_PATH_KEY: "/repo",
                _PROJECT_AGENTS_KEY: {
                    "codex": {
                        _AGENT_BASE_KEY: "ubuntu",
                        _AGENT_EXTENSION_MOUNTS_KEY: {"gh": True, "maven": False},
                    }
                },
            },
            cfg.to_mapping(),
        )
