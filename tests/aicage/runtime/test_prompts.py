from unittest import TestCase, mock

from aicage.config.context import ConfigContext
from aicage.config.global_config import GlobalConfig
from aicage.config.project_config import ProjectConfig
from aicage.errors import CliError
from aicage.registry.images_metadata.models import AgentMetadata, ImagesMetadata
from aicage.runtime.prompts import (
    BaseSelectionRequest,
    ensure_tty_for_prompt,
    prompt_for_base,
    prompt_yes_no,
)


class PromptTests(TestCase):
    def test_prompt_requires_tty(self) -> None:
        with mock.patch("sys.stdin.isatty", return_value=False):
            with self.assertRaises(CliError):
                ensure_tty_for_prompt()

    def test_prompt_validates_choice(self) -> None:
        with mock.patch("sys.stdin.isatty", return_value=True), mock.patch(
            "builtins.input", return_value="fedora"
        ):
            with self.assertRaises(CliError):
                prompt_for_base(
                    BaseSelectionRequest(
                        agent="codex",
                        context=self._build_context(["ubuntu"]),
                        agent_metadata=self._agent_metadata(["ubuntu"]),
                    )
                )

    def test_prompt_accepts_number_and_default(self) -> None:
        with mock.patch("sys.stdin.isatty", return_value=True), mock.patch("builtins.input", side_effect=["2", ""]):
            choice = prompt_for_base(
                BaseSelectionRequest(
                    agent="codex",
                    context=self._build_context(["alpine", "ubuntu"]),
                    agent_metadata=self._agent_metadata(["alpine", "ubuntu"]),
                )
            )
            self.assertEqual("ubuntu", choice)
            default_choice = prompt_for_base(
                BaseSelectionRequest(
                    agent="codex",
                    context=self._build_context(["ubuntu"]),
                    agent_metadata=self._agent_metadata(["ubuntu"]),
                )
            )
            self.assertEqual("ubuntu", default_choice)
        with mock.patch("sys.stdin.isatty", return_value=True), mock.patch("builtins.input", return_value="3"):
            with self.assertRaises(CliError):
                prompt_for_base(
                    BaseSelectionRequest(
                        agent="codex",
                        context=self._build_context(["alpine", "ubuntu"]),
                        agent_metadata=self._agent_metadata(["alpine", "ubuntu"]),
                    )
                )

    def test_prompt_accepts_default_without_list(self) -> None:
        with mock.patch("sys.stdin.isatty", return_value=True), mock.patch("builtins.input", return_value=""):
            choice = prompt_for_base(
                BaseSelectionRequest(
                    agent="codex",
                    context=self._build_context([]),
                    agent_metadata=self._agent_metadata([]),
                )
            )
        self.assertEqual("ubuntu", choice)

    def test_prompt_yes_no_defaults(self) -> None:
        with mock.patch("sys.stdin.isatty", return_value=True), mock.patch("builtins.input", return_value=""):
            self.assertTrue(prompt_yes_no("Continue?", default=True))
            self.assertFalse(prompt_yes_no("Continue?", default=False))

    def test_prompt_yes_no_parses_input(self) -> None:
        with mock.patch("sys.stdin.isatty", return_value=True), mock.patch("builtins.input", return_value="y"):
            self.assertTrue(prompt_yes_no("Continue?", default=False))
        with mock.patch("sys.stdin.isatty", return_value=True), mock.patch("builtins.input", return_value="no"):
            self.assertFalse(prompt_yes_no("Continue?", default=True))

    @staticmethod
    def _build_context(bases: list[str]) -> ConfigContext:
        metadata = PromptTests._metadata_with_bases(bases)
        return ConfigContext(
            store=mock.Mock(),
            project_cfg=ProjectConfig(path="/tmp/project", agents={}),
            global_cfg=GlobalConfig(
                image_registry="ghcr.io",
                image_registry_api_url="https://ghcr.io/v2",
                image_registry_api_token_url="https://ghcr.io/token?service=ghcr.io&scope=repository",
                image_repository="aicage/aicage",
                default_image_base="ubuntu",
                version_check_image="ghcr.io/aicage/aicage-image-util:latest",
                agents={},
            ),
            images_metadata=metadata,
        )

    @staticmethod
    def _agent_metadata(bases: list[str]) -> AgentMetadata:
        metadata = PromptTests._metadata_with_bases(bases)
        return metadata.agents["codex"]

    @staticmethod
    def _metadata_with_bases(bases: list[str]) -> ImagesMetadata:
        return ImagesMetadata.from_mapping(
            {
                "aicage-image": {"version": "0.3.3"},
                "aicage-image-base": {"version": "0.3.3"},
                "bases": {
                    name: {
                        "root_image": "ubuntu:latest",
                        "base_image_distro": "Ubuntu",
                        "base_image_description": "Default",
                        "os_installer": "distro/debian/install.sh",
                        "test_suite": "default",
                    }
                    for name in bases
                },
                "agent": {
                    "codex": {
                        "agent_path": "~/.codex",
                        "agent_full_name": "Codex CLI",
                        "agent_homepage": "https://example.com",
                        "redistributable": True,
                        "valid_bases": {name: f"repo:{name}" for name in bases},
                    }
                },
            }
        )
