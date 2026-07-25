from dataclasses import dataclass


@dataclass(frozen=True)
class BuiltInShareValue:
    source: str
    key: str
    label: str
    path: str
    persisted: bool | None
    enabled: bool
    row_key: str | None = None


@dataclass(frozen=True)
class SharesValues:
    shares: list[str]
    built_in_shares: list[BuiltInShareValue]


@dataclass(frozen=True)
class CustomShareValue:
    value: str


@dataclass(frozen=True)
class ShareEditorResult:
    share: str | None
    remove: bool


@dataclass(frozen=True)
class DockerOptionValue:
    key: str
    label: str
    description: str | None
    persisted: bool | None
    enabled: bool
    requires_confirmation: bool = True


@dataclass(frozen=True)
class HostAccessConfirmValues:
    docker_options: list[DockerOptionValue]
    git_support_shares: list[BuiltInShareValue]
    extension_shares: list[BuiltInShareValue]


@dataclass(frozen=True)
class ExtrasValues:
    docker_args: str
