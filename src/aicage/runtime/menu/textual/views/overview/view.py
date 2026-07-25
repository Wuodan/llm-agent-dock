from textual.app import ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.message import Message
from textual.widgets import Button, Header, SelectionList, Static
from textual.widgets.selection_list import Selection

from aicage.config.context import ConfigContext
from aicage.config.run_config_draft import RunConfigDraft

from ..._ids import (
    ROW_BASE,
    ROW_EXTENSIONS,
    ROW_EXTRAS,
    SECTION_IDS,
    docker_selection_key,
)
from ..._models import BuiltInShareValue, CustomShareValue, DockerOptionValue
from ..._state import OverviewState
from ...services.host_access import (
    built_in_group_selection_values,
    current_built_in_shares,
    current_clipboard_option,
    current_docker_option,
)
from ...services.summary import (
    extensions_summary,
    extras_summary,
    extras_values,
    shares_values,
)
from ._layout import shell_width
from ._selection_list import _OverviewSelectionList
from ._shares import (
    current_custom_shares,
    merge_built_in_shares,
    refresh_shares,
    share_widgets,
)


class Overview(Container):
    _CONTEXT_LABEL_WIDTH = 8

    class AcceptRequested(Message):
        pass

    class CancelRequested(Message):
        pass

    class AddShareRequested(Message):
        pass

    class EditSectionRequested(Message):
        def __init__(self, section_id: str) -> None:
            self.section_id = section_id
            super().__init__()

    class EditCustomShareRequested(Message):
        def __init__(self, current_value: str) -> None:
            self.current_value = current_value
            super().__init__()

    def __init__(self, agent: str, project_path: str, state: OverviewState) -> None:
        super().__init__(id="overview_root")
        self._agent = agent
        self._project_path = project_path
        self._state = state

    def compose(self) -> ComposeResult:
        yield Container(
            Container(
                Header(show_clock=False, classes="app_header"),
                Static(self._context_line("Agent:", self._agent), id="title"),
                Static(
                    self._context_line("Project:", self._project_path), id="context"
                ),
                Horizontal(
                    Button(id=ROW_EXTENSIONS, classes="section"),
                    Button(id=ROW_EXTRAS, classes="section"),
                    Button(id=ROW_BASE, classes="section"),
                    id="sections",
                ),
                Vertical(
                    Vertical(*share_widgets(self._state), id="shares_overview"),
                    Vertical(*self._docker_widgets(), id="docker_overview"),
                    id="access_overview",
                ),
                Horizontal(
                    Button("Cancel", id="cancel", variant="default"),
                    Button("OK", id="ok", variant="primary"),
                    id="actions",
                ),
                id="shell",
            ),
            id="overview_frame",
        )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "ok":
            self.post_message(self.AcceptRequested())
        elif event.button.id == "cancel":
            self.post_message(self.CancelRequested())
        elif event.button.id == "add_share":
            self.post_message(self.AddShareRequested())
        elif event.button.id in SECTION_IDS:
            self.post_message(self.EditSectionRequested(event.button.id))

    def on_selection_list_selected_changed(
        self, event: SelectionList.SelectedChanged
    ) -> None:
        if event.selection_list.id == "shares_overview_list":
            self._state.built_in_shares = current_built_in_shares(
                set(event.selection_list.selected),
                self._state.built_in_shares,
            )
            return
        if event.selection_list.id == "docker_overview_list":
            self._state.docker_socket_enabled = (
                docker_selection_key("socket") in event.selection_list.selected
            )
            self._state.clipboard_enabled = (
                docker_selection_key("clipboard") in event.selection_list.selected
            )
            self.apply_shell_width(self.size.width)

    def on_selection_list_selection_toggled(
        self, event: SelectionList.SelectionToggled
    ) -> None:
        if event.selection_list.id != "shares_overview_list":
            return
        selection_value = event.selection.value
        if not isinstance(selection_value, str) or not selection_value.startswith(
            "custom:"
        ):
            if isinstance(selection_value, str):
                self._sync_built_in_share_group_selection(
                    event.selection_list, selection_value
                )
            return
        event.selection_list.select(selection_value)
        self.post_message(
            self.EditCustomShareRequested(selection_value.removeprefix("custom:"))
        )

    def refresh_from(self, draft: RunConfigDraft, context: ConfigContext) -> None:
        self._state.built_in_shares = merge_built_in_shares(
            shares_values(draft, context).built_in_shares,
            self._state.built_in_shares,
        )
        self.apply_shell_width(self.size.width)
        self._section_button(ROW_BASE).label = self._section_label(
            "Base", draft.agent_cfg.base or ""
        )
        self._section_button(ROW_EXTENSIONS).label = self._section_label(
            "Extensions",
            extensions_summary(draft.agent_cfg.extensions),
        )
        self._section_button(ROW_EXTRAS).label = self._section_label(
            "Docker Args",
            extras_summary(extras_values(draft)),
        )
        refresh_shares(self, self._state)
        self._refresh_docker()

    def apply_shell_width(self, viewport_width: int) -> None:
        width = shell_width(
            self._state.built_in_shares, self._state.custom_shares, viewport_width
        )
        shell = self.query_one("#shell", Container)
        shell.styles.width = width
        shell.styles.min_width = width
        shell.styles.max_width = width
        shell.refresh(layout=True)

    def focus_default(self) -> None:
        self.query_one("#ok", Button).focus()

    def focus_section(self, section_id: str) -> None:
        self._section_button(section_id).focus()

    def hide_shell(self) -> None:
        self.query_one("#shell", Container).display = False

    def show_shell(self) -> None:
        self.query_one("#shell", Container).display = True

    def current_built_in_shares(self) -> list[BuiltInShareValue]:
        return current_built_in_shares(
            set(self.query_one("#shares_overview_list", SelectionList).selected),
            self._state.built_in_shares,
        )

    def current_custom_shares(self) -> list[CustomShareValue]:
        return current_custom_shares(self._state)

    def current_host_options(
        self,
        docker_socket_value: bool | None,
        clipboard_value: bool | None,
    ) -> list[DockerOptionValue]:
        selected = set(self.query_one("#docker_overview_list", SelectionList).selected)
        options = [current_docker_option(selected, docker_socket_value)]
        if self._state.show_clipboard:
            options.append(
                current_clipboard_option(
                    selected,
                    clipboard_value,
                    self._state.clipboard_description,
                    self._state.clipboard_requires_confirmation,
                )
            )
        return options

    def _section_button(self, section_id: str) -> Button:
        return self.query_one(f"#{section_id}", Button)

    def _sync_built_in_share_group_selection(
        self, selection_list: SelectionList, selection_value: str
    ) -> None:
        related_values = built_in_group_selection_values(
            selection_value, self._state.built_in_shares
        )
        if not related_values:
            return
        selected_values = set(selection_list.selected)
        if selection_value in selected_values:
            for related_value in related_values:
                selection_list.select(related_value)
            return
        for related_value in related_values:
            selection_list.deselect(related_value)

    def _docker_widgets(self) -> list[Static | SelectionList]:
        selections = [
            Selection(
                "Docker socket",
                docker_selection_key("socket"),
                self._state.docker_socket_enabled,
            )
        ]
        if self._state.show_clipboard:
            selections.append(
                Selection(
                    "Clipboard integration",
                    docker_selection_key("clipboard"),
                    self._state.clipboard_enabled,
                )
            )
        return [
            Static("Host Integration", id="docker_overview_title"),
            _OverviewSelectionList(
                *selections,
                id="docker_overview_list",
                compact=True,
            ),
        ]

    def _refresh_docker(self) -> None:
        self.query_one("#docker_overview_title", Static).update("Host Integration")
        selection_list = self.query_one("#docker_overview_list", SelectionList)
        selection_list.clear_options()
        options = [
            Selection(
                "Docker socket",
                docker_selection_key("socket"),
                self._state.docker_socket_enabled,
            )
        ]
        if self._state.show_clipboard:
            options.append(
                Selection(
                    "Clipboard integration",
                    docker_selection_key("clipboard"),
                    self._state.clipboard_enabled,
                )
            )
        selection_list.add_options(options)

    def _section_label(self, title: str, summary: str) -> str:
        return f"{title}\n{self._truncate_summary(summary)}"

    @classmethod
    def _context_line(cls, label: str, value: str) -> str:
        return f"{label:<{cls._CONTEXT_LABEL_WIDTH}} {value}"

    @staticmethod
    def _truncate_summary(summary: str, limit: int = 34) -> str:
        if len(summary) <= limit:
            return summary
        return f"{summary[: limit - 1]}..."
