from unittest import TestCase

from aicage.errors import CliError
from aicage.registry.custom_agent import _validation


class CustomAgentValidationTests(TestCase):
    def test_expect_string_rejects_empty(self) -> None:
        with self.assertRaises(CliError):
            _validation.expect_string(" ", "agent_path")

    def test_expect_bool_rejects_non_bool(self) -> None:
        with self.assertRaises(CliError):
            _validation.expect_bool("true", "build_local")

    def test_maybe_str_list_rejects_non_string_items(self) -> None:
        with self.assertRaises(CliError):
            _validation.maybe_str_list(["ok", ""], "base_exclude")

    def test_validate_agent_mapping_rejects_missing_required(self) -> None:
        with self.assertRaises(CliError):
            _validation.validate_agent_mapping({"agent_path": "~/.custom"})

    def test_validate_agent_mapping_defaults_build_local(self) -> None:
        payload = _validation.validate_agent_mapping(
            {
                "agent_path": "~/.custom",
                "agent_full_name": "Custom",
                "agent_homepage": "https://example.com",
            }
        )
        self.assertTrue(payload["build_local"])
