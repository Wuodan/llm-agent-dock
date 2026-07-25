from pathlib import Path
from unittest import TestCase, mock

from aicage.cli_types import ParsedArgs
from aicage.config.context import ConfigContext
from aicage.config.project_config import AgentConfig, _AgentMounts, _ProjectConfig
from aicage.runtime.docker_args.resolvers.clipboard import (
    clipboard_requires_confirmation,
    describe_host_clipboard_access,
    resolve,
)

_MODULE = "aicage.runtime.docker_args.resolvers.clipboard"


class ClipboardMountTests(TestCase):
    def test_describe_host_clipboard_access_returns_wayland_details(self) -> None:
        with (
            mock.patch(f"{_MODULE}.os.name", "posix"),
            mock.patch.dict(
                f"{_MODULE}.os.environ",
                {
                    "XDG_RUNTIME_DIR": "/run/user/1000",
                    "WAYLAND_DISPLAY": "wayland-0",
                },
                clear=True,
            ),
            mock.patch(
                f"{_MODULE}.Path.exists",
                lambda self: self == Path("/run/user/1000/wayland-0"),
            ),
        ):
            description = describe_host_clipboard_access()

        self.assertEqual(
            "Wayland socket /run/user/1000/wayland-0; env XDG_RUNTIME_DIR, WAYLAND_DISPLAY",
            description,
        )

    def test_describe_host_clipboard_access_returns_osc52_fallback_message(
        self,
    ) -> None:
        with (
            mock.patch(f"{_MODULE}.os.name", "posix"),
            mock.patch.dict(f"{_MODULE}.os.environ", {}, clear=True),
        ):
            description = describe_host_clipboard_access()

        self.assertEqual(
            "OSC 52 terminal clipboard fallback; no host mounts", description
        )

    def test_resolve_prefers_wayland_when_socket_available(self) -> None:
        agent_cfg = AgentConfig(mounts=_AgentMounts(clipboard=True))
        context = _build_context(agent_cfg)
        with (
            mock.patch(f"{_MODULE}.os.name", "posix"),
            mock.patch.dict(
                f"{_MODULE}.os.environ",
                {
                    "XDG_RUNTIME_DIR": "/run/user/1000",
                    "WAYLAND_DISPLAY": "wayland-0",
                    "DISPLAY": ":0",
                },
                clear=True,
            ),
            mock.patch(
                f"{_MODULE}.Path.exists",
                lambda self: self == Path("/run/user/1000/wayland-0"),
            ),
        ):
            resolved = resolve(context, "codex", _build_parsed())

        self.assertEqual(
            ["/run/user/1000/wayland-0"],
            [item.host_path.as_posix() for item in resolved.mounts],
        )
        self.assertEqual(
            [
                ("XDG_RUNTIME_DIR", "/run/user/1000"),
                ("WAYLAND_DISPLAY", "wayland-0"),
            ],
            [(item.name, item.value) for item in resolved.env],
        )

    def test_resolve_falls_back_to_x11_with_xauthority(self) -> None:
        agent_cfg = AgentConfig(mounts=_AgentMounts(clipboard=True))
        context = _build_context(agent_cfg)
        with (
            mock.patch(f"{_MODULE}.os.name", "posix"),
            mock.patch.dict(
                f"{_MODULE}.os.environ",
                {"DISPLAY": ":0", "XAUTHORITY": "/home/user/.Xauthority"},
                clear=True,
            ),
            mock.patch(
                f"{_MODULE}.Path.exists",
                lambda self: self == Path("/tmp/.X11-unix"),
            ),
            mock.patch(
                f"{_MODULE}.Path.is_file",
                lambda self: self == Path("/home/user/.Xauthority"),
            ),
        ):
            resolved = resolve(context, "codex", _build_parsed())

        self.assertEqual(
            ["/tmp/.X11-unix", "/home/user/.Xauthority"],
            [item.host_path.as_posix() for item in resolved.mounts],
        )
        self.assertEqual([False, True], [item.read_only for item in resolved.mounts])
        self.assertEqual(
            [("DISPLAY", ":0"), ("XAUTHORITY", "/home/user/.Xauthority")],
            [(item.name, item.value) for item in resolved.env],
        )

    def test_resolve_disabled_returns_no_mounts(self) -> None:
        context = _build_context(AgentConfig())

        resolved = resolve(context, "codex", _build_parsed())

        self.assertEqual([], resolved.mounts)
        self.assertEqual([], resolved.env)

    def test_resolve_falls_back_to_osc52_env_without_mounts(self) -> None:
        agent_cfg = AgentConfig(mounts=_AgentMounts(clipboard=True))
        context = _build_context(agent_cfg)
        with (
            mock.patch(f"{_MODULE}.os.name", "nt"),
            mock.patch.dict(f"{_MODULE}.os.environ", {}, clear=True),
        ):
            resolved = resolve(context, "codex", _build_parsed())

        self.assertEqual([], resolved.mounts)
        self.assertEqual(
            [("AICAGE_ENABLE_OSC52_CLIPBOARD", "1")],
            [(item.name, item.value) for item in resolved.env],
        )

    def test_clipboard_requires_confirmation_returns_false_for_osc52(self) -> None:
        with (
            mock.patch(f"{_MODULE}.os.name", "nt"),
            mock.patch.dict(f"{_MODULE}.os.environ", {}, clear=True),
        ):
            requires_confirmation = clipboard_requires_confirmation()

        self.assertFalse(requires_confirmation)


def _build_context(agent_cfg: AgentConfig) -> ConfigContext:
    project_cfg = _ProjectConfig(path="/test-tmp/project", agents={"codex": agent_cfg})
    return ConfigContext(
        store=mock.Mock(),
        project_cfg=project_cfg,
        agents={},
        bases={},
        extensions={},
    )


def _build_parsed() -> ParsedArgs:
    return ParsedArgs(False, "", "codex", [], False, [], None)
