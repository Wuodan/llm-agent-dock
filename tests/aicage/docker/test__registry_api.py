import urllib.error
from email.message import Message
from unittest import TestCase, mock

from aicage.docker import _registry_api
from aicage.docker.types import _RegistryApiConfig


class RemoteApiTests(TestCase):
    def test_fetch_pull_token_returns_token(self) -> None:
        def fake_fetch_json(_url: str, _headers: dict[str, str] | None):
            return {"token": "abc"}, {}

        with mock.patch("aicage.docker._registry_api._fetch_json", fake_fetch_json):
            token = _registry_api._fetch_pull_token_for_repository(
                _RegistryApiConfig(
                    registry_api_url="https://example.test/api",
                    registry_api_token_url="https://example.test/token",
                ),
                "repo",
            )
        self.assertEqual("abc", token)

    def test_fetch_pull_token_missing_token(self) -> None:
        def fake_fetch_json(_url: str, _headers: dict[str, str] | None):
            return {}, {}

        with mock.patch("aicage.docker._registry_api._fetch_json", fake_fetch_json):
            with self.assertRaises(_registry_api._RegistryDiscoveryError):
                _registry_api._fetch_pull_token_for_repository(
                    _RegistryApiConfig(
                        registry_api_url="https://example.test/api",
                        registry_api_token_url="https://example.test/token",
                    ),
                    "repo",
                )

    def test_fetch_json_raises_on_request_failure(self) -> None:
        with mock.patch(
            "aicage.docker._registry_api.urllib.request.urlopen",
            side_effect=urllib.error.URLError("boom"),
        ):
            with self.assertRaises(_registry_api._RegistryDiscoveryError):
                _registry_api._fetch_json("https://example.test/api", None)

    def test_fetch_json_raises_on_http_error(self) -> None:
        headers = Message()
        error = urllib.error.HTTPError(
            "https://example.test/api", 500, "boom", hdrs=headers, fp=None
        )
        with mock.patch(
            "aicage.docker._registry_api.urllib.request.urlopen",
            side_effect=error,
        ):
            with self.assertRaises(_registry_api._RegistryDiscoveryError):
                _registry_api._fetch_json("https://example.test/api", None)

    def test_fetch_json_raises_on_invalid_json(self) -> None:
        response = mock.Mock()
        response.read.return_value = b"not-json"
        response.headers = {}
        response.__enter__ = mock.Mock(return_value=response)
        response.__exit__ = mock.Mock(return_value=None)
        with mock.patch(
            "aicage.docker._registry_api.urllib.request.urlopen",
            return_value=response,
        ):
            with self.assertRaises(_registry_api._RegistryDiscoveryError):
                _registry_api._fetch_json("https://example.test/api", None)

    def test_fetch_json_returns_payload_and_headers(self) -> None:
        response = mock.Mock()
        response.read.return_value = b'{"token": "abc"}'
        response.headers = {"x-test": "1"}
        response.__enter__ = mock.Mock(return_value=response)
        response.__exit__ = mock.Mock(return_value=None)
        with mock.patch(
            "aicage.docker._registry_api.urllib.request.urlopen",
            return_value=response,
        ):
            data, headers = _registry_api._fetch_json("https://example.test/api", None)
        self.assertEqual({"token": "abc"}, data)
        self.assertEqual({"x-test": "1"}, headers)

    def test_fetch_json_raises_on_non_http_scheme(self) -> None:
        with self.assertRaises(_registry_api._RegistryDiscoveryError):
            _registry_api._fetch_json("file:///tmp/example.json", None)
