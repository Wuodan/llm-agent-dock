from typing import TypeVar

from textual import work
from textual.app import ComposeResult
from textual.binding import Binding
from textual.screen import Screen

from aicage.config.context import ConfigContext
from aicage.config.extensions.order import canonical_extensions
from aicage.config.overview_selection import resolve_overview_selection
from aicage.config.run_config_draft import RunConfigDraft
from aicage.registry.image_selection.extensions.missing_extensions import (
    ensure_extensions_exist,
)
from aicage.registry.image_selection.interaction import ExtensionChoiceOption
from aicage.runtime.docker_args.resolvers.clipboard import (
    clipboard_requires_confirmation,
    describe_host_clipboard_access,
)
from aicage.runtime.menu._interaction_types import ConfigSelectionResult

from ._ids import ROW_BASE, ROW_EXTENSIONS, ROW_EXTRAS
from ._models import CustomShareValue, HostAccessConfirmValues
from ._state import OverviewState
from ._textual_app import TextualApp
from .services.base_support import base_metadata_for_draft, ensure_base_default
from .services.custom_share_flow import add_custom_share, update_custom_share
from .services.host_access_flow import confirm_and_apply_host_access
from .services.summary import extras_values, shares_values
from .views.base_screen import BaseScreen
from .views.docker_args_screen import DockerArgsScreen
from .views.extensions_screen import ExtensionsScreen
from .views.host_access_confirm_screen import HostAccessConfirmScreen
from .views.overview.view import Overview
from .views.share_editor_screen import ShareEditorScreen

_ScreenResultT = TypeVar("_ScreenResultT")


class ConfigApp(TextualApp[ConfigSelectionResult | None]):
    BINDINGS = [
        Binding("enter", "accept", "OK"),
        Binding("escape", "cancel", "Cancel"),
        *TextualApp.BINDINGS,
    ]

    def __init__(self, draft: RunConfigDraft, context: ConfigContext) -> None:
        super().__init__("container config")
        self._draft = draft
        self._config_context = context
        self._state = self._initial_state()

    def compose(self) -> ComposeResult:
        yield Overview(
            self._draft.agent,
            self._draft.project_cfg.path,
            self._state,
        )

    def on_mount(self) -> None:
        ensure_base_default(self._draft, self._config_context)
        self._apply_shell_width()
        self._refresh_sections()
        self._overview().focus_default()

    def action_accept(self) -> None:
        self._accept()

    def action_cancel(self) -> None:
        self._finish(None)

    @work(exclusive=True)
    async def _accept(self) -> None:
        accepted = await self._confirm_undecided_built_in_shares()
        if not accepted:
            return
        if ensure_extensions_exist(self._draft.agent, self._config_context):
            self._refresh_sections()
        self._finish(
            ConfigSelectionResult(
                selection=resolve_overview_selection(
                    self._draft,
                    self._config_context,
                ),
                project_docker_args=self._draft.agent_cfg.docker_args,
            )
        )

    @work(exclusive=True)
    async def _edit_section(self, section_id: str) -> None:
        self._state.last_section_id = section_id
        if section_id == ROW_BASE:
            await self._edit_base()
        elif section_id == ROW_EXTENSIONS:
            await self._edit_extensions()
        elif section_id == ROW_EXTRAS:
            await self._edit_extras()
        self._refresh_sections()

    def on_overview_accept_requested(self, _: Overview.AcceptRequested) -> None:
        self.action_accept()

    def on_overview_cancel_requested(self, _: Overview.CancelRequested) -> None:
        self.action_cancel()

    def on_overview_add_share_requested(self, _: Overview.AddShareRequested) -> None:
        self._add_share()

    def on_overview_edit_section_requested(
        self, message: Overview.EditSectionRequested
    ) -> None:
        self._edit_section(message.section_id)

    def on_overview_edit_custom_share_requested(
        self, message: Overview.EditCustomShareRequested
    ) -> None:
        self._edit_custom_share(message.current_value)

    async def _edit_base(self) -> None:
        selected = await self._push_view(
            BaseScreen(
                base_metadata_for_draft(self._draft, self._config_context),
                self._draft.agent_cfg.base or "",
            )
        )
        if selected is not None and selected != self._draft.agent_cfg.base:
            self._draft.agent_cfg.base = selected
            self._draft.reset_extension_image()

    async def _edit_extensions(self) -> None:
        selected = await self._push_view(
            ExtensionsScreen(
                [
                    ExtensionChoiceOption(
                        name=extension.extension_id,
                        description=f"{extension.name} - {extension.description}",
                        has_dockerfile=extension.dockerfile_path is not None,
                    )
                    for extension in canonical_extensions(
                        list(self._config_context.extensions.values())
                    )
                ],
                list(self._draft.agent_cfg.extensions),
            )
        )
        if selected is not None and selected != self._draft.agent_cfg.extensions:
            self._draft.agent_cfg.extensions = selected
            self._draft.reset_extension_image()

    async def _edit_extras(self) -> None:
        selected = await self._push_view(DockerArgsScreen(extras_values(self._draft)))
        if selected is None:
            return
        self._draft.agent_cfg.docker_args = selected.docker_args

    @work(exclusive=True)
    async def _add_share(self) -> None:
        result = await self._push_view(ShareEditorScreen())
        if result is None or result.share is None:
            return
        if not add_custom_share(self._state, self._draft, result.share):
            return
        self._apply_shell_width()
        self._refresh_sections()

    @work(exclusive=True)
    async def _edit_custom_share(self, current_value: str) -> None:
        result = await self._push_view(
            ShareEditorScreen(current_value, allow_remove=True)
        )
        if result is None:
            return
        if not update_custom_share(
            self._state,
            self._draft,
            current_value,
            result,
        ):
            return
        self._apply_shell_width()
        self._refresh_sections()

    async def _push_view(self, screen: Screen[_ScreenResultT]) -> _ScreenResultT:
        overview = self._overview()
        overview.hide_shell()
        try:
            return await self.push_screen_wait(screen)
        finally:
            overview.show_shell()
            self._focus_last_section()

    def _finish(self, result: ConfigSelectionResult | None) -> None:
        self.exit(result)

    def _focus_last_section(self) -> None:
        if self._state.last_section_id is None:
            self._overview().focus_default()
            return
        self._overview().focus_section(self._state.last_section_id)

    def _apply_shell_width(self) -> None:
        self._overview().apply_shell_width(self.size.width)

    def _refresh_sections(self) -> None:
        self._overview().refresh_from(self._draft, self._config_context)

    async def _confirm_undecided_built_in_shares(self) -> bool:
        overview = self._overview()
        self._state.custom_shares = overview.current_custom_shares()
        accepted, self._state.built_in_shares = await confirm_and_apply_host_access(
            self._draft,
            overview.current_built_in_shares(),
            self._state.custom_shares,
            overview.current_host_options(
                self._draft.agent_cfg.mounts.docker,
                self._draft.agent_cfg.mounts.clipboard,
            ),
            self._confirm_host_access,
        )
        return accepted

    def _overview(self) -> Overview:
        return self.query_one(Overview)

    async def _confirm_host_access(
        self,
        values: HostAccessConfirmValues,
    ) -> HostAccessConfirmValues | None:
        return await self._push_view(
            HostAccessConfirmScreen(
                values.docker_options,
                values.git_support_shares,
                values.extension_shares,
            )
        )

    def _initial_state(self) -> OverviewState:
        return OverviewState(
            last_section_id=None,
            built_in_shares=shares_values(
                self._draft, self._config_context
            ).built_in_shares,
            custom_shares=[
                CustomShareValue(share) for share in self._draft.agent_cfg.shares
            ],
            docker_socket_enabled=bool(self._draft.agent_cfg.mounts.docker),
            show_clipboard=True,
            clipboard_enabled=bool(self._draft.agent_cfg.mounts.clipboard),
            clipboard_description=describe_host_clipboard_access(),
            clipboard_requires_confirmation=clipboard_requires_confirmation(),
        )
