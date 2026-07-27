from pathlib import Path
from unittest import TestCase

from aicage.config.extensions.loader import ExtensionMetadata
from aicage.config.extensions.order import (
    canonical_extension_ids,
    canonical_extensions,
)


class CanonicalExtensionOrderTests(TestCase):
    def test_canonical_extensions_groups_scripts_before_dockerfiles(self) -> None:
        ordered = canonical_extensions(
            [
                _extension("zeta", dockerfile=True),
                _extension("alpha"),
                _extension("beta", dockerfile=True),
                _extension("gamma"),
            ]
        )

        self.assertEqual(
            ["alpha", "gamma", "beta", "zeta"],
            [extension.extension_id for extension in ordered],
        )

    def test_canonical_extension_ids_groups_scripts_before_dockerfiles(self) -> None:
        extensions = {
            "zeta": _extension("zeta", dockerfile=True),
            "alpha": _extension("alpha"),
            "beta": _extension("beta", dockerfile=True),
            "gamma": _extension("gamma"),
        }

        self.assertEqual(
            ["alpha", "gamma", "beta", "zeta"],
            canonical_extension_ids(["zeta", "alpha", "beta", "gamma"], extensions),
        )


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
