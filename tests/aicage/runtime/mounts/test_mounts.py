import tempfile
from pathlib import Path
from unittest import TestCase, mock

from aicage.runtime.mounts import _git_config, _gpg, _ssh_keys


class MountResolutionTests(TestCase):
    def test_resolve_git_config_mount_persists_preference(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            gitconfig = Path(tmp_dir) / ".gitconfig"
            gitconfig.write_text("user.name = coder", encoding="utf-8")
            tool_cfg: dict[str, object] = {}

            with (
                mock.patch("aicage.runtime.mounts._git_config._resolve_git_config_path", return_value=gitconfig),
                mock.patch("aicage.runtime.mounts._git_config.prompt_yes_no", return_value=True),
            ):
                mounts = _git_config.resolve_git_config_mount(tool_cfg)

        self.assertEqual({"gitconfig": True}, tool_cfg["mounts"])
        self.assertEqual(1, len(mounts))

    def test_resolve_ssh_mount_uses_existing_preference(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            ssh_dir = Path(tmp_dir) / ".ssh"
            ssh_dir.mkdir()
            tool_cfg: dict[str, object] = {"mounts": {"ssh": True}}

            with (
                mock.patch("aicage.runtime.mounts._ssh_keys.is_commit_signing_enabled", return_value=True),
                mock.patch("aicage.runtime.mounts._ssh_keys.resolve_signing_format", return_value="ssh"),
                mock.patch("aicage.runtime.mounts._ssh_keys._default_ssh_dir", return_value=ssh_dir),
                mock.patch("aicage.runtime.mounts._ssh_keys.prompt_yes_no") as prompt_mock,
            ):
                mounts = _ssh_keys.resolve_ssh_mount(Path("/repo"), tool_cfg)

        prompt_mock.assert_not_called()
        self.assertEqual(1, len(mounts))
        self.assertEqual(ssh_dir, mounts[0].host_path)

    def test_resolve_gpg_mount_uses_existing_preference(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            gpg_home = Path(tmp_dir) / ".gnupg"
            gpg_home.mkdir()
            tool_cfg: dict[str, object] = {"mounts": {"gnupg": True}}

            with (
                mock.patch("aicage.runtime.mounts._gpg.is_commit_signing_enabled", return_value=True),
                mock.patch("aicage.runtime.mounts._gpg.resolve_signing_format", return_value=None),
                mock.patch("aicage.runtime.mounts._gpg._resolve_gpg_home", return_value=gpg_home),
                mock.patch("aicage.runtime.mounts._gpg.prompt_yes_no") as prompt_mock,
            ):
                mounts = _gpg.resolve_gpg_mount(Path("/repo"), tool_cfg)

        prompt_mock.assert_not_called()
        self.assertEqual(1, len(mounts))
        self.assertEqual(gpg_home, mounts[0].host_path)
