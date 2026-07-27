import tempfile
from pathlib import Path
from unittest import TestCase, mock

from aicage.registry._errors import RegistryError
from aicage.registry.agent_build import _digest


class LocalBuildDigestTests(TestCase):
    def test_resolve_base_digest_verify_failure_uses_local_digest(self) -> None:
        reporter = mock.Mock()
        with (
            mock.patch(
                "aicage.registry.agent_build._digest.get_local_repo_digest_for_repo",
                return_value="sha256:local",
            ),
            mock.patch(
                "aicage.registry.agent_build._digest.resolve_verified_digest",
                side_effect=RegistryError("offline"),
            ),
            mock.patch("aicage.registry.agent_build._digest.run_pull") as run_mock,
            mock.patch(
                "aicage.registry.agent_build._digest.cleanup_old_digest"
            ) as cleanup_mock,
        ):
            digest = _digest.resolve_base_digest(
                base_image_ref="ghcr.io/aicage/aicage-image-base:ubuntu",
                base_repository="ghcr.io/aicage/aicage-image-base",
                reporter=reporter,
            )
        self.assertEqual("ghcr.io/aicage/aicage-image-base@sha256:local", digest)
        run_mock.assert_not_called()
        cleanup_mock.assert_not_called()

    def test_resolve_base_digest_verify_failure_without_local_raises(self) -> None:
        reporter = mock.Mock()
        with (
            mock.patch(
                "aicage.registry.agent_build._digest.get_local_repo_digest_for_repo",
                return_value=None,
            ),
            mock.patch(
                "aicage.registry.agent_build._digest.resolve_verified_digest",
                side_effect=RegistryError("offline"),
            ),
            mock.patch("aicage.registry.agent_build._digest.run_pull") as run_mock,
        ):
            with self.assertRaises(RegistryError) as exc:
                _digest.resolve_base_digest(
                    base_image_ref="ghcr.io/aicage/aicage-image-base:ubuntu",
                    base_repository="ghcr.io/aicage/aicage-image-base",
                    reporter=reporter,
                )
        self.assertIn("offline", str(exc.exception))
        run_mock.assert_not_called()

    def test_resolve_base_digest_skips_pull_when_local_matches_remote(self) -> None:
        reporter = mock.Mock()
        with (
            mock.patch(
                "aicage.registry.agent_build._digest.get_local_repo_digest_for_repo",
                return_value="sha256:local",
            ),
            mock.patch(
                "aicage.registry.agent_build._digest.resolve_verified_digest",
                return_value="ghcr.io/aicage/aicage-image-base@sha256:local",
            ),
            mock.patch("aicage.registry.agent_build._digest.run_pull") as run_mock,
            mock.patch(
                "aicage.registry.agent_build._digest.cleanup_old_digest"
            ) as cleanup_mock,
        ):
            digest = _digest.resolve_base_digest(
                base_image_ref="ghcr.io/aicage/aicage-image-base:ubuntu",
                base_repository="ghcr.io/aicage/aicage-image-base",
                reporter=reporter,
            )
        self.assertEqual("ghcr.io/aicage/aicage-image-base@sha256:local", digest)
        run_mock.assert_not_called()
        cleanup_mock.assert_not_called()

    def test_resolve_base_digest_pull_failure_uses_local_digest(self) -> None:
        reporter = mock.Mock()
        with tempfile.TemporaryDirectory() as tmp_dir:
            with (
                mock.patch(
                    "aicage.registry.agent_build._digest.get_local_repo_digest_for_repo",
                    return_value="sha256:local",
                ),
                mock.patch(
                    "aicage.registry.agent_build._digest.resolve_verified_digest",
                    return_value="ghcr.io/aicage/aicage-image-base@sha256:remote",
                ),
                mock.patch(
                    "aicage.registry.agent_build._digest.run_pull",
                    side_effect=RegistryError("docker pull failed"),
                ),
                mock.patch(
                    "aicage.registry.agent_build._digest.cleanup_old_digest"
                ) as cleanup_mock,
                mock.patch(
                    "aicage.registry.agent_build._digest.pull_log_path",
                    return_value=Path(tmp_dir),
                ),
            ):
                digest = _digest.resolve_base_digest(
                    base_image_ref="ghcr.io/aicage/aicage-image-base:ubuntu",
                    base_repository="ghcr.io/aicage/aicage-image-base",
                    reporter=reporter,
                )
            self.assertEqual("ghcr.io/aicage/aicage-image-base@sha256:local", digest)
            cleanup_mock.assert_not_called()

    def test_resolve_base_digest_pull_failure_without_local_raises(self) -> None:
        reporter = mock.Mock()
        with tempfile.TemporaryDirectory() as tmp_dir:
            with (
                mock.patch(
                    "aicage.registry.agent_build._digest.get_local_repo_digest_for_repo",
                    return_value=None,
                ),
                mock.patch(
                    "aicage.registry.agent_build._digest.resolve_verified_digest",
                    return_value="ghcr.io/aicage/aicage-image-base@sha256:remote",
                ),
                mock.patch(
                    "aicage.registry.agent_build._digest.run_pull",
                    side_effect=RegistryError("docker pull failed"),
                ),
                mock.patch(
                    "aicage.registry.agent_build._digest.cleanup_old_digest"
                ) as cleanup_mock,
                mock.patch(
                    "aicage.registry.agent_build._digest.pull_log_path",
                    return_value=Path(tmp_dir),
                ),
            ):
                with self.assertRaises(RegistryError) as exc:
                    _digest.resolve_base_digest(
                        base_image_ref="ghcr.io/aicage/aicage-image-base:ubuntu",
                        base_repository="ghcr.io/aicage/aicage-image-base",
                        reporter=reporter,
                    )
            self.assertIn("docker pull failed", str(exc.exception))
            cleanup_mock.assert_not_called()

    def test_resolve_base_digest_pull_success_updates_digest(self) -> None:
        reporter = mock.Mock()
        with tempfile.TemporaryDirectory() as tmp_dir:
            with (
                mock.patch(
                    "aicage.registry.agent_build._digest.get_local_repo_digest_for_repo",
                    side_effect=["sha256:old", "sha256:remote"],
                ),
                mock.patch(
                    "aicage.registry.agent_build._digest.resolve_verified_digest",
                    return_value="ghcr.io/aicage/aicage-image-base@sha256:remote",
                ),
                mock.patch(
                    "aicage.registry.agent_build._digest.run_pull",
                    return_value=None,
                ),
                mock.patch(
                    "aicage.registry.agent_build._digest.cleanup_old_digest"
                ) as cleanup_mock,
                mock.patch(
                    "aicage.registry.agent_build._digest.pull_log_path",
                    return_value=Path(tmp_dir),
                ),
            ):
                digest = _digest.resolve_base_digest(
                    base_image_ref="ghcr.io/aicage/aicage-image-base:ubuntu",
                    base_repository="ghcr.io/aicage/aicage-image-base",
                    reporter=reporter,
                )
            self.assertEqual("ghcr.io/aicage/aicage-image-base@sha256:remote", digest)
            cleanup_mock.assert_called_once_with(
                "ghcr.io/aicage/aicage-image-base",
                "sha256:old",
                "ghcr.io/aicage/aicage-image-base:ubuntu",
            )
