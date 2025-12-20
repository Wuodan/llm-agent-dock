import json
from unittest import TestCase, mock

from aicage.registry.discovery import catalog


class DiscoveryTests(TestCase):
    @staticmethod
    def _fake_context() -> mock.Mock:
        return mock.Mock(
            global_cfg=mock.Mock(
                image_registry="ghcr.io",
                image_repository="aicage/aicage",
                image_registry_api_url="https://ghcr.io/v2",
                image_registry_api_token_url="https://ghcr.io/token?service=ghcr.io&scope=repository",
            ),
            image_repository_ref=lambda: "ghcr.io/aicage/aicage",
        )

    def test_discover_base_aliases_parses_latest(self) -> None:
        class FakeResponse:
            def __init__(self, payload: dict, headers: dict | None = None) -> None:
                self._payload = payload
                self.headers = headers or {}

            def __enter__(self):
                return self

            def __exit__(self, exc_type, exc, tb):
                return False

            def read(self) -> bytes:
                return json.dumps(self._payload).encode("utf-8")

        token_url = "https://ghcr.io/token?service=ghcr.io&scope=repository:aicage/aicage:pull"
        first_tags_url = "https://ghcr.io/v2/aicage/aicage/tags/list?n=1000"
        next_tags_url = "https://ghcr.io/v2/aicage/aicage/tags/list?n=1000&last=codex-ubuntu-latest"

        def fake_urlopen(request):  # pylint: disable=unused-argument
            url = request.full_url if hasattr(request, "full_url") else request
            if url == token_url:
                return FakeResponse({"token": "abc"})
            if url == first_tags_url:
                payload = {"tags": ["codex-ubuntu-latest", "codex-ubuntu-amd64-latest", "codex-fedora-1.0"]}
                headers = {"Link": f'<{next_tags_url}>; rel="next"'}
                return FakeResponse(payload, headers)
            if url == next_tags_url:
                payload = {"tags": ["codex-debian-latest", "codex-debian-arm64-latest", "cline-ubuntu-latest"]}
                return FakeResponse(payload)
            raise AssertionError(f"Unexpected URL {url}")

        with (
            mock.patch("urllib.request.urlopen", fake_urlopen),
            mock.patch("aicage.registry.discovery.catalog.discover_local_bases", return_value=[]),
        ):
            aliases = catalog.discover_tool_bases(self._fake_context(), "codex")

        self.assertEqual(["debian", "ubuntu"], aliases)

    def test_discover_base_aliases_http_failure(self) -> None:
        def fake_urlopen(url: str):  # pylint: disable=unused-argument
            raise OSError("network down")

        with (
            mock.patch("urllib.request.urlopen", fake_urlopen),
            mock.patch("aicage.registry.discovery.catalog.discover_local_bases", return_value=[]),
        ):
            aliases = catalog.discover_tool_bases(self._fake_context(), "codex")
        self.assertEqual([], aliases)

    def test_discover_base_aliases_invalid_json(self) -> None:
        class FakeResponse:
            def __enter__(self):
                return self

            def __exit__(self, exc_type, exc, tb):
                return False

            @staticmethod
            def read() -> bytes:
                return b"not-json"

            headers = {}

        def fake_urlopen(request):  # pylint: disable=unused-argument
            return FakeResponse()

        with (
            mock.patch("urllib.request.urlopen", fake_urlopen),
            mock.patch("aicage.registry.discovery.catalog.discover_local_bases", return_value=[]),
        ):
            aliases = catalog.discover_tool_bases(self._fake_context(), "codex")
        self.assertEqual([], aliases)
