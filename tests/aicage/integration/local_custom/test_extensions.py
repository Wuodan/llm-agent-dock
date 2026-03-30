from pathlib import Path

import pytest

from aicage.config.config_store import SettingsStore
from aicage.constants import DEFAULT_EXTENDED_IMAGE_NAME
from aicage.docker.query import local_image_exists
from aicage.registry.agent_build._store import BuildStore as AgentBuildStore
from aicage.registry.extension_build._store import BuildStore as ExtendedBuildStore

from .._helpers import (
    assert_marker_extension_ready,
    assert_old_image_replaced,
    assert_rootfs_layer_present,
    copy_forge_sample,
    copy_marker_extension_sample,
    custom_agents_dir,
    custom_extensions_dir,
    force_record_agent_version,
    get_last_rootfs_layer,
    replace_with_dummy_image,
    require_integration,
    setup_workspace,
)

pytestmark = pytest.mark.integration


def test_local_custom_extension_builds_and_runs(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    require_integration()
    workspace, env, share_dir = _setup_extension_workspace(monkeypatch, tmp_path)
    assert_marker_extension_ready(env, workspace, "forge", share_dir=share_dir)


def test_local_custom_extension_rebuilds_on_agent_version(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    require_integration()
    workspace, env, share_dir = _setup_extension_workspace(monkeypatch, tmp_path)
    assert_marker_extension_ready(env, workspace, "forge", share_dir=share_dir)

    store = AgentBuildStore()
    record = store.load("forge", "ubuntu")
    assert record is not None
    force_record_agent_version(store, record, agent_version="0.0.0")
    old_image_ref = replace_with_dummy_image(record.image_ref)
    assert local_image_exists(old_image_ref)

    assert_marker_extension_ready(env, workspace, "forge", share_dir=share_dir)
    updated = store.load("forge", "ubuntu")
    assert updated is not None
    assert updated.agent_version != "0.0.0"
    assert_old_image_replaced(old_image_ref, record.image_ref)

    extended_record = ExtendedBuildStore().load(f"{DEFAULT_EXTENDED_IMAGE_NAME}:forge-ubuntu-marker")
    assert extended_record is not None
    expected_base_layer = get_last_rootfs_layer(extended_record.base_image)
    assert_rootfs_layer_present(expected_base_layer, extended_record.image_ref)


def test_local_custom_extension_rebuilds_on_base_layer(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    require_integration()
    workspace, env, share_dir = _setup_extension_workspace(monkeypatch, tmp_path)
    assert_marker_extension_ready(env, workspace, "forge", share_dir=share_dir)

    extended_store = ExtendedBuildStore()
    record = extended_store.load(f"{DEFAULT_EXTENDED_IMAGE_NAME}:forge-ubuntu-marker")
    assert record is not None

    expected_base_layer = get_last_rootfs_layer(record.base_image)
    old_image_ref = replace_with_dummy_image(record.image_ref)
    assert local_image_exists(old_image_ref)

    assert_marker_extension_ready(env, workspace, "forge", share_dir=share_dir)
    assert_old_image_replaced(old_image_ref, record.image_ref)
    assert_rootfs_layer_present(expected_base_layer, record.image_ref)


def _setup_extension_workspace(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> tuple[Path, dict[str, str], Path]:
    workspace, env = setup_workspace(
        monkeypatch,
        tmp_path,
        "forge",
        docker_args="--env AICAGE_ENTRYPOINT_CMD=bash",
    )
    share_dir = tmp_path / "forge-marker-share"
    share_dir.mkdir()
    agent_dir = custom_agents_dir() / "forge"
    copy_forge_sample(agent_dir)

    extension_dir = custom_extensions_dir() / "marker"
    extension_dir.parent.mkdir(parents=True, exist_ok=True)
    copy_marker_extension_sample(extension_dir)
    (extension_dir / "extension.yml").write_text(
        (extension_dir / "extension.yml").read_text(encoding="utf-8").rstrip()
        + f"\nshares:\n  - {share_dir}\n",
        encoding="utf-8",
    )

    store = SettingsStore()
    project_cfg = store.load_project(workspace)
    agent_cfg = project_cfg.agents["forge"]
    agent_cfg.base = "ubuntu"
    agent_cfg.docker_args = "--env AICAGE_ENTRYPOINT_CMD=bash"
    agent_cfg.image_ref = f"{DEFAULT_EXTENDED_IMAGE_NAME}:forge-ubuntu-marker"
    agent_cfg.extensions = ["marker"]
    store.save_project(workspace, project_cfg)
    return workspace, env, share_dir
