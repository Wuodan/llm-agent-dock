from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

import yaml

_DEFAULT_STATE_DIR = "~/.aicage/state/local-build"
_AGENT_KEY: str = "agent"
_BASE_KEY: str = "base"
_AGENT_VERSION_KEY: str = "agent_version"
_BASE_IMAGE_KEY: str = "base_image"
_BASE_DIGEST_KEY: str = "base_digest"
_IMAGE_REF_KEY: str = "image_ref"
_BUILT_AT_KEY: str = "built_at"


@dataclass(frozen=True)
class BuildRecord:
    agent: str
    base: str
    agent_version: str
    base_image: str
    base_digest: str | None
    image_ref: str
    built_at: str


class BuildStore:
    def __init__(self, base_dir: Path | None = None) -> None:
        self._base_dir = base_dir or Path(os.path.expanduser(_DEFAULT_STATE_DIR))

    def load(self, agent: str, base: str) -> BuildRecord | None:
        path = self._path(agent, base)
        if not path.is_file():
            return None
        payload = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        if not isinstance(payload, dict):
            return None
        base_digest = payload.get(_BASE_DIGEST_KEY)
        return BuildRecord(
            agent=str(payload.get(_AGENT_KEY, "")),
            base=str(payload.get(_BASE_KEY, "")),
            agent_version=str(payload.get(_AGENT_VERSION_KEY, "")),
            base_image=str(payload.get(_BASE_IMAGE_KEY, "")),
            base_digest=str(base_digest) if base_digest is not None else None,
            image_ref=str(payload.get(_IMAGE_REF_KEY, "")),
            built_at=str(payload.get(_BUILT_AT_KEY, "")),
        )

    def save(self, record: BuildRecord) -> Path:
        self._base_dir.mkdir(parents=True, exist_ok=True)
        path = self._path(record.agent, record.base)
        payload = {
            _AGENT_KEY: record.agent,
            _BASE_KEY: record.base,
            _AGENT_VERSION_KEY: record.agent_version,
            _BASE_IMAGE_KEY: record.base_image,
            _BASE_DIGEST_KEY: record.base_digest,
            _IMAGE_REF_KEY: record.image_ref,
            _BUILT_AT_KEY: record.built_at,
        }
        path.write_text(yaml.safe_dump(payload, sort_keys=True), encoding="utf-8")
        return path

    def _path(self, agent: str, base: str) -> Path:
        filename = f"{sanitize(agent)}-{base}.yaml"
        return self._base_dir / filename


def sanitize(value: str) -> str:
    return value.replace("/", "_")
