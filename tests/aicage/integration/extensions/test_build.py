from pathlib import Path

import pytest

from aicage.config.config_store import SettingsStore
from aicage.constants import (
    DEFAULT_EXTENDED_IMAGE_NAME,
    IMAGE_REGISTRY,
    IMAGE_REPOSITORY,
)
from aicage.docker.query import local_image_exists
from aicage.registry.extension_build._store import BuildStore

from .._helpers import (
    assert_marker_extension_ready,
    assert_old_image_replaced,
    assert_rootfs_layer_present,
    copy_marker_dockerfile_extension_sample,
    custom_extensions_dir,
    keep_pulled_image_last_rootfs_layer,
    marker_shared_extension_dir,
    replace_with_dummy_image,
    require_integration,
    resolve_remote_digest_ref,
    setup_marker_extension_workspace,
    setup_workspace,
)

pytestmark = pytest.mark.integration


def test_dockerfile_extension_builds_and_runs(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    require_integration()
    workspace, env = setup_workspace(
        monkeypatch,
        tmp_path,
        "codex",
        docker_args="--env AICAGE_ENTRYPOINT_CMD=bash",
    )
    marker_shared_extension_dir(Path(env["HOME"])).mkdir(parents=True, exist_ok=True)
    extension_dir = custom_extensions_dir() / "marker-dockerfile"
    extension_dir.parent.mkdir(parents=True, exist_ok=True)
    copy_marker_dockerfile_extension_sample(extension_dir)

    store = SettingsStore()
    project_cfg = store.load_project(workspace)
    agent_cfg = project_cfg.agents["codex"]
    agent_cfg.base = "ubuntu"
    agent_cfg.docker_args = "--env AICAGE_ENTRYPOINT_CMD=bash"
    agent_cfg.image_ref = (
        f"{DEFAULT_EXTENDED_IMAGE_NAME}:codex-ubuntu-marker-dockerfile"
    )
    agent_cfg.extensions = ["marker-dockerfile"]
    agent_cfg.extension_mounts["marker-dockerfile"] = True
    store.save_project(workspace, project_cfg)

    assert_marker_extension_ready(env, workspace, "codex")


def test_extension_builds_and_runs(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    workspace, env, _, share_dir = setup_marker_extension_workspace(
        monkeypatch,
        tmp_path,
        "codex",
    )

    image_repository = f"{IMAGE_REGISTRY}/{IMAGE_REPOSITORY}"
    local_base_image_ref = f"{image_repository}:codex-ubuntu"
    old_image_ref = replace_with_dummy_image(local_base_image_ref)
    assert local_image_exists(old_image_ref)

    assert_marker_extension_ready(env, workspace, "codex", share_dir=share_dir)
    assert_old_image_replaced(old_image_ref, local_base_image_ref)


def test_extension_rebuilds_on_base_image_change(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    workspace, env, image_ref, share_dir = setup_marker_extension_workspace(
        monkeypatch,
        tmp_path,
        "copilot",
    )

    assert_marker_extension_ready(env, workspace, "copilot", share_dir=share_dir)

    extended_store = BuildStore()
    record = extended_store.load(image_ref)
    assert record is not None

    base_digest_ref = resolve_remote_digest_ref(record.base_image)
    with keep_pulled_image_last_rootfs_layer(base_digest_ref) as expected_base_layer:
        old_base_image_ref = replace_with_dummy_image(record.base_image)
        assert local_image_exists(old_base_image_ref)

        assert_marker_extension_ready(env, workspace, "copilot", share_dir=share_dir)
        assert_old_image_replaced(old_base_image_ref, record.base_image)
        assert_rootfs_layer_present(expected_base_layer, record.image_ref)
