import tempfile
from pathlib import Path
from unittest import TestCase, mock

from aicage.registry.agent_build._store import BuildRecord, BuildStore, sanitize


class LocalBuildStoreTests(TestCase):
    def test_save_and_load_round_trip(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            base_dir = Path(tmp_dir)
            with mock.patch(
                "aicage.registry.agent_build._store.paths_module.IMAGE_BUILD_STATE_DIR",
                base_dir,
            ):
                store = BuildStore()
                record = BuildRecord(
                    agent="claude",
                    base="ubuntu",
                    agent_version="1.2.3",
                    base_image="ghcr.io/aicage/aicage-image-base:ubuntu",
                    image_ref="aicage:claude-ubuntu",
                    built_at="2024-01-01T00:00:00+00:00",
                    image_id="sha256:local",
                )
                store.save(record)
                loaded = store.load("claude", "ubuntu")

        self.assertEqual(record, loaded)

    def test_load_uses_empty_image_id_for_legacy_record(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            base_dir = Path(tmp_dir)
            with mock.patch(
                "aicage.registry.agent_build._store.paths_module.IMAGE_BUILD_STATE_DIR",
                base_dir,
            ):
                store = BuildStore()
                record_path = base_dir / "claude-ubuntu.yml"
                record_path.write_text(
                    "\n".join(
                        [
                            "agent: claude",
                            "base: ubuntu",
                            "agent_version: 1.2.3",
                            "base_image: ghcr.io/aicage/aicage-image-base:ubuntu",
                            "image_ref: aicage:claude-ubuntu",
                            "built_at: '2024-01-01T00:00:00+00:00'",
                        ]
                    ),
                    encoding="utf-8",
                )
                loaded = store.load("claude", "ubuntu")

        assert loaded is not None
        self.assertEqual("", loaded.image_id)

    def test_load_returns_none_for_missing_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            base_dir = Path(tmp_dir)
            with mock.patch(
                "aicage.registry.agent_build._store.paths_module.IMAGE_BUILD_STATE_DIR",
                base_dir,
            ):
                store = BuildStore()
                loaded = store.load("claude", "ubuntu")

        self.assertIsNone(loaded)

    def test_load_ignores_non_mapping(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            base_dir = Path(tmp_dir)
            with mock.patch(
                "aicage.registry.agent_build._store.paths_module.IMAGE_BUILD_STATE_DIR",
                base_dir,
            ):
                store = BuildStore()
                record_path = base_dir / "claude-ubuntu.yml"
                record_path.write_text("- item\n", encoding="utf-8")
                loaded = store.load("claude", "ubuntu")

        self.assertIsNone(loaded)

    def test_sanitize_replaces_slashes(self) -> None:
        self.assertEqual("foo_bar", sanitize("foo/bar"))
        self.assertEqual("foo_bar", sanitize("foo:bar"))
