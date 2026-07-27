from collections.abc import Callable

from aicage.config.context import ConfigContext
from aicage.config.run_config_draft import RunConfigDraft
from aicage.registry.image_selection.interaction import (
    BaseChoiceRequest,
    ExtensionChoiceOption,
)
from aicage.registry.image_selection.selection import select_agent_image
from aicage.runtime.docker_args.mount_preferences import apply_mount_preferences
from aicage.runtime.menu._interaction_types import (
    ConfigSelectionResult,
    ImageSetupOperation,
)

from ._base import BaseSelectionRequest, prompt_for_base
from ._confirm import (
    prompt_mount_git_support,
    prompt_persist_docker_args,
    prompt_persist_docker_socket,
    prompt_persist_shares,
    prompt_update_aicage,
    prompt_update_image,
)
from ._extensions import ExtensionOption, prompt_for_extensions
from ._image_ref import prompt_for_image_ref

_PersistDockerArgsPrompt = Callable[[str, str | None], bool]
_PersistSharesPrompt = Callable[[list[str], list[str]], bool]


class SimpleInteraction:
    def configure_run(
        self,
        draft: RunConfigDraft,
        context: ConfigContext,
        agent: str,
    ) -> ConfigSelectionResult:
        selection = select_agent_image(
            agent,
            context,
            _SimpleSelectionInteraction(),
        )
        draft.apply_selection(selection)
        _persist_docker_args(draft, prompt_persist_docker_args)
        _persist_shares(draft, prompt_persist_shares)
        apply_mount_preferences(
            context,
            agent,
            draft.parsed,
            prompt_mount_git_support,
            prompt_persist_docker_socket,
        )
        return ConfigSelectionResult(
            selection=selection,
            project_docker_args=draft.existing_project_docker_args,
        )

    def confirm_aicage_update(
        self,
        installed_version: str,
        latest_version: str,
    ) -> bool:
        return prompt_update_aicage(installed_version, latest_version)

    def confirm_image_update(self, image_ref: str) -> bool:
        return prompt_update_image(image_ref)

    def execute_image_setup(
        self,
        operation: ImageSetupOperation,
    ) -> None:
        operation(None)


class _SimpleSelectionInteraction:
    def choose_base(self, request: BaseChoiceRequest) -> str:
        return prompt_for_base(
            BaseSelectionRequest(
                agent=request.agent,
                context=request.context,
                agent_metadata=request.agent_metadata,
                default_base=request.default_base,
            )
        )

    def choose_extensions(
        self,
        options: list[ExtensionChoiceOption],
    ) -> list[str]:
        return prompt_for_extensions(
            [
                ExtensionOption(
                    name=option.name,
                    description=option.description,
                    has_dockerfile=option.has_dockerfile,
                )
                for option in options
            ]
        )

    def choose_image_ref(self, default_ref: str) -> str:
        return prompt_for_image_ref(default_ref)


def _persist_docker_args(
    draft: RunConfigDraft,
    confirm_persist: _PersistDockerArgsPrompt,
) -> None:
    if draft.parsed is None or not draft.parsed.docker_args:
        return
    existing = draft.agent_cfg.docker_args
    if existing == draft.parsed.docker_args:
        return
    draft.persist_docker_args(
        confirm_persist(draft.parsed.docker_args, existing),
    )


def _persist_shares(
    draft: RunConfigDraft,
    confirm_persist: _PersistSharesPrompt,
) -> None:
    if draft.parsed is None:
        return
    existing_shares = list(draft.agent_cfg.shares)
    new_shares = draft.persist_shares(False)
    if not new_shares:
        return
    draft.persist_shares(confirm_persist(new_shares, existing_shares))
