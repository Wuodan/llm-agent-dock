import tempfile
from pathlib import Path
from unittest import TestCase, mock

from aicage.cli_types import ParsedArgs
from aicage.errors import AicageError
from aicage.runtime.mounts.shares import merge_share_values, resolve_share_specs


class ShareMountsTests(TestCase):
    def test_merge_share_values_merges_cli_over_existing(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            cwd = Path(tmp_dir)
            existing = [f"{cwd / 'shared'}:ro", str(cwd / 'existing')]
            cli = ["shared", "new"]

            merged, new_shares = merge_share_values(cli, existing, cwd)

        self.assertEqual(
            [str(cwd / "shared"), str(cwd / "new"), str(cwd / "existing")],
            merged,
        )
        self.assertEqual([str(cwd / "new")], new_shares)

    def test_merge_share_values_deduplicates(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            cwd = Path(tmp_dir)
            cli = ["data", "data:ro"]

            merged, new_shares = merge_share_values(cli, [], cwd)

        self.assertEqual([str(cwd / "data")], merged)
        self.assertEqual([str(cwd / "data")], new_shares)

    def test_resolve_share_mounts_resolves_relative_host(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            cwd = Path(tmp_dir)
            share_dir = cwd / "data"
            share_dir.mkdir()
            parsed = ParsedArgs(False, "", "codex", [], False, ["data"], None)

            with mock.patch("aicage.runtime.mounts.shares.Path.cwd", return_value=cwd):
                mounts = resolve_share_specs(parsed.shares, cwd)

        self.assertEqual(1, len(mounts))
        self.assertEqual(share_dir.resolve(), mounts[0].host_path)
        self.assertFalse(mounts[0].read_only)

    def test_resolve_share_mounts_sets_read_only(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            cwd = Path(tmp_dir)
            share_dir = cwd / "data"
            share_dir.mkdir()
            parsed = ParsedArgs(False, "", "codex", [], False, ["data:ro"], None)

            with mock.patch("aicage.runtime.mounts.shares.Path.cwd", return_value=cwd):
                mounts = resolve_share_specs(parsed.shares, cwd)

        self.assertEqual(1, len(mounts))
        self.assertTrue(mounts[0].read_only)

    def test_resolve_share_mounts_skips_duplicates(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            cwd = Path(tmp_dir)
            shared_dir = cwd / "shared"
            shared_dir.mkdir()
            parsed = ParsedArgs(
                False,
                "",
                "codex",
                [],
                False,
                ["shared", "shared:ro"],
                None,
            )

            with mock.patch("aicage.runtime.mounts.shares.Path.cwd", return_value=cwd):
                mounts = resolve_share_specs(parsed.shares, cwd)

        self.assertEqual(1, len(mounts))
        self.assertEqual(shared_dir.resolve(), mounts[0].host_path)

    def test_resolve_share_mounts_does_not_create_missing_dir(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            cwd = Path(tmp_dir)
            parsed = ParsedArgs(False, "", "codex", [], False, ["missing"], None)

            with mock.patch("aicage.runtime.mounts.shares.Path.cwd", return_value=cwd):
                mounts = resolve_share_specs(parsed.shares, cwd)

            self.assertEqual(1, len(mounts))
            self.assertFalse((cwd / "missing").exists())

    def test_resolve_share_mounts_does_not_create_missing_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            cwd = Path(tmp_dir)
            parsed = ParsedArgs(False, "", "codex", [], False, ["missing.txt"], None)

            with mock.patch("aicage.runtime.mounts.shares.Path.cwd", return_value=cwd):
                mounts = resolve_share_specs(parsed.shares, cwd)

            self.assertEqual(1, len(mounts))
            self.assertFalse((cwd / "missing.txt").exists())

    def test_resolve_share_mounts_rejects_destination(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            cwd = Path(tmp_dir)
            parsed = ParsedArgs(False, "", "codex", [], False, ["data:/dst"], None)

            with (
                mock.patch("aicage.runtime.mounts.shares.Path.cwd", return_value=cwd),
                self.assertRaises(AicageError) as ctx,
            ):
                resolve_share_specs(parsed.shares, cwd)

        self.assertIn("Share destinations are not supported", str(ctx.exception))

    def test_resolve_share_specs_deduplicates_by_host_path(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            cwd = Path(tmp_dir)
            share_dir = cwd / "data"
            share_dir.mkdir()

            mounts = resolve_share_specs(["data:ro", "data"], cwd)

        self.assertEqual(1, len(mounts))
        self.assertEqual(share_dir.resolve(), mounts[0].host_path)
        self.assertTrue(mounts[0].read_only)
