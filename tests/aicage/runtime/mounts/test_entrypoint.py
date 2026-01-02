import tempfile
from pathlib import Path
from unittest import TestCase, mock

from aicage.config.project_config import AgentConfig
from aicage.errors import CliError
from aicage.runtime.mounts._entrypoint import (
    _resolve_entrypoint_path,
    _validate_entrypoint_path,
    resolve_entrypoint_mount,
)


class EntrypointMountTests(TestCase):
    def test_resolve_entrypoint_path(self) -> None:
        resolved = _resolve_entrypoint_path("./entrypoint.sh")
        self.assertTrue(resolved.is_absolute())

    def test_validate_entrypoint_path_errors(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            missing = Path(tmp_dir) / "missing.sh"
            with self.assertRaises(CliError):
                _validate_entrypoint_path(missing)

            entrypoint = Path(tmp_dir) / "entrypoint.sh"
            entrypoint.write_text("#!/bin/sh\necho ok\n", encoding="utf-8")
            with mock.patch("os.access", return_value=False):
                with self.assertRaises(CliError):
                    _validate_entrypoint_path(entrypoint)

    def test_resolve_entrypoint_mount_persists_entrypoint(self) -> None:
        agent_cfg = AgentConfig()
        entrypoint_path = Path("/tmp/entrypoint.sh")
        with (
            mock.patch("aicage.runtime.mounts._entrypoint._resolve_entrypoint_path", return_value=entrypoint_path),
            mock.patch("aicage.runtime.mounts._entrypoint._validate_entrypoint_path"),
            mock.patch("aicage.runtime.mounts._entrypoint.prompt_yes_no", return_value=True),
        ):
            mounts = resolve_entrypoint_mount(agent_cfg, "./entrypoint.sh")

        self.assertEqual(str(entrypoint_path), agent_cfg.entrypoint)
        self.assertEqual(1, len(mounts))
        self.assertTrue(mounts[0].read_only)

    def test_resolve_entrypoint_mount_uses_persisted_entrypoint(self) -> None:
        agent_cfg = AgentConfig(entrypoint="/bin/sh")
        entrypoint_path = Path("/bin/sh")
        with (
            mock.patch("aicage.runtime.mounts._entrypoint._resolve_entrypoint_path", return_value=entrypoint_path),
            mock.patch("aicage.runtime.mounts._entrypoint._validate_entrypoint_path"),
            mock.patch("aicage.runtime.mounts._entrypoint.prompt_yes_no") as prompt_mock,
        ):
            mounts = resolve_entrypoint_mount(agent_cfg, None)

        prompt_mock.assert_not_called()
        self.assertEqual(1, len(mounts))
