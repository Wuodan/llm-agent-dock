import hashlib

from aicage.config.extensions.loader import ExtensionMetadata, extension_hash
from aicage.config.run_config import RunConfig
from aicage.docker.build.extended import run
from aicage.docker.query import (
    cleanup_old_digest,
    get_local_repo_digest_for_repo,
)
from aicage.docker.refs import repository_from_image_ref
from aicage.docker.reporting import OperationReporter
from aicage.registry._build_flow import maybe_build
from aicage.registry._errors import RegistryError
from aicage.registry._time import now_iso

from ._logs import build_log_path
from ._plan import should_rebuild
from ._store import BuildRecord, BuildStore


def ensure(run_config: RunConfig, reporter: OperationReporter | None = None) -> None:
    if not run_config.selection.extensions:
        raise RegistryError("No extensions selected for extended image build.")

    resolved = _resolve_extensions(
        run_config.selection.extensions, run_config.context.extensions
    )
    combined_hash = _combined_extension_hash(resolved)
    store = BuildStore()
    image_ref = run_config.selection.image_ref
    maybe_build(
        load_record=lambda: store.load(image_ref),
        should_rebuild=lambda record: should_rebuild(
            run_config=run_config,
            record=record,
            base_image_ref=run_config.selection.base_image_ref,
            extension_hash=combined_hash,
        ),
        run_build=lambda: _run_build(run_config, resolved, reporter),
        save_record=lambda: store.save(
            BuildRecord(
                agent=run_config.agent,
                base=run_config.selection.base,
                image_ref=image_ref,
                extensions=list(run_config.selection.extensions),
                extension_hash=combined_hash,
                base_image=run_config.selection.base_image_ref,
                built_at=now_iso(),
            )
        ),
    )


def build_needed(run_config: RunConfig) -> bool:
    resolved = _resolve_extensions(
        run_config.selection.extensions, run_config.context.extensions
    )
    combined_hash = _combined_extension_hash(resolved)
    store = BuildStore()
    return should_rebuild(
        run_config=run_config,
        record=store.load(run_config.selection.image_ref),
        base_image_ref=run_config.selection.base_image_ref,
        extension_hash=combined_hash,
    )


def _run_build(
    run_config: RunConfig,
    resolved: list[ExtensionMetadata],
    reporter: OperationReporter | None,
) -> None:
    image_ref = run_config.selection.image_ref
    image_repository = repository_from_image_ref(image_ref)
    old_digest = get_local_repo_digest_for_repo(image_ref, image_repository)
    log_path = build_log_path(image_ref)
    run(
        run_config=run_config,
        base_image_ref=run_config.selection.base_image_ref,
        extensions=resolved,
        log_path=log_path,
        reporter=reporter,
    )
    cleanup_old_digest(image_repository, old_digest, image_ref)


def _resolve_extensions(
    extension_ids: list[str],
    extensions: dict[str, ExtensionMetadata],
) -> list[ExtensionMetadata]:
    missing = [ext for ext in extension_ids if ext not in extensions]
    if missing:
        raise RegistryError(f"Missing extensions: {', '.join(sorted(missing))}.")
    return [extensions[ext] for ext in extension_ids]


def _combined_extension_hash(extensions: list[ExtensionMetadata]) -> str:
    digest = hashlib.sha256()
    for extension in extensions:
        digest.update(extension.extension_id.encode("utf-8"))
        digest.update(extension_hash(extension).encode("utf-8"))
    return digest.hexdigest()
