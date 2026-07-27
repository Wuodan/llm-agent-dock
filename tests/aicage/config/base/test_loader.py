import tempfile
from pathlib import Path
from unittest import TestCase, mock

from aicage.config.base import loader
from aicage.config.base.loader import load_bases
from aicage.config.base.models import BaseMetadata
from aicage.config.errors import ConfigError


class BaseLoaderTests(TestCase):
    def test_load_bases_merges_custom_overrides(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            root = Path(tmp_dir)
            dockerfile = root / "agent-build" / "Dockerfile"
            dockerfile.parent.mkdir(parents=True)
            dockerfile.write_text("FROM scratch\n", encoding="utf-8")

            ubuntu_dir = root / "base-build" / "bases" / "ubuntu"
            ubuntu_dir.mkdir(parents=True)
            (ubuntu_dir / "base.yml").write_text(
                "\n".join(
                    [
                        "from_image: ubuntu:latest",
                        "base_image_distro: Ubuntu",
                        "base_image_description: Default",
                        "architectures:",
                        "  - amd64",
                        "  - arm64",
                    ]
                ),
                encoding="utf-8",
            )

            debian_dir = root / "base-build" / "bases" / "debian"
            debian_dir.mkdir(parents=True)
            (debian_dir / "base.yml").write_text(
                "\n".join(
                    [
                        "from_image: debian:latest",
                        "base_image_distro: Debian",
                        "base_image_description: Default",
                        "architectures:",
                        "  - amd64",
                        "  - arm64",
                    ]
                ),
                encoding="utf-8",
            )

            custom_base = BaseMetadata(
                from_image="custom:latest",
                base_image_distro="Custom",
                base_image_description="Custom base",
                architectures=["amd64", "arm64"],
                build_local=True,
                local_definition_dir=Path("/test-tmp/custom"),
            )
            with (
                mock.patch(
                    "aicage.config.base.loader.find_packaged_path",
                    return_value=dockerfile,
                ),
                mock.patch(
                    "aicage.config.base.loader.load_custom_bases",
                    return_value={"ubuntu": custom_base},
                ),
            ):
                bases = load_bases()

        self.assertEqual(custom_base, bases["ubuntu"])
        self.assertFalse(bases["debian"].build_local)
        self.assertEqual(["amd64", "arm64"], bases["debian"].architectures)

    def test_load_builtin_bases_raises_when_directory_missing(self) -> None:
        with mock.patch(
            "aicage.config.base.loader._builtin_bases_dir",
            return_value=Path("/test-tmp/missing"),
        ):
            with self.assertRaises(ConfigError) as raised:
                loader._load_builtin_bases()

        self.assertEqual(
            "Built-in base directory '/test-tmp/missing' is missing.",
            str(raised.exception),
        )

    def test_load_builtin_bases_skips_non_directories(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            root = Path(tmp_dir)
            dockerfile = root / "agent-build" / "Dockerfile"
            dockerfile.parent.mkdir(parents=True)
            dockerfile.write_text("FROM scratch\n", encoding="utf-8")
            bases_dir = root / "base-build" / "bases"
            bases_dir.mkdir(parents=True)
            (bases_dir / "README.md").write_text("ignored\n", encoding="utf-8")

            with mock.patch(
                "aicage.config.base.loader.find_packaged_path",
                return_value=dockerfile,
            ):
                bases = loader._load_builtin_bases()

        self.assertEqual({}, bases)

    def test_find_base_definition_raises_for_missing_definition(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            base_dir = Path(tmp_dir) / "ubuntu"
            base_dir.mkdir()

            with self.assertRaises(ConfigError) as raised:
                loader._find_base_definition(base_dir)

        self.assertEqual(
            "Base 'ubuntu' is missing base.yaml, base.yml.", str(raised.exception)
        )
