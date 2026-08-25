from pathlib import Path
from unittest import TestCase, mock

from aicage.config.agent.models import AgentMetadata
from aicage.config.base.models import BaseMetadata
from aicage.config.runtime_config import RunConfig
from aicage.constants import IMAGE_BASE_REPOSITORY, IMAGE_REGISTRY
from aicage.paths import CUSTOM_BASES_DIR
from aicage.registry._pull_decision import _PullDecisionAction
from aicage.registry.agent_build.ensure import AgentBuildSetupAction
from aicage.registry.ensure_image import (
    ImageSetupAction,
    ensure_image,
    image_setup_plan,
)


class EnsureImageTests(TestCase):
    @staticmethod
    def test_ensure_image_pulls_when_not_local() -> None:
        run_config = _run_config(build_local=False, extensions=[])
        reporter = mock.Mock()
        with (
            mock.patch("aicage.registry.ensure_image.pull_image") as pull_mock,
            mock.patch("aicage.registry.ensure_image.ensure_agent_image") as local_mock,
            mock.patch(
                "aicage.registry.ensure_image.ensure_extended_image"
            ) as extended_mock,
        ):
            ensure_image(run_config, update_approved=False, reporter=reporter)

        pull_mock.assert_called_once()
        assert pull_mock.call_args.kwargs == {
            "update_approved": False,
            "reporter": reporter,
        }
        assert run_config.selection.base_image_ref == pull_mock.call_args.args[0]
        local_mock.assert_not_called()
        extended_mock.assert_not_called()

    @staticmethod
    def test_ensure_image_builds_local_when_custom_base() -> None:
        run_config = _run_config(
            build_local=False,
            extensions=[],
            base="custom",
            base_definition_dir=CUSTOM_BASES_DIR / "custom",
        )
        reporter = mock.Mock()
        with (
            mock.patch("aicage.registry.ensure_image.pull_image") as pull_mock,
            mock.patch("aicage.registry.ensure_image.ensure_agent_image") as local_mock,
        ):
            ensure_image(run_config, update_approved=False, reporter=reporter)

        pull_mock.assert_not_called()
        local_mock.assert_called_once()
        assert run_config is local_mock.call_args.args[0]
        assert local_mock.call_args.kwargs == {
            "update_approved": False,
            "reporter": reporter,
        }

    @staticmethod
    def test_ensure_image_runs_extended_build() -> None:
        run_config = _run_config(build_local=True, extensions=["extra"])
        reporter = mock.Mock()
        with (
            mock.patch("aicage.registry.ensure_image.ensure_agent_image") as local_mock,
            mock.patch(
                "aicage.registry.ensure_image.ensure_extended_image"
            ) as extended_mock,
        ):
            ensure_image(run_config, update_approved=False, reporter=reporter)

        local_mock.assert_called_once()
        assert run_config is local_mock.call_args.args[0]
        assert local_mock.call_args.kwargs == {
            "update_approved": False,
            "reporter": reporter,
        }
        extended_mock.assert_called_once_with(run_config, reporter=reporter)

    @staticmethod
    def test_image_setup_plan_true_when_pull_needed() -> None:
        run_config = _run_config(build_local=False, extensions=[])
        reporter = mock.Mock()

        with mock.patch(
            "aicage.registry.ensure_image.pull_decision_plan",
            return_value=mock.Mock(action=_PullDecisionAction.PULL),
        ):
            assert (
                image_setup_plan(run_config, reporter).action is ImageSetupAction.SETUP
            )

    @staticmethod
    def test_image_setup_plan_false_when_pull_not_needed_and_no_extensions() -> None:
        run_config = _run_config(build_local=False, extensions=[])
        reporter = mock.Mock()

        with mock.patch(
            "aicage.registry.ensure_image.pull_decision_plan",
            return_value=mock.Mock(action=_PullDecisionAction.SKIP),
        ):
            assert (
                image_setup_plan(run_config, reporter).action is ImageSetupAction.SKIP
            )

    @staticmethod
    def test_image_setup_plan_true_when_extensions_need_build() -> None:
        run_config = _run_config(build_local=False, extensions=["extra"])
        reporter = mock.Mock()

        with (
            mock.patch(
                "aicage.registry.ensure_image.pull_decision_plan",
                return_value=mock.Mock(action=_PullDecisionAction.SKIP),
            ),
            mock.patch(
                "aicage.registry.ensure_image.extension_build_needed", return_value=True
            ),
        ):
            assert (
                image_setup_plan(run_config, reporter).action is ImageSetupAction.SETUP
            )

    @staticmethod
    def test_image_setup_plan_true_for_local_build_without_running_preflight() -> None:
        run_config = _run_config(build_local=True, extensions=[])
        reporter = mock.Mock()

        with mock.patch(
            "aicage.registry.ensure_image.agent_build_setup_plan",
            return_value=AgentBuildSetupAction.BUILD,
        ) as setup_plan_mock:
            assert (
                image_setup_plan(run_config, reporter).action is ImageSetupAction.SETUP
            )
        setup_plan_mock.assert_called_once_with(run_config, reporter)

    @staticmethod
    def test_image_setup_plan_reports_confirmation_when_remote_pull_differs() -> None:
        run_config = _run_config(build_local=False, extensions=[])
        reporter = mock.Mock()

        with mock.patch(
            "aicage.registry.ensure_image.pull_decision_plan",
            return_value=mock.Mock(action=_PullDecisionAction.CONFIRM_PULL),
        ):
            plan = image_setup_plan(run_config, reporter)

        assert plan.action is ImageSetupAction.CONFIRM_UPDATE
        assert plan.image_ref == run_config.selection.base_image_ref

    @staticmethod
    def test_image_setup_plan_skips_when_local_build_is_current() -> None:
        run_config = _run_config(build_local=True, extensions=[])
        reporter = mock.Mock()

        with mock.patch(
            "aicage.registry.ensure_image.agent_build_setup_plan",
            return_value=AgentBuildSetupAction.USE_LOCAL,
        ) as setup_plan_mock:
            plan = image_setup_plan(run_config, reporter)

        assert plan.action is ImageSetupAction.SKIP
        assert (
            plan.image_ref == f"{IMAGE_REGISTRY}/{IMAGE_BASE_REPOSITORY}:ubuntu"
        )
        setup_plan_mock.assert_called_once_with(run_config, reporter)

    @staticmethod
    def test_image_setup_plan_reports_confirmation_for_local_build_update() -> None:
        run_config = _run_config(build_local=True, extensions=[])
        reporter = mock.Mock()

        with mock.patch(
            "aicage.registry.ensure_image.agent_build_setup_plan",
            return_value=AgentBuildSetupAction.CONFIRM_UPDATE,
        ) as setup_plan_mock:
            plan = image_setup_plan(run_config, reporter)

        assert plan.action is ImageSetupAction.CONFIRM_UPDATE_AND_DO_SETUP
        assert (
            plan.image_ref == f"{IMAGE_REGISTRY}/{IMAGE_BASE_REPOSITORY}:ubuntu"
        )
        setup_plan_mock.assert_called_once_with(run_config, reporter)


def _run_config(
    build_local: bool,
    extensions: list[str],
    *,
    base: str = "ubuntu",
    base_definition_dir: Path | None = None,
) -> RunConfig:
    base_dir = base_definition_dir or Path("/test-tmp/base")
    run_config = mock.Mock(spec=RunConfig)
    run_config.agent = "codex"
    run_config.selection = mock.Mock()
    run_config.selection.base = base
    run_config.selection.base_image_ref = "ghcr.io/aicage/aicage:codex-ubuntu"
    run_config.selection.extensions = extensions
    run_config.context = mock.Mock()
    run_config.context.bases = {
        base: BaseMetadata(
            from_image="ubuntu:latest",
            base_image_distro="Ubuntu",
            base_image_description="Default",
            architectures=["amd64", "arm64"],
            build_local=False,
            local_definition_dir=base_dir,
        )
    }
    run_config.context.agents = {
        "codex": AgentMetadata(
            agent_path_files=[],
            agent_path_directories=["~/.custom"],
            agent_full_name="Custom",
            agent_homepage="https://example.com",
            build_local=build_local,
            valid_bases={},
            local_definition_dir=Path("/test-tmp/agent"),
        )
    }
    return run_config
