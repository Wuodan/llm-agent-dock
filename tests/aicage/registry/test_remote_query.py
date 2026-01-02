from unittest import TestCase, mock

from aicage.config.global_config import GlobalConfig
from aicage.registry import _remote_query
from aicage.registry._remote_api import RegistryDiscoveryError


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
    def test_get_remote_repo_digest_returns_none_on_token_error(self) -> None:
        with (
            mock.patch(
                "aicage.registry._remote_query.fetch_pull_token_for_repository",
                side_effect=RegistryDiscoveryError("boom"),
            ),
            mock.patch("aicage.registry._remote_query.urllib.request.urlopen") as urlopen_mock,
        ):
            digest = _remote_query.get_remote_repo_digest_for_repo(
                "ghcr.io/aicage/aicage:tag",
                "aicage/aicage",
                self._global_config(),
            )
        self.assertIsNone(digest)
        urlopen_mock.assert_not_called()

    def test_get_remote_repo_digest_with_token(self) -> None:
        with (
            mock.patch(
                "aicage.registry._remote_query.fetch_pull_token_for_repository",
                return_value="abc",
            ),
            mock.patch(
                "aicage.registry._remote_query.urllib.request.urlopen",
                return_value=FakeResponse({"Docker-Content-Digest": "sha256:remote"}),
            ),
        ):
            digest = _remote_query.get_remote_repo_digest_for_repo(
                "ghcr.io/aicage/aicage:tag",
                "aicage/aicage",
                self._global_config(),
            )
        self.assertEqual("sha256:remote", digest)

    def _global_config(self) -> GlobalConfig:
        return GlobalConfig(
            image_registry="ghcr.io",
            image_registry_api_url="https://ghcr.io/v2",
            image_registry_api_token_url="https://ghcr.io/token?service=ghcr.io&scope=repository",
            image_repository="aicage/aicage",
            image_base_repository="aicage/aicage-image-base",
            default_image_base="ubuntu",
            version_check_image="ghcr.io/aicage/aicage-image-util:latest",
            agents={},
        )
