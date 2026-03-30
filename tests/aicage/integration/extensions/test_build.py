from pathlib import Path

import pytest

from aicage.constants import IMAGE_REGISTRY, IMAGE_REPOSITORY
from aicage.docker.query import local_image_exists
from aicage.registry.extension_build._store import BuildStore

from .._helpers import (
    assert_marker_extension_ready,
    assert_old_image_replaced,
    assert_rootfs_layer_present,
    keep_pulled_image_last_rootfs_layer,
    replace_with_dummy_image,
    resolve_remote_digest_ref,
    setup_marker_extension_workspace,
)

pytestmark = pytest.mark.integration


def test_extension_builds_and_runs(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    share_dir = tmp_path / "marker-share"
    share_dir.mkdir()
    workspace, env, _ = setup_marker_extension_workspace(
        monkeypatch,
        tmp_path,
        "codex",
        shares=[str(share_dir)],
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
    share_dir = tmp_path / "marker-share"
    share_dir.mkdir()
    workspace, env, image_ref = setup_marker_extension_workspace(
        monkeypatch,
        tmp_path,
        "copilot",
        shares=[str(share_dir)],
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
