import tempfile
from pathlib import Path
from unittest import TestCase, mock

import yaml

from aicage.config import ConfigError, ProjectConfig, SettingsStore
from aicage.config.project_config import AgentConfig, AgentMounts


class ConfigStoreTests(TestCase):
    def test_global_and_project_round_trip(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            base_dir = Path(tmp_dir)
            packaged_dir = base_dir / "packaged"
            packaged_dir.mkdir(parents=True, exist_ok=True)
            packaged_config = packaged_dir / "config.yaml"
            packaged_config.write_text(
                yaml.safe_dump(
                    {
                        "image_registry": "ghcr.io",
                        "image_registry_api_url": "https://ghcr.io/v2",
                        "image_registry_api_token_url": "https://ghcr.io/token",
                        "image_repository": "aicage/aicage",
                        "default_image_base": "ubuntu",
                        "version_check_image": "ghcr.io/aicage/aicage-image-util:latest",
                    },
                    sort_keys=False,
                ),
                encoding="utf-8",
            )

            with mock.patch(
                "aicage.config.config_store.find_packaged_path",
                return_value=packaged_config,
            ):
                store = SettingsStore(base_dir=base_dir)
                global_path = store._global_config()
                self.assertTrue(global_path.exists())
                global_data = yaml.safe_load(global_path.read_text())
                self.assertEqual("aicage/aicage", global_data["image_repository"])

                global_cfg = store.load_global()
                self.assertEqual("aicage/aicage", global_cfg.image_repository)
                self.assertEqual("ubuntu", global_cfg.default_image_base)
                self.assertEqual({}, global_cfg.agents)

            project_path = base_dir / "project"
            project_path.mkdir(parents=True, exist_ok=True)
            project_cfg = store.load_project(project_path)
            self.assertEqual(ProjectConfig(path=str(project_path), agents={}), project_cfg)

            project_cfg.agents["codex"] = AgentConfig(
                base="fedora",
                docker_args="--add-host=host.docker.internal:host-gateway",
                mounts=AgentMounts(),
            )
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
