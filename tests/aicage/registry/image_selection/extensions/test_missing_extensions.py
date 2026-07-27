import tempfile
from pathlib import Path
from unittest import TestCase, mock

from aicage.config.context import ConfigContext
from aicage.config.extensions.loader import ExtensionMetadata
from aicage.config.project_config import AgentConfig, _ProjectConfig
from aicage.registry.image_selection.extensions.missing_extensions import (
    ensure_extensions_exist,
)


class MissingExtensionsTests(TestCase):
    def test_ensure_extensions_exist_returns_false_when_available(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            extension = ExtensionMetadata(
                extension_id="extra",
                name="Extra",
                description="Extra tools",
                shares=[],
                directory=Path(tmp_dir),
                scripts_dir=Path(tmp_dir),
                dockerfile_path=None,
            )
            agent_cfg = AgentConfig(
                extensions=["extra"], image_ref="aicage:codex-ubuntu"
            )
            save_project_mock = mock.Mock()
            context = self._context(
                tmp_dir,
                agent_cfg,
                save_project_mock,
                extensions={"extra": extension},
            )

            result = ensure_extensions_exist(
                agent="codex",
                context=context,
            )

            self.assertFalse(result)
            save_project_mock.assert_not_called()

    def test_ensure_extensions_exist_removes_missing_extensions(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            agent_cfg = AgentConfig(
                base="ubuntu",
                extensions=["extra", "kept"],
                image_ref="aicage:codex-ubuntu",
                extension_mounts={"extra": True, "kept": True},
            )
            extension = ExtensionMetadata(
                extension_id="kept",
                name="Kept",
                description="Kept tools",
                shares=[],
                directory=Path(tmp_dir),
                scripts_dir=Path(tmp_dir),
                dockerfile_path=None,
            )
            save_project_mock = mock.Mock()
            context = self._context(
                tmp_dir,
                agent_cfg,
                save_project_mock,
                extensions={"kept": extension},
            )

            result = ensure_extensions_exist(
                agent="codex",
                context=context,
            )

            self.assertTrue(result)
            self.assertEqual(["kept"], context.project_cfg.agents["codex"].extensions)
            self.assertEqual(
                {"kept": True}, context.project_cfg.agents["codex"].extension_mounts
            )
            self.assertEqual(
                "aicage-extended:codex-ubuntu-kept",
                context.project_cfg.agents["codex"].image_ref,
            )
            save_project_mock.assert_not_called()

    def test_ensure_extensions_exist_preserves_remaining_extension_order(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            agent_cfg = AgentConfig(
                base="ubuntu",
                extensions=["zeta", "alpha", "missing"],
                image_ref="aicage:codex-ubuntu",
                extension_mounts={"zeta": True, "alpha": True, "missing": True},
            )
            context = self._context(
                tmp_dir,
                agent_cfg,
                extensions={
                    "zeta": ExtensionMetadata(
                        extension_id="zeta",
                        name="Zeta",
                        description="Dockerfile extension",
                        shares=[],
                        directory=Path(tmp_dir) / "zeta",
                        scripts_dir=Path(tmp_dir) / "zeta" / "scripts",
                        dockerfile_path=Path(tmp_dir) / "zeta" / "Dockerfile",
                    ),
                    "alpha": ExtensionMetadata(
                        extension_id="alpha",
                        name="Alpha",
                        description="Script extension",
                        shares=[],
                        directory=Path(tmp_dir) / "alpha",
                        scripts_dir=Path(tmp_dir) / "alpha" / "scripts",
                        dockerfile_path=None,
                    ),
                },
            )

            ensure_extensions_exist(agent="codex", context=context)

        self.assertEqual(
            ["zeta", "alpha"],
            context.project_cfg.agents["codex"].extensions,
        )
        self.assertEqual(
            {"zeta": True, "alpha": True},
            context.project_cfg.agents["codex"].extension_mounts,
        )
        self.assertEqual(
            "aicage-extended:codex-ubuntu-alpha-zeta",
            context.project_cfg.agents["codex"].image_ref,
        )

    def test_ensure_extensions_exist_clears_image_ref_when_no_extensions_remain(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            agent_cfg = AgentConfig(
                base="ubuntu", extensions=["extra"], image_ref="repo:tag"
            )
            context = self._context(tmp_dir, agent_cfg)

            result = ensure_extensions_exist(
                agent="codex",
                context=context,
            )

        self.assertTrue(result)
        self.assertEqual([], context.project_cfg.agents["codex"].extensions)
        self.assertIsNone(context.project_cfg.agents["codex"].image_ref)

    @staticmethod
    def _context(
        tmp_dir: str,
        agent_cfg: AgentConfig,
        save_project_mock: mock.Mock | None = None,
        extensions: dict[str, ExtensionMetadata] | None = None,
    ) -> ConfigContext:
        store = mock.Mock()
        store.projects_dir = Path(tmp_dir)
        if save_project_mock is not None:
            store.save_project = save_project_mock
        project_cfg = _ProjectConfig(
            path=str(Path(tmp_dir) / "project"), agents={"codex": agent_cfg}
        )
        return ConfigContext(
            store=store,
            project_cfg=project_cfg,
            agents={},
            bases={},
            extensions=extensions or {},
        )
