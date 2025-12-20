import shlex
import subprocess
import sys
from typing import List, Sequence

from aicage.config import ConfigError
from aicage.cli_parse import parse_cli
from aicage.config import RunConfig, load_run_config
from aicage.cli_types import ParsedArgs
from aicage.errors import CliError
from aicage.registry import pull_image
from aicage.runtime.run_args import DockerRunArgs, assemble_docker_run
from aicage.runtime.run_plan import build_run_args

__all__ = ["ParsedArgs", "parse_cli", "main"]


def main(argv: Sequence[str] | None = None) -> int:
    parsed_argv: Sequence[str] = argv if argv is not None else sys.argv[1:]
    try:
        parsed: ParsedArgs = parse_cli(parsed_argv)
        run_config: RunConfig = load_run_config(parsed.tool)
        pull_image(run_config.image_ref)
        run_args: DockerRunArgs = build_run_args(config=run_config, parsed=parsed)

        run_cmd: List[str] = assemble_docker_run(run_args)

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
