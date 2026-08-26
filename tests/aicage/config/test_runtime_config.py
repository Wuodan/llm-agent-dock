import tempfile
from pathlib import Path, PurePosixPath
from types import SimpleNamespace
from unittest import TestCase, mock

from aicage.cli_types import ParsedArgs
from aicage.config.agent.models import AgentMetadata
from aicage.config.base.models import BaseMetadata
from aicage.config.config_store import SettingsStore
from aicage.config.extensions.loader import ExtensionMetadata
from aicage.config.image_refs import default_extended_image_ref
from aicage.config.project_config import AgentConfig, _AgentMounts
from aicage.config.run_config_draft import RunConfigDraft
from aicage.config.runtime_config import RunConfig, load_run_config
from aicage.registry.errors import RegistryError
from aicage.registry.image_selection.models import ImageSelection
from aicage.runtime.menu.interaction import create_runtime_interaction
from aicage.runtime.run_args import EnvVar, MountSpec


class RuntimeConfigTests(TestCase):
    def test_load_run_config_reads_docker_args_and_mount_prefs(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            projects_dir = Path(tmp_dir)
            project_path = projects_dir / "project"
            project_path.mkdir()

            store = SettingsStore()

            project_cfg = store.load_project(project_path)
            project_cfg.agents["codex"] = AgentConfig(
                base="ubuntu",
                docker_args="--project",
                mounts=_AgentMounts(gitconfig=True),
            )
            store.save_project(project_path, project_cfg)

            def store_factory(*_args: object, **_kwargs: object) -> SettingsStore:
                return SettingsStore()

            mounts = [
                MountSpec(
                    host_path=Path("/test-tmp/host"),
                    container_path=PurePosixPath("/test-tmp/container"),
                )
            ]
            env: list[EnvVar] = []
            with (
                mock.patch(
                    "aicage.config.runtime_config.SettingsStore", new=store_factory
                ),
                mock.patch(
                    "aicage.config.runtime_config.Path.cwd", return_value=project_path
                ),
                mock.patch(
                    "aicage.config.runtime_config.resolve_docker_args",
                    return_value=(mounts, env),
                ),
                mock.patch(
                    "aicage.config.runtime_config.load_extensions", return_value={}
                ),
                mock.patch(
                    "aicage.config.runtime_config.load_bases",
                    return_value=self._get_bases(),
                ),
                mock.patch(
                    "aicage.config.runtime_config.load_agents",
                    return_value=self._get_agents(),
                ),
            ):
                run_config = load_run_config("codex", self._interaction())

        self.assertIsInstance(run_config, RunConfig)
        self.assertEqual("--project", run_config.project_docker_args)
        self.assertEqual(mounts, run_config.mounts)
        self.assertEqual(env, run_config.env)

    def test_load_run_config_does_not_persist_config_for_none_menu(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            project_path = Path(tmp_dir) / "project"
            project_path.mkdir()
            projects_dir = Path(tmp_dir) / "configs"
            projects_dir_patch = mock.patch(
                "aicage.config.config_store.PROJECTS_DIR", projects_dir
            )
            projects_dir_patch.start()
            self.addCleanup(projects_dir_patch.stop)

            store = SettingsStore()
            project_cfg = store.load_project(project_path)
            project_cfg.agents["codex"] = AgentConfig(
                base="ubuntu",
                docker_args="--existing",
            )
            store.save_project(project_path, project_cfg)

            def store_factory(*_args: object, **_kwargs: object) -> SettingsStore:
                return SettingsStore()

            parsed = ParsedArgs(
                dry_run=False,
                docker_args="--new",
                agent="codex",
                agent_args=[],
                docker_socket=False,
                shares=[],
                config_action=None,
                menu="none",
            )
            with (
                mock.patch(
                    "aicage.config.runtime_config.SettingsStore", new=store_factory
                ),
                mock.patch(
                    "aicage.config.runtime_config.Path.cwd", return_value=project_path
                ),
                mock.patch(
                    "aicage.config.runtime_config.resolve_docker_args",
                    return_value=([], []),
                ),
                mock.patch(
                    "aicage.config.runtime_config.load_extensions", return_value={}
                ),
                mock.patch(
                    "aicage.config.runtime_config.load_bases",
                    return_value=self._get_bases(),
                ),
                mock.patch(
                    "aicage.config.runtime_config.load_agents",
                    return_value=self._get_agents(),
                ),
                mock.patch(
                    "aicage.runtime.menu._none_interaction.select_agent_image",
                    return_value=ImageSelection(
                        image_ref="ref",
                        base="ubuntu",
                        extensions=[],
                        agent_image_ref="ref",
                    ),
                ),
                mock.patch(
                    "aicage.runtime.menu._none_interaction.apply_mount_preferences"
                ),
            ):
                run_config = load_run_config(
                    "codex",
                    create_runtime_interaction("none"),
                    parsed,
                )

                updated_cfg = store.load_project(project_path)

        self.assertEqual("--existing", run_config.project_docker_args)
        self.assertEqual("--existing", updated_cfg.agents["codex"].docker_args)

    def test_load_run_config_defaults_base_when_missing(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            project_path = Path(tmp_dir) / "project"
            project_path.mkdir()

            store = SettingsStore()
            project_cfg = store.load_project(project_path)
            project_cfg.agents["codex"] = AgentConfig()
            store.save_project(project_path, project_cfg)

            def store_factory(*_args: object, **_kwargs: object) -> SettingsStore:
                return SettingsStore()

            with (
                mock.patch(
                    "aicage.config.runtime_config.SettingsStore", new=store_factory
                ),
                mock.patch(
                    "aicage.config.runtime_config.Path.cwd", return_value=project_path
                ),
                mock.patch(
                    "aicage.config.runtime_config.resolve_docker_args",
                    return_value=([], []),
                ),
                mock.patch(
                    "aicage.config.runtime_config.load_extensions", return_value={}
                ),
                mock.patch(
                    "aicage.config.runtime_config.load_bases",
                    return_value=self._get_bases(),
                ),
                mock.patch(
                    "aicage.config.runtime_config.load_agents",
                    return_value=self._get_agents(),
                ),
            ):
                run_config = load_run_config("codex", self._interaction())

        self.assertEqual("ubuntu", run_config.selection.base)

    def test_load_run_config_removes_missing_extensions_when_loading_project(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            project_path = Path(tmp_dir) / "project"
            project_path.mkdir()

            store = SettingsStore()
            project_cfg = store.load_project(project_path)
            project_cfg.agents["codex"] = AgentConfig(
                base="ubuntu",
                image_ref="aicage:codex-ubuntu",
                extensions=["gh", "missing"],
                extension_mounts={"gh": True, "missing": True},
            )
            project_cfg.agents["claude"] = AgentConfig(
                base="ubuntu",
                image_ref="aicage:claude-ubuntu",
                extensions=["missing"],
                extension_mounts={"missing": True},
            )
            store.save_project(project_path, project_cfg)

            def store_factory(*_args: object, **_kwargs: object) -> SettingsStore:
                return SettingsStore()

            def interaction_side_effect(
                draft: RunConfigDraft,
                _context: object,
                _agent: str,
            ) -> object:
                expected_image_ref = default_extended_image_ref(
                    "codex",
                    "ubuntu",
                    ["gh"],
                    {"gh": self._extension("gh")},
                )
                self.assertEqual(["gh"], draft.agent_cfg.extensions)
                self.assertEqual({"gh": True}, draft.agent_cfg.extension_mounts)
                self.assertEqual(expected_image_ref, draft.agent_cfg.image_ref)
                return self._selection_result()

            with (
                mock.patch(
                    "aicage.config.runtime_config.SettingsStore", new=store_factory
                ),
                mock.patch(
                    "aicage.config.runtime_config.Path.cwd", return_value=project_path
                ),
                mock.patch(
                    "aicage.config.runtime_config.resolve_docker_args",
                    return_value=([], []),
                ),
                mock.patch(
                    "aicage.config.runtime_config.load_extensions",
                    return_value={"gh": self._extension("gh")},
                ),
                mock.patch(
                    "aicage.config.runtime_config.load_bases",
                    return_value=self._get_bases(),
                ),
                mock.patch(
                    "aicage.config.runtime_config.load_agents",
                    return_value=self._get_agents(),
                ),
            ):
                load_run_config(
                    "codex",
                    self._interaction(side_effect=interaction_side_effect),
                )

            updated_cfg = store.load_project(project_path)

        self.assertEqual(["gh"], updated_cfg.agents["codex"].extensions)
        self.assertEqual({"gh": True}, updated_cfg.agents["codex"].extension_mounts)
        self.assertEqual(
            default_extended_image_ref(
                "codex",
                "ubuntu",
                ["gh"],
                {"gh": self._extension("gh")},
            ),
            updated_cfg.agents["codex"].image_ref,
        )
        self.assertEqual(["missing"], updated_cfg.agents["claude"].extensions)
        self.assertEqual(
            {"missing": True}, updated_cfg.agents["claude"].extension_mounts
        )
        self.assertEqual("aicage:claude-ubuntu", updated_cfg.agents["claude"].image_ref)

    def test_load_run_config_does_not_persist_share_mounts_for_none_menu(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            projects_dir = Path(tmp_dir) / "configs"
            project_path = Path(tmp_dir) / "project"
            project_path.mkdir()

            with mock.patch("aicage.config.config_store.PROJECTS_DIR", projects_dir):
                store = SettingsStore()
                project_cfg = store.load_project(project_path)
                project_cfg.agents["codex"] = AgentConfig(base="ubuntu")
                store.save_project(project_path, project_cfg)

                def store_factory(*_args: object, **_kwargs: object) -> SettingsStore:
                    return SettingsStore()

                parsed = ParsedArgs(
                    dry_run=False,
                    docker_args="",
                    agent="codex",
                    agent_args=[],
                    docker_socket=False,
                    shares=["data", "logs:ro"],
                    config_action=None,
                    menu="none",
                )
                with (
                    mock.patch(
                        "aicage.config.runtime_config.SettingsStore", new=store_factory
                    ),
                    mock.patch(
                        "aicage.config.runtime_config.Path.cwd",
                        return_value=project_path,
                    ),
                    mock.patch(
                        "aicage.config.runtime_config.resolve_docker_args",
                        return_value=([], []),
                    ),
                    mock.patch(
                        "aicage.config.runtime_config.load_extensions", return_value={}
                    ),
                    mock.patch(
                        "aicage.config.runtime_config.load_bases",
                        return_value=self._get_bases(),
                    ),
                    mock.patch(
                        "aicage.config.runtime_config.load_agents",
                        return_value=self._get_agents(),
                    ),
                    mock.patch(
                        "aicage.runtime.menu._none_interaction.select_agent_image",
                        return_value=ImageSelection(
                            image_ref="ref",
                            base="ubuntu",
                            extensions=[],
                            agent_image_ref="ref",
                        ),
                    ),
                    mock.patch(
                        "aicage.runtime.menu._none_interaction.apply_mount_preferences"
                    ),
                ):
                    load_run_config(
                        "codex",
                        create_runtime_interaction("none"),
                        parsed,
                    )

                updated_cfg = store.load_project(project_path)

        expected_data = str(project_path / "data")
        expected_logs = f"{project_path / 'logs'}:ro"
        self.assertEqual([], updated_cfg.agents["codex"].shares)
        self.assertEqual([expected_data, expected_logs], parsed.shares)

    def test_load_run_config_merges_share_mounts_without_persisting_for_none_menu(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            projects_dir = Path(tmp_dir) / "configs"
            project_path = Path(tmp_dir) / "project"
            project_path.mkdir()

            with mock.patch("aicage.config.config_store.PROJECTS_DIR", projects_dir):
                store = SettingsStore()
                project_cfg = store.load_project(project_path)
                project_cfg.agents["codex"] = AgentConfig(
                    base="ubuntu",
                    shares=[
                        str(project_path / "existing"),
                        f"{project_path / 'shared'}:ro",
                    ],
                )
                store.save_project(project_path, project_cfg)

                def store_factory(*_args: object, **_kwargs: object) -> SettingsStore:
                    return SettingsStore()

                parsed = ParsedArgs(
                    dry_run=False,
                    docker_args="",
                    agent="codex",
                    agent_args=[],
                    docker_socket=False,
                    shares=["shared", "new"],
                    config_action=None,
                    menu="none",
                )
                with (
                    mock.patch(
                        "aicage.config.runtime_config.SettingsStore", new=store_factory
                    ),
                    mock.patch(
                        "aicage.config.runtime_config.Path.cwd",
                        return_value=project_path,
                    ),
                    mock.patch(
                        "aicage.config.runtime_config.resolve_docker_args",
                        return_value=([], []),
                    ),
                    mock.patch(
                        "aicage.config.runtime_config.load_extensions", return_value={}
                    ),
                    mock.patch(
                        "aicage.config.runtime_config.load_bases",
                        return_value=self._get_bases(),
                    ),
                    mock.patch(
                        "aicage.config.runtime_config.load_agents",
                        return_value=self._get_agents(),
                    ),
                    mock.patch(
                        "aicage.runtime.menu._none_interaction.select_agent_image",
                        return_value=ImageSelection(
                            image_ref="ref",
                            base="ubuntu",
                            extensions=[],
                            agent_image_ref="ref",
                        ),
                    ),
                    mock.patch(
                        "aicage.runtime.menu._none_interaction.apply_mount_preferences"
                    ),
                ):
                    load_run_config(
                        "codex",
                        create_runtime_interaction("none"),
                        parsed,
                    )

                updated_cfg = store.load_project(project_path)

        expected_shared = str(project_path / "shared")
        expected_new = str(project_path / "new")
        expected_existing = str(project_path / "existing")
        self.assertEqual(
            [expected_shared, expected_new, expected_existing], parsed.shares
        )
        self.assertEqual(
            [expected_existing, f"{expected_shared}:ro"],
            updated_cfg.agents["codex"].shares,
        )

    def test_load_run_config_interactive_uses_overview_values_for_current_run(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            project_path = Path(tmp_dir) / "project"
            project_path.mkdir()

            store = SettingsStore()
            project_cfg = store.load_project(project_path)
            project_cfg.agents["codex"] = AgentConfig(
                base="ubuntu",
                docker_args="--existing",
            )
            store.save_project(project_path, project_cfg)

            def store_factory(*_args: object, **_kwargs: object) -> SettingsStore:
                return SettingsStore()

            parsed = ParsedArgs(
                dry_run=False,
                docker_args="--new",
                agent="codex",
                agent_args=[],
                docker_socket=True,
                shares=["logs"],
                config_action=None,
            )

            def interaction_side_effect(
                draft: RunConfigDraft,
                _context: object,
                _agent: str,
            ) -> object:
                draft.prefill_for_overview()
                draft.consume_overview_prefill()
                return SimpleNamespace(
                    selection=ImageSelection(
                        image_ref="ref",
                        base="ubuntu",
                        extensions=[],
                        agent_image_ref="ref",
                    ),
                    project_docker_args="--new",
                )

            with (
                mock.patch(
                    "aicage.config.runtime_config.SettingsStore", new=store_factory
                ),
                mock.patch(
                    "aicage.config.runtime_config.Path.cwd", return_value=project_path
                ),
                mock.patch(
                    "aicage.config.runtime_config.resolve_docker_args",
                    return_value=([], []),
                ),
                mock.patch(
                    "aicage.config.runtime_config.load_extensions", return_value={}
                ),
                mock.patch(
                    "aicage.config.runtime_config.load_bases",
                    return_value=self._get_bases(),
                ),
                mock.patch(
                    "aicage.config.runtime_config.load_agents",
                    return_value=self._get_agents(),
                ),
            ):
                run_config = load_run_config(
                    "codex",
                    self._interaction(side_effect=interaction_side_effect),
                    parsed,
                )

        self.assertEqual("--new", run_config.project_docker_args)
        self.assertEqual("", parsed.docker_args)
        self.assertEqual([], parsed.shares)
        self.assertFalse(parsed.docker_socket)

    def test_load_run_config_calls_interaction_before_runtime_resolution(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            project_path = Path(tmp_dir) / "project"
            project_path.mkdir()

            def store_factory(*_args: object, **_kwargs: object) -> SettingsStore:
                return SettingsStore()

            parsed = ParsedArgs(
                dry_run=False,
                docker_args="",
                agent="codex",
                agent_args=[],
                docker_socket=False,
                shares=[],
                config_action=None,
                menu="none",
            )
            call_order: list[str] = []

            def configure_run_side_effect(*_args: object, **_kwargs: object) -> object:
                call_order.append("configure")
                return self._selection_result()

            def resolve_docker_args_side_effect(
                *_args: object, **_kwargs: object
            ) -> tuple[list[object], list[object]]:
                call_order.append("resolve")
                return [], []

            interaction = self._interaction()
            interaction.configure_run.side_effect = configure_run_side_effect
            with (
                mock.patch(
                    "aicage.config.runtime_config.SettingsStore", new=store_factory
                ),
                mock.patch(
                    "aicage.config.runtime_config.Path.cwd", return_value=project_path
                ),
                mock.patch(
                    "aicage.config.runtime_config.resolve_docker_args",
                    side_effect=resolve_docker_args_side_effect,
                ),
                mock.patch(
                    "aicage.config.runtime_config.load_extensions", return_value={}
                ),
                mock.patch(
                    "aicage.config.runtime_config.load_bases",
                    return_value=self._get_bases(),
                ),
                mock.patch(
                    "aicage.config.runtime_config.load_agents",
                    return_value=self._get_agents(),
                ),
            ):
                load_run_config("codex", interaction, parsed)

        self.assertEqual(["configure", "resolve"], call_order)

    def test_load_run_config_rejects_unknown_config_agent_before_interaction(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            project_path = Path(tmp_dir) / "project"
            project_path.mkdir()

            def store_factory(*_args: object, **_kwargs: object) -> SettingsStore:
                return SettingsStore()

            parsed = ParsedArgs(
                dry_run=False,
                docker_args="",
                agent="config",
                agent_args=[],
                docker_socket=False,
                shares=[],
                config_action=None,
                menu="ui",
            )
            interaction = self._interaction()
            with (
                mock.patch(
                    "aicage.config.runtime_config.SettingsStore", new=store_factory
                ),
                mock.patch(
                    "aicage.config.runtime_config.Path.cwd", return_value=project_path
                ),
                mock.patch(
                    "aicage.config.runtime_config.load_extensions", return_value={}
                ),
                mock.patch(
                    "aicage.config.runtime_config.load_bases",
                    return_value=self._get_bases(),
                ),
                mock.patch(
                    "aicage.config.runtime_config.load_agents",
                    return_value=self._get_agents(),
                ),
            ):
                with self.assertRaises(RegistryError) as raised:
                    load_run_config("config", interaction, parsed)

        self.assertEqual(
            (
                "Unknown agent 'config'. Use '--config' for config commands. "
                "Available agents: codex."
            ),
            str(raised.exception),
        )
        interaction.configure_run.assert_not_called()

    @staticmethod
    def _selection_result() -> object:
        return SimpleNamespace(
            selection=ImageSelection(
                image_ref="ref",
                base="ubuntu",
                extensions=[],
                agent_image_ref="ref",
            ),
            project_docker_args="--project",
        )

    @classmethod
    def _interaction(
        cls,
        side_effect: object | None = None,
    ) -> mock.Mock:
        interaction = mock.Mock()
        interaction.configure_run.return_value = cls._selection_result()
        if side_effect is not None:
            interaction.configure_run.side_effect = side_effect
        return interaction

    @staticmethod
    def _get_bases() -> dict[str, BaseMetadata]:
        return {
            "ubuntu": BaseMetadata(
                from_image="ubuntu:latest",
                base_image_distro="Ubuntu",
                base_image_description="Default",
                architectures=["amd64", "arm64"],
                build_local=False,
                local_definition_dir=Path("/test-tmp/base"),
            )
        }

    @staticmethod
    def _get_agents() -> dict[str, AgentMetadata]:
        return {
            "codex": AgentMetadata(
                agent_path_files=[],
                agent_path_directories=["~/.codex"],
                agent_full_name="Codex CLI",
                agent_homepage="https://example.com",
                build_local=False,
                valid_bases={"ubuntu": "ghcr.io/aicage/aicage:codex-ubuntu"},
                local_definition_dir=Path("/test-tmp/agent"),
            )
        }

    @staticmethod
    def _extension(extension_id: str) -> ExtensionMetadata:
        return ExtensionMetadata(
            extension_id=extension_id,
            name=extension_id,
            description="desc",
            shares=[],
            directory=Path("/test-tmp") / extension_id,
            scripts_dir=Path("/test-tmp") / extension_id / "scripts",
            dockerfile_path=None,
        )
