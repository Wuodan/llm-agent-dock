import tempfile
from pathlib import Path
from unittest import TestCase, mock

from aicage.config import SettingsStore
from aicage.config.runtime_config import RunConfig, load_run_config
from aicage.runtime.run_args import MountSpec


class RuntimeConfigTests(TestCase):
    def test_load_run_config_reads_docker_args_and_mount_prefs(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            base_dir = Path(tmp_dir) / "config"
            project_path = Path(tmp_dir) / "project"
            project_path.mkdir()

            store = SettingsStore(base_dir=base_dir)

            project_cfg = store.load_project(project_path)
            project_cfg.tools["codex"] = {"base": "ubuntu", "docker_args": "--project", "mounts": {"gitconfig": True}}
            store.save_project(project_path, project_cfg)

            def store_factory(*args: object, **kwargs: object) -> SettingsStore:
                ensure = bool(kwargs.get("ensure_global_config", True))
                return SettingsStore(base_dir=base_dir, ensure_global_config=ensure)

            mounts = [MountSpec(host_path=Path("/tmp/host"), container_path=Path("/tmp/container"))]
            with (
                mock.patch("aicage.config.runtime_config.SettingsStore", new=store_factory),
                mock.patch("aicage.config.runtime_config.Path.cwd", return_value=project_path),
                mock.patch("aicage.config.runtime_config.build_auth_mounts", return_value=(mounts, False)),
            ):
                run_config = load_run_config("codex")

        self.assertIsInstance(run_config, RunConfig)
        self.assertEqual("--project", run_config.project_docker_args)
        self.assertTrue(run_config.mount_preferences.gitconfig)
        self.assertEqual(mounts, run_config.mounts)
