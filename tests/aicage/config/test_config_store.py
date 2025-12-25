import tempfile
from pathlib import Path
from unittest import TestCase

import yaml

from aicage.config import ConfigError, ProjectConfig, SettingsStore


class ConfigStoreTests(TestCase):
    def test_global_and_project_round_trip(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            base_dir = Path(tmp_dir)
            store = SettingsStore(base_dir=base_dir)
            global_path = store.global_config()
            self.assertTrue(global_path.exists())
            global_data = yaml.safe_load(global_path.read_text())
            self.assertEqual("aicage/aicage", global_data["image_repository"])

            global_cfg = store.load_global()
            self.assertEqual("aicage/aicage", global_cfg.image_repository)
            self.assertEqual("ubuntu", global_cfg.default_image_base)
            self.assertEqual({}, global_cfg.tools)

            global_cfg.tools["codex"] = {"base": "ubuntu"}
            store.save_global(global_cfg)

            reloaded_global = store.load_global()
            self.assertEqual(global_cfg, reloaded_global)
            updated_global = yaml.safe_load(global_path.read_text())
            self.assertEqual("aicage/aicage", updated_global["image_repository"])
            self.assertEqual({"codex": {"base": "ubuntu"}}, updated_global["tools"])

            project_path = base_dir / "project"
            project_path.mkdir(parents=True, exist_ok=True)
            project_cfg = store.load_project(project_path)
            self.assertEqual(ProjectConfig(path=str(project_path), tools={}), project_cfg)

            project_cfg.tools["codex"] = {
                "base": "fedora",
                "docker_args": "--add-host=host.docker.internal:host-gateway",
            }
            store.save_project(project_path, project_cfg)

            reloaded_project = store.load_project(project_path)
            self.assertEqual(project_cfg, reloaded_project)

            yaml_files = list(store.projects_dir.glob("*.yaml"))
            self.assertEqual(1, len(yaml_files))
            with yaml_files[0].open("r", encoding="utf-8") as handle:
                raw = yaml.safe_load(handle)
            self.assertEqual(project_cfg.to_mapping(), raw)

    def test_load_yaml_reports_parse_errors(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            base_dir = Path(tmp_dir)
            bad_file = base_dir / "bad.yaml"
            bad_file.write_text("key: [unterminated", encoding="utf-8")
            store = SettingsStore(base_dir=base_dir)
            with self.assertRaises(ConfigError):
                store._load_yaml(bad_file)  # noqa: SLF001
