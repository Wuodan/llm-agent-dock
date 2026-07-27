import tempfile
from pathlib import Path
from unittest import TestCase, mock

import yaml

from aicage.config.base.models import BaseMetadata
from aicage.config.runtime_config import RunConfig
from aicage.paths import CUSTOM_BASES_DIR
from aicage.registry._errors import RegistryError
from aicage.registry.agent_build import ensure as ensure_module
from aicage.registry.agent_build._refresh import _BaseRefreshAction
from aicage.registry.agent_build._store import (
    _AGENT_KEY,
    _AGENT_VERSION_KEY,
    _BASE_IMAGE_KEY,
    _BASE_KEY,
    _BUILT_AT_KEY,
    _IMAGE_REF_KEY,
)
from aicage.registry.agent_build.ensure import _AgentBuildSetupAction
from aicage.registry.image_selection.models import ImageSelection

from ..._run_config_fixtures import build_custom_run_config, build_run_config


class EnsureLocalImageTests(TestCase):
    @staticmethod
    def test_ensure_runs_for_custom_agent() -> None:
        run_config = build_custom_run_config()
        reporter = mock.Mock()
        with tempfile.TemporaryDirectory() as tmp_dir:
            state_dir = Path(tmp_dir) / "state"
            with (
                mock.patch(
                    "aicage.registry.agent_build._store.paths_module.IMAGE_BUILD_STATE_DIR",
                    state_dir,
                ),
                mock.patch(
                    "aicage.registry.agent_build.ensure.refresh_base_image",
                    return_value="ghcr.io/aicage/aicage-image-base@sha256:base",
                ) as refresh_mock,
                mock.patch(
                    "aicage.registry.agent_build.ensure.should_rebuild",
                    return_value=False,
                ),
                mock.patch(
                    "aicage.registry.agent_build.ensure.AgentVersionChecker"
                ) as checker_cls,
            ):
                checker_cls.return_value.get_version.return_value = "1.2.3"
                ensure_module.ensure(
                    run_config, update_approved=False, reporter=reporter
                )
            refresh_mock.assert_called_once()

    def test_ensure_raises_on_version_failure(self) -> None:
        run_config = build_run_config()
        reporter = mock.Mock()
        with (
            mock.patch(
                "aicage.registry.agent_build.ensure.refresh_base_image",
                return_value="ghcr.io/aicage/aicage-image-base@sha256:base",
            ),
            mock.patch(
                "aicage.registry.agent_build.ensure.AgentVersionChecker"
            ) as checker_cls,
        ):
            checker_cls.return_value.get_version.side_effect = RegistryError(
                "version failed"
            )
            with self.assertRaises(RegistryError):
                ensure_module.ensure(
                    run_config, update_approved=False, reporter=reporter
                )

    @staticmethod
    def test_ensure_uses_local_agent_image_when_base_refresh_fails() -> None:
        run_config = build_run_config()
        reporter = mock.Mock()
        with (
            mock.patch(
                "aicage.registry.agent_build.ensure.refresh_base_image",
                side_effect=RegistryError("offline"),
            ),
            mock.patch(
                "aicage.registry.agent_build.ensure.local_image_exists",
                return_value=True,
            ),
            mock.patch(
                "aicage.registry.agent_build.ensure.AgentVersionChecker"
            ) as checker_cls,
            mock.patch("aicage.registry.agent_build.ensure.run") as build_mock,
        ):
            ensure_module.ensure(run_config, update_approved=False, reporter=reporter)
        checker_cls.assert_not_called()
        build_mock.assert_not_called()

    def test_ensure_raises_when_base_refresh_fails_and_agent_image_missing(
        self,
    ) -> None:
        run_config = build_run_config()
        reporter = mock.Mock()
        with (
            mock.patch(
                "aicage.registry.agent_build.ensure.refresh_base_image",
                side_effect=RegistryError("offline"),
            ),
            mock.patch(
                "aicage.registry.agent_build.ensure.local_image_exists",
                return_value=False,
            ),
        ):
            with self.assertRaises(RegistryError) as raised:
                ensure_module.ensure(
                    run_config, update_approved=False, reporter=reporter
                )
        self.assertIn("offline", str(raised.exception))

    @staticmethod
    def test_ensure_uses_custom_base() -> None:
        run_config = build_run_config()
        reporter = mock.Mock()
        run_config = RunConfig(
            project_path=run_config.project_path,
            agent=run_config.agent,
            context=run_config.context,
            selection=ImageSelection(
                image_ref="aicage:claude-custom",
                base="custom",
                extensions=[],
                base_image_ref="aicage:claude-custom",
            ),
            project_docker_args=run_config.project_docker_args,
            mounts=run_config.mounts,
            env=run_config.env,
        )
        custom_base = BaseMetadata(
            from_image="ubuntu:latest",
            base_image_distro="Ubuntu",
            base_image_description="Custom",
            architectures=["amd64", "arm64"],
            build_local=True,
            local_definition_dir=CUSTOM_BASES_DIR / "custom",
        )
        run_config.context.bases["custom"] = custom_base
        with (
            mock.patch(
                "aicage.registry.agent_build.ensure.ensure_base_build"
            ) as base_mock,
            mock.patch(
                "aicage.registry.agent_build.ensure.refresh_base_image"
            ) as refresh_mock,
            mock.patch(
                "aicage.registry.agent_build.ensure.should_rebuild",
                return_value=False,
            ),
            mock.patch(
                "aicage.registry.agent_build.ensure.AgentVersionChecker"
            ) as checker_cls,
        ):
            checker_cls.return_value.get_version.return_value = "1.2.3"
            ensure_module.ensure(run_config, update_approved=False, reporter=reporter)
        base_mock.assert_called_once()
        refresh_mock.assert_not_called()

    def test_ensure_builds_when_missing_image(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            state_dir = Path(tmp_dir) / "state"
            log_dir = Path(tmp_dir) / "logs"
            run_config = build_run_config()
            reporter = mock.Mock()

            with (
                mock.patch(
                    "aicage.registry.agent_build._store.paths_module.IMAGE_BUILD_STATE_DIR",
                    state_dir,
                ),
                mock.patch(
                    "aicage.registry.agent_build._logs.IMAGE_BUILD_LOG_DIR",
                    log_dir,
                ),
                mock.patch(
                    "aicage.registry.agent_build._plan.local_image_exists",
                    return_value=False,
                ),
                mock.patch(
                    "aicage.registry.agent_build.ensure.refresh_base_image",
                    return_value="ghcr.io/aicage/aicage-image-base@sha256:base",
                ) as refresh_mock,
                mock.patch("aicage.registry.agent_build.ensure.run") as build_mock,
                mock.patch(
                    "aicage.registry.agent_build.ensure.get_local_repo_digest_for_repo",
                    return_value="sha256:old",
                ),
                mock.patch(
                    "aicage.registry.agent_build.ensure.cleanup_old_digest"
                ) as cleanup_mock,
                mock.patch(
                    "aicage.registry.agent_build.ensure.AgentVersionChecker"
                ) as checker_cls,
            ):
                checker_cls.return_value.get_version.return_value = "1.2.3"
                ensure_module.ensure(
                    run_config,
                    update_approved=False,
                    reporter=reporter,
                )

            build_mock.assert_called_once()
            refresh_mock.assert_called_once()
            self.assertEqual(reporter, refresh_mock.call_args.kwargs["reporter"])
            cleanup_mock.assert_called_once_with(
                "aicage",
                "sha256:old",
                "aicage:claude-ubuntu",
            )
            record_path = state_dir / "claude-ubuntu.yml"
            payload = yaml.safe_load(record_path.read_text(encoding="utf-8"))
            self.assertEqual("1.2.3", payload[_AGENT_VERSION_KEY])

    @staticmethod
    def test_ensure_skips_when_up_to_date() -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            state_dir = Path(tmp_dir) / "state"
            log_dir = Path(tmp_dir) / "logs"
            run_config = build_run_config()
            reporter = mock.Mock()
            record_path = state_dir / "claude-ubuntu.yml"
            record_path.parent.mkdir(parents=True, exist_ok=True)
            record_path.write_text(
                yaml.safe_dump(
                    {
                        _AGENT_KEY: "claude",
                        _BASE_KEY: "ubuntu",
                        _AGENT_VERSION_KEY: "1.2.3",
                        _BASE_IMAGE_KEY: "ghcr.io/aicage/aicage-image-base:ubuntu",
                        _IMAGE_REF_KEY: "aicage:claude-ubuntu",
                        _BUILT_AT_KEY: "2024-01-01T00:00:00+00:00",
                    }
                ),
                encoding="utf-8",
            )

            with (
                mock.patch(
                    "aicage.registry.agent_build._store.paths_module.IMAGE_BUILD_STATE_DIR",
                    state_dir,
                ),
                mock.patch(
                    "aicage.registry.agent_build._logs.IMAGE_BUILD_LOG_DIR",
                    log_dir,
                ),
                mock.patch(
                    "aicage.registry.agent_build._plan.local_image_exists",
                    return_value=True,
                ),
                mock.patch(
                    "aicage.registry.agent_build.ensure.refresh_base_image",
                    return_value="ghcr.io/aicage/aicage-image-base@sha256:base",
                ),
                mock.patch(
                    "aicage.registry.agent_build._plan.base_layer_missing",
                    return_value=False,
                ),
                mock.patch("aicage.registry.agent_build.ensure.run") as build_mock,
                mock.patch(
                    "aicage.registry.agent_build.ensure.AgentVersionChecker"
                ) as checker_cls,
            ):
                checker_cls.return_value.get_version.return_value = "1.2.3"
                ensure_module.ensure(
                    run_config, update_approved=False, reporter=reporter
                )

            build_mock.assert_not_called()

    @staticmethod
    def test_setup_plan_reports_confirmation_when_base_refresh_requires_it() -> None:
        run_config = build_run_config()
        reporter = mock.Mock()

        with mock.patch(
            "aicage.registry.agent_build.ensure.refresh_base_image_plan",
            return_value=mock.Mock(
                image_ref="ghcr.io/aicage/aicage-image-base@sha256:local",
                action=_BaseRefreshAction.CONFIRM_PULL,
            ),
        ):
            plan = ensure_module.setup_plan(run_config, reporter)

        assert plan.action is _AgentBuildSetupAction.CONFIRM_UPDATE
