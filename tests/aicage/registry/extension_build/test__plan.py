from unittest import TestCase, mock

from aicage.config.runtime_config import RunConfig
from aicage.registry.extension_build._plan import should_rebuild
from aicage.registry.extension_build._store import BuildRecord

from ..._run_config_fixtures import build_extended_run_config


class ExtendedPlanTests(TestCase):
    def test_should_rebuild_when_local_image_missing(self) -> None:
        run_config = self._run_config()
        record = self._record(run_config)
        with mock.patch(
            "aicage.registry.extension_build._plan.local_image_exists",
            return_value=False,
        ):
            self.assertTrue(
                should_rebuild(
                    run_config=run_config,
                    record=record,
                    agent_image_ref=run_config.selection.agent_image_ref,
                    extension_hash=record.extension_hash,
                )
            )

    def test_should_rebuild_returns_false_when_layers_unknown(self) -> None:
        run_config = self._run_config()
        record = self._record(run_config)
        with (
            mock.patch(
                "aicage.registry.extension_build._plan.local_image_exists",
                return_value=True,
            ),
            mock.patch(
                "aicage.registry._layers.get_local_rootfs_layers",
                return_value=None,
            ),
        ):
            self.assertFalse(
                should_rebuild(
                    run_config=run_config,
                    record=record,
                    agent_image_ref=run_config.selection.agent_image_ref,
                    extension_hash=record.extension_hash,
                )
            )

    def test_should_rebuild_when_base_layer_missing(self) -> None:
        run_config = self._run_config()
        record = self._record(run_config)
        with (
            mock.patch(
                "aicage.registry.extension_build._plan.local_image_exists",
                return_value=True,
            ),
            mock.patch(
                "aicage.registry._layers.get_local_rootfs_layers",
                side_effect=[["layer-a"], ["layer-b"]],
            ),
        ):
            self.assertTrue(
                should_rebuild(
                    run_config=run_config,
                    record=record,
                    agent_image_ref=run_config.selection.agent_image_ref,
                    extension_hash=record.extension_hash,
                )
            )

    def test_should_rebuild_returns_false_when_final_layers_unknown(self) -> None:
        run_config = self._run_config()
        record = self._record(run_config)
        with (
            mock.patch(
                "aicage.registry.extension_build._plan.local_image_exists",
                return_value=True,
            ),
            mock.patch(
                "aicage.registry._layers.get_local_rootfs_layers",
                side_effect=[["layer-a"], None],
            ),
        ):
            self.assertFalse(
                should_rebuild(
                    run_config=run_config,
                    record=record,
                    agent_image_ref=run_config.selection.agent_image_ref,
                    extension_hash=record.extension_hash,
                )
            )

    @staticmethod
    def _run_config() -> RunConfig:
        return build_extended_run_config()

    @staticmethod
    def _record(run_config: RunConfig) -> BuildRecord:
        return BuildRecord(
            agent=run_config.agent,
            base=run_config.selection.base,
            image_ref=run_config.selection.image_ref,
            extensions=list(run_config.selection.extensions),
            extension_hash="hash",
            base_image=run_config.selection.agent_image_ref,
            built_at="2024-01-01T00:00:00+00:00",
        )
