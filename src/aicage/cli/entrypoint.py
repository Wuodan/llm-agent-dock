import shlex
import subprocess
import sys
from collections.abc import Sequence

from aicage._logging import get_logger
from aicage.cli._parse import parse_cli
from aicage.cli._print_config import print_project_config
from aicage.cli_types import ParsedArgs
from aicage.config import ConfigError, RunConfig, load_run_config
from aicage.errors import CliError
from aicage.registry.image_pull import pull_image
from aicage.registry.local_build.ensure_local_image import ensure_local_image
from aicage.runtime.run_args import DockerRunArgs, assemble_docker_run
from aicage.runtime.run_plan import build_run_args


def main(argv: Sequence[str] | None = None) -> int:
    parsed_argv: Sequence[str] = argv if argv is not None else sys.argv[1:]
    logger = get_logger()
    try:
        parsed: ParsedArgs = parse_cli(parsed_argv)
        if parsed.config_action == "print":
            print_project_config()
            return 0
        run_config: RunConfig = load_run_config(parsed.agent, parsed)
        logger.info("Resolved run config for agent %s", run_config.agent)
        agent_metadata = run_config.images_metadata.agents[run_config.agent]
        if agent_metadata.local_definition_dir is None:
            pull_image(run_config)
        else:
            ensure_local_image(run_config)
        run_args: DockerRunArgs = build_run_args(config=run_config, parsed=parsed)

        run_cmd: list[str] = assemble_docker_run(run_args)

        if parsed.dry_run:
            print(shlex.join(run_cmd))
            logger.info("Dry-run docker command printed.")
            return 0

        subprocess.run(run_cmd, check=True)
        return 0
    except KeyboardInterrupt:
        print()
        logger.warning("Interrupted by user.")
        return 130
    except (CliError, ConfigError) as exc:
        print(f"[aicage] {exc}", file=sys.stderr)
        logger.error("CLI error: %s", exc)
        return 1
