import os
from pathlib import Path
from unittest import TestCase, mock

from aicage.docker import runtime
from aicage.docker.errors import DockerError


class ContainerRuntimeTests(TestCase):
    def setUp(self) -> None:
        runtime.get_container_runtime.cache_clear()

    def test_get_container_runtime_prefers_docker(self) -> None:
        with mock.patch("aicage.docker.runtime.shutil.which", side_effect=["/usr/bin/docker", "/usr/bin/podman"]):
            selected_runtime = runtime.get_container_runtime()
        self.assertEqual("docker", selected_runtime)

    def test_get_container_runtime_falls_back_to_podman(self) -> None:
        with mock.patch("aicage.docker.runtime.shutil.which", side_effect=[None, "/usr/bin/podman"]):
            selected_runtime = runtime.get_container_runtime()
        self.assertEqual("podman", selected_runtime)

    def test_get_container_runtime_raises_when_missing(self) -> None:
        with mock.patch("aicage.docker.runtime.shutil.which", return_value=None):
            with self.assertRaises(DockerError) as raised:
                runtime.get_container_runtime()
        self.assertEqual(
            "Container runtime CLI not found. Install Docker or Podman and ensure it is on PATH.",
            str(raised.exception),
        )

    def test_get_container_runtime_socket_path_returns_docker_socket(self) -> None:
        with mock.patch("aicage.docker.runtime.get_container_runtime", return_value="docker"):
            socket_path = runtime.get_container_runtime_socket_path()
        self.assertEqual(Path("/run/docker.sock"), socket_path)

    def test_get_container_runtime_socket_path_prefers_existing_podman_socket(self) -> None:
        with (
            mock.patch("aicage.docker.runtime.get_container_runtime", return_value="podman"),
            mock.patch.dict(os.environ, {"XDG_RUNTIME_DIR": "/tmp/runtime"}, clear=True),
            mock.patch("aicage.docker.runtime.Path.exists", side_effect=[True, False, False]),
        ):
            socket_path = runtime.get_container_runtime_socket_path()
        self.assertEqual(Path("/tmp/runtime/podman/podman.sock"), socket_path)

    def test_get_container_runtime_socket_path_falls_back_to_user_socket(self) -> None:
        with (
            mock.patch("aicage.docker.runtime.get_container_runtime", return_value="podman"),
            mock.patch.dict(os.environ, {}, clear=True),
            mock.patch("aicage.docker.runtime.os.getuid", return_value=1000, create=True),
            mock.patch("aicage.docker.runtime.Path.exists", return_value=False),
        ):
            socket_path = runtime.get_container_runtime_socket_path()
        self.assertEqual(Path("/run/user/1000/podman/podman.sock"), socket_path)
