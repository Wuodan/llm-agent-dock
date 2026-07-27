import io
import subprocess
import tempfile
from pathlib import Path
from subprocess import CompletedProcess
from unittest import TestCase, mock

from aicage.registry.agent_build.agent_version import _command


class AgentVersionCommandTests(TestCase):
    def test_run_host_uses_bash_for_script(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            script_path = Path(tmp_dir) / "version.sh"
            script_path.write_text("echo 1.2.3\n", encoding="utf-8")
            with (
                mock.patch(
                    "aicage.registry.agent_build.agent_version._command.os.access",
                    return_value=False,
                ),
                mock.patch(
                    "aicage.registry.agent_build.agent_version._command.subprocess.run",
                    return_value=CompletedProcess([], 0, stdout="1.2.3\n", stderr=""),
                ) as run_mock,
                mock.patch(
                    "aicage.registry.agent_build.agent_version._command.shutil.which",
                    return_value="/bin/bash",
                ),
                mock.patch("sys.stderr", new_callable=io.StringIO),
            ):
                result = _command.run_host(script_path)
            run_mock.assert_called_once_with(
                ["/bin/bash", str(script_path)],
                check=False,
                capture_output=True,
                text=True,
                timeout=15.0,
            )
            self.assertTrue(result.success)
            self.assertEqual("1.2.3", result.output)

    def test_run_host_returns_error_on_exception(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            script_path = Path(tmp_dir) / "version.sh"
            script_path.write_text("echo 1.2.3\n", encoding="utf-8")
            with (
                mock.patch(
                    "aicage.registry.agent_build.agent_version._command.shutil.which",
                    return_value="/bin/bash",
                ),
                mock.patch(
                    "aicage.registry.agent_build.agent_version._command.subprocess.run",
                    side_effect=FileNotFoundError("missing"),
                ),
            ):
                result = _command.run_host(script_path)
            self.assertFalse(result.success)
            self.assertEqual("missing", result.error)

    def test_run_host_returns_timeout_error(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            script_path = Path(tmp_dir) / "version.sh"
            script_path.write_text("echo 1.2.3\n", encoding="utf-8")
            with (
                mock.patch(
                    "aicage.registry.agent_build.agent_version._command.shutil.which",
                    return_value="/bin/bash",
                ),
                mock.patch(
                    "aicage.registry.agent_build.agent_version._command.subprocess.run",
                    side_effect=subprocess.TimeoutExpired(cmd=["/bin/bash"], timeout=1),
                ),
            ):
                result = _command.run_host(script_path)
            self.assertFalse(result.success)
            self.assertEqual("Version check timed out.", result.error)

    def test_run_host_returns_error_when_bash_missing(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            script_path = Path(tmp_dir) / "version.sh"
            script_path.write_text("echo 1.2.3\n", encoding="utf-8")
            with (
                mock.patch(
                    "aicage.registry.agent_build.agent_version._command.shutil.which",
                    return_value=None,
                ),
                mock.patch(
                    "aicage.registry.agent_build.agent_version._command.subprocess.run"
                ) as run_mock,
            ):
                result = _command.run_host(script_path)
            self.assertFalse(result.success)
            self.assertEqual("bash is not available on the host.", result.error)
            run_mock.assert_not_called()

    def test_run_version_check_image_returns_error_on_failure(self) -> None:
        reporter = mock.Mock()
        with tempfile.TemporaryDirectory() as tmp_dir:
            definition_dir = Path(tmp_dir)
            with (
                mock.patch(
                    "aicage.registry.agent_build.agent_version._command.ensure_version_check_image"
                ) as ensure_mock,
                mock.patch(
                    "aicage.registry.agent_build.agent_version._command.run_builder_version_check",
                    return_value=CompletedProcess([], 1, stdout="", stderr="failed"),
                ),
            ):
                result = _command.run_version_check_image(
                    "ghcr.io/aicage/aicage-image-util:agent-version",
                    definition_dir,
                    reporter=reporter,
                )
            self.assertFalse(result.success)
            self.assertEqual("failed", result.error)
            ensure_mock.assert_called_once_with(
                "ghcr.io/aicage/aicage-image-util:agent-version",
                reporter=reporter,
            )

    def test_run_version_check_image_returns_error_on_prepare_exception(self) -> None:
        reporter = mock.Mock()
        with tempfile.TemporaryDirectory() as tmp_dir:
            definition_dir = Path(tmp_dir)
            with (
                mock.patch(
                    "aicage.registry.agent_build.agent_version._command.ensure_version_check_image",
                    side_effect=RuntimeError("offline"),
                ),
                mock.patch(
                    "aicage.registry.agent_build.agent_version._command.run_builder_version_check"
                ) as run_mock,
            ):
                result = _command.run_version_check_image(
                    "ghcr.io/aicage/aicage-image-util:agent-version",
                    definition_dir,
                    reporter=reporter,
                )
            self.assertFalse(result.success)
            self.assertEqual("offline", result.error)
            run_mock.assert_not_called()
