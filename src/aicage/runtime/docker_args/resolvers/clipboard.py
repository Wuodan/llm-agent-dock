import os
from pathlib import Path

from aicage.cli_types import ParsedArgs
from aicage.config.context import ConfigContext
from aicage.config.project_config import AgentConfig
from aicage.runtime.docker_args.support.resolver_types import MountRequest, ResolvedArgs
from aicage.runtime.run_args import EnvVar

_AICAGE_ENABLE_OSC52_CLIPBOARD = "AICAGE_ENABLE_OSC52_CLIPBOARD"
_DISPLAY = "DISPLAY"
_WAYLAND_DISPLAY = "WAYLAND_DISPLAY"
_XAUTHORITY = "XAUTHORITY"
_XDG_RUNTIME_DIR = "XDG_RUNTIME_DIR"
_X11_SOCKET_DIR = Path(
    "/tmp/.X11-unix"
)  # nosec B108 -- X11 sockets live at this fixed host path.


def describe_host_clipboard_access() -> str:
    return _resolve_host_clipboard_access().description


def clipboard_requires_confirmation() -> bool:
    return _resolve_host_clipboard_access().requires_confirmation


def resolve(
    context: ConfigContext,
    agent: str,
    parsed: ParsedArgs | None,
) -> ResolvedArgs:
    _ = parsed
    agent_cfg: AgentConfig = context.project_cfg.agents[agent]
    if agent_cfg.mounts.clipboard is not True:
        return ResolvedArgs()
    return _resolve_host_clipboard_access().resolved_args


class _ResolvedClipboardAccess:
    def __init__(
        self,
        resolved_args: ResolvedArgs,
        description: str,
        requires_confirmation: bool,
    ) -> None:
        self.resolved_args = resolved_args
        self.description = description
        self.requires_confirmation = requires_confirmation


def _resolve_host_clipboard_access() -> _ResolvedClipboardAccess:
    wayland = _resolve_wayland()
    if wayland is not None:
        return wayland
    x11 = _resolve_x11()
    if x11 is not None:
        return x11
    return _resolve_osc52()


def _resolve_wayland() -> _ResolvedClipboardAccess | None:
    runtime_dir = os.environ.get(_XDG_RUNTIME_DIR)
    display = os.environ.get(_WAYLAND_DISPLAY)
    if not runtime_dir or not display:
        return None
    socket_path = Path(runtime_dir) / display
    if not socket_path.exists():
        return None
    return _ResolvedClipboardAccess(
        resolved_args=ResolvedArgs(
            mounts=[MountRequest(host_path=socket_path)],
            env=[
                EnvVar(name=_XDG_RUNTIME_DIR, value=runtime_dir),
                EnvVar(name=_WAYLAND_DISPLAY, value=display),
            ],
        ),
        description=(
            f"Wayland socket {socket_path}; env {_XDG_RUNTIME_DIR}, {_WAYLAND_DISPLAY}"
        ),
        requires_confirmation=True,
    )


def _resolve_x11() -> _ResolvedClipboardAccess | None:
    display = os.environ.get(_DISPLAY)
    if not display or not _X11_SOCKET_DIR.exists():
        return None
    mounts = [MountRequest(host_path=_X11_SOCKET_DIR)]
    env = [EnvVar(name=_DISPLAY, value=display)]
    details = [f"X11 socket {_X11_SOCKET_DIR}", f"env {_DISPLAY}"]
    xauthority = os.environ.get(_XAUTHORITY)
    if xauthority:
        xauthority_path = Path(xauthority)
        if xauthority_path.is_file():
            mounts.append(MountRequest(host_path=xauthority_path, read_only=True))
            env.append(EnvVar(name=_XAUTHORITY, value=xauthority))
            details.append(f"read-only {_XAUTHORITY} {xauthority_path}")
    return _ResolvedClipboardAccess(
        resolved_args=ResolvedArgs(mounts=mounts, env=env),
        description="; ".join(details),
        requires_confirmation=True,
    )


def _resolve_osc52() -> _ResolvedClipboardAccess:
    return _ResolvedClipboardAccess(
        resolved_args=ResolvedArgs(
            env=[EnvVar(name=_AICAGE_ENABLE_OSC52_CLIPBOARD, value="1")]
        ),
        description="OSC 52 terminal clipboard fallback; no host mounts",
        requires_confirmation=False,
    )
