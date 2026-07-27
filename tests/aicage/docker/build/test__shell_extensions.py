import tempfile
from pathlib import Path
from unittest import TestCase, mock

from aicage.config.extensions.loader import ExtensionMetadata
from aicage.docker.build import _shell_extensions


class ShellExtensionsBuildTests(TestCase):
    def test_build_shell_extensions(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            extension_dir = Path(tmp_dir) / "extra"
            (extension_dir / "scripts").mkdir(parents=True)
            (extension_dir / "scripts" / "01-install.sh").write_text(
                "#!/usr/bin/env bash\necho ok\n",
                encoding="utf-8",
            )
            dockerfile_builtin = Path(tmp_dir) / "Dockerfile"
            dockerfile_builtin.write_text("FROM ubuntu:latest\n", encoding="utf-8")
            batch_script = Path(tmp_dir) / "run-selected-extensions.sh"
            batch_script.write_text("#!/usr/bin/env bash\n", encoding="utf-8")
            extension = ExtensionMetadata(
                extension_id="extra",
                name="extra",
                description="desc",
                shares=[],
                directory=extension_dir,
                scripts_dir=extension_dir / "scripts",
                dockerfile_path=None,
            )

            with (
                mock.patch(
                    "aicage.docker.build._shell_extensions.find_packaged_path",
                    side_effect=[dockerfile_builtin, batch_script],
                ),
                mock.patch(
                    "aicage.docker.build._shell_extensions.proxy_build_args_from_host",
                    return_value=[],
                ),
                mock.patch(
                    "aicage.docker.build._shell_extensions._common.run_build_command",
                    return_value=0,
                ) as run_mock,
            ):
                returncode = _shell_extensions.build_shell_extensions(
                    base_image_ref="ghcr.io/aicage/aicage:codex-ubuntu",
                    target_ref="aicage-extended:codex-ubuntu-extra",
                    shell_extensions=[extension],
                    log_handle=mock.Mock(),
                    operation_reporter=mock.Mock(),
                )

        self.assertEqual(0, returncode)
        run_mock.assert_called_once()
