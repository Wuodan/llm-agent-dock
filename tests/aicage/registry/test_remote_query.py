from pathlib import Path
from unittest import TestCase, mock

from aicage.config.global_config import GlobalConfig
from aicage.config.runtime_config import RunConfig
from aicage.registry import _remote_query
from aicage.registry._remote_api import RegistryDiscoveryError
from aicage.registry.images_metadata.models import ImagesMetadata


class FakeResponse:
    def __init__(self, headers: dict[str, str], payload: str = "") -> None:
        self.headers = headers
        self._payload = payload

    def read(self) -> bytes:
        return self._payload.encode("utf-8")

    def __enter__(self) -> "FakeResponse":
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        return None


class RemoteQueryTests(TestCase):
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
                version_check_image="ghcr.io/aicage/aicage-image-util:latest",
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

    def test_get_remote_repo_digest_returns_none_on_token_error(self) -> None:
        with (
            mock.patch(
                "aicage.registry._remote_query.fetch_pull_token",
                side_effect=RegistryDiscoveryError("boom"),
            ),
            mock.patch("aicage.registry._remote_query.urllib.request.urlopen") as urlopen_mock,
        ):
            digest = _remote_query.get_remote_repo_digest(self._build_run_config("ghcr.io/aicage/aicage:tag"))
        self.assertIsNone(digest)
        urlopen_mock.assert_not_called()

    def test_get_remote_repo_digest_with_token(self) -> None:
        with (
            mock.patch("aicage.registry._remote_query.fetch_pull_token", return_value="abc"),
            mock.patch(
                "aicage.registry._remote_query.urllib.request.urlopen",
                return_value=FakeResponse({"Docker-Content-Digest": "sha256:remote"}),
            ),
        ):
            digest = _remote_query.get_remote_repo_digest(self._build_run_config("ghcr.io/aicage/aicage:tag"))
        self.assertEqual("sha256:remote", digest)
