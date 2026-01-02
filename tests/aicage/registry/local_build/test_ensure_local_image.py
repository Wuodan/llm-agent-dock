import tempfile
from pathlib import Path
from unittest import TestCase, mock

import yaml

from aicage.errors import CliError
from aicage.registry.local_build import ensure_local_image as ensure_local_image_module

from ._fixtures import build_run_config


class EnsureLocalImageTests(TestCase):
    def test_ensure_local_image_skips_redistributable(self) -> None:
        run_config = build_run_config(redistributable=True)
        with mock.patch(
            "aicage.registry.local_build.ensure_local_image.refresh_base_digest"
        ) as refresh_mock:
            ensure_local_image_module.ensure_local_image(run_config)
        refresh_mock.assert_not_called()

    def test_ensure_local_image_raises_without_version(self) -> None:
        run_config = build_run_config(agent_version=None)
        with self.assertRaises(CliError):
            ensure_local_image_module.ensure_local_image(run_config)

    def test_ensure_local_image_builds_when_missing_image(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            state_dir = Path(tmp_dir) / "state"
            log_dir = Path(tmp_dir) / "logs"
            run_config = build_run_config()

            with (
                mock.patch(
                    "aicage.registry.local_build._store._DEFAULT_STATE_DIR",
                    str(state_dir),
                ),
                mock.patch(
                    "aicage.registry.local_build._logs._DEFAULT_LOG_DIR",
                    str(log_dir),
                ),
                mock.patch(
                    "aicage.registry.local_build._plan.local_image_exists",
                    return_value=False,
                ),
                mock.patch(
                    "aicage.registry.local_build.ensure_local_image.refresh_base_digest",
                    return_value="sha256:base",
                ),
                mock.patch(
                    "aicage.registry.local_build.ensure_local_image.run_build"
                ) as build_mock,
                mock.patch(
                    "aicage.registry.local_build.ensure_local_image._local_query.get_local_repo_digest_for_repo",
                    return_value="sha256:base",
                ),
            ):
                ensure_local_image_module.ensure_local_image(run_config)

            build_mock.assert_called_once()
            record_path = state_dir / "claude-ubuntu.yaml"
            payload = yaml.safe_load(record_path.read_text(encoding="utf-8"))
            self.assertEqual("1.2.3", payload["agent_version"])

    def test_ensure_local_image_skips_when_up_to_date(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            state_dir = Path(tmp_dir) / "state"
            log_dir = Path(tmp_dir) / "logs"
            run_config = build_run_config()
            record_path = state_dir / "claude-ubuntu.yaml"
            record_path.parent.mkdir(parents=True, exist_ok=True)
            record_path.write_text(
                yaml.safe_dump(
                    {
                        "agent": "claude",
                        "base": "ubuntu",
                        "agent_version": "1.2.3",
                        "base_image": "ghcr.io/aicage/aicage-image-base:ubuntu",
                        "base_digest": "sha256:base",
                        "image_ref": "aicage:claude-ubuntu",
                        "built_at": "2024-01-01T00:00:00+00:00",
                    }
                ),
                encoding="utf-8",
            )

            with (
                mock.patch(
                    "aicage.registry.local_build._store._DEFAULT_STATE_DIR",
                    str(state_dir),
                ),
                mock.patch(
                    "aicage.registry.local_build._logs._DEFAULT_LOG_DIR",
                    str(log_dir),
                ),
                mock.patch(
                    "aicage.registry.local_build._plan.local_image_exists",
                    return_value=True,
                ),
                mock.patch(
                    "aicage.registry.local_build.ensure_local_image.refresh_base_digest",
                    return_value="sha256:base",
                ),
                mock.patch(
                    "aicage.registry.local_build.ensure_local_image.run_build"
                ) as build_mock,
            ):
                ensure_local_image_module.ensure_local_image(run_config)

            build_mock.assert_not_called()
