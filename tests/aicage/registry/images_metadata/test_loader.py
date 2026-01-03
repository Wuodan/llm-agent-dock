import tempfile
from pathlib import Path
from unittest import TestCase, mock

from aicage.errors import CliError
from aicage.registry.images_metadata.loader import load_images_metadata
from aicage.registry.images_metadata.models import (
    _AGENT_KEY,
    _AICAGE_IMAGE_BASE_KEY,
    _AICAGE_IMAGE_KEY,
    _BASE_IMAGE_DESCRIPTION_KEY,
    _BASE_IMAGE_DISTRO_KEY,
    _BASES_KEY,
    _OS_INSTALLER_KEY,
    _ROOT_IMAGE_KEY,
    _TEST_SUITE_KEY,
    _VALID_BASES_KEY,
    _VERSION_KEY,
    AGENT_FULL_NAME_KEY,
    AGENT_HOMEPAGE_KEY,
    AGENT_PATH_KEY,
    BUILD_LOCAL_KEY,
)


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
                metadata = load_images_metadata("aicage")
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
                load_images_metadata("aicage")


def _valid_payload() -> str:
    return f"""
{_AICAGE_IMAGE_KEY}:
  {_VERSION_KEY}: 0.3.3
{_AICAGE_IMAGE_BASE_KEY}:
  {_VERSION_KEY}: 0.3.3
{_BASES_KEY}:
  ubuntu:
    {_ROOT_IMAGE_KEY}: ubuntu:latest
    {_BASE_IMAGE_DISTRO_KEY}: Ubuntu
    {_BASE_IMAGE_DESCRIPTION_KEY}: Good default
    {_OS_INSTALLER_KEY}: distro/debian/install.sh
    {_TEST_SUITE_KEY}: default
{_AGENT_KEY}:
  codex:
    {AGENT_PATH_KEY}: ~/.codex
    {AGENT_FULL_NAME_KEY}: Codex CLI
    {AGENT_HOMEPAGE_KEY}: https://example.com
    {BUILD_LOCAL_KEY}: false
    {_VALID_BASES_KEY}:
      ubuntu: ghcr.io/aicage/aicage:codex-ubuntu
"""
