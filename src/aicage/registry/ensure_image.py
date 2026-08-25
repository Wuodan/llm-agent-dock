from dataclasses import dataclass
from enum import Enum

from aicage.config.run_config import RunConfig
from aicage.paths import CUSTOM_BASES_DIR
from aicage.registry._image_pull import pull_image
from aicage.registry._pull_decision import _PullDecisionAction, pull_decision_plan
from aicage.registry.agent_build.ensure import AgentBuildSetupAction
from aicage.registry.agent_build.ensure import ensure as ensure_agent_image
from aicage.registry.agent_build.ensure import setup_plan as agent_build_setup_plan
from aicage.registry.agent_build.refs import get_base_image_ref
from aicage.registry.extension_build.ensure import (
    build_needed as extension_build_needed,
)
from aicage.registry.extension_build.ensure import ensure as ensure_extended_image
from aicage.reporting import OperationReporter


class ImageSetupAction(Enum):
    SKIP = "skip"
    SETUP = "setup"
    CONFIRM_UPDATE = "confirm_update"
    CONFIRM_UPDATE_AND_DO_SETUP = "confirm_update_and_do_setup"


@dataclass(frozen=True)
class ImageSetupPlan:
    action: ImageSetupAction
    image_ref: str


def ensure_image(
    run_config: RunConfig,
    update_approved: bool,
    reporter: OperationReporter,
) -> None:
    agent_metadata = run_config.context.agents[run_config.agent]
    base_metadata = run_config.context.bases[run_config.selection.base]
    custom_base = base_metadata.local_definition_dir.is_relative_to(CUSTOM_BASES_DIR)
    if not agent_metadata.build_local and not custom_base:
        pull_image(
            run_config.selection.base_image_ref,
            update_approved=update_approved,
            reporter=reporter,
        )
    else:
        ensure_agent_image(
            run_config,
            update_approved=update_approved,
            reporter=reporter,
        )
    if run_config.selection.extensions:
        # Extensions rebuild unconditionally; no user confirmation needed.
        ensure_extended_image(run_config, reporter=reporter)


def image_setup_plan(
    run_config: RunConfig,
    reporter: OperationReporter,
) -> ImageSetupPlan:
    agent_metadata = run_config.context.agents[run_config.agent]
    base_metadata = run_config.context.bases[run_config.selection.base]
    custom_base = base_metadata.local_definition_dir.is_relative_to(CUSTOM_BASES_DIR)
    image_ref = run_config.selection.base_image_ref
    if not agent_metadata.build_local and not custom_base:
        pull_plan = pull_decision_plan(image_ref)
        match pull_plan.action:
            case _PullDecisionAction.SKIP:
                action = ImageSetupAction.SKIP
            case _PullDecisionAction.PULL:
                action = ImageSetupAction.SETUP
            case _PullDecisionAction.CONFIRM_PULL:
                action = ImageSetupAction.CONFIRM_UPDATE
    else:
        image_ref = get_base_image_ref(run_config)
        agent_action = agent_build_setup_plan(run_config, reporter)
        match agent_action:
            case AgentBuildSetupAction.USE_LOCAL:
                action = ImageSetupAction.SKIP
            case AgentBuildSetupAction.BUILD:
                action = ImageSetupAction.SETUP
            case AgentBuildSetupAction.CONFIRM_UPDATE:
                action = ImageSetupAction.CONFIRM_UPDATE_AND_DO_SETUP
    if run_config.selection.extensions and extension_build_needed(run_config):
        action = ImageSetupAction.SETUP
    return ImageSetupPlan(action=action, image_ref=image_ref)
