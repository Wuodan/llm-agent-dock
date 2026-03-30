import tempfile
from pathlib import Path
from unittest import TestCase, mock

from aicage.config.extensions.loader import ExtensionMetadata
from aicage.config.project_config import AgentConfig, _AgentMounts
from aicage.runtime.docker_args._support import _mount_prompt

_MODULE = "aicage.runtime.docker_args._support._mount_prompt"


class MountPromptTests(TestCase):
    def test_resolve_mount_prompt_prefs_returns_relevant_git_prefs(self) -> None:
        agent_cfg = AgentConfig(mounts=_AgentMounts())
        project_path = Path("/repo")
        git_items = [
            ("gitconfig", "Git config (name/email): /tmp/gitconfig"),
            ("gitroot", "Git root (repository access): /tmp/root"),
            ("gnupg", "GnuPG keys (for Git signing): /tmp/gnupg"),
        ]

        with (
            mock.patch(f"{_MODULE}.git_support_prompt_items", return_value=git_items),
            mock.patch(f"{_MODULE}.prompt_mount_git_support", return_value=["gitconfig", "gitroot", "gnupg"]),
        ):
            prefs = _mount_prompt.resolve_mount_prompt_prefs(project_path, agent_cfg, {})

        self.assertEqual({"gitconfig", "gitroot", "gnupg"}, prefs.git_mounts)
        self.assertEqual({}, prefs.extension_mounts)

    def test_resolve_mount_prompt_prefs_skips_when_no_items(self) -> None:
        agent_cfg = AgentConfig(mounts=_AgentMounts())

        with (
            mock.patch(f"{_MODULE}.git_support_prompt_items", return_value=[]),
            mock.patch(f"{_MODULE}.prompt_mount_git_support") as prompt_mock,
        ):
            prefs = _mount_prompt.resolve_mount_prompt_prefs(Path("/repo"), agent_cfg, {})

        self.assertIsNone(prefs)
        prompt_mock.assert_not_called()

    def test_resolve_mount_prompt_prefs_appends_extension_group_items(self) -> None:
        agent_cfg = AgentConfig(mounts=_AgentMounts(), extensions=["gh"])
        project_path = Path("/repo")
        extension = ExtensionMetadata(
            extension_id="gh",
            name="GitHub CLI",
            description="Desc",
            shares=["~/.config/gh", "~/.cache/gh:ro"],
            directory=Path("/tmp/ext"),
            scripts_dir=Path("/tmp/ext/scripts"),
            dockerfile_path=None,
        )

        with tempfile.TemporaryDirectory() as tmp_dir:
            git_items = [("gitconfig", f"Git config (name/email): {Path(tmp_dir) / '.gitconfig'}")]
            with (
                mock.patch(f"{_MODULE}.git_support_prompt_items", return_value=git_items),
                mock.patch(f"{_MODULE}.prompt_mount_git_support", return_value=["gitconfig", "gh"]) as prompt_mock,
            ):
                prefs = _mount_prompt.resolve_mount_prompt_prefs(project_path, agent_cfg, {"gh": extension})

        git_prompt_items = prompt_mock.call_args.args[0]
        extension_prompt_items = prompt_mock.call_args.args[1]
        self.assertEqual("gitconfig", git_prompt_items[0][0])
        self.assertEqual("gh", extension_prompt_items[0][0])
        self.assertIn("Extension gh shares:", extension_prompt_items[0][1])
        self.assertEqual({"gitconfig"}, prefs.git_mounts)
        self.assertEqual({"gh": True}, prefs.extension_mounts)

    def test_resolve_mount_prompt_prefs_returns_unselected_extension_group_false(self) -> None:
        agent_cfg = AgentConfig(mounts=_AgentMounts(), extensions=["gh"])
        extension = ExtensionMetadata(
            extension_id="gh",
            name="GitHub CLI",
            description="Desc",
            shares=["~/.config/gh"],
            directory=Path("/tmp/ext"),
            scripts_dir=Path("/tmp/ext/scripts"),
            dockerfile_path=None,
        )

        with (
            mock.patch(f"{_MODULE}.git_support_prompt_items", return_value=[]),
            mock.patch(f"{_MODULE}.prompt_mount_git_support", return_value=[]),
        ):
            prefs = _mount_prompt.resolve_mount_prompt_prefs(Path("/repo"), agent_cfg, {"gh": extension})

        self.assertEqual(set(), prefs.git_mounts)
        self.assertEqual({"gh": False}, prefs.extension_mounts)

    def test_resolve_mount_prompt_prefs_skips_extensions_with_stored_choice(self) -> None:
        agent_cfg = AgentConfig(
            mounts=_AgentMounts(),
            extensions=["gh", "sample"],
            extension_mounts={"gh": True},
        )
        extension = ExtensionMetadata(
            extension_id="sample",
            name="Sample",
            description="Desc",
            shares=["~/.sample"],
            directory=Path("/tmp/ext"),
            scripts_dir=Path("/tmp/ext/scripts"),
            dockerfile_path=None,
        )

        with (
            mock.patch(f"{_MODULE}.git_support_prompt_items", return_value=[]),
            mock.patch(f"{_MODULE}.prompt_mount_git_support", return_value=["sample"]) as prompt_mock,
        ):
            prefs = _mount_prompt.resolve_mount_prompt_prefs(Path("/repo"), agent_cfg, {"sample": extension})

        self.assertEqual(
            [("sample", f"Extension sample shares: {Path.home().resolve() / '.sample'}")],
            prompt_mock.call_args.args[1],
        )
        self.assertEqual({"sample": True}, prefs.extension_mounts)

    def test_resolve_mount_prompt_prefs_skips_missing_or_shareless_extensions(self) -> None:
        agent_cfg = AgentConfig(mounts=_AgentMounts(), extensions=["missing", "empty"])
        extension = ExtensionMetadata(
            extension_id="empty",
            name="Empty",
            description="Desc",
            shares=[],
            directory=Path("/tmp/ext"),
            scripts_dir=Path("/tmp/ext/scripts"),
            dockerfile_path=None,
        )

        with (
            mock.patch(f"{_MODULE}.git_support_prompt_items", return_value=[]),
            mock.patch(f"{_MODULE}.prompt_mount_git_support") as prompt_mock,
        ):
            prefs = _mount_prompt.resolve_mount_prompt_prefs(Path("/repo"), agent_cfg, {"empty": extension})

        self.assertIsNone(prefs)
        prompt_mock.assert_not_called()
