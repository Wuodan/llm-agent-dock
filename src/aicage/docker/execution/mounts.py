from pathlib import Path, PurePosixPath


def append_mount(
    cmd: list[str],
    host_path: Path,
    container_path: PurePosixPath,
    *,
    read_only: bool,
) -> None:
    mount_value = _format_mount_value(host_path, container_path, read_only=read_only)
    cmd.extend(["--mount", mount_value])


def _format_mount_value(
    host_path: Path,
    container_path: PurePosixPath,
    *,
    read_only: bool,
) -> str:
    parts = [
        "type=bind",
        f"src={host_path.as_posix()}",
        f"dst={container_path.as_posix()}",
    ]
    if read_only:
        parts.append("readonly")
    return ",".join(parts)
