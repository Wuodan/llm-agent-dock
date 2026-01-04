import os
from pathlib import Path

import pytest

from aicage.config.config_store import SettingsStore
from aicage.config.project_config import AgentConfig, ProjectConfig
from aicage.registry import _local_query
from aicage.registry.custom_agent.loader import DEFAULT_CUSTOM_AGENTS_DIR
from aicage.registry.local_build._store import BuildRecord, BuildStore

from ._helpers import build_cli_env, copy_forge_sample, run_cli_pty

pytestmark = pytest.mark.integration


def _require_integration() -> None:
    if not os.environ.get("AICAGE_RUN_INTEGRATION"):
        pytest.skip("Set AICAGE_RUN_INTEGRATION=1 to run integration tests.")


def _write_project_config(workspace: Path, agent_name: str) -> None:
    store = SettingsStore()
    project_cfg = ProjectConfig(
        path=str(workspace),
        agents={agent_name: AgentConfig(base="ubuntu")},
    )
    store.save_project(workspace, project_cfg)


def _run_agent(env: dict[str, str], workspace: Path, agent_name: str) -> None:
    exit_code, output = run_cli_pty([agent_name, "--version"], env=env, cwd=workspace)
    assert exit_code == 0, output
    output_lines = [line.strip() for line in output.splitlines() if line.strip()]
    assert output_lines
    assert output_lines[-1]


def _force_record(
    store: BuildStore,
    record: BuildRecord,
    *,
    agent_version: str | None = None,
    base_digest: str | None = None,
    built_at: str,
) -> None:
    updated = BuildRecord(
        agent=record.agent,
        base=record.base,
        agent_version=agent_version if agent_version is not None else record.agent_version,
        base_image=record.base_image,
        base_digest=base_digest if base_digest is not None else record.base_digest,
        image_ref=record.image_ref,
        built_at=built_at,
    )
    store.save(updated)


def _setup_workspace(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path, agent_name: str
) -> tuple[Path, Path, dict[str, str]]:
    home_dir = tmp_path / "home"
    workspace = tmp_path / "workspace"
    home_dir.mkdir()
    workspace.mkdir()
    monkeypatch.setenv("HOME", str(home_dir))
    monkeypatch.chdir(workspace)
    _write_project_config(workspace, agent_name)
    env = build_cli_env(home_dir)
    return home_dir, workspace, env


def _base_digest_available(record: BuildRecord) -> bool:
    cfg = SettingsStore().load_global()
    repository = f"{cfg.image_registry}/{cfg.image_base_repository}"
    digest = _local_query.get_local_repo_digest_for_repo(record.base_image, repository)
    return digest is not None


def test_builtin_agent_runs(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    _require_integration()
    _, workspace, env = _setup_workspace(monkeypatch, tmp_path, "codex")
    _run_agent(env, workspace, "codex")


def test_local_builtin_agent_rebuilds(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    _require_integration()
    _, workspace, env = _setup_workspace(monkeypatch, tmp_path, "claude")
    _run_agent(env, workspace, "claude")

    store = BuildStore()
    record = store.load("claude", "ubuntu")
    assert record is not None

    _force_record(
        store,
        record,
        agent_version="0.0.0",
        built_at="2000-01-01T00:00:00+00:00",
    )
    _run_agent(env, workspace, "claude")
    updated = store.load("claude", "ubuntu")
    assert updated is not None
    assert updated.built_at != "2000-01-01T00:00:00+00:00"
    assert updated.agent_version != "0.0.0"

    if _base_digest_available(updated):
        _force_record(
            store,
            updated,
            base_digest="sha256:old",
            built_at="2000-01-02T00:00:00+00:00",
        )
        _run_agent(env, workspace, "claude")
        refreshed = store.load("claude", "ubuntu")
        assert refreshed is not None
        assert refreshed.built_at != "2000-01-02T00:00:00+00:00"
        assert refreshed.base_digest != "sha256:old"
    else:
        pytest.skip("Base image digest unavailable; cannot verify base digest rebuild.")


def test_custom_agent_rebuilds(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    _require_integration()
    _, workspace, env = _setup_workspace(monkeypatch, tmp_path, "forge")
    agent_dir = Path(os.path.expanduser(DEFAULT_CUSTOM_AGENTS_DIR)) / "forge"
    copy_forge_sample(agent_dir)

    _run_agent(env, workspace, "forge")
    store = BuildStore()
    record = store.load("forge", "ubuntu")
    assert record is not None

    _force_record(
        store,
        record,
        agent_version="0.0.0",
        built_at="2000-01-03T00:00:00+00:00",
    )
    _run_agent(env, workspace, "forge")
    updated = store.load("forge", "ubuntu")
    assert updated is not None
    assert updated.built_at != "2000-01-03T00:00:00+00:00"
    assert updated.agent_version != "0.0.0"

    if _base_digest_available(updated):
        _force_record(
            store,
            updated,
            base_digest="sha256:old",
            built_at="2000-01-04T00:00:00+00:00",
        )
        _run_agent(env, workspace, "forge")
        refreshed = store.load("forge", "ubuntu")
        assert refreshed is not None
        assert refreshed.built_at != "2000-01-04T00:00:00+00:00"
        assert refreshed.base_digest != "sha256:old"
    else:
        pytest.skip("Base image digest unavailable; cannot verify base digest rebuild.")
