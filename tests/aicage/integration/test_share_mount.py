from pathlib import Path

import pytest

from aicage.config.config_store import SettingsStore
from aicage.paths import container_project_path

from ._helpers import require_integration, run_cli_pty, setup_marker_extension_workspace, setup_workspace

pytestmark = pytest.mark.integration


def test_share_mounts_directory(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    require_integration()
    workspace, env = setup_workspace(monkeypatch, tmp_path, "copilot")
    share_dir = tmp_path / "share"
    share_dir.mkdir()
    container_path = container_project_path(share_dir).as_posix()
    exit_code, output = run_cli_pty(
        [
            "--yes",
            "--share",
            str(share_dir),
            "--env",
            "AICAGE_ENTRYPOINT_CMD=bash",
            "--",
            "copilot",
            "-lc",
            f"test -d {container_path} && touch {container_path}/ok.txt",
        ],
        env=env,
        cwd=workspace,
    )

    assert exit_code == 0, output
    assert (share_dir / "ok.txt").exists()


def test_share_mounts_directory_read_only(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    require_integration()
    workspace, env = setup_workspace(monkeypatch, tmp_path, "copilot")
    share_dir = tmp_path / "share-ro"
    share_dir.mkdir()
    container_path = container_project_path(share_dir).as_posix()
    exit_code, output = run_cli_pty(
        [
            "--yes",
            "--share",
            f"{share_dir}:ro",
            "--env",
            "AICAGE_ENTRYPOINT_CMD=bash",
            "--",
            "copilot",
            "-lc",
            f"test -d {container_path} && touch {container_path}/blocked.txt",
        ],
        env=env,
        cwd=workspace,
    )

    assert exit_code != 0, output
    assert not (share_dir / "blocked.txt").exists()


def test_extension_defined_share_mounts_directory(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    require_integration()
    share_dir = tmp_path / "marker-share"
    share_dir.mkdir()
    workspace, env, _ = setup_marker_extension_workspace(
        monkeypatch,
        tmp_path,
        "copilot",
        shares=[str(share_dir)],
    )
    container_path = container_project_path(share_dir).as_posix()
    exit_code, output = run_cli_pty(
        [
            "--yes",
            "copilot",
            "-lc",
            f"test -d {container_path} && touch {container_path}/ok.txt",
        ],
        env=env,
        cwd=workspace,
    )

    assert exit_code == 0, output
    assert (share_dir / "ok.txt").exists()

    project_cfg = SettingsStore().load_project(workspace)
    assert project_cfg is not None
    assert project_cfg.agents["copilot"].extension_mounts == {"marker": True}
