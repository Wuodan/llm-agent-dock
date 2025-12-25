from pathlib import Path
from unittest import TestCase, mock

from aicage.config.global_config import GlobalConfig
from aicage.config.runtime_config import RunConfig
from aicage.registry import _local_query


class FakeCompleted:
    def __init__(self, stdout: str = "", stderr: str = "", returncode: int = 0):
        self.stdout = stdout
        self.stderr = stderr
        self.returncode = returncode


class LocalQueryTests(TestCase):
    def _build_run_config(self, image_ref: str) -> RunConfig:
        return RunConfig(
            project_path=Path("/tmp/project"),
            tool="codex",
            image_ref=image_ref,
            global_cfg=GlobalConfig(
                image_registry="ghcr.io",
                image_registry_api_url="https://ghcr.io/v2",
                image_registry_api_token_url="https://ghcr.io/token?service=ghcr.io&scope=repository",
                image_repository="aicage/aicage",
                default_image_base="ubuntu",
            ),
            global_docker_args="",
            project_docker_args="",
            mounts=[],
            mount_preferences=mock.Mock(),
        )

    def test_get_local_repo_digest(self) -> None:
        run_config = self._build_run_config("repo:tag")
        with mock.patch(
            "aicage.registry._local_query.subprocess.run",
            return_value=FakeCompleted(returncode=1, stdout=""),
        ):
            self.assertIsNone(_local_query._get_local_repo_digest(run_config))

        with mock.patch(
            "aicage.registry._local_query.subprocess.run",
            return_value=FakeCompleted(returncode=0, stdout="not-json"),
        ):
            self.assertIsNone(_local_query._get_local_repo_digest(run_config))

        with mock.patch(
            "aicage.registry._local_query.subprocess.run",
            return_value=FakeCompleted(returncode=0, stdout='{"bad": "data"}'),
        ):
            self.assertIsNone(_local_query._get_local_repo_digest(run_config))

        payload = '["ghcr.io/aicage/aicage@sha256:deadbeef", "other@sha256:skip"]'
        with mock.patch(
            "aicage.registry._local_query.subprocess.run",
            return_value=FakeCompleted(returncode=0, stdout=payload),
        ):
            digest = _local_query._get_local_repo_digest(run_config)
        self.assertEqual("sha256:deadbeef", digest)
