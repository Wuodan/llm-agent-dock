import shlex
import subprocess
import sys
from collections.abc import Sequence
from pathlib import Path

from aicage.cli_parse import parse_cli
from aicage.cli_types import ParsedArgs
from aicage.config import ConfigError, RunConfig, SettingsStore, load_run_config
from aicage.errors import CliError
from aicage.registry import pull_image
from aicage.runtime.run_args import DockerRunArgs, assemble_docker_run
from aicage.runtime.run_plan import build_run_args

__all__ = ["ParsedArgs", "parse_cli", "main"]


def _print_project_config() -> None:
    store = SettingsStore(ensure_global_config=False)
    project_path = Path.cwd().resolve()
    config_path = store.project_config_path(project_path)
    print("Project config path:")
    print(config_path)
    print()
    print("Project config content:")
    if config_path.exists():
        contents = config_path.read_text(encoding="utf-8").rstrip()
        if contents:
            print(contents)
        else:
            print("(empty)")
    else:
        print("(missing)")


def main(argv: Sequence[str] | None = None) -> int:
    parsed_argv: Sequence[str] = argv if argv is not None else sys.argv[1:]
    try:
        parsed: ParsedArgs = parse_cli(parsed_argv)
        if parsed.config_action == "print":
            _print_project_config()
            return 0
        run_config: RunConfig = load_run_config(parsed.tool, parsed)
        pull_image(run_config)
        run_args: DockerRunArgs = build_run_args(config=run_config, parsed=parsed)

        run_cmd: list[str] = assemble_docker_run(run_args)

        if parsed.dry_run:
            print(shlex.join(run_cmd))
            return 0

        subprocess.run(run_cmd, check=True)
        return 0
    except KeyboardInterrupt:
        print()
        return 130
    except (CliError, ConfigError) as exc:
        print(f"[aicage] {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
