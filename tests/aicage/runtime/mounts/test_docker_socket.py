from pathlib import Path
from unittest import TestCase, mock

from aicage.runtime.mounts._docker_socket import _resolve_docker_socket_mount


class DockerSocketMountTests(TestCase):
    def test_resolve_docker_socket_mount_persists_socket(self) -> None:
        tool_cfg: dict[str, object] = {}
        with mock.patch("aicage.runtime.mounts._docker_socket.prompt_yes_no", return_value=True):
            mounts = _resolve_docker_socket_mount(tool_cfg, True)

        self.assertEqual({"docker": True}, tool_cfg["mounts"])
        self.assertEqual(1, len(mounts))
        self.assertEqual(Path("/run/docker.sock"), mounts[0].container_path)

    def test_resolve_docker_socket_mount_uses_persisted_socket(self) -> None:
        tool_cfg: dict[str, object] = {"mounts": {"docker": True}}
        with mock.patch("aicage.runtime.mounts._docker_socket.prompt_yes_no") as prompt_mock:
            mounts = _resolve_docker_socket_mount(tool_cfg, False)

        prompt_mock.assert_not_called()
        self.assertEqual(1, len(mounts))

    def test_resolve_docker_socket_mount_disabled(self) -> None:
        tool_cfg: dict[str, object] = {}
        mounts = _resolve_docker_socket_mount(tool_cfg, False)

        self.assertEqual([], mounts)
