import tempfile
from pathlib import Path
from unittest import TestCase, mock

from aicage.runtime.auth import mounts as auth_mounts


class AuthMountTests(TestCase):
    def test_build_auth_mounts_collects_git_and_gpg(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            home = Path(tmp_dir)
            gitconfig = home / ".gitconfig"
            gitconfig.write_text("user.name = coder", encoding="utf-8")
            gnupg = home / ".gnupg"
            gnupg.mkdir()

            prefs = auth_mounts.MountPreferences()
            with mock.patch("pathlib.Path.home", return_value=home), mock.patch(
                "aicage.runtime.auth.mounts.resolve_git_config_path", return_value=gitconfig
            ), mock.patch("aicage.runtime.auth.mounts.is_commit_signing_enabled", return_value=True), mock.patch(
                "aicage.runtime.auth.mounts.resolve_signing_format", return_value=None
            ), mock.patch(
                "aicage.runtime.auth.mounts.resolve_gpg_home", return_value=gnupg
            ), mock.patch(
                "aicage.runtime.auth.mounts.prompt_yes_no", return_value=True
            ):
                mounts, updated = auth_mounts.build_auth_mounts(Path("/repo"), prefs)

        self.assertTrue(updated)
        self.assertEqual({gitconfig, gnupg}, {mount.host_path for mount in mounts})

    def test_build_auth_mounts_uses_existing_ssh_preference(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            home = Path(tmp_dir)
            ssh_dir = home / ".ssh"
            ssh_dir.mkdir()

            prefs = auth_mounts.MountPreferences(ssh=True)
            with mock.patch("pathlib.Path.home", return_value=home), mock.patch(
                "aicage.runtime.auth.mounts.resolve_git_config_path", return_value=None
            ), mock.patch("aicage.runtime.auth.mounts.is_commit_signing_enabled", return_value=True), mock.patch(
                "aicage.runtime.auth.mounts.resolve_signing_format", return_value="ssh"
            ), mock.patch(
                "aicage.runtime.auth.mounts.prompt_yes_no"
            ) as prompt_mock:
                mounts, updated = auth_mounts.build_auth_mounts(Path("/repo"), prefs)

        prompt_mock.assert_not_called()
        self.assertFalse(updated)
        self.assertEqual(ssh_dir, mounts[0].host_path)
