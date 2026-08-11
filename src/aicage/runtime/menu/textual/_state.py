from dataclasses import dataclass

from ._models import BuiltInShareValue, CustomShareValue


@dataclass
class OverviewState:
    last_section_id: str | None
    built_in_shares: list[BuiltInShareValue]
    custom_shares: list[CustomShareValue]
    docker_socket_enabled: bool
