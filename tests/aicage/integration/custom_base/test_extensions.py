from pathlib import Path

import pytest

from aicage.config.config_store import SettingsStore
from aicage.constants import DEFAULT_EXTENDED_IMAGE_NAME

from .._helpers import (
    assert_marker_extension_ready,
    copy_custom_base_sample,
    copy_forge_sample,
    copy_marker_extension_sample,
    custom_agents_dir,
    custom_bases_dir,
    custom_extensions_dir,
    require_integration,
    setup_workspace,
)

pytestmark = pytest.mark.integration

_CUSTOM_BASE_NAME: str = "php"


@pytest.mark.parametrize(
    ("agent_name", "is_custom_agent"),
    [
        ("codex", False),
        ("copilot", False),
        ("forge", True),
    ],
)
def test_custom_base_extension_builds_and_runs(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    agent_name: str,
    is_custom_agent: bool,
) -> None:
    require_integration()
    share_dir = tmp_path / f"{agent_name}-marker-share"
    share_dir.mkdir()
    workspace, env = setup_workspace(
        monkeypatch,
        tmp_path,
        agent_name,
        docker_args="--env AICAGE_ENTRYPOINT_CMD=bash",
    )
    base_dir = custom_bases_dir() / _CUSTOM_BASE_NAME
    base_dir.parent.mkdir(parents=True, exist_ok=True)
    copy_custom_base_sample(_CUSTOM_BASE_NAME, base_dir)
    if is_custom_agent:
        agent_dir = custom_agents_dir() / agent_name
        copy_forge_sample(agent_dir)

    extension_dir = custom_extensions_dir() / "marker"
    extension_dir.parent.mkdir(parents=True, exist_ok=True)
    copy_marker_extension_sample(extension_dir)
    (extension_dir / "extension.yml").write_text(
        (extension_dir / "extension.yml").read_text(encoding="utf-8").rstrip()
        + f"\nshares:\n  - {share_dir}\n",
        encoding="utf-8",
    )

    _configure_extension(workspace, agent_name, _CUSTOM_BASE_NAME)

    assert_marker_extension_ready(env, workspace, agent_name, share_dir=share_dir)


def _configure_extension(workspace: Path, agent_name: str, base_name: str) -> None:
    store = SettingsStore()
    project_cfg = store.load_project(workspace)
    agent_cfg = project_cfg.agents[agent_name]
    agent_cfg.base = base_name
    agent_cfg.docker_args = "--env AICAGE_ENTRYPOINT_CMD=bash"
    agent_cfg.image_ref = f"{DEFAULT_EXTENDED_IMAGE_NAME}:{agent_name}-{base_name}-marker"
    agent_cfg.extensions = ["marker"]
    store.save_project(workspace, project_cfg)
