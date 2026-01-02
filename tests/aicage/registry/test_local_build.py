import tempfile
from pathlib import Path
from unittest import TestCase, mock

import yaml

from aicage.config.global_config import GlobalConfig
from aicage.config.runtime_config import RunConfig
from aicage.registry._local_build import ensure_local_image
from aicage.registry.images_metadata.models import ImagesMetadata


class LocalBuildTests(TestCase):
    def test_builds_when_missing_image(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            state_dir = Path(tmp_dir) / "state"
            log_dir = Path(tmp_dir) / "logs"
            run_config = self._run_config()

            with (
                mock.patch("aicage.registry._local_build._DEFAULT_STATE_DIR", str(state_dir)),
                mock.patch("aicage.registry._local_build._DEFAULT_LOG_DIR", str(log_dir)),
                mock.patch("aicage.registry._local_build._local_image_exists", return_value=False),
                mock.patch("aicage.registry._local_build._refresh_base_digest", return_value="sha256:base"),
                mock.patch("aicage.registry._local_build._run_build") as build_mock,
                mock.patch(
                    "aicage.registry._local_build._local_query.get_local_repo_digest_for_repo",
                    return_value="sha256:base",
                ),
            ):
                ensure_local_image(run_config)

            build_mock.assert_called_once()
            record_path = state_dir / "claude-ubuntu.yaml"
            self.assertTrue(record_path.is_file())
            payload = yaml.safe_load(record_path.read_text(encoding="utf-8"))
            self.assertEqual("1.2.3", payload["agent_version"])

    def test_skips_when_up_to_date(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            state_dir = Path(tmp_dir) / "state"
            log_dir = Path(tmp_dir) / "logs"
            run_config = self._run_config()
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
                mock.patch("aicage.registry._local_build._DEFAULT_STATE_DIR", str(state_dir)),
                mock.patch("aicage.registry._local_build._DEFAULT_LOG_DIR", str(log_dir)),
                mock.patch("aicage.registry._local_build._local_image_exists", return_value=True),
                mock.patch("aicage.registry._local_build._refresh_base_digest", return_value="sha256:base"),
                mock.patch("aicage.registry._local_build._run_build") as build_mock,
            ):
                ensure_local_image(run_config)

            build_mock.assert_not_called()

    @staticmethod
    def _run_config() -> RunConfig:
        return RunConfig(
            project_path=Path("/tmp/project"),
            agent="claude",
            base="ubuntu",
            image_ref="aicage:claude-ubuntu",
            agent_version="1.2.3",
            global_cfg=GlobalConfig(
                image_registry="ghcr.io",
                image_registry_api_url="https://ghcr.io/v2",
                image_registry_api_token_url="https://ghcr.io/token?service=ghcr.io&scope=repository",
                image_repository="aicage/aicage",
                image_base_repository="aicage/aicage-image-base",
                default_image_base="ubuntu",
                version_check_image="ghcr.io/aicage/aicage-image-util:latest",
                agents={},
            ),
            images_metadata=LocalBuildTests._images_metadata(),
            project_docker_args="",
            mounts=[],
        )

    @staticmethod
    def _images_metadata() -> ImagesMetadata:
        return ImagesMetadata.from_mapping(
            {
                "aicage-image": {"version": "0.3.3"},
                "aicage-image-base": {"version": "0.3.3"},
                "bases": {
                    "ubuntu": {
                        "root_image": "ubuntu:latest",
                        "base_image_distro": "Ubuntu",
                        "base_image_description": "Default",
                        "os_installer": "distro/debian/install.sh",
                        "test_suite": "default",
                    }
                },
                "agent": {
                    "claude": {
                        "agent_path": "~/.claude",
                        "agent_full_name": "Claude Code",
                        "agent_homepage": "https://example.com",
                        "redistributable": False,
                        "valid_bases": {"ubuntu": "ghcr.io/aicage/aicage:claude-ubuntu"},
                    }
                },
            }
        )
