import tempfile
from pathlib import Path
from unittest import TestCase, mock

from aicage.config.agent import _loader_shared
from aicage.config.base.models import BaseMetadata
from aicage.config.errors import ConfigError


class LoaderSharedTests(TestCase):
    def test_load_agents_from_directory_builds_entries(self) -> None:
        bases = {
            "ubuntu": BaseMetadata(
                from_image="ubuntu:latest",
                base_image_distro="Ubuntu",
                base_image_description="Default",
                architectures=["amd64", "arm64"],
                build_local=False,
                local_definition_dir=Path("/test-tmp/base"),
            )
        }
        with tempfile.TemporaryDirectory() as tmp_dir:
            agents_dir = Path(tmp_dir)
            agent_dir = agents_dir / "codex"
            agent_dir.mkdir()
            (agent_dir / "agent.yml").write_text("name: codex\n", encoding="utf-8")
            with (
                mock.patch(
                    "aicage.config.agent._loader_shared.load_yaml",
                    return_value={"k": "v"},
                ) as load_yaml_mock,
                mock.patch(
                    "aicage.config.agent._loader_shared.ensure_required_files",
                ) as ensure_mock,
                mock.patch(
                    "aicage.config.agent._loader_shared.build_agent_metadata",
                    return_value=mock.Mock(),
                ) as build_mock,
            ):
                agents = _loader_shared.load_agents_from_directory(
                    agents_dir=agents_dir,
                    bases=bases,
                    definition_files=("agent.yml",),
                    agent_label="Agent",
                )
        self.assertEqual({"codex"}, set(agents))
        load_yaml_mock.assert_called_once_with(agent_dir / "agent.yml")
        ensure_mock.assert_called_once_with("codex", agent_dir)
        build_mock.assert_called_once_with(
            agent_name="codex",
            agent_mapping={"k": "v"},
            bases=bases,
            definition_dir=agent_dir,
        )

    def test_load_agents_from_directory_skips_non_directories(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            agents_dir = Path(tmp_dir)
            (agents_dir / "README.md").write_text("ignored\n", encoding="utf-8")

            agents = _loader_shared.load_agents_from_directory(
                agents_dir=agents_dir,
                bases={},
                definition_files=("agent.yml",),
                agent_label="Agent",
            )

        self.assertEqual({}, agents)

    def test_find_agent_definition_raises_for_missing_definition(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            agent_dir = Path(tmp_dir) / "codex"
            agent_dir.mkdir()

            with self.assertRaises(ConfigError) as raised:
                _loader_shared._find_agent_definition(
                    agent_dir, ("agent.yml", "agent.yaml"), "Agent"
                )

        self.assertEqual(
            "Agent 'codex' is missing agent.yml, agent.yaml.", str(raised.exception)
        )
