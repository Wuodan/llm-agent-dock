from unittest import TestCase, mock

from docker.errors import DockerException

from aicage.docker import _client
from aicage.docker.errors import DockerError


class DockerClientTests(TestCase):
    def setUp(self) -> None:
        _client.get_docker_client.cache_clear()
        _client.get_docker_pull_client.cache_clear()

    @staticmethod
    def test_get_docker_client_uses_timeout() -> None:
        host = mock.Mock(host="unix:///run/docker.sock")
        with (
            mock.patch(
                "aicage.docker._client.get_active_docker_host", return_value=host
            ),
            mock.patch("aicage.docker._client.docker.DockerClient") as client_ctor,
        ):
            _client.get_docker_client()

        client_ctor.assert_called_once_with(
            base_url="unix:///run/docker.sock",
            timeout=_client.DOCKER_LOCAL_METADATA_TIMEOUT_SECONDS,
        )

    @staticmethod
    def test_get_docker_pull_client_uses_timeout() -> None:
        host = mock.Mock(host="unix:///run/docker.sock")
        with (
            mock.patch(
                "aicage.docker._client.get_active_docker_host", return_value=host
            ),
            mock.patch("aicage.docker._client.docker.DockerClient") as client_ctor,
        ):
            _client.get_docker_pull_client()

        client_ctor.assert_called_once_with(
            base_url="unix:///run/docker.sock",
            timeout=_client.DOCKER_PULL_REQUEST_TIMEOUT_SECONDS,
        )

    def test_get_docker_client_raises_clean_error_when_docker_missing(self) -> None:
        host = mock.Mock(host="unix:///run/docker.sock")
        with (
            mock.patch(
                "aicage.docker._client.get_active_docker_host", return_value=host
            ),
            mock.patch(
                "aicage.docker._client.docker.DockerClient",
                side_effect=DockerException("boom"),
            ),
        ):
            with self.assertRaises(DockerError) as raised:
                _client.get_docker_client()

        self.assertEqual(
            "Docker is not running or not reachable. Start Docker and retry.",
            str(raised.exception),
        )

    def test_get_docker_pull_client_raises_clean_error_when_docker_missing(self) -> None:
        host = mock.Mock(host="unix:///run/docker.sock")
        with (
            mock.patch(
                "aicage.docker._client.get_active_docker_host", return_value=host
            ),
            mock.patch(
                "aicage.docker._client.docker.DockerClient",
                side_effect=DockerException("boom"),
            ),
        ):
            with self.assertRaises(DockerError) as raised:
                _client.get_docker_pull_client()

        self.assertEqual(
            "Docker is not running or not reachable. Start Docker and retry.",
            str(raised.exception),
        )
