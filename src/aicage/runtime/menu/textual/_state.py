from dataclasses import dataclass

from ._models import BuiltInShareValue, CustomShareValue


@dataclass
class OverviewState:
    last_section_id: str | None
    built_in_shares: list[BuiltInShareValue]
    custom_shares: list[CustomShareValue]
    docker_socket_enabled: bool
    show_clipboard: bool = False
    clipboard_enabled: bool = False
    clipboard_description: str | None = None
    clipboard_requires_confirmation: bool = True
