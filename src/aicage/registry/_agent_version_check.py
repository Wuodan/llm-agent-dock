from __future__ import annotations

import os
import subprocess
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

import yaml

from aicage._logging import get_logger
from aicage.config.global_config import GlobalConfig
from aicage.errors import CliError
from aicage.registry._custom_agent_loader import DEFAULT_CUSTOM_AGENTS_DIR
from aicage.registry.images_metadata.models import AgentMetadata

__all__ = ["AgentVersionChecker"]

_DEFAULT_STATE_DIR = "~/.aicage/state/version-check"


class AgentVersionChecker:
    def __init__(self, global_cfg: GlobalConfig, store: _VersionCheckStore | None = None) -> None:
        self._global_cfg = global_cfg
        self._store = store or _VersionCheckStore()

    def get_version(self, agent_name: str, agent_metadata: AgentMetadata) -> str:
        logger = get_logger()
        definition_dir = Path(os.path.expanduser(DEFAULT_CUSTOM_AGENTS_DIR)) / agent_name
        script_path = definition_dir / "version.sh"
        if not script_path.is_file():
            raise CliError(f"Agent '{agent_name}' is missing version.sh at {script_path}.")

        errors: list[str] = []
        builder_result = _run_builder(
            image_ref=self._global_cfg.version_check_image,
            definition_dir=definition_dir,
        )
        if builder_result.success:
            logger.info("Version check succeeded in builder for %s", agent_name)
            self._store.save(agent_name, builder_result.output)
            return builder_result.output

        logger.warning(
            "Version check failed in builder for %s: %s",
            agent_name,
            builder_result.error,
        )
        errors.append(builder_result.error)
        host_result = _run_host(script_path)
        if host_result.success:
            logger.info("Version check succeeded on host for %s", agent_name)
            self._store.save(agent_name, host_result.output)
            return host_result.output

        logger.warning(
            "Version check failed on host for %s: %s",
            agent_name,
            host_result.error,
        )
        errors.append(host_result.error)
        logger.error("Version check failed for %s: %s", agent_name, "; ".join(errors))
        raise CliError("; ".join(errors))


class _VersionCheckStore:
    def __init__(self, base_dir: Path | None = None) -> None:
        self._base_dir = base_dir or Path(os.path.expanduser(_DEFAULT_STATE_DIR))

    def save(self, agent: str, version: str) -> Path:
        self._base_dir.mkdir(parents=True, exist_ok=True)
        path = self._base_dir / f"{_sanitize_agent_name(agent)}.yaml"
        with path.open("w", encoding="utf-8") as handle:
            payload = {
                "agent": agent,
                "version": version,
                "checked_at": _now_iso(),
            }
            yaml.safe_dump(payload, handle, sort_keys=True)
        return path


@dataclass(frozen=True)
class _CommandResult:
    success: bool
    output: str
    error: str


def _run_builder(image_ref: str, definition_dir: Path) -> _CommandResult:
    command = [
        "docker",
        "run",
        "--rm",
        "-v",
        f"{definition_dir.resolve()}:/agent:ro",
        "-w",
        "/agent",
        image_ref,
        "/bin/sh",
        "/agent/version.sh",
    ]
    return _run_command(command, "builder image")


def _run_host(script_path: Path) -> _CommandResult:
    if not os.access(script_path, os.X_OK):
        get_logger().warning(
            "version.sh at %s is not executable; running with /bin/sh.",
            script_path,
        )
    return _run_command(["/bin/sh", str(script_path)], "host")


def _run_command(command: list[str], context: str) -> _CommandResult:
    process = subprocess.run(command, check=False, capture_output=True, text=True)
    output = process.stdout.strip() if process.stdout else ""
    if process.returncode == 0 and output:
        return _CommandResult(success=True, output=output, error="")

    stderr = process.stderr.strip() if process.stderr else ""
    error = stderr or output or f"Version check failed in {context}."
    return _CommandResult(success=False, output=output, error=error)


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _sanitize_agent_name(agent_name: str) -> str:
    return agent_name.replace("/", "_")
