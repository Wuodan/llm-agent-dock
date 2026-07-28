from enum import Enum
from pathlib import Path

from aicage._logging import get_logger
from aicage.config.agent.models import AgentMetadata
from aicage.config.run_config import RunConfig
from aicage.docker.build.agent import run
from aicage.docker.query import (
    cleanup_old_digest,
    get_local_repo_digest_for_repo,
    local_image_exists,
)
from aicage.docker.refs import repository_from_image_ref
from aicage.paths import CUSTOM_BASES_DIR
from aicage.registry._build_flow import maybe_build
from aicage.registry._errors import RegistryError
from aicage.registry._time import now_iso
from aicage.reporting import OperationReporter

from ..base_build.ensure import build_needed as base_build_needed
from ..base_build.ensure import ensure as ensure_base_build
from ._logs import build_log_path
from ._plan import should_rebuild
from ._refresh import (
    _BaseRefreshAction,
    refresh_base_image,
    refresh_base_image_plan,
)
from ._refs import base_repository, get_base_image_ref
from ._store import BuildRecord, BuildStore
from .agent_version.checker import AgentVersionChecker


class AgentBuildSetupAction(Enum):
    USE_LOCAL = "use_local"
    BUILD = "build"
    CONFIRM_UPDATE = "confirm_update"


def ensure(
    run_config: RunConfig,
    update_approved: bool,
    reporter: OperationReporter,
) -> None:
    agent_metadata = run_config.context.agents[run_config.agent]
    definition_dir = agent_metadata.local_definition_dir

    base_metadata = run_config.context.bases[run_config.selection.base]
    custom_base = base_metadata.local_definition_dir.is_relative_to(CUSTOM_BASES_DIR)
    base_image = get_base_image_ref(run_config)
    image_ref = run_config.selection.base_image_ref
    if custom_base:
        ensure_base_build(
            run_config.selection.base,
            base_metadata,
            base_metadata.local_definition_dir,
            reporter=reporter,
        )
    else:
        base_repo = base_repository(run_config)
        try:
            base_image = refresh_base_image(
                base_image_ref=base_image,
                base_repository=base_repo,
                update_approved=update_approved,
                reporter=reporter,
            )
        except RegistryError:
            if not local_image_exists(image_ref):
                raise
            logger = get_logger()
            logger.warning(
                "Base image refresh failed; using local agent image %s.",
                image_ref,
            )
            return

    store = BuildStore()
    agent_version = _get_agent_version(
        run_config,
        agent_metadata,
        definition_dir,
        reporter,
    )
    maybe_build(
        load_record=lambda: store.load(run_config.agent, run_config.selection.base),
        should_rebuild=lambda record: should_rebuild(
            run_config=run_config,
            record=record,
            agent_version=agent_version,
            base_image_ref=base_image,
        ),
        run_build=lambda: _run_build(run_config, base_image, image_ref, reporter),
        save_record=lambda: store.save(
            BuildRecord(
                agent=run_config.agent,
                base=run_config.selection.base,
                agent_version=agent_version,
                base_image=base_image,
                image_ref=image_ref,
                built_at=now_iso(),
            )
        ),
    )


def setup_plan(
    run_config: RunConfig,
    reporter: OperationReporter,
) -> AgentBuildSetupAction:
    agent_metadata = run_config.context.agents[run_config.agent]
    definition_dir = agent_metadata.local_definition_dir
    base_metadata = run_config.context.bases[run_config.selection.base]
    custom_base = base_metadata.local_definition_dir.is_relative_to(CUSTOM_BASES_DIR)
    base_image = get_base_image_ref(run_config)
    image_ref = run_config.selection.base_image_ref
    if custom_base:
        if base_build_needed(
            run_config.selection.base,
            base_metadata,
            base_image,
        ):
            return AgentBuildSetupAction.BUILD
    base_repo = base_repository(run_config)
    if not custom_base:
        try:
            refresh_plan = refresh_base_image_plan(
                base_image_ref=base_image,
                base_repository=base_repo,
            )
        except RegistryError:
            action = (
                AgentBuildSetupAction.BUILD
                if not local_image_exists(image_ref)
                else AgentBuildSetupAction.USE_LOCAL
            )
            return action
        if refresh_plan.action is _BaseRefreshAction.CONFIRM_PULL:
            return AgentBuildSetupAction.CONFIRM_UPDATE
        base_image = refresh_plan.image_ref

    store = BuildStore()
    agent_version = _get_agent_version(
        run_config,
        agent_metadata,
        definition_dir,
        reporter,
    )
    action = (
        AgentBuildSetupAction.BUILD
        if should_rebuild(
            run_config=run_config,
            record=store.load(run_config.agent, run_config.selection.base),
            agent_version=agent_version,
            base_image_ref=base_image,
        )
        else AgentBuildSetupAction.USE_LOCAL
    )
    return action


def _get_agent_version(
    run_config: RunConfig,
    agent_metadata: AgentMetadata,
    definition_dir: Path,
    reporter: OperationReporter,
) -> str:
    checker = AgentVersionChecker()
    return checker.get_version(
        run_config.agent,
        agent_metadata,
        definition_dir,
        reporter=reporter,
    )


def _run_build(
    run_config: RunConfig,
    base_image_ref: str,
    image_ref: str,
    reporter: OperationReporter,
) -> None:
    image_repository = repository_from_image_ref(image_ref)
    old_digest = get_local_repo_digest_for_repo(image_ref, image_repository)
    log_path = build_log_path(run_config.agent, run_config.selection.base)
    run(
        run_config=run_config,
        base_image_ref=base_image_ref,
        image_ref=image_ref,
        log_path=log_path,
        reporter=reporter,
    )
    cleanup_old_digest(image_repository, old_digest, image_ref)
