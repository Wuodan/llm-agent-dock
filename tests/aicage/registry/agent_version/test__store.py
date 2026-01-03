import tempfile
from pathlib import Path
from unittest import TestCase

import yaml

from aicage.registry.agent_version._store import (
    _AGENT_KEY,
    _CHECKED_AT_KEY,
    _VERSION_KEY,
    VersionCheckStore,
)


class VersionCheckStoreTests(TestCase):
    def test_save_writes_sanitized_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            store = VersionCheckStore(Path(tmp_dir))

            path = store.save("custom/agent", "1.2.3")

            self.assertEqual(Path(tmp_dir) / "custom_agent.yaml", path)
            payload = yaml.safe_load(path.read_text(encoding="utf-8"))
            self.assertEqual("custom/agent", payload[_AGENT_KEY])
            self.assertEqual("1.2.3", payload[_VERSION_KEY])
            self.assertIn(_CHECKED_AT_KEY, payload)
