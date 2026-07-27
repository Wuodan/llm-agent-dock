import shutil
import tempfile
from pathlib import Path
from typing import TextIO

from aicage._proxy import proxy_build_args_from_host
from aicage.config.extensions.loader import ExtensionMetadata
from aicage.config.resources import find_packaged_path
from aicage.reporting import OperationReporter

from . import _common


def build_shell_extensions(
    base_image_ref: str,
    target_ref: str,
    shell_extensions: list[ExtensionMetadata],
    log_handle: TextIO,
    operation_reporter: OperationReporter,
) -> int:
    with tempfile.TemporaryDirectory(prefix="aicage-extension-build-") as tmp_dir:
        build_root = Path(tmp_dir)
        dockerfile_builtin = find_packaged_path("extension-build/Dockerfile")
        batch_script = find_packaged_path(
            "extension-build/helpers/run-selected-extensions.sh"
        )
        _write_shell_extensions_build_context(
            build_root,
            shell_extensions,
            dockerfile_builtin,
            batch_script,
        )
        command = [
            "docker",
            "build",
            "--no-cache",
            "--file",
            str(build_root / "Dockerfile"),
            "--build-arg",
            f"BASE_IMAGE={base_image_ref}",
            "--build-arg",
            "EXTENSIONS="
            + " ".join(extension.extension_id for extension in shell_extensions),
            "--tag",
            target_ref,
            str(build_root),
        ]
        command.extend(proxy_build_args_from_host())
        return _common.run_build_command(
            command,
            log_handle,
            operation_reporter,
        )


def _write_shell_extensions_build_context(
    build_root: Path,
    shell_extensions: list[ExtensionMetadata],
    dockerfile_builtin: Path,
    batch_script: Path,
) -> None:
    shutil.copy2(dockerfile_builtin, build_root / "Dockerfile")
    helpers_root = build_root / "helpers"
    helpers_root.mkdir(parents=True, exist_ok=True)
    shutil.copy2(batch_script, helpers_root / "run-selected-extensions.sh")
    extensions_root = build_root / "extensions"
    extensions_root.mkdir(parents=True, exist_ok=True)
    for extension in shell_extensions:
        shutil.copytree(
            extension.directory,
            extensions_root / extension.extension_id,
        )
