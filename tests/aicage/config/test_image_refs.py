from pathlib import Path
from unittest import TestCase

from aicage.config.extensions.loader import ExtensionMetadata
from aicage.config.image_refs import (
    default_extended_image_ref,
    extended_image_name,
    local_image_ref,
)


class ImageRefsTests(TestCase):
    def test_local_image_ref_formats_tag(self) -> None:
        self.assertEqual(
            "aicage:agent-ubuntu", local_image_ref("aicage", "Agent", "Ubuntu")
        )
        self.assertEqual(
            "aicage:agent-sub-base", local_image_ref("aicage", "agent/sub", "base")
        )

    def test_default_extended_image_ref_groups_scripts_before_dockerfiles(self) -> None:
        self.assertEqual(
            "aicage-extended:codex-ubuntu-alpha-zeta",
            default_extended_image_ref(
                "codex",
                "ubuntu",
                ["zeta", "alpha"],
                {
                    "zeta": _extension("zeta", dockerfile=True),
                    "alpha": _extension("alpha"),
                },
            ),
        )

    def test_extended_image_name_extracts_tag(self) -> None:
        self.assertEqual("tag", extended_image_name("repo:tag"))
        self.assertEqual("latest", extended_image_name("registry.io/repo:latest"))

    def test_extended_image_name_returns_ref_without_tag(self) -> None:
        self.assertEqual("repo", extended_image_name("repo"))


def _extension(extension_id: str, dockerfile: bool = False) -> ExtensionMetadata:
    base_dir = Path("/test-tmp") / extension_id
    return ExtensionMetadata(
        extension_id=extension_id,
        name=extension_id,
        description="desc",
        shares=[],
        directory=base_dir,
        scripts_dir=base_dir / "scripts",
        dockerfile_path=base_dir / "Dockerfile" if dockerfile else None,
    )
