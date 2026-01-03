from pathlib import Path
from unittest import TestCase, mock

from docker.errors import ImageNotFound

from aicage.config.global_config import GlobalConfig
from aicage.config.runtime_config import RunConfig
from aicage.registry import _local_query
from aicage.registry.images_metadata.models import (
    _AGENT_KEY,
    _AICAGE_IMAGE_BASE_KEY,
    _AICAGE_IMAGE_KEY,
    _BASE_IMAGE_DESCRIPTION_KEY,
    _BASE_IMAGE_DISTRO_KEY,
    _BASES_KEY,
    _OS_INSTALLER_KEY,
    _ROOT_IMAGE_KEY,
    _TEST_SUITE_KEY,
    _VALID_BASES_KEY,
    _VERSION_KEY,
    AGENT_FULL_NAME_KEY,
    AGENT_HOMEPAGE_KEY,
    AGENT_PATH_KEY,
    BUILD_LOCAL_KEY,
    ImagesMetadata,
)


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
            base="ubuntu",
            image_ref=image_ref,
            agent_version=None,
            global_cfg=GlobalConfig(
                image_registry="ghcr.io",
                image_registry_api_url="https://ghcr.io/v2",
                image_registry_api_token_url="https://ghcr.io/token?service=ghcr.io&scope=repository",
                image_repository="aicage/aicage",
                image_base_repository="aicage/aicage-image-base",
                default_image_base="ubuntu",
                version_check_image="ghcr.io/aicage/aicage-image-util:agent-version",
                local_image_repository="aicage",
                agents={},
            ),
            images_metadata=self._get_images_metadata(),
            project_docker_args="",
            mounts=[],
        )

    @staticmethod
    def _get_images_metadata() -> ImagesMetadata:
        return ImagesMetadata.from_mapping(
            {
                _AICAGE_IMAGE_KEY: {_VERSION_KEY: "0.3.3"},
                _AICAGE_IMAGE_BASE_KEY: {_VERSION_KEY: "0.3.3"},
                _BASES_KEY: {
                    "ubuntu": {
                        _ROOT_IMAGE_KEY: "ubuntu:latest",
                        _BASE_IMAGE_DISTRO_KEY: "Ubuntu",
                        _BASE_IMAGE_DESCRIPTION_KEY: "Default",
                        _OS_INSTALLER_KEY: "distro/debian/install.sh",
                        _TEST_SUITE_KEY: "default",
                    }
                },
                _AGENT_KEY: {
                    "codex": {
                        AGENT_PATH_KEY: "~/.codex",
                        AGENT_FULL_NAME_KEY: "Codex CLI",
                        AGENT_HOMEPAGE_KEY: "https://example.com",
                        BUILD_LOCAL_KEY: False,
                        _VALID_BASES_KEY: {"ubuntu": "ghcr.io/aicage/aicage:codex-ubuntu"},
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
