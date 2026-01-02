from unittest import TestCase

from aicage import registry


class RegistryInitTests(TestCase):
    def test_exports(self) -> None:
        self.assertFalse(hasattr(registry, "__all__"))
