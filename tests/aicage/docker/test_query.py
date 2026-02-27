import json
import subprocess
from unittest import TestCase, mock

from aicage.docker.query import (
    _remove_image_ref,
    _remove_old_image_digest,
    cleanup_old_digest,
    get_local_repo_digest,
    get_local_repo_digest_for_repo,
    get_local_rootfs_layers,
    local_image_exists,
)
from aicage.docker.types import ImageRefRepository


def _inspect_result(image: dict[str, object] | None) -> subprocess.CompletedProcess[str]:
    if image is None:
        return subprocess.CompletedProcess(["docker", "image", "inspect"], 1, stdout="", stderr="missing")
    return subprocess.CompletedProcess(
        ["docker", "image", "inspect"],
        0,
        stdout=json.dumps([image]),
        stderr="",
    )


class LocalQueryTests(TestCase):
    def setUp(self) -> None:
        runtime_patcher = mock.patch("aicage.docker.query.get_container_runtime", return_value="podman")
        self._runtime_mock = runtime_patcher.start()
        self.addCleanup(runtime_patcher.stop)

    @staticmethod
    def test_remove_image_ref_removes_image() -> None:
        with (
            mock.patch("aicage.docker.query.get_logger", return_value=mock.Mock()),
            mock.patch(
                "aicage.docker.query.run_docker_command",
                return_value=mock.Mock(returncode=0),
            ) as run_mock,
        ):
            _remove_image_ref("ghcr.io/aicage/aicage@sha256:old", "old image digest")
        run_mock.assert_called_once_with(
            ["podman", "image", "rm", "ghcr.io/aicage/aicage@sha256:old"],
            check=False,
            stdout=mock.ANY,
            stderr=mock.ANY,
        )

    @staticmethod
    def test_remove_image_ref_ignores_docker_errors() -> None:
        logger = mock.Mock()
        with (
            mock.patch("aicage.docker.query.get_logger", return_value=logger),
            mock.patch(
                "aicage.docker.query.run_docker_command",
                return_value=mock.Mock(returncode=1),
            ),
        ):
            _remove_image_ref("ghcr.io/aicage/aicage@sha256:old", "old image digest")
        logger.warning.assert_called_once()

    def test_get_local_repo_digest(self) -> None:
        image = ImageRefRepository(image_ref="repo:tag", repository="ghcr.io/aicage/aicage")
        with mock.patch(
            "aicage.docker.query.run_docker_command_capture",
            return_value=_inspect_result(None),
        ):
            self.assertIsNone(get_local_repo_digest(image))

        with mock.patch(
            "aicage.docker.query.run_docker_command_capture",
            return_value=_inspect_result({"RepoDigests": {"bad": "data"}}),
        ):
            self.assertIsNone(get_local_repo_digest(image))

        with mock.patch(
            "aicage.docker.query.run_docker_command_capture",
            return_value=_inspect_result({"RepoDigests": ["bad"]}),
        ):
            self.assertIsNone(get_local_repo_digest(image))

        payload = ["ghcr.io/aicage/aicage@sha256:deadbeef", "other@sha256:skip"]
        with mock.patch(
            "aicage.docker.query.run_docker_command_capture",
            return_value=_inspect_result({"RepoDigests": payload}),
        ):
            digest = get_local_repo_digest(image)
        self.assertEqual("sha256:deadbeef", digest)

    def test_get_local_repo_digest_for_repo(self) -> None:
        with mock.patch(
            "aicage.docker.query.run_docker_command_capture",
            return_value=_inspect_result(None),
        ):
            self.assertIsNone(get_local_repo_digest_for_repo("repo:tag", "ghcr.io/aicage/aicage"))

        payload = ["ghcr.io/aicage/aicage@sha256:deadbeef", "other@sha256:skip"]
        with mock.patch(
            "aicage.docker.query.run_docker_command_capture",
            return_value=_inspect_result({"RepoDigests": payload}),
        ):
            digest = get_local_repo_digest_for_repo("repo:tag", "ghcr.io/aicage/aicage")
        self.assertEqual("sha256:deadbeef", digest)

    def test_get_local_rootfs_layers(self) -> None:
        with mock.patch(
            "aicage.docker.query.run_docker_command_capture",
            return_value=_inspect_result(None),
        ):
            self.assertIsNone(get_local_rootfs_layers("repo:tag"))

        with mock.patch(
            "aicage.docker.query.run_docker_command_capture",
            return_value=_inspect_result({"RepoDigests": [], "RootFS": {"Layers": ["a", "b"]}}),
        ):
            layers = get_local_rootfs_layers("repo:tag")
        self.assertEqual(["a", "b"], layers)

    def test_local_image_exists_true_on_success(self) -> None:
        with mock.patch(
            "aicage.docker.query.run_docker_command_capture",
            return_value=_inspect_result({"RepoDigests": []}),
        ):
            exists = local_image_exists("aicage:claude-ubuntu")
        self.assertTrue(exists)

    def test_local_image_exists_false_on_failure(self) -> None:
        with mock.patch(
            "aicage.docker.query.run_docker_command_capture",
            return_value=_inspect_result(None),
        ):
            exists = local_image_exists("aicage:claude-ubuntu")
        self.assertFalse(exists)

    def test_local_image_exists_false_on_invalid_json(self) -> None:
        with mock.patch(
            "aicage.docker.query.run_docker_command_capture",
            return_value=subprocess.CompletedProcess(["docker", "image", "inspect"], 0, stdout="{", stderr=""),
        ):
            exists = local_image_exists("aicage:claude-ubuntu")
        self.assertFalse(exists)

    @staticmethod
    def test_remove_old_image_digest_removes_image() -> None:
        with mock.patch("aicage.docker.query._remove_image_ref") as remove_mock:
            _remove_old_image_digest(
                repository="ghcr.io/aicage/aicage",
                old_digest="sha256:old",
            )
        remove_mock.assert_called_once_with(
            "ghcr.io/aicage/aicage@sha256:old",
            "old image digest",
        )

    @staticmethod
    def test_remove_old_image_digest_ignores_docker_errors() -> None:
        with mock.patch("aicage.docker.query._remove_image_ref") as remove_mock:
            _remove_old_image_digest(
                repository="ghcr.io/aicage/aicage",
                old_digest="sha256:old",
            )
        remove_mock.assert_called_once_with(
            "ghcr.io/aicage/aicage@sha256:old",
            "old image digest",
        )

    @staticmethod
    def test_cleanup_old_digest_skips_without_local() -> None:
        logger = mock.Mock()
        with (
            mock.patch("aicage.docker.query.get_logger", return_value=logger),
            mock.patch("aicage.docker.query.get_local_repo_digest_for_repo") as digest_mock,
        ):
            cleanup_old_digest(
                repository="ghcr.io/aicage/aicage",
                local_digest=None,
                image_ref="repo:tag",
            )
        digest_mock.assert_not_called()

    @staticmethod
    def test_cleanup_old_digest_skips_when_unchanged() -> None:
        logger = mock.Mock()
        with (
            mock.patch("aicage.docker.query.get_logger", return_value=logger),
            mock.patch(
                "aicage.docker.query.get_local_repo_digest_for_repo",
                return_value="sha256:old",
            ),
            mock.patch("aicage.docker.query._remove_old_image_digest") as remove_mock,
        ):
            cleanup_old_digest(
                repository="ghcr.io/aicage/aicage",
                local_digest="sha256:old",
                image_ref="repo:tag",
            )
        remove_mock.assert_not_called()

    @staticmethod
    def test_cleanup_old_digest_removes_when_updated() -> None:
        logger = mock.Mock()
        with (
            mock.patch("aicage.docker.query.get_logger", return_value=logger),
            mock.patch(
                "aicage.docker.query.get_local_repo_digest_for_repo",
                return_value="sha256:new",
            ),
            mock.patch("aicage.docker.query._remove_old_image_digest") as remove_mock,
        ):
            cleanup_old_digest(
                repository="ghcr.io/aicage/aicage",
                local_digest="sha256:old",
                image_ref="repo:tag",
            )
        remove_mock.assert_called_once_with("ghcr.io/aicage/aicage", "sha256:old")
