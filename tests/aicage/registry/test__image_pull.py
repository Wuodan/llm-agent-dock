import io
import json
import tempfile
from pathlib import Path
from unittest import TestCase, mock

from docker.errors import DockerException

from aicage.constants import IMAGE_REGISTRY, IMAGE_REPOSITORY
from aicage.registry import _image_pull as image_pull


class FakeDockerApi:
    def __init__(self, events: list[object], exc: Exception | None = None) -> None:
        self._events = events
        self._exc = exc
        self.calls: list[tuple[str, bool, bool]] = []

    def pull(self, image_ref: str, stream: bool, decode: bool) -> list[object]:
        self.calls.append((image_ref, stream, decode))
        if self._exc is not None:
            raise self._exc
        return list(self._events)


class FakeDockerClient:
    def __init__(self, api: FakeDockerApi) -> None:
        self.api = api
        self.closed = False

    def close(self) -> None:
        self.closed = True


class DockerInvocationTests(TestCase):
    def test_pull_image_success_writes_log(self) -> None:
        image_ref = "repo:tag"
        reporter = mock.Mock()
        api = FakeDockerApi(
            events=[
                {"status": "Pulling from org/repo", "id": "repo:tag"},
                {"status": "Downloading", "id": "abc123"},
            ]
        )
        client = FakeDockerClient(api)
        with tempfile.TemporaryDirectory() as tmp_dir:
            log_path = Path(tmp_dir) / "pull.log"
            with (
                mock.patch(
                    "aicage.registry._pull_decision.get_local_repo_digest",
                    return_value=None,
                ),
                mock.patch(
                    "aicage.registry._image_pull.get_local_repo_digest_for_repo",
                    side_effect=["sha256:old", "sha256:new"],
                ),
                mock.patch(
                    "aicage.registry._pull_decision.get_remote_digest"
                ) as remote_mock,
                mock.patch(
                    "aicage.registry._image_pull.resolve_verified_digest",
                    return_value="repo@sha256:verified",
                ) as verify_mock,
                mock.patch(
                    "aicage.docker.execution.client.get_docker_pull_client",
                    return_value=client,
                ),
                mock.patch(
                    "aicage.registry._image_pull.cleanup_old_digest"
                ) as cleanup_mock,
                mock.patch(
                    "aicage.registry._image_pull.pull_log_path", return_value=log_path
                ),
                mock.patch("sys.stdout", new_callable=io.StringIO) as stdout,
            ):
                image_pull.pull_image(
                    image_ref,
                    update_approved=False,
                    reporter=reporter,
                )
            remote_mock.assert_not_called()
            verify_mock.assert_called_once_with(image_ref, reporter=reporter)
            cleanup_mock.assert_called_once_with(
                f"{IMAGE_REGISTRY}/{IMAGE_REPOSITORY}",
                "sha256:old",
                image_ref,
            )
            self.assertEqual("", stdout.getvalue())
            log_lines = log_path.read_text(encoding="utf-8").splitlines()
            self.assertEqual(2, len(log_lines))
            self.assertEqual(
                {"status": "Pulling from org/repo", "id": "repo:tag"},
                json.loads(log_lines[0]),
            )
            self.assertEqual(
                {"status": "Downloading", "id": "abc123"},
                json.loads(log_lines[1]),
            )
            self.assertEqual([("repo:tag", True, True)], api.calls)
            reporter.on_phase_started.assert_has_calls(
                [
                    mock.call(
                        "pull",
                        "Preparing image repo:tag",
                        log_path,
                    ),
                    mock.call(
                        "pull",
                        "Pulling image repo:tag",
                        log_path,
                    ),
                ]
            )
            reporter.on_phase_progress.assert_any_call(
                "pull",
                "Resolving digest and verifying image signature",
                None,
                None,
            )

    def test_pull_image_raises_on_sdk_error(self) -> None:
        image_ref = "repo:tag"
        reporter = mock.Mock()
        api = FakeDockerApi(events=[], exc=DockerException("network down"))
        client = FakeDockerClient(api)
        with tempfile.TemporaryDirectory() as tmp_dir:
            log_path = Path(tmp_dir) / "pull.log"
            with (
                mock.patch(
                    "aicage.registry._pull_decision.get_local_repo_digest",
                    return_value=None,
                ),
                mock.patch(
                    "aicage.registry._image_pull.get_local_repo_digest_for_repo",
                    side_effect=["sha256:old", "sha256:new"],
                ),
                mock.patch(
                    "aicage.registry._pull_decision.get_remote_digest"
                ) as remote_mock,
                mock.patch(
                    "aicage.registry._image_pull.resolve_verified_digest",
                    return_value="repo@sha256:verified",
                ) as verify_mock,
                mock.patch(
                    "aicage.docker.execution.client.get_docker_pull_client",
                    return_value=client,
                ),
                mock.patch(
                    "aicage.registry._image_pull.cleanup_old_digest"
                ) as cleanup_mock,
                mock.patch(
                    "aicage.registry._image_pull.pull_log_path", return_value=log_path
                ),
                mock.patch("sys.stdout", new_callable=io.StringIO),
            ):
                with self.assertRaises(DockerException):
                    image_pull.pull_image(
                        image_ref,
                        update_approved=False,
                        reporter=reporter,
                    )
            remote_mock.assert_not_called()
            verify_mock.assert_called_once_with(image_ref, reporter=reporter)
            cleanup_mock.assert_not_called()

    def test_pull_image_skips_when_up_to_date(self) -> None:
        image_ref = "repo:tag"
        reporter = mock.Mock()
        with tempfile.TemporaryDirectory() as tmp_dir:
            log_path = Path(tmp_dir) / "pull.log"
            with (
                mock.patch(
                    "aicage.registry._pull_decision.get_local_repo_digest",
                    return_value="same",
                ),
                mock.patch(
                    "aicage.registry._image_pull.get_local_repo_digest_for_repo"
                ) as local_repo_mock,
                mock.patch(
                    "aicage.registry._pull_decision.get_remote_digest",
                    return_value="same",
                ),
                mock.patch(
                    "aicage.registry._image_pull.resolve_verified_digest"
                ) as verify_mock,
                mock.patch(
                    "aicage.docker.execution.client.get_docker_pull_client"
                ) as client_mock,
                mock.patch(
                    "aicage.registry._image_pull.cleanup_old_digest"
                ) as cleanup_mock,
                mock.patch(
                    "aicage.registry._image_pull.pull_log_path", return_value=log_path
                ),
                mock.patch("sys.stdout", new_callable=io.StringIO) as stdout,
            ):
                image_pull.pull_image(
                    image_ref,
                    update_approved=False,
                    reporter=reporter,
                )
            client_mock.assert_not_called()
            verify_mock.assert_not_called()
            local_repo_mock.assert_not_called()
            cleanup_mock.assert_not_called()
            self.assertEqual("", stdout.getvalue())

    def test_pull_image_skips_when_remote_unknown(self) -> None:
        image_ref = "repo:tag"
        reporter = mock.Mock()
        with tempfile.TemporaryDirectory() as tmp_dir:
            log_path = Path(tmp_dir) / "pull.log"
            with (
                mock.patch(
                    "aicage.registry._pull_decision.get_local_repo_digest",
                    return_value="local",
                ),
                mock.patch(
                    "aicage.registry._image_pull.get_local_repo_digest_for_repo"
                ) as local_repo_mock,
                mock.patch(
                    "aicage.registry._pull_decision.get_remote_digest",
                    return_value=None,
                ),
                mock.patch(
                    "aicage.registry._image_pull.resolve_verified_digest"
                ) as verify_mock,
                mock.patch(
                    "aicage.docker.execution.client.get_docker_pull_client"
                ) as client_mock,
                mock.patch(
                    "aicage.registry._image_pull.cleanup_old_digest"
                ) as cleanup_mock,
                mock.patch(
                    "aicage.registry._image_pull.pull_log_path", return_value=log_path
                ),
                mock.patch("sys.stdout", new_callable=io.StringIO) as stdout,
            ):
                image_pull.pull_image(
                    image_ref,
                    update_approved=False,
                    reporter=reporter,
                )
            client_mock.assert_not_called()
            verify_mock.assert_not_called()
            local_repo_mock.assert_not_called()
            cleanup_mock.assert_not_called()
            self.assertEqual("", stdout.getvalue())
