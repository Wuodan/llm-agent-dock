from pathlib import Path

from aicage.config.base.models import BaseMetadata
from aicage.constants import LOCAL_IMAGE_BASE_REPOSITORY
from aicage.docker.build.custom_base import run
from aicage.docker.query import (
    cleanup_old_digest,
    get_local_repo_digest_for_repo,
    local_image_exists,
)
from aicage.docker.reporting import OperationReporter
from aicage.registry._build_flow import maybe_build
from aicage.registry._time import now_iso
from aicage.registry.digest.remote_digest import get_remote_digest

from ._logs import build_log_path
from ._store import BuildRecord, BuildStore


def image_ref(base: str) -> str:
    return f"{LOCAL_IMAGE_BASE_REPOSITORY}:{base}"


def ensure(
    base: str,
    base_metadata: BaseMetadata,
    base_dir: Path,
    reporter: OperationReporter | None = None,
) -> None:
    target_image_ref = image_ref(base)
    local_exists = local_image_exists(target_image_ref)
    store = BuildStore()
    source_digest = get_remote_digest(base_metadata.from_image)

    def _run_build() -> None:
        old_digest = None
        if local_exists:
            old_digest = get_local_repo_digest_for_repo(
                target_image_ref, LOCAL_IMAGE_BASE_REPOSITORY
            )
        log_path = build_log_path(base)
        run(
            build_root=base_dir,
            from_image=base_metadata.from_image,
            image_ref=target_image_ref,
            log_path=log_path,
            reporter=reporter,
        )
        cleanup_old_digest(LOCAL_IMAGE_BASE_REPOSITORY, old_digest, target_image_ref)

    maybe_build(
        load_record=lambda: store.load(base),
        should_rebuild=lambda record: _should_rebuild(
            local_exists=local_exists,
            record=record,
            base_metadata=base_metadata,
            source_digest=source_digest,
        ),
        run_build=_run_build,
        save_record=lambda: store.save(
            BuildRecord(
                base=base,
                from_image=base_metadata.from_image,
                from_image_digest=source_digest or "",
                image_ref=target_image_ref,
                built_at=now_iso(),
            )
        ),
    )


def build_needed(
    base: str,
    base_metadata: BaseMetadata,
    target_image_ref: str,
) -> bool:
    local_exists = local_image_exists(target_image_ref)
    store = BuildStore()
    source_digest = get_remote_digest(base_metadata.from_image)
    return _should_rebuild(
        local_exists=local_exists,
        record=store.load(base),
        base_metadata=base_metadata,
        source_digest=source_digest,
    )


def _should_rebuild(
    local_exists: bool,
    record: BuildRecord | None,
    base_metadata: BaseMetadata,
    source_digest: str | None,
) -> bool:
    if not local_exists or record is None:
        return True
    if record.from_image != base_metadata.from_image:
        return True
    if source_digest and record.from_image_digest != source_digest:
        return True
    return False
