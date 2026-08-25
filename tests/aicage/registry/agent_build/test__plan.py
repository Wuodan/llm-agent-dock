from unittest import TestCase, mock

from aicage.registry.agent_build import _plan
from aicage.registry.agent_build._store import BuildRecord

from ..._run_config_fixtures import build_run_config


class LocalBuildPlanTests(TestCase):
    def test_should_rebuild_when_missing_local_image(self) -> None:
        run_config = build_run_config()
        with mock.patch(
            "aicage.registry.agent_build._plan.local_image_exists",
            return_value=False,
        ):
            should_rebuild = _plan.should_rebuild(
                run_config,
                None,
                "1.2.3",
                "ghcr.io/aicage/aicage-image-base@sha256:base",
            )
        self.assertTrue(should_rebuild)

    def test_should_rebuild_when_record_missing(self) -> None:
        run_config = build_run_config()
        with mock.patch(
            "aicage.registry.agent_build._plan.local_image_exists",
            return_value=True,
        ):
            should_rebuild = _plan.should_rebuild(
                run_config,
                None,
                "1.2.3",
                "ghcr.io/aicage/aicage-image-base@sha256:base",
            )
        self.assertTrue(should_rebuild)

    def test_should_rebuild_when_agent_version_changes(self) -> None:
        run_config = build_run_config()
        record = BuildRecord(
            agent="claude",
            base="ubuntu",
            agent_version="1.2.2",
            base_image="ghcr.io/aicage/aicage-image-base:ubuntu",
            image_ref="aicage:claude-ubuntu",
            built_at="2024-01-01T00:00:00+00:00",
            image_id="sha256:current",
        )
        with (
            mock.patch(
                "aicage.registry.agent_build._plan.local_image_exists",
                return_value=True,
            ),
            mock.patch(
                "aicage.registry.agent_build._plan.base_layer_missing",
                return_value=False,
            ),
        ):
            should_rebuild = _plan.should_rebuild(
                run_config,
                record,
                "1.2.3",
                "ghcr.io/aicage/aicage-image-base@sha256:base",
            )
        self.assertTrue(should_rebuild)

    def test_should_rebuild_when_record_has_no_image_id(self) -> None:
        run_config = build_run_config()
        record = BuildRecord(
            agent="claude",
            base="ubuntu",
            agent_version="1.2.3",
            base_image="ghcr.io/aicage/aicage-image-base:ubuntu",
            image_ref="aicage:claude-ubuntu",
            built_at="2024-01-01T00:00:00+00:00",
            image_id="",
        )
        with mock.patch(
            "aicage.registry.agent_build._plan.local_image_exists",
            return_value=True,
        ):
            should_rebuild = _plan.should_rebuild(
                run_config,
                record,
                "1.2.3",
                "ghcr.io/aicage/aicage-image-base@sha256:base",
            )
        self.assertTrue(should_rebuild)

    def test_should_rebuild_when_local_image_id_changes(self) -> None:
        run_config = build_run_config()
        record = BuildRecord(
            agent="claude",
            base="ubuntu",
            agent_version="1.2.3",
            base_image="ghcr.io/aicage/aicage-image-base:ubuntu",
            image_ref="aicage:claude-ubuntu",
            built_at="2024-01-01T00:00:00+00:00",
            image_id="sha256:current",
        )
        with (
            mock.patch(
                "aicage.registry.agent_build._plan.local_image_exists",
                return_value=True,
            ),
            mock.patch(
                "aicage.registry.agent_build._plan.get_local_image_id",
                return_value="sha256:stale",
            ),
        ):
            should_rebuild = _plan.should_rebuild(
                run_config,
                record,
                "1.2.3",
                "ghcr.io/aicage/aicage-image-base@sha256:base",
            )
        self.assertTrue(should_rebuild)

    def test_should_rebuild_when_base_layer_missing(self) -> None:
        run_config = build_run_config()
        record = BuildRecord(
            agent="claude",
            base="ubuntu",
            agent_version="1.2.3",
            base_image="ghcr.io/aicage/aicage-image-base:ubuntu",
            image_ref="aicage:claude-ubuntu",
            built_at="2024-01-01T00:00:00+00:00",
            image_id="sha256:current",
        )
        with (
            mock.patch(
                "aicage.registry.agent_build._plan.local_image_exists",
                return_value=True,
            ),
            mock.patch(
                "aicage.registry.agent_build._plan.get_local_image_id",
                return_value="sha256:current",
            ),
            mock.patch(
                "aicage.registry.agent_build._plan.base_layer_missing",
                return_value=True,
            ),
        ):
            should_rebuild = _plan.should_rebuild(
                run_config,
                record,
                "1.2.3",
                "ghcr.io/aicage/aicage-image-base@sha256:base",
            )
        self.assertTrue(should_rebuild)

    def test_should_rebuild_false_when_layer_data_missing(self) -> None:
        run_config = build_run_config()
        record = BuildRecord(
            agent="claude",
            base="ubuntu",
            agent_version="1.2.3",
            base_image="ghcr.io/aicage/aicage-image-base:ubuntu",
            image_ref="aicage:claude-ubuntu",
            built_at="2024-01-01T00:00:00+00:00",
            image_id="sha256:current",
        )
        with (
            mock.patch(
                "aicage.registry.agent_build._plan.local_image_exists",
                return_value=True,
            ),
            mock.patch(
                "aicage.registry.agent_build._plan.get_local_image_id",
                return_value="sha256:current",
            ),
            mock.patch(
                "aicage.registry.agent_build._plan.base_layer_missing",
                return_value=False,
            ),
        ):
            should_rebuild = _plan.should_rebuild(
                run_config,
                record,
                "1.2.3",
                "ghcr.io/aicage/aicage-image-base@sha256:base",
            )
        self.assertFalse(should_rebuild)

    def test_should_rebuild_false_when_up_to_date(self) -> None:
        run_config = build_run_config()
        record = BuildRecord(
            agent="claude",
            base="ubuntu",
            agent_version="1.2.3",
            base_image="ghcr.io/aicage/aicage-image-base:ubuntu",
            image_ref="aicage:claude-ubuntu",
            built_at="2024-01-01T00:00:00+00:00",
            image_id="sha256:current",
        )
        with (
            mock.patch(
                "aicage.registry.agent_build._plan.local_image_exists",
                return_value=True,
            ),
            mock.patch(
                "aicage.registry.agent_build._plan.get_local_image_id",
                return_value="sha256:current",
            ),
            mock.patch(
                "aicage.registry.agent_build._plan.base_layer_missing",
                return_value=False,
            ),
        ):
            should_rebuild = _plan.should_rebuild(
                run_config,
                record,
                "1.2.3",
                "ghcr.io/aicage/aicage-image-base@sha256:base",
            )
        self.assertFalse(should_rebuild)
