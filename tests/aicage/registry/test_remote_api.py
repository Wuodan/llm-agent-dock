from unittest import TestCase, mock

from aicage.registry import remote_api


class RemoteApiTests(TestCase):
    def test_fetch_pull_token_missing_token(self) -> None:
        def fake_fetch_json(url: str, headers: dict[str, str] | None):
            return {}, {}

        with mock.patch("aicage.registry.remote_api.fetch_json", fake_fetch_json):
            with self.assertRaises(remote_api.RegistryDiscoveryError):
                remote_api.fetch_pull_token(
                    mock.Mock(
                        image_registry_api_token_url="https://example.test/token",
                        image_repository="repo",
                    )
                )
