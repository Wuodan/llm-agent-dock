from __future__ import annotations

import os
from datetime import datetime, timezone
from pathlib import Path

import yaml

_DEFAULT_STATE_DIR = "~/.aicage/state/version-check"


class VersionCheckStore:
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


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _sanitize_agent_name(agent_name: str) -> str:
    return agent_name.replace("/", "_")
