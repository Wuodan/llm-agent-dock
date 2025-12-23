from pathlib import Path
from unittest import TestCase, mock

from aicage.runtime.run_args import DockerRunArgs, assemble_docker_run


class RunArgsTests(TestCase):
    def test_assemble_includes_workspace_mount(self) -> None:
        with mock.patch("aicage.runtime.run_args._resolve_user_ids", return_value=[]):
            run_args = DockerRunArgs(
                image_ref="ghcr.io/aicage/aicage:codex-ubuntu-latest",
                project_path=Path("/work/project"),
                tool_config_host=Path("/host/.codex"),
                tool_mount_container=Path("/aicage/tool-config"),
                merged_docker_args="--network=host",
                tool_args=["--flag"],
                tool_path="~/.codex",
            )
            cmd = assemble_docker_run(run_args)
        self.assertEqual(
            [
                "docker",
                "run",
                "--rm",
                "-it",
                "-e",
                "AICAGE_WORKSPACE=/work/project",
                "-e",
                "AICAGE_TOOL_PATH=~/.codex",
                "-v",
                "/work/project:/workspace",
                "-v",
                "/work/project:/work/project",
                "-v",
                "/host/.codex:/aicage/tool-config",
                "--network=host",
                "ghcr.io/aicage/aicage:codex-ubuntu-latest",
                "--flag",
            ],
            cmd,
        )
