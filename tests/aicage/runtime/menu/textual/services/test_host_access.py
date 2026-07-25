from unittest import TestCase

from aicage.cli_types import ParsedArgs
from aicage.config.project_config import AgentConfig
from aicage.runtime.menu.textual._models import (
    BuiltInShareValue,
    CustomShareValue,
    DockerOptionValue,
    HostAccessConfirmValues,
)
from aicage.runtime.menu.textual.services import host_access

from ..._test_support import _build_draft


class HostAccessTests(TestCase):
    def test_built_in_selection_value_returns_row_key_when_present(self) -> None:
        value = host_access.built_in_selection_value(
            BuiltInShareValue(
                "extension",
                "gcloud",
                "Extension gcloud",
                "/test-tmp/gcloud",
                None,
                True,
                "gcloud:/test-tmp/gcloud",
            )
        )

        self.assertEqual("builtin:extension:gcloud:/test-tmp/gcloud", value)

    def test_current_built_in_shares_updates_enabled_state(self) -> None:
        values = host_access.current_built_in_shares(
            {"builtin:git_support:ssh"},
            [
                BuiltInShareValue(
                    "git_support", "ssh", "SSH", "/test-tmp/.ssh", None, False
                )
            ],
        )

        self.assertEqual(
            [
                BuiltInShareValue(
                    "git_support", "ssh", "SSH", "/test-tmp/.ssh", None, True
                )
            ],
            values,
        )

    def test_current_built_in_shares_updates_all_extension_rows_in_group(self) -> None:
        values = host_access.current_built_in_shares(
            {"builtin:extension:gcloud:/test-tmp/gcloud"},
            [
                BuiltInShareValue(
                    "extension",
                    "gcloud",
                    "Extension gcloud",
                    "/test-tmp/gcloud",
                    None,
                    False,
                    "gcloud:/test-tmp/gcloud",
                ),
                BuiltInShareValue(
                    "extension",
                    "gcloud",
                    "Extension gcloud",
                    "/test-tmp/boto",
                    None,
                    False,
                    "gcloud:/test-tmp/boto",
                ),
            ],
        )

        self.assertEqual(
            [
                BuiltInShareValue(
                    "extension",
                    "gcloud",
                    "Extension gcloud",
                    "/test-tmp/gcloud",
                    None,
                    True,
                    "gcloud:/test-tmp/gcloud",
                ),
                BuiltInShareValue(
                    "extension",
                    "gcloud",
                    "Extension gcloud",
                    "/test-tmp/boto",
                    None,
                    True,
                    "gcloud:/test-tmp/boto",
                ),
            ],
            values,
        )

    def test_current_docker_option_updates_enabled_state(self) -> None:
        value = host_access.current_docker_option({"docker:socket"}, None)

        self.assertEqual(
            DockerOptionValue("docker", "Docker socket", None, None, True), value
        )

    def test_current_clipboard_option_updates_enabled_state(self) -> None:
        value = host_access.current_clipboard_option(
            {"docker:clipboard"},
            None,
            "Wayland socket /run/user/1000/wayland-0",
            True,
        )

        self.assertEqual(
            DockerOptionValue(
                "clipboard",
                "Clipboard integration",
                "Wayland socket /run/user/1000/wayland-0",
                None,
                True,
                True,
            ),
            value,
        )

    def test_built_in_group_selection_values_returns_extension_group_rows(self) -> None:
        values = host_access.built_in_group_selection_values(
            "builtin:extension:gcloud:/test-tmp/gcloud",
            [
                BuiltInShareValue(
                    "extension",
                    "gcloud",
                    "Extension gcloud",
                    "/test-tmp/gcloud",
                    None,
                    True,
                    "gcloud:/test-tmp/gcloud",
                ),
                BuiltInShareValue(
                    "extension",
                    "gcloud",
                    "Extension gcloud",
                    "/test-tmp/boto",
                    None,
                    True,
                    "gcloud:/test-tmp/boto",
                ),
            ],
        )

        self.assertEqual(
            [
                "builtin:extension:gcloud:/test-tmp/gcloud",
                "builtin:extension:gcloud:/test-tmp/boto",
            ],
            values,
        )

    def test_build_confirmation_request_filters_newly_enabled_values(self) -> None:
        built_in_shares = [
            BuiltInShareValue(
                "git_support", "ssh", "SSH", "/test-tmp/.ssh", None, True
            ),
            BuiltInShareValue(
                "extension", "gh", "Extension gh", "/test-tmp/.config/gh", False, True
            ),
        ]
        docker_options = [
            DockerOptionValue("docker", "Docker socket", None, True, True),
            DockerOptionValue(
                "clipboard", "Clipboard integration", "Wayland socket", None, True
            ),
        ]

        values = host_access._build_confirmation_request(
            built_in_shares, docker_options
        )

        self.assertEqual([docker_options[1]], values.docker_options)
        self.assertEqual([built_in_shares[0]], values.git_support_shares)
        self.assertEqual([built_in_shares[1]], values.extension_shares)

    def test_build_confirmation_request_skips_non_sensitive_clipboard_option(
        self,
    ) -> None:
        values = host_access._build_confirmation_request(
            [],
            [
                DockerOptionValue(
                    "clipboard",
                    "Clipboard integration",
                    "OSC 52 terminal clipboard fallback; no host mounts",
                    None,
                    True,
                    False,
                )
            ],
        )

        self.assertEqual([], values.docker_options)

    def test_merge_confirmed_host_access_applies_confirmed_values(self) -> None:
        built_in_shares = [
            BuiltInShareValue("git_support", "ssh", "SSH", "/test-tmp/.ssh", None, True)
        ]
        docker_options = [
            DockerOptionValue("docker", "Docker socket", None, None, True),
            DockerOptionValue(
                "clipboard", "Clipboard integration", "Wayland socket", None, True
            ),
        ]
        confirmed = HostAccessConfirmValues(
            docker_options=[
                DockerOptionValue("docker", "Docker socket", None, None, False),
                DockerOptionValue(
                    "clipboard", "Clipboard integration", "Wayland socket", None, False
                ),
            ],
            git_support_shares=[
                BuiltInShareValue(
                    "git_support", "ssh", "SSH", "/test-tmp/.ssh", None, False
                )
            ],
            extension_shares=[],
        )

        merged_shares, merged_docker = host_access._merge_confirmed_host_access(
            built_in_shares,
            docker_options,
            confirmed,
        )

        self.assertEqual(
            [
                BuiltInShareValue(
                    "git_support", "ssh", "SSH", "/test-tmp/.ssh", None, False
                )
            ],
            merged_shares,
        )
        self.assertEqual(
            [
                DockerOptionValue("docker", "Docker socket", None, None, False),
                DockerOptionValue(
                    "clipboard", "Clipboard integration", "Wayland socket", None, False
                ),
            ],
            merged_docker,
        )

    def test_apply_confirmed_host_access_persists_values(self) -> None:
        draft = _build_draft(
            AgentConfig(base="ubuntu"),
            ParsedArgs(False, "", "codex", [], False, [], None),
        )

        host_access._apply_confirmed_host_access(
            draft,
            [
                BuiltInShareValue(
                    "git_support", "ssh", "SSH", "/test-tmp/.ssh", None, True
                ),
                BuiltInShareValue(
                    "extension",
                    "gh",
                    "Extension gh",
                    "/test-tmp/.config/gh",
                    None,
                    False,
                ),
            ],
            [CustomShareValue("/test-tmp/logs")],
            [
                DockerOptionValue("docker", "Docker socket", None, None, True),
                DockerOptionValue(
                    "clipboard", "Clipboard integration", "Wayland socket", None, True
                ),
            ],
        )

        self.assertEqual(["/test-tmp/logs"], draft.agent_cfg.shares)
        self.assertTrue(draft.agent_cfg.mounts.ssh)
        self.assertEqual({"gh": False}, draft.agent_cfg.extension_mounts)
        self.assertTrue(draft.agent_cfg.mounts.docker)
        self.assertTrue(draft.agent_cfg.mounts.clipboard)
