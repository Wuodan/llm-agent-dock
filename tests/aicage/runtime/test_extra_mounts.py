from pathlib import Path
from unittest import TestCase, mock

from aicage.runtime.extra_mounts import _build_extra_mounts, _ExtraMountPreferences


class ExtraMountsTests(TestCase):
    def test_build_extra_mounts_persists_entrypoint(self) -> None:
        prefs = _ExtraMountPreferences()
        with (
            mock.patch("aicage.runtime.extra_mounts._validate_entrypoint_path"),
            mock.patch("aicage.runtime.extra_mounts.prompt_yes_no", return_value=True),
        ):
            mounts, updated = _build_extra_mounts("./entrypoint.sh", False, prefs)

        self.assertTrue(updated)
        self.assertEqual(str(Path("./entrypoint.sh").expanduser().resolve()), prefs.entrypoint)
        self.assertEqual(1, len(mounts))
        self.assertTrue(mounts[0].read_only)

    def test_build_extra_mounts_persists_docker_socket(self) -> None:
        prefs = _ExtraMountPreferences()
        with mock.patch("aicage.runtime.extra_mounts.prompt_yes_no", return_value=True):
            mounts, updated = _build_extra_mounts(None, True, prefs)

        self.assertTrue(updated)
        self.assertTrue(prefs.docker_socket)
        self.assertEqual(1, len(mounts))
        self.assertEqual(Path("/run/docker.sock"), mounts[0].container_path)

    def test_build_extra_mounts_uses_persisted_docker_socket(self) -> None:
        prefs = _ExtraMountPreferences(docker_socket=True)
        with mock.patch("aicage.runtime.extra_mounts.prompt_yes_no") as prompt_mock:
            mounts, updated = _build_extra_mounts(None, False, prefs)

        self.assertFalse(updated)
        self.assertEqual(1, len(mounts))
        prompt_mock.assert_not_called()
