import tempfile
from pathlib import Path
from unittest import TestCase, mock

import yaml

from aicage.config.base.models import BaseMetadata
from aicage.constants import LOCAL_IMAGE_BASE_REPOSITORY
from aicage.docker.errors import DockerError
from aicage.registry.base_build import ensure as _ensure
from aicage.registry.base_build._store import (
    BuildRecord,
    BuildStore,
)


class EnsureCustomBaseImageTests(TestCase):
    def test_image_ref_uses_base_repository(self) -> None:
        self.assertEqual(
            f"{LOCAL_IMAGE_BASE_REPOSITORY}:custom",
            _ensure.image_ref("custom"),
        )

    def test_ensure_builds_when_missing(self) -> None:
        base_metadata = self._base_metadata()
        with tempfile.TemporaryDirectory() as tmp_dir:
            base_dir = Path(tmp_dir) / "custom"
            base_dir.mkdir()
            (base_dir / "Dockerfile").write_text(
                "FROM ${FROM_IMAGE}\n", encoding="utf-8"
            )
            state_dir = Path(tmp_dir) / "state"
            with (
                mock.patch(
                    "aicage.registry.base_build._store.paths_module.BASE_IMAGE_BUILD_STATE_DIR",
                    state_dir,
                ),
                mock.patch(
                    "aicage.registry.base_build.ensure.local_image_exists",
                    return_value=False,
                ),
                mock.patch(
                    "aicage.registry.base_build.ensure.get_remote_digest",
                    return_value="sha256:remote",
                ),
                mock.patch("aicage.registry.base_build.ensure.run") as build_mock,
            ):
                _ensure.ensure("custom", base_metadata, base_dir)

            build_mock.assert_called_once()
            record_path = state_dir / "base-custom.yml"
            payload = yaml.safe_load(record_path.read_text(encoding="utf-8"))
            self.assertEqual("custom", payload["base"])
            self.assertEqual("sha256:remote", payload["from_image_digest"])

    def test_ensure_skips_when_digest_matches(self) -> None:
        base_metadata = self._base_metadata()
        with tempfile.TemporaryDirectory() as tmp_dir:
            base_dir = Path(tmp_dir) / "custom"
            base_dir.mkdir()
            (base_dir / "Dockerfile").write_text(
                "FROM ${FROM_IMAGE}\n", encoding="utf-8"
            )
            state_dir = Path(tmp_dir) / "state"
            with (
                mock.patch(
                    "aicage.registry.base_build._store.paths_module.BASE_IMAGE_BUILD_STATE_DIR",
                    state_dir,
                ),
                mock.patch(
                    "aicage.registry.base_build.ensure.local_image_exists",
                    return_value=True,
                ),
                mock.patch(
                    "aicage.registry.base_build.ensure.get_remote_digest",
                    return_value="sha256:remote",
                ),
                mock.patch("aicage.registry.base_build.ensure.run") as build_mock,
            ):
                store = BuildStore()
                store.save(
                    BuildRecord(
                        base="custom",
                        from_image=base_metadata.from_image,
                        from_image_digest="sha256:remote",
                        image_ref=_ensure.image_ref("custom"),
                        built_at="2024-01-01T00:00:00+00:00",
                    )
                )
                _ensure.ensure("custom", base_metadata, base_dir)

            build_mock.assert_not_called()

    def test_ensure_raises_on_build_failure(self) -> None:
        base_metadata = self._base_metadata()
        with tempfile.TemporaryDirectory() as tmp_dir:
            base_dir = Path(tmp_dir) / "custom"
            base_dir.mkdir()
            (base_dir / "Dockerfile").write_text(
                "FROM ${FROM_IMAGE}\n", encoding="utf-8"
            )
            state_dir = Path(tmp_dir) / "state"
            with (
                mock.patch(
                    "aicage.registry.base_build._store.paths_module.BASE_IMAGE_BUILD_STATE_DIR",
                    state_dir,
                ),
                mock.patch(
                    "aicage.registry.base_build.ensure.local_image_exists",
                    return_value=True,
                ),
                mock.patch(
                    "aicage.registry.base_build.ensure.get_remote_digest",
                    return_value="sha256:remote",
                ),
                mock.patch(
                    "aicage.registry.base_build.ensure.run",
                    side_effect=DockerError("build failed"),
                ),
            ):
                with self.assertRaises(DockerError):
                    _ensure.ensure("custom", base_metadata, base_dir)

    @staticmethod
    def test_ensure_cleans_up_old_digest() -> None:
        base_metadata = BaseMetadata(
            from_image="ubuntu:latest",
            base_image_distro="Ubuntu",
            base_image_description="Custom",
            architectures=["amd64", "arm64"],
            build_local=True,
            local_definition_dir=Path("/test-tmp/custom-base"),
        )
        with (
            mock.patch(
                "aicage.registry.base_build.ensure.local_image_exists",
                return_value=True,
            ),
            mock.patch("aicage.registry.base_build.ensure.BuildStore") as store_cls,
            mock.patch(
                "aicage.registry.base_build.ensure._should_rebuild",
                return_value=True,
            ),
            mock.patch("aicage.registry.base_build.ensure.run") as build_mock,
            mock.patch(
                "aicage.registry.base_build.ensure.get_remote_digest",
                return_value="sha256:remote",
            ),
            mock.patch(
                "aicage.registry.base_build.ensure.get_local_repo_digest_for_repo",
                return_value="sha256:old",
            ),
            mock.patch(
                "aicage.registry.base_build.ensure.cleanup_old_digest"
            ) as cleanup_mock,
            mock.patch(
                "aicage.registry.base_build.ensure.build_log_path",
                return_value=Path("/test-tmp/logs/custom-base.log"),
            ),
            mock.patch(
                "aicage.registry.base_build.ensure.now_iso",
                return_value="2024-01-01T00:00:00+00:00",
            ),
        ):
            store_cls.return_value.load.return_value = None
            _ensure.ensure("custom", base_metadata, Path("/test-tmp/custom-base"))

        build_mock.assert_called_once()
        cleanup_mock.assert_called_once_with(
            LOCAL_IMAGE_BASE_REPOSITORY,
            "sha256:old",
            f"{LOCAL_IMAGE_BASE_REPOSITORY}:custom",
        )

    def test_ensure_reads_source_digest(self) -> None:
        base_metadata = self._base_metadata()
        with (
            mock.patch(
                "aicage.registry.base_build.ensure.local_image_exists",
                return_value=False,
            ),
            mock.patch("aicage.registry.base_build.ensure.BuildStore") as store_cls,
            mock.patch(
                "aicage.registry.base_build.ensure.get_remote_digest",
                return_value="sha256:remote",
            ) as digest_mock,
            mock.patch("aicage.registry.base_build.ensure.run"),
            mock.patch(
                "aicage.registry.base_build.ensure.build_log_path",
                return_value=Path("/test-tmp/logs/custom-base.log"),
            ),
            mock.patch(
                "aicage.registry.base_build.ensure.now_iso",
                return_value="2024-01-01T00:00:00+00:00",
            ),
        ):
            store_cls.return_value.load.return_value = None
            _ensure.ensure(
                "custom",
                base_metadata,
                Path("/test-tmp/custom-base"),
            )
        digest_mock.assert_called_once_with("ubuntu:latest")

    def test_build_needed_uses_should_rebuild_result(self) -> None:
        base_metadata = self._base_metadata()

        with (
            mock.patch(
                "aicage.registry.base_build.ensure.local_image_exists",
                return_value=True,
            ),
            mock.patch("aicage.registry.base_build.ensure.BuildStore") as store_cls,
            mock.patch(
                "aicage.registry.base_build.ensure.get_remote_digest",
                return_value="sha256:remote",
            ),
            mock.patch(
                "aicage.registry.base_build.ensure._should_rebuild",
                return_value=True,
            ) as should_rebuild_mock,
        ):
            store_cls.return_value.load.return_value = None
            assert (
                _ensure.build_needed(
                    "custom", base_metadata, _ensure.image_ref("custom")
                )
                is True
            )

        should_rebuild_mock.assert_called_once()

    @staticmethod
    def _base_metadata() -> BaseMetadata:
        return BaseMetadata(
            from_image="ubuntu:latest",
            base_image_distro="Ubuntu",
            base_image_description="Custom",
            architectures=["amd64", "arm64"],
            build_local=True,
            local_definition_dir=Path("/test-tmp/base"),
        )


class CustomBasePlanTests(TestCase):
    def test_should_rebuild_false_when_metadata_and_digest_match(self) -> None:
        should_rebuild = _ensure._should_rebuild(
            local_exists=True,
            record=BuildRecord(
                base="custom",
                from_image="ubuntu:latest",
                from_image_digest="sha256:remote",
                image_ref=_ensure.image_ref("custom"),
                built_at="2024-01-01T00:00:00+00:00",
            ),
            base_metadata=EnsureCustomBaseImageTests._base_metadata(),
            source_digest="sha256:remote",
        )
        self.assertFalse(should_rebuild)
