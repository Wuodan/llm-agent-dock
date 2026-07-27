import io
from pathlib import Path
from unittest import TestCase, mock

from aicage.constants import DEFAULT_EXTENDED_IMAGE_NAME
from aicage.docker.build import _dockerfile_extensions

from ..._run_config_fixtures import build_extended_run_config
from .test_extended import _extension


class DockerfileExtensionsBuildTests(TestCase):
    def test_build_dockerfile_extensions(self) -> None:
        run_config = build_extended_run_config()
        reporter = mock.Mock()
        extensions = [
            _extension("first", dockerfile_path=Path("/test-tmp/first/Dockerfile")),
            _extension("second", dockerfile_path=Path("/test-tmp/second/Dockerfile")),
        ]

        with (
            mock.patch(
                "aicage.docker.build._dockerfile_extensions.find_packaged_path",
                return_value=Path("/test-tmp/Dockerfile"),
            ),
            mock.patch(
                "aicage.docker.build._dockerfile_extensions.proxy_build_args_from_host",
                return_value=[],
            ),
            mock.patch(
                "aicage.docker.build._dockerfile_extensions._common.run_build_command",
                return_value=0,
            ) as run_mock,
        ):
            current_image_ref, intermediate_refs, returncode = (
                _dockerfile_extensions.build_dockerfile_extensions(
                    dockerfile_extensions=extensions,
                    run_config=run_config,
                    current_image_ref="ghcr.io/aicage/aicage:codex-ubuntu",
                    log_handle=io.StringIO(),
                    operation_reporter=reporter,
                )
            )

        self.assertEqual(run_config.selection.image_ref, current_image_ref)
        self.assertEqual(
            [f"{DEFAULT_EXTENDED_IMAGE_NAME}:tmp-codex-ubuntu-1-first"],
            intermediate_refs,
        )
        self.assertEqual(0, returncode)
        self.assertEqual(2, run_mock.call_count)
