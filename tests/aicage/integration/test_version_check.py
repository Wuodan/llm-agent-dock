import os
import stat
import tempfile
from pathlib import Path

import pytest

from aicage.config.config_store import SettingsStore
from aicage.registry.agent_version import AgentVersionChecker
from aicage.registry.images_metadata.models import AgentMetadata

pytestmark = pytest.mark.integration


def _require_integration() -> None:
    if not os.environ.get("AICAGE_RUN_INTEGRATION"):
        pytest.skip("Set AICAGE_RUN_INTEGRATION=1 to run integration tests.")


def _write_executable(path: Path, content: str) -> None:
    path.write_text(content, encoding="utf-8")
    current = path.stat().st_mode
    path.chmod(current | stat.S_IEXEC)


def _write_npm_shim(bin_dir: Path) -> None:
    shim = "\n".join(
        [
            "#!/bin/bash",
            "set -euo pipefail",
            "echo 'npm: command not found' >&2",
            "exit 127",
        ]
    )
    _write_executable(bin_dir / "npm", shim)


def test_version_check_falls_back_to_builder(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _require_integration()
    with tempfile.TemporaryDirectory(dir=Path.cwd()) as temp_dir:
        temp_path = Path(temp_dir)
        bin_dir = temp_path / "bin"
        bin_dir.mkdir()
        _write_npm_shim(bin_dir)
        original_path = os.environ.get("PATH", "")
        monkeypatch.setenv("PATH", f"{bin_dir}:{original_path}")

        agent_dir = temp_path / "agent"
        agent_dir.mkdir()
        version_sh = "\n".join(
            [
                "#!/usr/bin/env bash",
                "set -euo pipefail",
                "npm --version",
            ]
        )
        _write_executable(agent_dir / "version.sh", version_sh)

        store = SettingsStore()
        checker = AgentVersionChecker(store.load_global())
        result = checker.get_version(
            "npm-agent",
            AgentMetadata(
                agent_path="~/.npm-agent",
                agent_full_name="Npm Agent",
                agent_homepage="https://example.com",
                valid_bases={},
            ),
            agent_dir,
        )

        assert result
