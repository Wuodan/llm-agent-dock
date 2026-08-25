from unittest import TestCase, mock

from docker.errors import ImageNotFound

from aicage.docker.query import (
    _remove_image_ref,
    _remove_old_image_digest,
    cleanup_old_digest,
    get_local_image_id,
    get_local_repo_digest,
    get_local_repo_digest_for_repo,
    get_local_rootfs_layers,
    local_image_exists,
)
from aicage.docker.types import ImageRefRepository


class FakeImage:
    def __init__(
        self,
        repo_digests: object,
        rootfs: object | None = None,
        image_id: object = "sha256:local",
    ):
        self.attrs = {"Id": image_id, "RepoDigests": repo_digests}
        if rootfs is not None:
            self.attrs["RootFS"] = rootfs


class FakeImages:
    def __init__(self, image: FakeImage | None):
        self._image = image

    def get(self, image_ref: str) -> FakeImage:
        if self._image is None:
            raise ImageNotFound(image_ref)
        return self._image


class FakeClient:
    def __init__(self, image: FakeImage | None):
        self.images = FakeImages(image)


class LocalQueryTests(TestCase):
    @staticmethod
    def test_remove_image_ref_removes_image() -> None:
        with (
            mock.patch("aicage.docker.query.get_logger", return_value=mock.Mock()),
            mock.patch(
                "aicage.docker.execution.cli.run_docker_command",
                return_value=mock.Mock(returncode=0),
            ) as run_mock,
        ):
            _remove_image_ref("ghcr.io/aicage/aicage@sha256:old", "old image digest")
        run_mock.assert_called_once_with(
            ["docker", "image", "rm", "ghcr.io/aicage/aicage@sha256:old"],
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
                "aicage.docker.execution.cli.run_docker_command",
                return_value=mock.Mock(returncode=1),
            ),
        ):
            _remove_image_ref("ghcr.io/aicage/aicage@sha256:old", "old image digest")
        logger.warning.assert_called_once()

    def test_get_local_repo_digest(self) -> None:
        image = ImageRefRepository(
            image_ref="repo:tag", repository="ghcr.io/aicage/aicage"
        )
        with mock.patch(
            "aicage.docker.execution.client.get_docker_client",
            return_value=FakeClient(None),
        ):
            self.assertIsNone(get_local_repo_digest(image))

        with mock.patch(
            "aicage.docker.execution.client.get_docker_client",
            return_value=FakeClient(FakeImage(repo_digests={"bad": "data"})),
        ):
            self.assertIsNone(get_local_repo_digest(image))

        with mock.patch(
            "aicage.docker.execution.client.get_docker_client",
            return_value=FakeClient(FakeImage(repo_digests=["bad"])),
        ):
            self.assertIsNone(get_local_repo_digest(image))

        payload = ["ghcr.io/aicage/aicage@sha256:deadbeef", "other@sha256:skip"]
        with mock.patch(
            "aicage.docker.execution.client.get_docker_client",
            return_value=FakeClient(FakeImage(repo_digests=payload)),
        ):
            digest = get_local_repo_digest(image)
        self.assertEqual("sha256:deadbeef", digest)

    def test_get_local_repo_digest_for_repo(self) -> None:
        with mock.patch(
            "aicage.docker.execution.client.get_docker_client",
            return_value=FakeClient(None),
        ):
            self.assertIsNone(
                get_local_repo_digest_for_repo("repo:tag", "ghcr.io/aicage/aicage")
            )

        payload = ["ghcr.io/aicage/aicage@sha256:deadbeef", "other@sha256:skip"]
        with mock.patch(
            "aicage.docker.execution.client.get_docker_client",
            return_value=FakeClient(FakeImage(repo_digests=payload)),
        ):
            digest = get_local_repo_digest_for_repo("repo:tag", "ghcr.io/aicage/aicage")
        self.assertEqual("sha256:deadbeef", digest)

    def test_get_local_rootfs_layers(self) -> None:
        with mock.patch(
            "aicage.docker.execution.client.get_docker_client",
            return_value=FakeClient(None),
        ):
            self.assertIsNone(get_local_rootfs_layers("repo:tag"))

        with mock.patch(
            "aicage.docker.execution.client.get_docker_client",
            return_value=FakeClient(
                FakeImage(repo_digests=[], rootfs={"Layers": ["a", "b"]})
            ),
        ):
            layers = get_local_rootfs_layers("repo:tag")
        self.assertEqual(["a", "b"], layers)

    def test_local_image_exists_true_on_success(self) -> None:
        with mock.patch(
            "aicage.docker.execution.client.get_docker_client",
            return_value=FakeClient(FakeImage(repo_digests=[])),
        ):
            exists = local_image_exists("aicage:claude-ubuntu")
        self.assertTrue(exists)

    def test_local_image_exists_false_on_failure(self) -> None:
        with mock.patch(
            "aicage.docker.execution.client.get_docker_client",
            return_value=FakeClient(None),
        ):
            exists = local_image_exists("aicage:claude-ubuntu")
        self.assertFalse(exists)

    def test_get_local_image_id(self) -> None:
        with mock.patch(
            "aicage.docker.execution.client.get_docker_client",
            return_value=FakeClient(FakeImage(repo_digests=[], image_id="sha256:abc")),
        ):
            self.assertEqual("sha256:abc", get_local_image_id("repo:tag"))

        with mock.patch(
            "aicage.docker.execution.client.get_docker_client",
            return_value=FakeClient(FakeImage(repo_digests=[], image_id={})),
        ):
            self.assertIsNone(get_local_image_id("repo:tag"))

        with mock.patch(
            "aicage.docker.execution.client.get_docker_client",
            return_value=FakeClient(None),
        ):
            self.assertIsNone(get_local_image_id("repo:tag"))

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
            mock.patch(
                "aicage.docker.query.get_local_repo_digest_for_repo"
            ) as digest_mock,
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
