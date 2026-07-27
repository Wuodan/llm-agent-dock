import tempfile
from pathlib import Path
from unittest import TestCase, mock

from aicage.docker.build import custom_base


class CustomBaseBuildTests(TestCase):
    def test_run(self) -> None:
        reporter = mock.Mock()

        with tempfile.TemporaryDirectory() as tmp_dir:
            build_root = Path(tmp_dir)
            (build_root / "Dockerfile").write_text(
                "FROM ubuntu:latest\n", encoding="utf-8"
            )
            log_path = build_root / "logs" / "build.log"
            with mock.patch(
                "aicage.docker.build.custom_base._common.run_build_command",
                return_value=0,
            ) as run_mock:
                custom_base.run(
                    build_root,
                    "ubuntu:latest",
                    "aicage:base-sample",
                    log_path,
                    reporter,
                )

        run_mock.assert_called_once()
        reporter.on_phase_started.assert_called_once()
        reporter.on_phase_finished.assert_called_once()
