import io
from unittest import TestCase, mock

from aicage.cli_parse import parse_cli
from aicage.errors import CliError


class ParseCliTests(TestCase):
    def test_parse_with_docker_args(self) -> None:
        parsed = parse_cli(["--dry-run", "--network=host", "codex", "--foo"])
        self.assertTrue(parsed.dry_run)
        self.assertEqual("--network=host", parsed.docker_args)
        self.assertEqual("codex", parsed.tool)
        self.assertEqual(["--foo"], parsed.tool_args)
        self.assertIsNone(parsed.entrypoint)
        self.assertFalse(parsed.docker_socket)
        self.assertIsNone(parsed.config_action)

    def test_parse_with_separator(self) -> None:
        parsed = parse_cli(["--dry-run", "--", "codex", "--bar"])
        self.assertTrue(parsed.dry_run)
        self.assertEqual("", parsed.docker_args)
        self.assertEqual("codex", parsed.tool)
        self.assertEqual(["--bar"], parsed.tool_args)

    def test_parse_with_separator_and_docker_args(self) -> None:
        parsed = parse_cli(["--dry-run", "-v", "/run/docker.sock:/run/docker.sock", "--", "codex", "--bar"])
        self.assertTrue(parsed.dry_run)
        self.assertEqual("-v /run/docker.sock:/run/docker.sock", parsed.docker_args)
        self.assertEqual("codex", parsed.tool)
        self.assertEqual(["--bar"], parsed.tool_args)
        self.assertIsNone(parsed.entrypoint)
        self.assertFalse(parsed.docker_socket)
        self.assertIsNone(parsed.config_action)

    def test_parse_without_docker_args(self) -> None:
        parsed = parse_cli(["codex", "--flag"])
        self.assertFalse(parsed.dry_run)
        self.assertEqual("", parsed.docker_args)
        self.assertEqual("codex", parsed.tool)
        self.assertEqual(["--flag"], parsed.tool_args)
        self.assertIsNone(parsed.entrypoint)
        self.assertFalse(parsed.docker_socket)
        self.assertIsNone(parsed.config_action)

    def test_parse_help_exits(self) -> None:
        with mock.patch("sys.stdout", new_callable=io.StringIO) as stdout:
            with self.assertRaises(SystemExit) as ctx:
                parse_cli(["--help"])
        self.assertEqual(0, ctx.exception.code)
        self.assertIn("Usage:", stdout.getvalue())

    def test_parse_requires_arguments(self) -> None:
        with self.assertRaises(CliError):
            parse_cli([])

    def test_parse_requires_tool_after_separator(self) -> None:
        with self.assertRaises(CliError):
            parse_cli(["--"])

    def test_parse_requires_tool_name(self) -> None:
        with self.assertRaises(CliError):
            parse_cli([""])

    def test_parse_config_print(self) -> None:
        parsed = parse_cli(["--config", "print"])
        self.assertEqual("print", parsed.config_action)
        self.assertEqual("", parsed.docker_args)
        self.assertEqual("", parsed.tool)
        self.assertEqual([], parsed.tool_args)

    def test_parse_config_print_rejects_args(self) -> None:
        with self.assertRaises(CliError):
            parse_cli(["--config", "print", "codex"])

    def test_parse_cli_flags_before_separator(self) -> None:
        parsed = parse_cli(
            [
                "--docker",
                "--entrypoint",
                "/tmp/entrypoint.sh",
                "--dry-run",
                "--",
                "codex",
            ]
        )
        self.assertTrue(parsed.dry_run)
        self.assertTrue(parsed.docker_socket)
        self.assertEqual("/tmp/entrypoint.sh", parsed.entrypoint)
        self.assertEqual("", parsed.docker_args)
        self.assertEqual("codex", parsed.tool)
