import io
import json
from unittest import TestCase, mock

from aicage.discovery import DiscoveryError, discover_base_aliases


class DiscoveryTests(TestCase):
    def test_discover_base_aliases_parses_latest(self) -> None:
        payload = {
            "results": [
                {"name": "codex-ubuntu-latest"},
                {"name": "codex-fedora-1.0"},
                {"name": "codex-debian-latest"},
                {"name": "cline-ubuntu-latest"},
            ],
            "next": "",
        }

        class FakeResponse:
            def __enter__(self):
                return io.BytesIO(json.dumps(payload).encode("utf-8"))

            def __exit__(self, exc_type, exc, tb):
                return False

        def fake_urlopen(url: str):  # pylint: disable=unused-argument
            return FakeResponse()

        with mock.patch("urllib.request.urlopen", fake_urlopen):
            aliases = discover_base_aliases("aicage/aicage", "codex")

        self.assertEqual(["debian", "ubuntu"], aliases)

    def test_discover_base_aliases_http_failure(self) -> None:
        def fake_urlopen(url: str):  # pylint: disable=unused-argument
            raise OSError("network down")

        with mock.patch("urllib.request.urlopen", fake_urlopen):
            with self.assertRaises(DiscoveryError):
                discover_base_aliases("aicage/aicage", "codex")

    def test_discover_base_aliases_invalid_json(self) -> None:
        class FakeResponse:
            def __enter__(self):
                return io.BytesIO(b"not-json")

            def __exit__(self, exc_type, exc, tb):
                return False

        def fake_urlopen(url: str):  # pylint: disable=unused-argument
            return FakeResponse()

        with mock.patch("urllib.request.urlopen", fake_urlopen):
            with self.assertRaises(DiscoveryError):
                discover_base_aliases("aicage/aicage", "codex")
