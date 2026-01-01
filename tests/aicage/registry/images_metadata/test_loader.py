import tempfile
from pathlib import Path
from unittest import TestCase, mock

from aicage.errors import CliError
from aicage.registry.images_metadata.loader import load_images_metadata


class ImagesMetadataLoaderTests(TestCase):
    def test_load_images_metadata_reads_local_file(self) -> None:
        payload = _valid_payload()
        with tempfile.TemporaryDirectory() as tmp_dir:
            path = Path(tmp_dir) / "images-metadata.yaml"
            path.write_text(payload, encoding="utf-8")
            with mock.patch(
                "aicage.registry.images_metadata.loader.find_packaged_path",
                return_value=path,
            ):
                metadata = load_images_metadata()
            self.assertEqual("0.3.3", metadata.aicage_image.version)

    def test_load_images_metadata_raises_without_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            missing = Path(tmp_dir) / "images-metadata.yaml"
            with (
                mock.patch(
                    "aicage.registry.images_metadata.loader.find_packaged_path",
                    return_value=missing,
                ),
                self.assertRaises(CliError),
            ):
                load_images_metadata()


def _valid_payload() -> str:
    return """
aicage-image:
  version: 0.3.3
aicage-image-base:
  version: 0.3.3
bases:
  ubuntu:
    root_image: ubuntu:latest
    base_image_distro: Ubuntu
    base_image_description: Good default
    os_installer: distro/debian/install.sh
    test_suite: default
agent:
  codex:
    agent_path: ~/.codex
    agent_full_name: Codex CLI
    agent_homepage: https://example.com
    redistributable: true
    valid_bases:
      ubuntu: ghcr.io/aicage/aicage:codex-ubuntu
"""
