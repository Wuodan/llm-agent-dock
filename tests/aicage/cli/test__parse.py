import io
from unittest import TestCase, mock

from aicage import __version__
from aicage.cli._errors import CliError
from aicage.cli._parse import parse_cli
from aicage.config.errors import ConfigError


class ParseCliTests(TestCase):
    def test_parse_cli_with_docker_args(self) -> None:
        with self.assertRaises(CliError) as ctx:
            parse_cli(["--dry-run", "--network=host", "codex", "--foo"])
        self.assertEqual(
            "Docker args require '--' before the agent.", str(ctx.exception)
        )

    def test_parse_cli_with_separator(self) -> None:
        parsed = parse_cli(["--dry-run", "--", "codex", "--bar"])
        self.assertTrue(parsed.dry_run)
        self.assertEqual("ui", parsed.menu)
        self.assertEqual("", parsed.docker_args)
        self.assertEqual("codex", parsed.agent)
        self.assertEqual(["--bar"], parsed.agent_args)
        self.assertEqual([], parsed.shares)

    def test_parse_cli_with_separator_and_docker_args(self) -> None:
        parsed = parse_cli(
            [
                "--dry-run",
                "-v",
                "/run/docker.sock:/run/docker.sock",
                "--",
                "codex",
                "--bar",
            ]
        )
        self.assertTrue(parsed.dry_run)
        self.assertEqual("ui", parsed.menu)
        self.assertEqual("-v /run/docker.sock:/run/docker.sock", parsed.docker_args)
        self.assertEqual("codex", parsed.agent)
        self.assertEqual(["--bar"], parsed.agent_args)
        self.assertFalse(parsed.docker_socket)
        self.assertEqual([], parsed.shares)
        self.assertIsNone(parsed.config_action)

    def test_parse_cli_without_docker_args(self) -> None:
        parsed = parse_cli(["codex", "--flag"])
        self.assertFalse(parsed.dry_run)
        self.assertEqual("ui", parsed.menu)
        self.assertEqual("", parsed.docker_args)
        self.assertEqual("codex", parsed.agent)
        self.assertEqual(["--flag"], parsed.agent_args)
        self.assertFalse(parsed.docker_socket)
        self.assertEqual([], parsed.shares)
        self.assertIsNone(parsed.config_action)

    def test_parse_cli_help_exits(self) -> None:
        with mock.patch("sys.stdout", new_callable=io.StringIO) as stdout:
            with self.assertRaises(SystemExit) as ctx:
                parse_cli(["--help"])
        self.assertEqual(0, ctx.exception.code)
        self.assertIn("Usage:", stdout.getvalue())

    def test_parse_cli_version_exits(self) -> None:
        with mock.patch("sys.stdout", new_callable=io.StringIO) as stdout:
            with self.assertRaises(SystemExit) as ctx:
                parse_cli(["--version"])
        self.assertEqual(0, ctx.exception.code)
        self.assertEqual(f"{__version__}\n", stdout.getvalue())

    def test_parse_cli_short_version_exits(self) -> None:
        with mock.patch("sys.stdout", new_callable=io.StringIO) as stdout:
            with self.assertRaises(SystemExit) as ctx:
                parse_cli(["-v"])
        self.assertEqual(0, ctx.exception.code)
        self.assertEqual(f"{__version__}\n", stdout.getvalue())

    def test_parse_cli_requires_arguments(self) -> None:
        with self.assertRaises(CliError) as ctx:
            parse_cli([])
        self.assertIn("Missing argument. Provide an agent name", str(ctx.exception))
        self.assertIn("Available agents:", str(ctx.exception))

    def test_parse_cli_requires_agent_after_separator(self) -> None:
        with self.assertRaises(CliError):
            parse_cli(["--"])

    def test_parse_cli_requires_agent_name(self) -> None:
        with self.assertRaises(CliError):
            parse_cli([""])

    def test_parse_cli_requires_arguments_without_agent_list_on_config_error(
        self,
    ) -> None:
        with mock.patch(
            "aicage.cli._parse.load_bases", side_effect=ConfigError("broken")
        ):
            with self.assertRaises(CliError) as ctx:
                parse_cli([])
        self.assertEqual(
            "Missing argument. Provide an agent name.",
            str(ctx.exception),
        )

    def test_parse_cli_requires_separator_for_docker_args(self) -> None:
        with self.assertRaises(CliError) as ctx:
            parse_cli(["-v", "/test-tmp/folder:/test-tmp/folder", "codex"])
        self.assertEqual(
            "Docker args require '--' before the agent.", str(ctx.exception)
        )

    def test_parse_cli_config_info(self) -> None:
        parsed = parse_cli(["--config", "info"])
        self.assertEqual("info", parsed.config_action)
        self.assertIsNone(parsed.config_agent)
        self.assertEqual("", parsed.docker_args)
        self.assertEqual("", parsed.agent)
        self.assertEqual([], parsed.agent_args)
        self.assertEqual([], parsed.shares)

    def test_parse_cli_config_defaults_to_info(self) -> None:
        parsed = parse_cli(["--config"])
        self.assertEqual("info", parsed.config_action)
        self.assertIsNone(parsed.config_agent)
        self.assertEqual("", parsed.docker_args)
        self.assertEqual("", parsed.agent)
        self.assertEqual([], parsed.agent_args)
        self.assertEqual([], parsed.shares)

    def test_parse_cli_config_print_alias(self) -> None:
        parsed = parse_cli(["--config", "print"])
        self.assertEqual("info", parsed.config_action)

    def test_parse_cli_config_info_rejects_args(self) -> None:
        with self.assertRaises(CliError):
            parse_cli(["--config", "info", "codex"])

    def test_parse_cli_config_remove(self) -> None:
        parsed = parse_cli(["--config", "remove"])
        self.assertEqual("remove", parsed.config_action)
        self.assertIsNone(parsed.config_agent)

    def test_parse_cli_config_remove_with_agent(self) -> None:
        parsed = parse_cli(["--config", "remove", "codex"])
        self.assertEqual("remove", parsed.config_action)
        self.assertEqual("codex", parsed.config_agent)

    def test_parse_cli_config_info_rejects_agent(self) -> None:
        with self.assertRaises(CliError) as ctx:
            parse_cli(["--config", "info", "codex"])
        self.assertEqual(
            "No agent value is allowed with '--config info'.", str(ctx.exception)
        )

    def test_parse_cli_config_rejects_too_many_values(self) -> None:
        with self.assertRaises(CliError) as ctx:
            parse_cli(["--config", "remove", "codex", "extra"])
        self.assertEqual(
            "Too many values for --config. Use '--config remove [agent]'.",
            str(ctx.exception),
        )

    def test_parse_cli_flags_before_separator(self) -> None:
        parsed = parse_cli(
            [
                "--docker",
                "--dry-run",
                "--",
                "codex",
            ]
        )
        self.assertTrue(parsed.dry_run)
        self.assertTrue(parsed.docker_socket)
        self.assertEqual("", parsed.docker_args)
        self.assertEqual("codex", parsed.agent)
        self.assertEqual([], parsed.shares)

    def test_parse_cli_with_share(self) -> None:
        parsed = parse_cli(
            ["--share", "data", "--share", "/test-tmp/one:ro", "--", "codex"]
        )
        self.assertEqual(["data", "/test-tmp/one:ro"], parsed.shares)

    def test_parse_cli_with_menu_none(self) -> None:
        parsed = parse_cli(["--menu", "none", "codex"])
        self.assertEqual("none", parsed.menu)
        self.assertEqual("codex", parsed.agent)

    def test_parse_cli_with_menu_simple(self) -> None:
        parsed = parse_cli(["--menu", "simple", "codex"])
        self.assertEqual("simple", parsed.menu)
        self.assertEqual("codex", parsed.agent)

    def test_parse_cli_with_stdio_preserves_menu(self) -> None:
        parsed = parse_cli(["--stdio", "codex", "exec", "--experimental-json"])
        self.assertTrue(parsed.stdio)
        self.assertEqual("ui", parsed.menu)
        self.assertEqual("codex", parsed.agent)
        self.assertEqual(["exec", "--experimental-json"], parsed.agent_args)

    def test_parse_cli_with_stdio_and_menu_none(self) -> None:
        parsed = parse_cli(
            ["--stdio", "--menu", "none", "codex", "exec", "--experimental-json"]
        )
        self.assertTrue(parsed.stdio)
        self.assertEqual("none", parsed.menu)
        self.assertEqual("codex", parsed.agent)
        self.assertEqual(["exec", "--experimental-json"], parsed.agent_args)

    def test_parse_cli_stdio_rejects_config_action(self) -> None:
        with self.assertRaises(CliError):
            parse_cli(["--stdio", "--config", "info"])

    def test_parse_cli_config_rejects_share(self) -> None:
        with self.assertRaises(CliError):
            parse_cli(["--config", "info", "--share", "data"])

    def test_parse_cli_config_rejects_non_default_menu(self) -> None:
        with self.assertRaises(CliError):
            parse_cli(["--config", "info", "--menu", "none"])

    def test_parse_cli_help_shows_config_default(self) -> None:
        with mock.patch("sys.stdout", new_callable=io.StringIO) as stdout:
            with self.assertRaises(SystemExit):
                parse_cli(["--help"])

        output = stdout.getvalue()
        self.assertIn("aicage --config\n", output)
        self.assertIn(
            "--config [<cmd>] Run config command: default info, or remove [agent].",
            output,
        )
        self.assertIn("--menu <mode>", output)
        self.assertIn("--stdio", output)
