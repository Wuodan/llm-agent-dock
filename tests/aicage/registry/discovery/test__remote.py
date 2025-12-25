from unittest import TestCase, mock

from aicage.registry.discovery import _remote as registry_remote


class RemoteDiscoveryTests(TestCase):
    def test_discover_base_aliases_paginates(self) -> None:
        def fake_fetch_token(global_cfg) -> str:
            return "token"

        first_page = {"tags": ["codex-ubuntu-latest", "codex-ubuntu-amd64-latest", "other-latest"]}
        next_page = {"tags": ["codex-debian-latest", "codex-debian-arm64-latest"]}

        def fake_fetch_json(url: str, headers: dict[str, str] | None):
            if url.endswith("/tags/list?n=1000"):
                link = '<https://ghcr.io/v2/aicage/aicage/tags/list?n=1000&last=codex-ubuntu-latest>; rel="next"'
                return first_page, {"Link": link}
            if url.endswith("last=codex-ubuntu-latest"):
                return next_page, {}
            raise AssertionError(f"Unexpected URL {url}")

        context = mock.Mock(
            global_cfg=mock.Mock(
                image_registry_api_url="https://ghcr.io/v2",
                image_repository="aicage/aicage",
                image_registry_api_token_url="https://ghcr.io/token?service=ghcr.io&scope=repository",
            )
        )

        with (
            mock.patch("aicage.registry.discovery._remote._fetch_pull_token", fake_fetch_token),
            mock.patch("aicage.registry.discovery._remote._fetch_json", fake_fetch_json),
        ):
            aliases = registry_remote.discover_base_aliases(context, "codex")

        self.assertEqual(["debian", "ubuntu"], aliases)

    def test_fetch_pull_token_missing_token(self) -> None:
        def fake_fetch_json(url: str, headers: dict[str, str] | None):
            return {}, {}

        with mock.patch("aicage.registry.discovery._remote._fetch_json", fake_fetch_json):
            with self.assertRaises(registry_remote.RegistryDiscoveryError):
                registry_remote._fetch_pull_token(
                    mock.Mock(
                        image_registry_api_token_url="https://example.test/token",
                        image_repository="repo",
                    )
                )

    def test_parse_next_link(self) -> None:
        header = '<https://example.test/next?page=2>; rel="next", <https://example.test/last>; rel="last"'
        link = registry_remote._parse_next_link(header)
        self.assertEqual("https://example.test/next?page=2", link)
