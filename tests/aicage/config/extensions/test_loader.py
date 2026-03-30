import tempfile
from pathlib import Path
from unittest import TestCase, mock

from aicage.config.errors import ConfigError
from aicage.config.extensions import loader as extensions_module
from aicage.config.yaml_loader import load_yaml

from ._fixtures import extension_definition, join_yaml, write_extension


class ExtensionDiscoveryTests(TestCase):
    def test_load_extensions_reads_metadata(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            extension_root = Path(tmp_dir) / "extension"
            extension_dir = extension_root / "sample"
            write_extension(extension_dir, name="Sample", description="Desc")
            with mock.patch(
                "aicage.config.extensions.loader.CUSTOM_EXTENSIONS_DIR",
                Path(extension_root),
            ):
                extensions = extensions_module.load_extensions()

        self.assertIn("sample", extensions)
        metadata = extensions["sample"]
        self.assertEqual("Sample", metadata.name)
        self.assertEqual("Desc", metadata.description)
        self.assertEqual([], metadata.shares)

    def test_load_extensions_reads_shares(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            extension_root = Path(tmp_dir) / "extension"
            extension_dir = extension_root / "sample"
            write_extension(
                extension_dir,
                name="Sample",
                description="Desc",
                extra_lines=["shares:", "  - ~/.m2", "  - ~/.cache:ro"],
            )
            with mock.patch(
                "aicage.config.extensions.loader.CUSTOM_EXTENSIONS_DIR",
                Path(extension_root),
            ):
                extensions = extensions_module.load_extensions()

        self.assertEqual(["~/.m2", "~/.cache:ro"], extensions["sample"].shares)

    def test_extension_hash_changes_on_script_edit(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            extension_root = Path(tmp_dir) / "extension"
            extension_dir = extension_root / "sample"
            write_extension(extension_dir, name="Sample", description="Desc")
            with mock.patch(
                "aicage.config.extensions.loader.CUSTOM_EXTENSIONS_DIR",
                Path(extension_root),
            ):
                extensions = extensions_module.load_extensions()
                metadata = extensions["sample"]
                first_hash = extensions_module.extension_hash(metadata)
                script_path = metadata.scripts_dir / "01-install.sh"
                script_path.write_text("#!/usr/bin/env bash\necho changed\n", encoding="utf-8")
                second_hash = extensions_module.extension_hash(metadata)

        self.assertNotEqual(first_hash, second_hash)

    def test_extension_hash_changes_on_dockerfile_edit(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            extension_root = Path(tmp_dir) / "extension"
            extension_dir = extension_root / "sample"
            write_extension(extension_dir, name="Sample", description="Desc")
            (extension_dir / "Dockerfile").write_text("FROM ubuntu:latest\n", encoding="utf-8")
            with mock.patch(
                "aicage.config.extensions.loader.CUSTOM_EXTENSIONS_DIR",
                Path(extension_root),
            ):
                extensions = extensions_module.load_extensions()
                metadata = extensions["sample"]
                first_hash = extensions_module.extension_hash(metadata)
                (extension_dir / "Dockerfile").write_text("FROM ubuntu:22.04\n", encoding="utf-8")
                second_hash = extensions_module.extension_hash(metadata)

        self.assertNotEqual(first_hash, second_hash)

    def test_load_extensions_skips_non_directories(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            extension_root = Path(tmp_dir) / "extension"
            extension_root.mkdir(parents=True)
            (extension_root / "README.md").write_text("ignore", encoding="utf-8")
            with mock.patch(
                "aicage.config.extensions.loader.CUSTOM_EXTENSIONS_DIR",
                Path(extension_root),
            ):
                extensions = extensions_module.load_extensions()

        self.assertEqual({}, extensions)

    def test_load_extensions_requires_scripts_or_shares(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            extension_root = Path(tmp_dir) / "extension"
            extension_dir = extension_root / "sample"
            extension_dir.mkdir(parents=True)
            (extension_dir / "extension.yml").write_text(
                extension_definition("Sample", "Desc"),
                encoding="utf-8",
            )
            with mock.patch(
                "aicage.config.extensions.loader.CUSTOM_EXTENSIONS_DIR",
                Path(extension_root),
            ):
                with self.assertRaises(ConfigError) as ctx:
                    extensions_module.load_extensions()
        self.assertEqual(
            "Extension 'sample' must define shares or provide scripts/ directory.",
            str(ctx.exception),
        )

    def test_load_extensions_allows_share_only_extension(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            extension_root = Path(tmp_dir) / "extension"
            extension_dir = extension_root / "sample"
            extension_dir.mkdir(parents=True)
            (extension_dir / "extension.yml").write_text(
                extension_definition("Sample", "Desc", extra_lines=["shares:", "  - ~/.m2"]),
                encoding="utf-8",
            )
            with mock.patch(
                "aicage.config.extensions.loader.CUSTOM_EXTENSIONS_DIR",
                Path(extension_root),
            ):
                extensions = extensions_module.load_extensions()

        metadata = extensions["sample"]
        self.assertEqual(["~/.m2"], metadata.shares)
        self.assertFalse(metadata.scripts_dir.exists())

    def test_load_extensions_requires_definition(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            extension_root = Path(tmp_dir) / "extension"
            extension_dir = extension_root / "sample"
            scripts_dir = extension_dir / "scripts"
            scripts_dir.mkdir(parents=True, exist_ok=True)
            with mock.patch(
                "aicage.config.extensions.loader.CUSTOM_EXTENSIONS_DIR",
                Path(extension_root),
            ):
                with self.assertRaises(ConfigError):
                    extensions_module.load_extensions()

    def test_load_extensions_rejects_invalid_yaml(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            extension_root = Path(tmp_dir) / "extension"
            extension_dir = extension_root / "sample"
            scripts_dir = extension_dir / "scripts"
            scripts_dir.mkdir(parents=True, exist_ok=True)
            (extension_dir / "extension.yml").write_text(
                "- not-a-mapping\n",
                encoding="utf-8",
            )
            with mock.patch(
                "aicage.config.extensions.loader.CUSTOM_EXTENSIONS_DIR",
                Path(extension_root),
            ):
                with self.assertRaises(ConfigError):
                    extensions_module.load_extensions()

    def test_load_extensions_reports_read_failure(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            missing_path = Path(tmp_dir) / "missing.yml"
            with self.assertRaises(ConfigError):
                load_yaml(missing_path)

    def test_load_extensions_rejects_unknown_keys(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            extension_root = Path(tmp_dir) / "extension"
            extension_dir = extension_root / "sample"
            scripts_dir = extension_dir / "scripts"
            scripts_dir.mkdir(parents=True, exist_ok=True)
            (extension_dir / "extension.yml").write_text(
                extension_definition("Sample", "Desc", extra_lines=["extra: true"]),
                encoding="utf-8",
            )
            with mock.patch(
                "aicage.config.extensions.loader.CUSTOM_EXTENSIONS_DIR",
                Path(extension_root),
            ):
                with self.assertRaises(ConfigError):
                    extensions_module.load_extensions()

    def test_load_extensions_rejects_blank_values(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            extension_root = Path(tmp_dir) / "extension"
            extension_dir = extension_root / "sample"
            scripts_dir = extension_dir / "scripts"
            scripts_dir.mkdir(parents=True, exist_ok=True)
            (extension_dir / "extension.yml").write_text(
                extension_definition("", "Desc"),
                encoding="utf-8",
            )
            with mock.patch(
                "aicage.config.extensions.loader.CUSTOM_EXTENSIONS_DIR",
                Path(extension_root),
            ):
                with self.assertRaises(ConfigError):
                    extensions_module.load_extensions()

    def test_load_extensions_requires_required_keys(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            extension_root = Path(tmp_dir) / "extension"
            extension_dir = extension_root / "sample"
            scripts_dir = extension_dir / "scripts"
            scripts_dir.mkdir(parents=True, exist_ok=True)
            (extension_dir / "extension.yml").write_text(
                join_yaml(["name: \"Sample\""]),
                encoding="utf-8",
            )
            with mock.patch(
                "aicage.config.extensions.loader.CUSTOM_EXTENSIONS_DIR",
                Path(extension_root),
            ):
                with self.assertRaises(ConfigError):
                    extensions_module.load_extensions()
