import tempfile
from pathlib import Path
from unittest import TestCase, mock

from aicage.errors import CliError
from aicage.registry.local_build import _runner

from ._fixtures import build_run_config


class LocalBuildRunnerTests(TestCase):
    def test_run_build_invokes_docker(self) -> None:
        run_config = build_run_config()
        with tempfile.TemporaryDirectory() as tmp_dir:
            log_path = Path(tmp_dir) / "logs" / "build.log"
            with (
                mock.patch(
                    "aicage.registry.local_build._runner.find_packaged_path",
                    return_value=Path("/tmp/build/Dockerfile"),
                ),
                mock.patch(
                    "aicage.registry.local_build._runner.subprocess.run",
                    return_value=mock.Mock(returncode=0),
                ) as run_mock,
            ):
                _runner.run_build(
                    run_config=run_config,
                    base_image_ref="ghcr.io/aicage/aicage-image-base:ubuntu",
                    log_path=log_path,
                )

        run_mock.assert_called_once()
        command = run_mock.call_args.args[0]
        self.assertEqual(
            [
                "docker",
                "build",
                "--no-cache",
                "--build-arg",
                "BASE_IMAGE=ghcr.io/aicage/aicage-image-base:ubuntu",
                "--build-arg",
                "AGENT=claude",
                "--tag",
                "aicage:claude-ubuntu",
                "/tmp/build",
            ],
            command,
        )

    def test_run_build_raises_on_failure(self) -> None:
        run_config = build_run_config()
        with tempfile.TemporaryDirectory() as tmp_dir:
            log_path = Path(tmp_dir) / "logs" / "build.log"
            with (
                mock.patch(
                    "aicage.registry.local_build._runner.find_packaged_path",
                    return_value=Path("/tmp/build/Dockerfile"),
                ),
                mock.patch(
                    "aicage.registry.local_build._runner.subprocess.run",
                    return_value=mock.Mock(returncode=1),
                ),
                self.assertRaises(CliError),
            ):
                _runner.run_build(
                    run_config=run_config,
                    base_image_ref="ghcr.io/aicage/aicage-image-base:ubuntu",
                    log_path=log_path,
                )

    def test_local_image_exists_true_on_success(self) -> None:
        with mock.patch(
            "aicage.registry.local_build._runner.subprocess.run",
            return_value=mock.Mock(returncode=0),
        ):
            exists = _runner.local_image_exists("aicage:claude-ubuntu")
        self.assertTrue(exists)

    def test_local_image_exists_false_on_failure(self) -> None:
        with mock.patch(
            "aicage.registry.local_build._runner.subprocess.run",
            return_value=mock.Mock(returncode=1),
        ):
            exists = _runner.local_image_exists("aicage:claude-ubuntu")
        self.assertFalse(exists)
