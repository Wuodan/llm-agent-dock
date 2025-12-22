from dataclasses import dataclass

__all__ = ["ParsedArgs"]


@dataclass
class ParsedArgs:
    dry_run: bool
    docker_args: str
    tool: str
    tool_args: list[str]
    entrypoint: str | None
    docker_socket: bool
    config_action: str | None
