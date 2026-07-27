import socket
import ssl
import urllib.error
from email.message import Message
from unittest import TestCase

from aicage._network import classify_network_failure, host_from_url, require_http_url


class NetworkTests(TestCase):
    def test_classify_network_failure_dns(self) -> None:
        error = urllib.error.URLError(socket.gaierror(-2, "Name or service not known"))
        self.assertEqual("dns", classify_network_failure(error))

    def test_classify_network_failure_timeout(self) -> None:
        error = urllib.error.URLError(TimeoutError("timed out"))
        self.assertEqual("connect_or_timeout", classify_network_failure(error))

    def test_classify_network_failure_tls(self) -> None:
        error = urllib.error.URLError(ssl.SSLError("tls failed"))
        self.assertEqual("tls", classify_network_failure(error))

    def test_classify_network_failure_proxy_auth(self) -> None:
        headers = Message()
        error = urllib.error.HTTPError(
            "https://example.test", 407, "Proxy Auth Required", headers, None
        )
        self.assertEqual("proxy_auth_407", classify_network_failure(error))

    def test_classify_network_failure_auth(self) -> None:
        headers = Message()
        error = urllib.error.HTTPError(
            "https://example.test", 403, "Forbidden", headers, None
        )
        self.assertEqual("auth_401_403", classify_network_failure(error))

    def test_classify_network_failure_other_http_error(self) -> None:
        headers = Message()
        error = urllib.error.HTTPError(
            "https://example.test", 500, "Server Error", headers, None
        )
        self.assertEqual("http_error", classify_network_failure(error))

    def test_host_from_url_returns_hostname(self) -> None:
        self.assertEqual(
            "api.github.com", host_from_url("https://api.github.com/repos")
        )

    def test_host_from_url_returns_original_when_hostname_missing(self) -> None:
        self.assertEqual("not-a-url", host_from_url("not-a-url"))

    def test_require_http_url_accepts_https(self) -> None:
        self.assertEqual(
            "https://example.test/path", require_http_url("https://example.test/path")
        )

    def test_require_http_url_rejects_file_scheme(self) -> None:
        with self.assertRaises(urllib.error.URLError):
            require_http_url("file:///tmp/example.json")
