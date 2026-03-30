from dataclasses import dataclass
from pathlib import Path, PureWindowsPath

from aicage.errors import AicageError


@dataclass(frozen=True)
class ShareSpec:
    host_path: Path
    read_only: bool


def resolve_share_specs(
    raw_shares: list[str],
    cwd: Path,
) -> list[ShareSpec]:
    share_mounts: list[ShareSpec] = []
    if not raw_shares:
        return share_mounts
    mounted_hosts: set[Path] = set()
    for raw in raw_shares:
        share = _parse_share(raw, cwd)
        if share.host_path in mounted_hosts:
            continue
        mounted_hosts.add(share.host_path)
        share_mounts.append(ShareSpec(host_path=share.host_path, read_only=share.read_only))
    return share_mounts


def merge_share_values(
    cli_shares: list[str],
    existing_shares: list[str],
    cwd: Path,
) -> tuple[list[str], list[str]]:
    cli_specs = _normalize_share_specs(cli_shares, cwd)
    existing_specs = _normalize_share_specs(existing_shares, cwd)
    existing_hosts = {spec.host_path for spec in existing_specs}
    cli_hosts: set[Path] = set()
    merged: list[str] = []
    new_shares: list[str] = []
    for spec in cli_specs:
        if spec.host_path in cli_hosts:
            continue
        share_value = _format_share_value(spec)
        cli_hosts.add(spec.host_path)
        merged.append(share_value)
        if spec.host_path not in existing_hosts:
            new_shares.append(share_value)
    for spec in existing_specs:
        if spec.host_path in cli_hosts:
            continue
        merged.append(_format_share_value(spec))
    return merged, new_shares


def _parse_share(raw: str, cwd: Path) -> ShareSpec:
    if not raw:
        raise AicageError("Share value cannot be empty.")
    read_only, host_raw = _parse_read_only(raw)
    if _has_destination_path(host_raw):
        raise AicageError("Share destinations are not supported. Use HOST or HOST:ro.")
    host_path = _resolve_host_path(host_raw, cwd)
    if host_path.exists() and not host_path.is_file() and not host_path.is_dir():
        raise AicageError(f"Path exists but is not a file or directory: {host_path}")
    return ShareSpec(host_path=host_path, read_only=read_only)


def _parse_read_only(raw: str) -> tuple[bool, str]:
    if raw.endswith(":ro"):
        host_raw = raw[:-3]
        if not host_raw:
            raise AicageError("Share host path cannot be empty.")
        return True, host_raw
    return False, raw


def _resolve_host_path(host_raw: str, cwd: Path) -> Path:
    host_path = Path(host_raw).expanduser()
    if not host_path.is_absolute():
        host_path = cwd / host_path
    return host_path.resolve()


def _has_destination_path(host_raw: str) -> bool:
    if ":" not in host_raw:
        return False
    windows_path = PureWindowsPath(host_raw)
    if windows_path.drive and host_raw.startswith(windows_path.drive):
        return host_raw.count(":") > 1
    return True


def _normalize_share_specs(raw_shares: list[str], cwd: Path) -> list[ShareSpec]:
    specs: list[ShareSpec] = []
    seen: set[Path] = set()
    for raw in raw_shares:
        spec = _parse_share(raw, cwd)
        if spec.host_path in seen:
            continue
        seen.add(spec.host_path)
        specs.append(spec)
    return specs


def _format_share_value(spec: ShareSpec) -> str:
    host_value = str(spec.host_path)
    return f"{host_value}:ro" if spec.read_only else host_value
