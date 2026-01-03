import io
import os
import shlex
import stat
import subprocess
from shutil import copytree
from pathlib import Path

import pytest

from aicage.cli.entrypoint import main as cli_main
from aicage.config.config_store import SettingsStore
from aicage.config.project_config import AgentConfig, ProjectConfig
from aicage.registry.custom_agent.loader import DEFAULT_CUSTOM_AGENTS_DIR

pytestmark = pytest.mark.integration


def _require_integration() -> None:
    if not os.environ.get("AICAGE_RUN_INTEGRATION"):
        pytest.skip("Set AICAGE_RUN_INTEGRATION=1 to run integration tests.")


def _make_executable(path: Path) -> None:
    current = path.stat().st_mode
    path.chmod(current | stat.S_IEXEC)


def _copy_custom_agent(agent_dir: Path) -> None:
    repo_root = Path(__file__).resolve().parents[3]
    source_dir = repo_root / "doc/sample/custom/agents/forge"
    copytree(source_dir, agent_dir, dirs_exist_ok=True)
    _make_executable(agent_dir / "install.sh")
    _make_executable(agent_dir / "version.sh")


def test_custom_agent_build_and_version(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    _require_integration()
    home_dir = tmp_path / "home"
    workspace = tmp_path / "workspace"
    home_dir.mkdir()
    workspace.mkdir()
    monkeypatch.setenv("HOME", str(home_dir))
    monkeypatch.chdir(workspace)

    agent_name = "forge"
    agent_dir = Path(os.path.expanduser(DEFAULT_CUSTOM_AGENTS_DIR)) / agent_name
    _copy_custom_agent(agent_dir)

    store = SettingsStore()
    project_cfg = ProjectConfig(
        path=str(workspace),
        agents={agent_name: AgentConfig(base="ubuntu")},
    )
    store.save_project(workspace, project_cfg)

    stdout = io.StringIO()
    monkeypatch.setattr("sys.stdout", stdout)
    exit_code = cli_main(["--dry-run", agent_name, "--version"])
    assert exit_code == 0
    output_lines = [line for line in stdout.getvalue().splitlines() if line.strip()]
    run_cmd = shlex.split(output_lines[-1])
    run_cmd = [arg for arg in run_cmd if arg not in {"-it", "-t"}]
    result = subprocess.run(run_cmd, check=True, capture_output=True, text=True)
    assert result.stdout.strip()
