from unittest import TestCase, mock

from aicage.cli_types import ParsedArgs
from aicage.config.context import ConfigContext
from aicage.config.project_config import AgentConfig, ProjectConfig, _AgentMounts
from aicage.runtime.docker_args._resolvers._docker_socket import resolve
from aicage.runtime.env_vars import DOCKER_HOST, WINDOWS_DOCKER_HOST

_MODULE = "aicage.runtime.docker_args._resolvers._docker_socket"


class DockerSocketMountTests(TestCase):
    def test_resolve_docker_socket_mount_persists_socket(self) -> None:
        agent_cfg = AgentConfig()
        context = _build_context(agent_cfg)
        parsed = _build_parsed(docker_socket=True)
        with (
            mock.patch(f"{_MODULE}.os.name", "posix"),
            mock.patch(f"{_MODULE}.get_container_runtime", return_value="podman"),
            mock.patch(
                f"{_MODULE}.get_container_runtime_socket_path",
                return_value=mock.Mock(as_posix=mock.Mock(return_value="/run/user/1000/podman/podman.sock")),
            ),
            mock.patch(f"{_MODULE}.prompt_persist_docker_socket", return_value=True),
        ):
            resolved = resolve(context, "codex", parsed)

        self.assertTrue(agent_cfg.mounts.docker)
        self.assertEqual(1, len(resolved.mounts))
        self.assertEqual("/run/user/1000/podman/podman.sock", resolved.mounts[0].host_path.as_posix())
        self.assertEqual([], resolved.env)

    def test_resolve_docker_socket_mount_uses_persisted_socket(self) -> None:
        agent_cfg = AgentConfig(mounts=_AgentMounts(docker=True))
        context = _build_context(agent_cfg)
        with (
            mock.patch(f"{_MODULE}.os.name", "posix"),
            mock.patch(f"{_MODULE}.get_container_runtime", return_value="docker"),
            mock.patch(
                f"{_MODULE}.get_container_runtime_socket_path",
                return_value=mock.Mock(as_posix=mock.Mock(return_value="/run/docker.sock")),
            ),
            mock.patch(f"{_MODULE}.prompt_persist_docker_socket") as prompt_mock,
        ):
            resolved = resolve(context, "codex", _build_parsed())

        prompt_mock.assert_not_called()
        self.assertEqual(1, len(resolved.mounts))
        self.assertEqual([], resolved.env)

    def test_resolve_docker_socket_mount_disabled(self) -> None:
        agent_cfg = AgentConfig()
        context = _build_context(agent_cfg)
        resolved = resolve(context, "codex", _build_parsed())

        self.assertEqual([], resolved.mounts)
        self.assertEqual([], resolved.env)

    def test_resolve_docker_socket_mount_windows_env(self) -> None:
        agent_cfg = AgentConfig(mounts=_AgentMounts(docker=True))
        context = _build_context(agent_cfg)
        with (
            mock.patch(f"{_MODULE}.os.name", "nt"),
            mock.patch(f"{_MODULE}.get_container_runtime", return_value="docker"),
        ):
            resolved = resolve(context, "codex", _build_parsed())

        self.assertEqual([], resolved.mounts)
        self.assertEqual(
            [(DOCKER_HOST, WINDOWS_DOCKER_HOST)],
            [(item.name, item.value) for item in resolved.env],
        )

    def test_resolve_docker_socket_mount_windows_podman_has_no_mapping(self) -> None:
        agent_cfg = AgentConfig(mounts=_AgentMounts(docker=True))
        context = _build_context(agent_cfg)
        with (
            mock.patch(f"{_MODULE}.os.name", "nt"),
            mock.patch(f"{_MODULE}.get_container_runtime", return_value="podman"),
        ):
            resolved = resolve(context, "codex", _build_parsed())

        self.assertEqual([], resolved.mounts)
        self.assertEqual([], resolved.env)


def _build_context(agent_cfg: AgentConfig) -> ConfigContext:
    project_cfg = ProjectConfig(path="/tmp/project", agents={"codex": agent_cfg})
    return ConfigContext(
        store=mock.Mock(),
        project_cfg=project_cfg,
        agents={},
        bases={},
        extensions={},
    )


def _build_parsed(docker_socket: bool = False) -> ParsedArgs:
    return ParsedArgs(False, "", "codex", [], docker_socket, [], None)
