from unittest import TestCase

from aicage.errors import CliError
from aicage.registry.custom_agent import _validation
from aicage.registry.images_metadata.models import (
    AGENT_FULL_NAME_KEY,
    AGENT_HOMEPAGE_KEY,
    AGENT_PATH_KEY,
    BASE_EXCLUDE_KEY,
    BUILD_LOCAL_KEY,
)


class CustomAgentValidationTests(TestCase):
    def test_expect_string_rejects_empty(self) -> None:
        with self.assertRaises(CliError):
            _validation.expect_string(" ", AGENT_PATH_KEY)

    def test_expect_bool_rejects_non_bool(self) -> None:
        with self.assertRaises(CliError):
            _validation.expect_bool("true", BUILD_LOCAL_KEY)

    def test_maybe_str_list_rejects_non_string_items(self) -> None:
        with self.assertRaises(CliError):
            _validation.maybe_str_list(["ok", ""], BASE_EXCLUDE_KEY)

    def test_validate_agent_mapping_rejects_missing_required(self) -> None:
        with self.assertRaises(CliError):
            _validation.validate_agent_mapping({AGENT_PATH_KEY: "~/.custom"})

    def test_validate_agent_mapping_defaults_build_local(self) -> None:
        payload = _validation.validate_agent_mapping(
            {
                AGENT_PATH_KEY: "~/.custom",
                AGENT_FULL_NAME_KEY: "Custom",
                AGENT_HOMEPAGE_KEY: "https://example.com",
            }
        )
        self.assertTrue(payload[BUILD_LOCAL_KEY])
