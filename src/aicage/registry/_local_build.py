from __future__ import annotations

import os
import subprocess
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

import yaml

from aicage._logging import get_logger
from aicage.config.runtime_config import RunConfig
from aicage.errors import CliError
from aicage.registry import _local_query, _remote_query
from aicage.registry._agent_definition import get_agent_build_root

__all__ = ["ensure_local_image"]

_DEFAULT_STATE_DIR = "~/.aicage/state/local-build"
_DEFAULT_LOG_DIR = "~/.aicage/logs/build"


@dataclass(frozen=True)
class _BuildRecord:
    agent: str
    base: str
    agent_version: str
    base_image: str
    base_digest: str | None
    image_ref: str
    built_at: str


class _BuildStore:
    def __init__(self, base_dir: Path | None = None) -> None:
        self._base_dir = base_dir or Path(os.path.expanduser(_DEFAULT_STATE_DIR))

    def load(self, agent: str, base: str) -> _BuildRecord | None:
        path = self._path(agent, base)
        if not path.is_file():
            return None
        payload = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        if not isinstance(payload, dict):
            return None
        base_digest = payload.get("base_digest")
        return _BuildRecord(
            agent=str(payload.get("agent", "")),
            base=str(payload.get("base", "")),
            agent_version=str(payload.get("agent_version", "")),
            base_image=str(payload.get("base_image", "")),
            base_digest=str(base_digest) if base_digest is not None else None,
            image_ref=str(payload.get("image_ref", "")),
            built_at=str(payload.get("built_at", "")),
        )

    def save(self, record: _BuildRecord) -> Path:
        self._base_dir.mkdir(parents=True, exist_ok=True)
        path = self._path(record.agent, record.base)
        payload = {
            "agent": record.agent,
            "base": record.base,
            "agent_version": record.agent_version,
            "base_image": record.base_image,
            "base_digest": record.base_digest,
            "image_ref": record.image_ref,
            "built_at": record.built_at,
        }
        path.write_text(yaml.safe_dump(payload, sort_keys=True), encoding="utf-8")
        return path

    def _path(self, agent: str, base: str) -> Path:
        filename = f"{_sanitize(agent)}-{base}.yaml"
        return self._base_dir / filename


def ensure_local_image(run_config: RunConfig) -> None:
    agent_metadata = run_config.images_metadata.agents[run_config.agent]
    if agent_metadata.redistributable:
        return

    if run_config.agent_version is None:
        raise CliError(f"Missing agent version for '{run_config.agent}'.")

    base_image_ref = _base_image_ref(run_config)
    base_repo = _base_repository(run_config)
    base_digest = _refresh_base_digest(
        base_image_ref=base_image_ref,
        base_repository=base_repo,
        global_cfg=run_config.global_cfg,
    )

    store = _BuildStore()
    record = store.load(run_config.agent, run_config.base)

    should_build = _should_build(
        run_config=run_config,
        record=record,
        base_digest=base_digest,
    )
    if not should_build:
        return

    log_path = _build_log_path(run_config.agent, run_config.base)
    _run_build(
        run_config=run_config,
        base_image_ref=base_image_ref,
        log_path=log_path,
    )

    updated_base_digest = _local_query.get_local_repo_digest_for_repo(base_image_ref, base_repo)
    store.save(
        _BuildRecord(
            agent=run_config.agent,
            base=run_config.base,
            agent_version=run_config.agent_version,
            base_image=base_image_ref,
            base_digest=updated_base_digest,
            image_ref=run_config.image_ref,
            built_at=_now_iso(),
        )
    )


def _should_build(
    run_config: RunConfig,
    record: _BuildRecord | None,
    base_digest: str | None,
) -> bool:
    if not _local_image_exists(run_config.image_ref):
        return True
    if record is None:
        return True
    if record.agent_version != run_config.agent_version:
        return True
    if record.base_digest is None:
        return True
    if base_digest and record.base_digest != base_digest:
        return True
    return False


def _run_build(run_config: RunConfig, base_image_ref: str, log_path: Path) -> None:
    logger = get_logger()
    log_path.parent.mkdir(parents=True, exist_ok=True)
    print(f"[aicage] Building local image {run_config.image_ref} (logs: {log_path})...")
    logger.info("Building local image %s (logs: %s)", run_config.image_ref, log_path)

    build_root = get_agent_build_root()
    command = [
        "docker",
        "build",
        "--build-arg",
        f"BASE_IMAGE={base_image_ref}",
        "--build-arg",
        f"AGENT={run_config.agent}",
        "--tag",
        run_config.image_ref,
        str(build_root),
    ]
    with log_path.open("w", encoding="utf-8") as log_handle:
        result = subprocess.run(command, check=False, stdout=log_handle, stderr=subprocess.STDOUT)
    if result.returncode != 0:
        logger.error("Local image build failed for %s (logs: %s)", run_config.image_ref, log_path)
        raise CliError(
            f"Local image build failed for {run_config.image_ref}. See log at {log_path}."
        )

    logger.info("Local image build succeeded for %s", run_config.image_ref)


def _build_log_path(agent: str, base: str) -> Path:
    log_dir = Path(os.path.expanduser(_DEFAULT_LOG_DIR))
    return log_dir / f"{_sanitize(agent)}-{base}.log"


def _refresh_base_digest(
    base_image_ref: str,
    base_repository: str,
    global_cfg: "GlobalConfig",
) -> str | None:
    logger = get_logger()
    local_digest = _local_query.get_local_repo_digest_for_repo(base_image_ref, base_repository)
    remote_digest = _remote_query.get_remote_repo_digest_for_repo(
        base_image_ref,
        global_cfg.image_base_repository,
        global_cfg,
    )
    if remote_digest is None or remote_digest == local_digest:
        return local_digest

    logger.info("Pulling base image %s", base_image_ref)
    pull = subprocess.run(
        ["docker", "pull", base_image_ref],
        check=False,
        capture_output=True,
        text=True,
    )
    if pull.returncode != 0:
        message = pull.stderr.strip() or pull.stdout.strip() or "docker pull failed"
        if local_digest:
            logger.warning("Base image pull failed; using local base image: %s", message)
            return local_digest
        raise CliError(message)

    return _local_query.get_local_repo_digest_for_repo(base_image_ref, base_repository)


def _local_image_exists(image_ref: str) -> bool:
    result = subprocess.run(
        ["docker", "image", "inspect", image_ref],
        check=False,
        capture_output=True,
        text=True,
    )
    return result.returncode == 0


def _base_repository(run_config: RunConfig) -> str:
    return f"{run_config.global_cfg.image_registry}/{run_config.global_cfg.image_base_repository}"


def _base_image_ref(run_config: RunConfig) -> str:
    repository = _base_repository(run_config)
    return f"{repository}:{run_config.base}"


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _sanitize(value: str) -> str:
    return value.replace("/", "_")
