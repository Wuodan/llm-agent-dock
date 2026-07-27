import os
import subprocess
import tempfile
from pathlib import Path
from subprocess import CompletedProcess
from unittest import TestCase, mock

from aicage.config.extensions.loader import ExtensionMetadata
from aicage.constants import DEFAULT_EXTENDED_IMAGE_NAME
from aicage.docker import build
from aicage.docker.errors import DockerError

from .._run_config_fixtures import build_extended_run_config
from .._run_config_fixtures import build_run_config as _build_run_config


class LocalBuildRunnerTests(TestCase):
    def test_run_build_invokes_docker(self) -> None:
        run_config = _build_run_config(
            local_definition_dir=Path("/test-tmp/build/agents/claude")
        )
        with tempfile.TemporaryDirectory() as tmp_dir:
            log_path = Path(tmp_dir) / "logs" / "build.log"
            with (
                mock.patch.dict(os.environ, {}, clear=True),
                mock.patch(
                    "aicage.docker.build.find_packaged_path",
                    return_value=Path("/test-tmp/build/Dockerfile"),
                ),
                mock.patch(
                    "aicage.docker.build._run_build_command",
                    return_value=0,
                ) as run_mock,
            ):
                build.run_build(
                    run_config=run_config,
                    base_image_ref="ghcr.io/aicage/aicage-image-base:ubuntu",
                    image_ref="aicage:claude-ubuntu",
                    log_path=log_path,
                )

        run_mock.assert_called_once()
        command = run_mock.call_args.args[0]
        self.assertEqual(
            [
                "docker",
                "build",
                "--no-cache",
                "--file",
                str(Path("/test-tmp/build/Dockerfile")),
                "--build-arg",
                "BASE_IMAGE=ghcr.io/aicage/aicage-image-base:ubuntu",
                "--build-arg",
                "AGENT=claude",
                "--tag",
                "aicage:claude-ubuntu",
                str(Path("/test-tmp/build")),
            ],
            command,
        )

    def test_run_build_raises_on_failure(self) -> None:
        run_config = _build_run_config(
            local_definition_dir=Path("/test-tmp/build/agents/claude")
        )
        with tempfile.TemporaryDirectory() as tmp_dir:
            log_path = Path(tmp_dir) / "logs" / "build.log"
            reporter = mock.Mock()
            with (
                mock.patch(
                    "aicage.docker.build.find_packaged_path",
                    return_value=Path("/test-tmp/build/Dockerfile"),
                ),
                mock.patch(
                    "aicage.docker.build._run_build_command",
                    return_value=1,
                ),
                self.assertRaises(DockerError),
            ):
                build.run_build(
                    run_config=run_config,
                    base_image_ref="ghcr.io/aicage/aicage-image-base:ubuntu",
                    image_ref="aicage:claude-ubuntu",
                    log_path=log_path,
                    reporter=reporter,
                )
        reporter.on_phase_failed.assert_called_once_with(
            "build",
            "Local image build failed for aicage:claude-ubuntu",
            log_path,
        )

    def test_run_custom_base_build_invokes_docker(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            log_path = Path(tmp_dir) / "logs" / "build.log"
            dockerfile_path = Path(tmp_dir) / "Dockerfile"
            dockerfile_path.write_text("FROM ubuntu:latest\n", encoding="utf-8")
            with (
                mock.patch.dict(os.environ, {}, clear=True),
                mock.patch(
                    "aicage.docker.build._run_build_command",
                    return_value=0,
                ) as run_mock,
            ):
                build.run_custom_base_build(
                    build_root=Path(tmp_dir),
                    from_image="ubuntu:latest",
                    image_ref="aicage:base-sample",
                    log_path=log_path,
                )

        command = run_mock.call_args.args[0]
        self.assertEqual(
            [
                "docker",
                "build",
                "--no-cache",
                "--file",
                str(dockerfile_path),
                "--build-arg",
                "FROM_IMAGE=ubuntu:latest",
                "--tag",
                "aicage:base-sample",
                str(Path(tmp_dir)),
            ],
            command,
        )

    def test_run_build_includes_proxy_build_args(self) -> None:
        run_config = _build_run_config(
            local_definition_dir=Path("/test-tmp/build/agents/claude")
        )
        with tempfile.TemporaryDirectory() as tmp_dir:
            log_path = Path(tmp_dir) / "logs" / "build.log"
            with (
                mock.patch.dict(
                    os.environ,
                    {"HTTP_PROXY": "http://proxy-http:8080"},
                    clear=True,
                ),
                mock.patch(
                    "aicage.docker.build.find_packaged_path",
                    return_value=Path("/test-tmp/build/Dockerfile"),
                ),
                mock.patch(
                    "aicage.docker.build._run_build_command",
                    return_value=0,
                ) as run_mock,
            ):
                build.run_build(
                    run_config=run_config,
                    base_image_ref="ghcr.io/aicage/aicage-image-base:ubuntu",
                    image_ref="aicage:claude-ubuntu",
                    log_path=log_path,
                )

        command = run_mock.call_args.args[0]
        self.assertIn("--build-arg", command)
        self.assertIn("HTTP_PROXY=http://proxy-http:8080", command)

    def test_run_custom_base_build_raises_on_failure(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            log_path = Path(tmp_dir) / "logs" / "build.log"
            dockerfile_path = Path(tmp_dir) / "Dockerfile"
            dockerfile_path.write_text("FROM ubuntu:latest\n", encoding="utf-8")
            with (
                mock.patch(
                    "aicage.docker.build._run_build_command",
                    return_value=1,
                ),
                self.assertRaises(DockerError),
            ):
                build.run_custom_base_build(
                    build_root=Path(tmp_dir),
                    from_image="ubuntu:latest",
                    image_ref="aicage:base-sample",
                    log_path=log_path,
                )

    def test_run_custom_base_build_reports_started_and_finished(self) -> None:
        reporter = mock.Mock()
        with tempfile.TemporaryDirectory() as tmp_dir:
            log_path = Path(tmp_dir) / "logs" / "build.log"
            dockerfile_path = Path(tmp_dir) / "Dockerfile"
            dockerfile_path.write_text("FROM ubuntu:latest\n", encoding="utf-8")
            with (
                mock.patch.dict(os.environ, {}, clear=True),
                mock.patch(
                    "aicage.docker.build._run_build_command",
                    return_value=0,
                ),
            ):
                build.run_custom_base_build(
                    build_root=Path(tmp_dir),
                    from_image="ubuntu:latest",
                    image_ref="aicage:base-sample",
                    log_path=log_path,
                    reporter=reporter,
                )

        reporter.on_phase_started.assert_called_once_with(
            "build",
            "Building custom base image aicage:base-sample",
            log_path,
        )
        reporter.on_phase_finished.assert_called_once_with(
            "build",
            "Custom base image build finished for aicage:base-sample",
        )

    def test_run_extended_build_batches_shell_extensions(self) -> None:
        run_config = build_extended_run_config()
        extensions = [_extension("extra"), _extension("more")]
        with tempfile.TemporaryDirectory() as tmp_dir:
            log_path = Path(tmp_dir) / "build.log"
            with (
                mock.patch(
                    "aicage.docker.build._run_shell_extensions_build",
                    return_value=0,
                ) as shell_build_mock,
                mock.patch(
                    "aicage.docker.build._cleanup_intermediate_images"
                ) as cleanup_mock,
            ):
                build.run_extended_build(
                    run_config=run_config,
                    base_image_ref="ghcr.io/aicage/aicage:codex-ubuntu",
                    extensions=extensions,
                    log_path=log_path,
                )
        shell_build_mock.assert_called_once()
        cleanup_mock.assert_called_once_with([])

    def test_run_extended_build_builds_dockerfile_extensions_after_shell_batch(
        self,
    ) -> None:
        run_config = build_extended_run_config()
        extensions = [
            _extension("extra"),
            _extension("custom", dockerfile_path=Path("/test-tmp/custom/Dockerfile")),
        ]
        with tempfile.TemporaryDirectory() as tmp_dir:
            log_path = Path(tmp_dir) / "build.log"
            with (
                mock.patch(
                    "aicage.docker.build.find_packaged_path",
                    return_value=Path("/test-tmp/Dockerfile"),
                ),
                mock.patch(
                    "aicage.docker.build._run_shell_extensions_build",
                    return_value=0,
                ) as shell_build_mock,
                mock.patch(
                    "aicage.docker.build._run_build_command",
                    return_value=0,
                ) as run_mock,
                mock.patch(
                    "aicage.docker.build._cleanup_intermediate_images"
                ) as cleanup_mock,
            ):
                build.run_extended_build(
                    run_config=run_config,
                    base_image_ref="ghcr.io/aicage/aicage:codex-ubuntu",
                    extensions=extensions,
                    log_path=log_path,
                )

        shell_build_mock.assert_called_once()
        run_mock.assert_called_once()
        command = run_mock.call_args.args[0]
        shell_ref = f"{DEFAULT_EXTENDED_IMAGE_NAME}:tmp-codex-ubuntu-shell-extensions"
        self.assertIn(
            f"BASE_IMAGE={shell_ref}",
            command,
        )
        cleanup_mock.assert_called_once_with([shell_ref])

    def test_run_extended_build_raises_on_failure(self) -> None:
        run_config = build_extended_run_config()
        extension = _extension("extra")
        with tempfile.TemporaryDirectory() as tmp_dir:
            log_path = Path(tmp_dir) / "build.log"
            reporter = mock.Mock()
            with (
                mock.patch(
                    "aicage.docker.build._run_shell_extensions_build",
                    return_value=1,
                ),
            ):
                with self.assertRaises(DockerError):
                    build.run_extended_build(
                        run_config=run_config,
                        base_image_ref="ghcr.io/aicage/aicage:codex-ubuntu",
                        extensions=[extension],
                        log_path=log_path,
                        reporter=reporter,
                    )
        reporter.on_phase_failed.assert_called_once_with(
            "build",
            f"Extended image build failed for {run_config.selection.image_ref}",
            log_path,
        )

    def test_run_shell_extensions_build_invokes_docker(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            extension_dir = Path(tmp_dir) / "extra"
            (extension_dir / "scripts").mkdir(parents=True)
            (extension_dir / "scripts" / "01-install.sh").write_text(
                "#!/usr/bin/env bash\necho ok\n",
                encoding="utf-8",
            )
            extension = ExtensionMetadata(
                extension_id="extra",
                name="extra",
                description="desc",
                shares=[],
                directory=extension_dir,
                scripts_dir=extension_dir / "scripts",
                dockerfile_path=None,
            )
            dockerfile_builtin = Path(tmp_dir) / "Dockerfile"
            dockerfile_builtin.write_text("FROM ubuntu:latest\n", encoding="utf-8")
            batch_script = Path(tmp_dir) / "run-selected-extensions.sh"
            batch_script.write_text("#!/usr/bin/env bash\n", encoding="utf-8")
            with mock.patch(
                "aicage.docker.build._run_build_command",
                return_value=0,
            ) as run_mock:
                returncode = build._run_shell_extensions_build(
                    base_image_ref="ghcr.io/aicage/aicage:codex-ubuntu",
                    target_ref="aicage-extended:codex-ubuntu-extra",
                    shell_extensions=[extension],
                    context=build._ShellExtensionsBuildContext(
                        dockerfile_builtin=dockerfile_builtin,
                        batch_script=batch_script,
                        proxy_build_args=[],
                        log_handle=mock.Mock(),
                        operation_reporter=mock.Mock(),
                    ),
                )

        self.assertEqual(0, returncode)
        command = run_mock.call_args.args[0]
        self.assertEqual("docker", command[0])
        self.assertIn("BASE_IMAGE=ghcr.io/aicage/aicage:codex-ubuntu", command)
        self.assertIn("EXTENSIONS=extra", command)

    def test_run_build_reports_started_and_finished(self) -> None:
        run_config = _build_run_config(
            local_definition_dir=Path("/test-tmp/build/agents/claude")
        )
        reporter = mock.Mock()
        with tempfile.TemporaryDirectory() as tmp_dir:
            log_path = Path(tmp_dir) / "logs" / "build.log"
            with (
                mock.patch.dict(os.environ, {}, clear=True),
                mock.patch(
                    "aicage.docker.build.find_packaged_path",
                    return_value=Path("/test-tmp/build/Dockerfile"),
                ),
                mock.patch(
                    "aicage.docker.build._run_build_command",
                    return_value=0,
                ),
            ):
                build.run_build(
                    run_config=run_config,
                    base_image_ref="ghcr.io/aicage/aicage-image-base:ubuntu",
                    image_ref="aicage:claude-ubuntu",
                    log_path=log_path,
                    reporter=reporter,
                )

        reporter.on_phase_started.assert_called_once_with(
            "build",
            "Building local image aicage:claude-ubuntu",
            log_path,
        )
        reporter.on_phase_finished.assert_called_once_with(
            "build",
            "Local image build finished for aicage:claude-ubuntu",
        )

    @staticmethod
    def test_run_build_command_streams_output_to_log_and_reporter() -> None:
        reporter = mock.Mock()
        process = mock.Mock()
        process.stdout = iter(["step 1\n", "step 2\n"])
        process.wait.return_value = 0
        popen_context = mock.Mock()
        popen_context.__enter__ = mock.Mock(return_value=process)
        popen_context.__exit__ = mock.Mock(return_value=None)
        log_handle = mock.Mock()

        with (
            mock.patch(
                "aicage.docker.build.subprocess.Popen", return_value=popen_context
            ) as popen_mock,
            mock.patch("aicage.docker.build.register_process") as register_mock,
        ):
            returncode = build._run_build_command(
                ["docker", "build"], log_handle, reporter
            )

        assert returncode == 0
        popen_mock.assert_called_once_with(
            ["docker", "build"],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding="utf-8",
        )
        assert log_handle.mock_calls == [
            mock.call.write("step 1\n"),
            mock.call.flush(),
            mock.call.write("step 2\n"),
            mock.call.flush(),
        ]
        reporter.on_phase_log.assert_has_calls(
            [
                mock.call("build", "step 1"),
                mock.call("build", "step 2"),
            ]
        )
        register_mock.assert_called_once_with(process)

    @staticmethod
    def test_cleanup_intermediate_images_logs_failures() -> None:
        logger = mock.Mock()
        with (
            mock.patch("aicage.docker.build.get_logger", return_value=logger),
            mock.patch(
                "aicage.docker.build._run_docker_command",
                return_value=CompletedProcess([], 1),
            ),
        ):
            build._cleanup_intermediate_images(["aicage:tmp"])
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
