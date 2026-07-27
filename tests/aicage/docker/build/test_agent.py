import tempfile
from pathlib import Path
from unittest import TestCase, mock

from aicage.docker.build import agent

from ..._run_config_fixtures import build_run_config as _build_run_config


class AgentBuildTests(TestCase):
    def test_run(self) -> None:
        run_config = _build_run_config(
            local_definition_dir=Path("/test-tmp/build/agents/claude")
        )
        reporter = mock.Mock()

        with tempfile.TemporaryDirectory() as tmp_dir:
            log_path = Path(tmp_dir) / "logs" / "build.log"
            with (
                mock.patch(
                    "aicage.docker.build.agent.find_packaged_path",
                    return_value=Path("/test-tmp/build/Dockerfile"),
                ),
                mock.patch(
                    "aicage.docker.build.agent._common.run_build_command",
                    return_value=0,
                ) as run_mock,
            ):
                agent.run(
                    run_config,
                    "ghcr.io/aicage/aicage-image-base:ubuntu",
                    "aicage:claude-ubuntu",
                    log_path,
                    reporter,
                )

        run_mock.assert_called_once()
        reporter.on_phase_started.assert_called_once()
        reporter.on_phase_finished.assert_called_once()
