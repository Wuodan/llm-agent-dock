from pathlib import Path
from unittest import TestCase

from aicage.cli_types import ParsedArgs
from aicage.config.project_config import AgentConfig, _ProjectConfig
from aicage.config.run_config_draft import RunConfigDraft, _create_run_config_draft
from aicage.registry.image_selection.models import ImageSelection


class RunConfigDraftTests(TestCase):
    def test_create_run_config_draft_reads_existing_docker_args(self) -> None:
        project_cfg = _ProjectConfig(
            path="/test-tmp/project",
            agents={"codex": AgentConfig(docker_args="--existing")},
        )

        draft = _create_run_config_draft(
            Path("/test-tmp/project"),
            "codex",
            project_cfg,
            _build_parsed(),
        )

        self.assertEqual("--existing", draft.existing_project_docker_args)

    def test_apply_selection_sets_base_when_missing(self) -> None:
        draft = _build_draft(AgentConfig())

        draft.apply_selection(_selection(base="ubuntu"))

        self.assertEqual("ubuntu", draft.agent_cfg.base)

    def test_apply_selection_keeps_existing_base(self) -> None:
        draft = _build_draft(AgentConfig(base="debian"))

        draft.apply_selection(_selection(base="ubuntu"))

        self.assertEqual("debian", draft.agent_cfg.base)

    def test_agent_cfg_recreates_config_after_agent_reset(self) -> None:
        draft = _build_draft(AgentConfig(base="ubuntu"))

        draft.project_cfg.agents.pop("codex")

        self.assertIsInstance(draft.agent_cfg, AgentConfig)
        self.assertEqual({}, draft.agent_cfg.to_mapping())

    def test_persist_docker_args_updates_config(self) -> None:
        draft = _build_draft(AgentConfig(docker_args="--existing"), docker_args="--new")

        draft.persist_docker_args()
        self.assertEqual("--new", draft.agent_cfg.docker_args)

    def test_merge_shares_normalizes_parsed_and_returns_only_new_shares(self) -> None:
        draft = _build_draft(
            AgentConfig(shares=["/repo/existing"]),
            shares=["existing", "new", "new:ro"],
            project_path=Path("/repo"),
        )

        new_shares = draft.merge_shares()
        parsed = draft.parsed
        if parsed is None:
            self.fail("Expected parsed args to be available.")

        self.assertEqual(["/repo/new"], new_shares)
        self.assertEqual(["/repo/existing", "/repo/new"], parsed.shares)
        self.assertEqual(["/repo/existing"], draft.agent_cfg.shares)

    def test_persist_shares_updates_config(self) -> None:
        draft = _build_draft(
            AgentConfig(shares=["/repo/existing"]),
            shares=["new:ro"],
            project_path=Path("/repo"),
        )

        new_shares = draft.merge_shares()
        draft.persist_shares(new_shares)

        self.assertEqual(["/repo/existing", "/repo/new:ro"], draft.agent_cfg.shares)

    def test_prefill_for_overview_applies_cli_values(self) -> None:
        draft = _build_draft(
            AgentConfig(docker_args="--existing", shares=["/repo/existing"]),
            docker_args="--new",
            shares=["logs"],
            project_path=Path("/repo"),
        )
        parsed = draft.parsed
        if parsed is None:
            self.fail("Expected parsed args to be available.")
        parsed.docker_socket = True

        draft.prefill_for_overview()

        self.assertEqual("--new", draft.agent_cfg.docker_args)
        self.assertEqual(["/repo/logs", "/repo/existing"], draft.agent_cfg.shares)
        self.assertTrue(draft.agent_cfg.mounts.docker)

    def test_consume_overview_prefill_clears_cli_runtime_values(self) -> None:
        draft = _build_draft(AgentConfig(), docker_args="--new", shares=["logs"])
        parsed = draft.parsed
        if parsed is None:
            self.fail("Expected parsed args to be available.")
        parsed.docker_socket = True

        draft.consume_overview_prefill()

        self.assertEqual("", parsed.docker_args)
        self.assertEqual([], parsed.shares)
        self.assertFalse(parsed.docker_socket)

    def test_image_selection_changed_detects_base_extension_change(self) -> None:
        draft = _build_draft(
            AgentConfig(
                base="ubuntu", image_ref="aicage:codex-ubuntu", extensions=["marker"]
            ),
        )

        self.assertFalse(draft.image_selection_changed())
        draft.agent_cfg.extensions = []
        self.assertTrue(draft.image_selection_changed())

    def test_reset_extension_image_clears_image_ref_and_removed_mounts(self) -> None:
        draft = _build_draft(
            AgentConfig(
                base="ubuntu",
                image_ref="aicage:custom",
                extensions=["one"],
                extension_mounts={"one": True, "two": False},
            )
        )

        draft.reset_extension_image()

        self.assertIsNone(draft.agent_cfg.image_ref)
        self.assertEqual({"one": True}, draft.agent_cfg.extension_mounts)


def _build_draft(
    agent_cfg: AgentConfig,
    docker_args: str = "",
    shares: list[str] | None = None,
    project_path: Path = Path("/test-tmp/project"),
) -> RunConfigDraft:
    return _create_run_config_draft(
        project_path,
        "codex",
        _ProjectConfig(path=str(project_path), agents={"codex": agent_cfg}),
        _build_parsed(docker_args=docker_args, shares=shares or []),
    )


def _build_parsed(docker_args: str = "", shares: list[str] | None = None) -> ParsedArgs:
    return ParsedArgs(
        dry_run=False,
        docker_args=docker_args,
        agent="codex",
        agent_args=[],
        docker_socket=False,
        shares=shares or [],
        config_action=None,
    )


def _selection(base: str) -> ImageSelection:
    return ImageSelection(
        image_ref=f"aicage:codex-{base}",
        base=base,
        extensions=[],
        agent_image_ref=f"aicage:codex-{base}",
    )
