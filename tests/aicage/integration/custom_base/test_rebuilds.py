from pathlib import Path

import pytest
import yaml

from aicage.config.config_store import SettingsStore
from aicage.docker.query import local_image_exists
from aicage.registry.agent_build._store import BuildStore as AgentBuildStore
from aicage.registry.base_build._store import (
    BuildRecord,
)
from aicage.registry.base_build._store import (
    BuildStore as BaseBuildStore,
)
from aicage.registry.base_build.ensure import image_ref

from .._helpers import (
    assert_old_image_replaced,
    assert_rootfs_layer_present,
    copy_custom_base_sample,
    custom_bases_dir,
    force_record_agent_version,
    get_last_rootfs_layer,
    replace_with_dummy_image,
    require_integration,
    run_agent_version,
    setup_workspace,
)

pytestmark = pytest.mark.integration


def test_custom_base_rebuilds_on_agent_version(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    require_integration()
    base_name = "php"
    workspace, env = setup_workspace(monkeypatch, tmp_path, "codex")
    base_dir = custom_bases_dir() / base_name
    base_dir.parent.mkdir(parents=True, exist_ok=True)
    copy_custom_base_sample(base_name, base_dir)
    _set_agent_base(workspace, "codex", base_name)

    run_agent_version(env, workspace, "codex")
    store = AgentBuildStore()
    record = store.load("codex", base_name)
    assert record is not None

    force_record_agent_version(store, record, agent_version="0.0.0")
    run_agent_version(env, workspace, "codex")
    updated = store.load("codex", base_name)
    assert updated is not None
    assert updated.agent_version != "0.0.0"


def test_custom_base_rebuilds_on_digest_change_ghcr(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    require_integration()
    base_name = "debian-mirror"
    workspace, env = setup_workspace(monkeypatch, tmp_path, "codex")
    base_dir = custom_bases_dir() / base_name
    base_dir.parent.mkdir(parents=True, exist_ok=True)
    copy_custom_base_sample(base_name, base_dir)
    _update_from_image(base_dir, "ghcr.io/rblaine95/debian:bookworm")
    _set_agent_base(workspace, "codex", base_name)

    run_agent_version(env, workspace, "codex")
    base_store = BaseBuildStore()
    base_record = base_store.load(base_name)
    assert base_record is not None
    assert base_record.from_image == "ghcr.io/rblaine95/debian:bookworm"
    assert base_record.from_image_digest

    _update_from_image(base_dir, "ghcr.io/rblaine95/debian:bookworm-slim")
    run_agent_version(env, workspace, "codex")
    rebuilt_base_record = base_store.load(base_name)
    assert rebuilt_base_record is not None
    assert rebuilt_base_record.from_image == "ghcr.io/rblaine95/debian:bookworm-slim"
    assert rebuilt_base_record.from_image_digest
    assert rebuilt_base_record.from_image_digest != base_record.from_image_digest

    final_image_record = AgentBuildStore().load("codex", base_name)
    assert final_image_record is not None
    expected_base_image_layer = get_last_rootfs_layer(rebuilt_base_record.image_ref)
    assert_rootfs_layer_present(expected_base_image_layer, final_image_record.image_ref)


def test_custom_base_rebuilds_on_digest_change_registry_image(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    require_integration()
    base_name = "php"
    from_image = "php:latest"
    workspace, env = setup_workspace(monkeypatch, tmp_path, "codex")
    base_dir = custom_bases_dir() / base_name
    base_dir.parent.mkdir(parents=True, exist_ok=True)
    copy_custom_base_sample(base_name, base_dir)
    _set_agent_base(workspace, "codex", base_name)

    base_image_ref = image_ref(base_name)
    old_image_ref = replace_with_dummy_image(base_image_ref)
    assert local_image_exists(old_image_ref)

    base_store = BaseBuildStore()
    stale_digest = "sha256:" + ("0" * 64)
    base_store.save(
        BuildRecord(
            base=base_name,
            from_image=from_image,
            from_image_digest=stale_digest,
            image_ref=base_image_ref,
            built_at="2000-01-01T00:00:00Z",
        )
    )

    run_agent_version(env, workspace, "codex")
    rebuilt_base_record = base_store.load(base_name)
    assert rebuilt_base_record is not None
    assert rebuilt_base_record.from_image == from_image
    assert rebuilt_base_record.from_image_digest
    assert rebuilt_base_record.from_image_digest != stale_digest
    assert_old_image_replaced(old_image_ref, base_image_ref)

    final_image_record = AgentBuildStore().load("codex", base_name)
    assert final_image_record is not None
    expected_base_image_layer = get_last_rootfs_layer(rebuilt_base_record.image_ref)
    assert_rootfs_layer_present(expected_base_image_layer, final_image_record.image_ref)


def _set_agent_base(workspace: Path, agent_name: str, base_name: str) -> None:
    store = SettingsStore()
    project_cfg = store.load_project(workspace)
    agent_cfg = project_cfg.agents[agent_name]
    agent_cfg.base = base_name
    store.save_project(workspace, project_cfg)


def _update_from_image(base_dir: Path, from_image: str) -> None:
    definition_path = base_dir / "base.yml"
    payload = yaml.safe_load(definition_path.read_text(encoding="utf-8")) or {}
    payload["from_image"] = from_image
    definition_path.write_text(yaml.safe_dump(payload, sort_keys=True), encoding="utf-8")
