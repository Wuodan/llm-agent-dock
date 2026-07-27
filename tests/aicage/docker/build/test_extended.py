import tempfile
from pathlib import Path
from subprocess import CompletedProcess
from unittest import TestCase, mock

from aicage.config.extensions.loader import ExtensionMetadata
from aicage.docker.build import extended

from ..._run_config_fixtures import build_extended_run_config


class ExtendedBuildTests(TestCase):
    def test_run(self) -> None:
        run_config = build_extended_run_config()
        reporter = mock.Mock()

        with tempfile.TemporaryDirectory() as tmp_dir:
            log_path = Path(tmp_dir) / "build.log"
            with (
                mock.patch(
                    "aicage.docker.build.extended.build_shell_extensions",
                    return_value=0,
                ) as shell_build_mock,
                mock.patch(
                    "aicage.docker.build.extended.build_dockerfile_extensions",
                ) as dockerfile_build_mock,
                mock.patch(
                    "aicage.docker.build.extended._cleanup_intermediate_images"
                ) as cleanup_mock,
            ):
                extended.run(
                    run_config,
                    "ghcr.io/aicage/aicage:codex-ubuntu",
                    [_extension("extra")],
                    log_path,
                    reporter,
                )

        shell_build_mock.assert_called_once()
        dockerfile_build_mock.assert_not_called()
        cleanup_mock.assert_called_once_with([])
        reporter.on_phase_started.assert_called_once()
        reporter.on_phase_finished.assert_called_once()

    def test_cleanup_intermediate_images(self) -> None:
        logger = mock.Mock()

        with (
            mock.patch(
                "aicage.docker.build.extended.get_logger",
                return_value=logger,
            ),
            mock.patch(
                "aicage.docker.build.extended._docker_cli.run_docker_command",
                return_value=CompletedProcess([], 1),
            ),
        ):
            extended._cleanup_intermediate_images(["aicage:tmp"])

        logger.warning.assert_called_once()


def _extension(
    extension_id: str,
    dockerfile_path: Path | None = None,
) -> ExtensionMetadata:
    return ExtensionMetadata(
        extension_id=extension_id,
        name=extension_id,
        description="desc",
        shares=[],
        directory=Path("/test-tmp/ext"),
        scripts_dir=Path("/test-tmp/ext/scripts"),
        dockerfile_path=dockerfile_path,
    )
