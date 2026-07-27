import tempfile
from pathlib import Path
from unittest import TestCase, mock

from aicage.constants import VERSION_CHECK_IMAGE
from aicage.registry.agent_build.agent_version import _images


class AgentVersionImagesTests(TestCase):
    @staticmethod
    def test_ensure_version_check_image_pulls_when_local_missing() -> None:
        image_ref = VERSION_CHECK_IMAGE
        repository, _, _tag = image_ref.partition(":")
        reporter = mock.Mock()
        with tempfile.TemporaryDirectory() as tmp_dir:
            log_path = Path(tmp_dir) / "pull.log"
            with (
                mock.patch(
                    "aicage.registry.agent_build.agent_version._images.get_local_repo_digest_for_repo",
                    return_value=None,
                ) as local_mock,
                mock.patch(
                    "aicage.registry.agent_build.agent_version._images.get_remote_digest"
                ) as remote_mock,
                mock.patch(
                    "aicage.registry.agent_build.agent_version._images.resolve_verified_digest",
                    return_value="ghcr.io/aicage/aicage-image-util@sha256:verified",
                ) as verify_mock,
                mock.patch(
                    "aicage.registry.agent_build.agent_version._images.run_pull"
                ) as pull_mock,
                mock.patch(
                    "aicage.registry.agent_build.agent_version._images.cleanup_old_digest"
                ) as cleanup_mock,
                mock.patch(
                    "aicage.registry.agent_build.agent_version._images.pull_log_path",
                    return_value=log_path,
                ),
            ):
                _images.ensure_version_check_image(
                    image_ref=image_ref, reporter=reporter
                )
        local_mock.assert_called_once()
        remote_mock.assert_not_called()
        verify_mock.assert_called_once_with(image_ref, reporter=reporter)
        pull_mock.assert_called_once_with(image_ref, log_path, reporter=reporter)
        cleanup_mock.assert_called_once_with(
            repository,
            None,
            image_ref,
        )

    @staticmethod
    def test_ensure_version_check_image_cleans_old_digest_after_pull() -> None:
        image_ref = VERSION_CHECK_IMAGE
        repository, _, _tag = image_ref.partition(":")
        reporter = mock.Mock()
        with tempfile.TemporaryDirectory() as tmp_dir:
            log_path = Path(tmp_dir) / "pull.log"
            with (
                mock.patch(
                    "aicage.registry.agent_build.agent_version._images.get_local_repo_digest_for_repo",
                    side_effect=["sha256:old", "sha256:new"],
                ),
                mock.patch(
                    "aicage.registry.agent_build.agent_version._images.get_remote_digest",
                    return_value="sha256:new",
                ),
                mock.patch(
                    "aicage.registry.agent_build.agent_version._images.resolve_verified_digest",
                    return_value="ghcr.io/aicage/aicage-image-util@sha256:new",
                ),
                mock.patch(
                    "aicage.registry.agent_build.agent_version._images.run_pull"
                ) as pull_mock,
                mock.patch(
                    "aicage.registry.agent_build.agent_version._images.cleanup_old_digest"
                ) as cleanup_mock,
                mock.patch(
                    "aicage.registry.agent_build.agent_version._images.pull_log_path",
                    return_value=log_path,
                ),
            ):
                _images.ensure_version_check_image(
                    image_ref=image_ref, reporter=reporter
                )
        pull_mock.assert_called_once_with(image_ref, log_path, reporter=reporter)
        cleanup_mock.assert_called_once_with(
            repository,
            "sha256:old",
            image_ref,
        )

    @staticmethod
    def test_ensure_version_check_image_skips_pull_when_remote_unknown() -> None:
        image_ref = VERSION_CHECK_IMAGE
        reporter = mock.Mock()
        with tempfile.TemporaryDirectory() as tmp_dir:
            log_path = Path(tmp_dir) / "pull.log"
            with (
                mock.patch(
                    "aicage.registry.agent_build.agent_version._images.get_local_repo_digest_for_repo",
                    return_value="sha256:local",
                ),
                mock.patch(
                    "aicage.registry.agent_build.agent_version._images.get_remote_digest",
                    return_value=None,
                ) as remote_mock,
                mock.patch(
                    "aicage.registry.agent_build.agent_version._images.resolve_verified_digest"
                ) as verify_mock,
                mock.patch(
                    "aicage.registry.agent_build.agent_version._images.run_pull"
                ) as pull_mock,
                mock.patch(
                    "aicage.registry.agent_build.agent_version._images.cleanup_old_digest"
                ) as cleanup_mock,
                mock.patch(
                    "aicage.registry.agent_build.agent_version._images.pull_log_path",
                    return_value=log_path,
                ),
            ):
                _images.ensure_version_check_image(
                    image_ref=image_ref, reporter=reporter
                )
        remote_mock.assert_called_once()
        verify_mock.assert_not_called()
        pull_mock.assert_not_called()
        cleanup_mock.assert_not_called()
