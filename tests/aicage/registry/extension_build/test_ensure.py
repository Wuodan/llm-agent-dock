from pathlib import Path
from unittest import TestCase, mock

from aicage.config.agent.models import AgentMetadata
from aicage.config.base.models import BaseMetadata
from aicage.config.context import ConfigContext
from aicage.config.extensions.loader import ExtensionMetadata
from aicage.config.project_config import _ProjectConfig
from aicage.config.runtime_config import RunConfig
from aicage.constants import DEFAULT_EXTENDED_IMAGE_NAME
from aicage.registry._errors import RegistryError
from aicage.registry.extension_build._store import BuildRecord
from aicage.registry.extension_build.ensure import build_needed, ensure
from aicage.registry.image_selection.models import ImageSelection


class EnsureExtendedImageTests(TestCase):
    def test_ensure_raises_without_extensions(self) -> None:
        run_config = self._run_config(extensions=[])
        with self.assertRaises(RegistryError):
            ensure(run_config)

    def test_ensure_raises_on_missing_extension(self) -> None:
        run_config = self._run_config(extensions=["missing"], available_extensions={})
        with self.assertRaises(RegistryError):
            ensure(run_config)

    def test_ensure_skips_when_not_needed(self) -> None:
        extension = self._extension("ext")
        run_config = self._run_config(
            extensions=["ext"],
            local_definition_dir=Path("/test-tmp/def"),
            available_extensions={"ext": extension},
        )
        store = mock.Mock()
        store.load.return_value = None
        with (
            mock.patch(
                "aicage.registry.extension_build.ensure.BuildStore",
                return_value=store,
            ),
            mock.patch(
                "aicage.registry.extension_build.ensure.extension_hash",
                return_value="hash",
            ),
            mock.patch(
                "aicage.registry.extension_build.ensure.should_rebuild",
                return_value=False,
            ),
            mock.patch("aicage.registry.extension_build.ensure.run") as run_mock,
        ):
            ensure(run_config)
        run_mock.assert_not_called()
        store.save.assert_not_called()

    def test_ensure_builds_when_needed(self) -> None:
        extension = self._extension("ext")
        run_config = self._run_config(
            extensions=["ext"],
            build_local=True,
            local_definition_dir=Path("/test-tmp/def"),
            available_extensions={"ext": extension},
        )
        store = mock.Mock()
        store.load.return_value = None
        with (
            mock.patch(
                "aicage.registry.extension_build.ensure.BuildStore",
                return_value=store,
            ),
            mock.patch(
                "aicage.registry.extension_build.ensure.extension_hash",
                return_value="hash",
            ),
            mock.patch(
                "aicage.registry.extension_build.ensure.should_rebuild",
                return_value=True,
            ),
            mock.patch("aicage.registry.extension_build.ensure.run") as run_mock,
            mock.patch(
                "aicage.registry.extension_build.ensure.get_local_repo_digest_for_repo",
                return_value="sha256:old",
            ),
            mock.patch(
                "aicage.registry.extension_build.ensure.cleanup_old_digest"
            ) as cleanup_mock,
            mock.patch(
                "aicage.registry.extension_build.ensure.build_log_path",
                return_value=Path("/test-tmp/logs/build.log"),
            ),
            mock.patch(
                "aicage.registry.extension_build.ensure.now_iso",
                return_value="2024-01-01T00:00:00+00:00",
            ),
        ):
            ensure(run_config)
        run_mock.assert_called_once()
        cleanup_mock.assert_called_once_with(
            DEFAULT_EXTENDED_IMAGE_NAME,
            "sha256:old",
            f"{DEFAULT_EXTENDED_IMAGE_NAME}:codex-ubuntu-ext",
        )
        store.save.assert_called_once()
        record = store.save.call_args.args[0]
        self.assertIsInstance(record, BuildRecord)

    def test_build_needed_uses_should_rebuild_result(self) -> None:
        extension = self._extension("ext")
        run_config = self._run_config(
            extensions=["ext"],
            local_definition_dir=Path("/test-tmp/def"),
            available_extensions={"ext": extension},
        )
        store = mock.Mock()
        store.load.return_value = None

        with (
            mock.patch(
                "aicage.registry.extension_build.ensure.BuildStore",
                return_value=store,
            ),
            mock.patch(
                "aicage.registry.extension_build.ensure.extension_hash",
                return_value="hash",
            ),
            mock.patch(
                "aicage.registry.extension_build.ensure.should_rebuild",
                return_value=True,
            ) as should_rebuild_mock,
        ):
            assert build_needed(run_config) is True

        should_rebuild_mock.assert_called_once()

    @staticmethod
    def _extension(extension_id: str) -> ExtensionMetadata:
        return ExtensionMetadata(
            extension_id=extension_id,
            name=extension_id,
            description="desc",
            shares=[],
            directory=Path("/test-tmp/ext"),
            scripts_dir=Path("/test-tmp/ext/scripts"),
            dockerfile_path=None,
        )

    @staticmethod
    def _run_config(
        extensions: list[str],
        build_local: bool = False,
        local_definition_dir: Path = Path("/test-tmp/def"),
        available_extensions: dict[str, ExtensionMetadata] | None = None,
    ) -> RunConfig:
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
        agents = {
            "codex": AgentMetadata(
                agent_path_files=[],
                agent_path_directories=["~/.codex"],
                agent_full_name="Codex",
                agent_homepage="https://example.com",
                build_local=build_local,
                valid_bases={"ubuntu": "ghcr.io/aicage/aicage:codex-ubuntu"},
                local_definition_dir=local_definition_dir,
            )
        }
        return RunConfig(
            project_path=Path("/test-tmp/project"),
            agent="codex",
            context=ConfigContext(
                store=mock.Mock(),
                project_cfg=_ProjectConfig(path="/test-tmp/project", agents={}),
                agents=agents,
                bases=bases,
                extensions=available_extensions or {},
            ),
            selection=ImageSelection(
                image_ref=f"{DEFAULT_EXTENDED_IMAGE_NAME}:codex-ubuntu-ext",
                base="ubuntu",
                extensions=extensions,
                base_image_ref="ghcr.io/aicage/aicage:codex-ubuntu",
            ),
            project_docker_args="",
            mounts=[],
            env=[],
        )
