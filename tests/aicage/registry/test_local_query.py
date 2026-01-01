from pathlib import Path
from unittest import TestCase, mock

from docker.errors import ImageNotFound

from aicage.config.global_config import GlobalConfig
from aicage.config.runtime_config import RunConfig
from aicage.registry import _local_query
from aicage.registry.images_metadata.models import ImagesMetadata


class FakeImage:
    def __init__(self, repo_digests: object):
        self.attrs = {"RepoDigests": repo_digests}


class FakeImages:
    def __init__(self, image: FakeImage | None):
        self._image = image

    def get(self, image_ref: str) -> FakeImage:
        if self._image is None:
            raise ImageNotFound(image_ref)
        return self._image


class FakeClient:
    def __init__(self, image: FakeImage | None):
        self.images = FakeImages(image)


class LocalQueryTests(TestCase):
    def _build_run_config(self, image_ref: str) -> RunConfig:
        return RunConfig(
            project_path=Path("/tmp/project"),
            agent="codex",
            image_ref=image_ref,
            global_cfg=GlobalConfig(
                image_registry="ghcr.io",
                image_registry_api_url="https://ghcr.io/v2",
                image_registry_api_token_url="https://ghcr.io/token?service=ghcr.io&scope=repository",
                image_repository="aicage/aicage",
                default_image_base="ubuntu",
            ),
            images_metadata=self._get_images_metadata(),
            project_docker_args="",
            mounts=[],
        )

    @staticmethod
    def _get_images_metadata() -> ImagesMetadata:
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
                    "codex": {
                        "agent_path": "~/.codex",
                        "agent_full_name": "Codex CLI",
                        "agent_homepage": "https://example.com",
                        "redistributable": True,
                        "valid_bases": {"ubuntu": "ghcr.io/aicage/aicage:codex-ubuntu"},
                    }
                },
            }
        )

    def test_get_local_repo_digest(self) -> None:
        run_config = self._build_run_config("repo:tag")
        with mock.patch(
            "aicage.registry._local_query.get_docker_client",
            return_value=FakeClient(None),
        ):
            self.assertIsNone(_local_query.get_local_repo_digest(run_config))

        with mock.patch(
            "aicage.registry._local_query.get_docker_client",
            return_value=FakeClient(FakeImage(repo_digests={"bad": "data"})),
        ):
            self.assertIsNone(_local_query.get_local_repo_digest(run_config))

        with mock.patch(
            "aicage.registry._local_query.get_docker_client",
            return_value=FakeClient(FakeImage(repo_digests=["bad"])),
        ):
            self.assertIsNone(_local_query.get_local_repo_digest(run_config))

        payload = ["ghcr.io/aicage/aicage@sha256:deadbeef", "other@sha256:skip"]
        with mock.patch(
            "aicage.registry._local_query.get_docker_client",
            return_value=FakeClient(FakeImage(repo_digests=payload)),
        ):
            digest = _local_query.get_local_repo_digest(run_config)
        self.assertEqual("sha256:deadbeef", digest)
