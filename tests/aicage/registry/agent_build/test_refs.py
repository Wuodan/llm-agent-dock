from pathlib import Path
from unittest import TestCase, mock

from aicage.config.base.models import BaseMetadata
from aicage.constants import IMAGE_BASE_REPOSITORY, IMAGE_REGISTRY
from aicage.paths import CUSTOM_BASES_DIR
from aicage.registry.agent_build import refs
from aicage.registry.base_build.ensure import image_ref as base_build_image_ref


class LocalBuildRefsTests(TestCase):
    def test_get_base_image_ref_uses_custom_base(self) -> None:
        run_config = mock.Mock()
        run_config.selection = mock.Mock()
        run_config.selection.base = "custom"
        run_config.context = mock.Mock()
        run_config.context.bases = {
            "custom": BaseMetadata(
                from_image="ubuntu:latest",
                base_image_distro="Ubuntu",
                base_image_description="Custom",
                architectures=["amd64", "arm64"],
                build_local=True,
                local_definition_dir=CUSTOM_BASES_DIR / "custom",
            )
        }
        ref = refs.get_base_image_ref(run_config)

        self.assertEqual(base_build_image_ref("custom"), ref)

    def test_get_base_image_ref_uses_repository(self) -> None:
        run_config = mock.Mock()
        run_config.selection = mock.Mock()
        run_config.selection.base = "ubuntu"
        run_config.context = mock.Mock()
        run_config.context.bases = {
            "ubuntu": BaseMetadata(
                from_image="ubuntu:latest",
                base_image_distro="Ubuntu",
                base_image_description="Default",
                architectures=["amd64", "arm64"],
                build_local=False,
                local_definition_dir=Path("/test-tmp/ubuntu"),
            )
        }
        ref = refs.get_base_image_ref(run_config)

        self.assertEqual(f"{IMAGE_REGISTRY}/{IMAGE_BASE_REPOSITORY}:ubuntu", ref)

    def test__base_repository_includes_registry(self) -> None:
        run_config = mock.Mock()

        repository = refs._base_repository(run_config)

        self.assertEqual(f"{IMAGE_REGISTRY}/{IMAGE_BASE_REPOSITORY}", repository)
