import hashlib
import tempfile
from pathlib import Path
from unittest import TestCase, mock

import yaml

from aicage.config.config_store import SettingsStore, _IndentedSafeDumper
from aicage.config.project_config import AgentConfig, _AgentMounts, _ProjectConfig


class ConfigStoreTests(TestCase):
    def test_increase_indent_indents_list_items(self) -> None:
        content = yaml.dump({"extensions": ["java17"]}, Dumper=_IndentedSafeDumper)

        self.assertEqual("extensions:\n  - java17\n", content)

    def test_project_config_path_returns_hashed_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            projects_dir = Path(tmp_dir)

            with mock.patch(
                "aicage.config.config_store.PROJECTS_DIR",
                projects_dir,
            ):
                store = SettingsStore()
                project_path = Path("/repo")
                expected = hashlib.sha256(str(project_path).encode("utf-8")).hexdigest()

                path = store.project_config_path(project_path)

            self.assertEqual(store.projects_dir / f"{expected}.yml", path)

    def test_load_project_returns_empty_config(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            projects_dir = Path(tmp_dir)

            with mock.patch(
                "aicage.config.config_store.PROJECTS_DIR",
                projects_dir,
            ):
                store = SettingsStore()
                project_path = projects_dir / "project"
                project_path.mkdir(parents=True, exist_ok=True)

                project_cfg = store.load_project(project_path)

            self.assertEqual(
                _ProjectConfig(path=str(project_path), agents={}), project_cfg
            )

    def test_save_project_writes_mapping(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            projects_dir = Path(tmp_dir)

            with mock.patch(
                "aicage.config.config_store.PROJECTS_DIR",
                projects_dir,
            ):
                store = SettingsStore()
                project_path = projects_dir / "project"
                project_path.mkdir(parents=True, exist_ok=True)

                project_cfg = _ProjectConfig(path=str(project_path), agents={})
                project_cfg.agents["codex"] = AgentConfig(
                    base="fedora",
                    docker_args="--add-host=host.docker.internal:host-gateway",
                    mounts=_AgentMounts(),
                    extensions=["java17"],
                )
                store.save_project(project_path, project_cfg)

                config_path = store.project_config_path(project_path)
                with config_path.open("r", encoding="utf-8") as handle:
                    raw = yaml.safe_load(handle)
                content = config_path.read_text(encoding="utf-8")

            self.assertEqual(project_cfg.to_mapping(), raw)
            self.assertIn("    extensions:\n      - java17\n", content)

    def test_load_project_accepts_indentless_list(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            projects_dir = Path(tmp_dir)

            with mock.patch(
                "aicage.config.config_store.PROJECTS_DIR",
                projects_dir,
            ):
                store = SettingsStore()
                project_path = projects_dir / "project"
                project_path.mkdir(parents=True, exist_ok=True)
                config_path = store.project_config_path(project_path)
                config_path.write_text(
                    "path: /project\nagents:\n  codex:\n    extensions:\n    - java17\n",
                    encoding="utf-8",
                )

                project_cfg = store.load_project(project_path)

            self.assertEqual(["java17"], project_cfg.agents["codex"].extensions)
