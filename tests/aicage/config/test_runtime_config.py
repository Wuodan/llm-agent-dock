import tempfile
from pathlib import Path
from unittest import TestCase, mock

from aicage.config import SettingsStore
from aicage.config.project_config import AgentConfig, AgentMounts
from aicage.config.runtime_config import RunConfig, load_run_config
from aicage.registry.images_metadata.models import ImagesMetadata
from aicage.runtime.run_args import MountSpec


class RuntimeConfigTests(TestCase):
    def test_load_run_config_reads_docker_args_and_mount_prefs(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            base_dir = Path(tmp_dir) / "config"
            project_path = Path(tmp_dir) / "project"
            project_path.mkdir()

            store = SettingsStore(base_dir=base_dir)

            project_cfg = store.load_project(project_path)
            project_cfg.agents["codex"] = AgentConfig(
                base="ubuntu",
                docker_args="--project",
                mounts=AgentMounts(gitconfig=True),
            )
            store.save_project(project_path, project_cfg)

            def store_factory(*args: object, **kwargs: object) -> SettingsStore:
                return SettingsStore(base_dir=base_dir)

            mounts = [MountSpec(host_path=Path("/tmp/host"), container_path=Path("/tmp/container"))]
            with (
                mock.patch("aicage.config.runtime_config.SettingsStore", new=store_factory),
                mock.patch("aicage.config.runtime_config.Path.cwd", return_value=project_path),
                mock.patch("aicage.config.runtime_config.resolve_mounts", return_value=mounts),
                mock.patch(
                    "aicage.config.runtime_config.load_images_metadata",
                    return_value=self._get_images_metadata(),
                ),
            ):
                run_config = load_run_config("codex")

        self.assertIsInstance(run_config, RunConfig)
        self.assertEqual("--project", run_config.project_docker_args)
        self.assertEqual(mounts, run_config.mounts)

    @staticmethod
    def _get_images_metadata() -> ImagesMetadata:
        return ImagesMetadata.from_mapping(
            {
                "aicage-image": {"version": "0.3.3"},
                "aicage-image-base": {"version": "0.3.3"},
                "bases": {
                    "ubuntu": {
                        "root_image": "ubuntu:latest",
                        "base_image_distro": "Ubuntu",
                        "base_image_description": "Default",
                        "os_installer": "distro/debian/install.sh",
                        "test_suite": "default",
                    }
                },
                "agent": {
                    "codex": {
                        "agent_path": "~/.codex",
                        "agent_full_name": "Codex CLI",
                        "agent_homepage": "https://example.com",
                        "redistributable": True,
                        "valid_bases": {"ubuntu": "ghcr.io/aicage/aicage:codex-ubuntu"},
                    }
                },
            }
        )
