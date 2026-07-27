from pathlib import Path

from aicage._logging import get_logger
from aicage.config.agent.models import AgentMetadata
from aicage.constants import VERSION_CHECK_IMAGE
from aicage.registry._errors import RegistryError
from aicage.reporting import OperationReporter

from ._command import run_host, run_version_check_image
from ._store import VersionCheckStore


class AgentVersionChecker:
    def __init__(self, store: VersionCheckStore | None = None) -> None:
        self._store = store or VersionCheckStore()

    def get_version(
        self,
        agent_name: str,
        agent_metadata: AgentMetadata,
        definition_dir: Path,
        reporter: OperationReporter,
    ) -> str:
        logger = get_logger()
        script_path = definition_dir / "version.sh"
        if not script_path.is_file():
            raise RegistryError(
                f"Agent '{agent_name}' is missing version.sh at {script_path}."
            )

        errors: list[str] = []
        host_result = run_host(script_path)
        if host_result.success:
            logger.info("Version check succeeded on host for %s", agent_name)
            self._store.save(agent_name, host_result.output)
            return host_result.output

        logger.warning(
            "Version check failed on host for %s: %s",
            agent_name,
            host_result.error,
        )
        errors.append(host_result.error)

        image_result = run_version_check_image(
            VERSION_CHECK_IMAGE,
            definition_dir,
            reporter=reporter,
        )
        if image_result.success:
            logger.info(
                "Version check succeeded in version check image for %s", agent_name
            )
            self._store.save(agent_name, image_result.output)
            return image_result.output

        logger.warning(
            "Version check failed in version check image for %s: %s",
            agent_name,
            image_result.error,
        )
        errors.append(image_result.error)

        cached_version = self._store.load(agent_name)
        if agent_metadata.build_local and cached_version:
            logger.warning(
                "Version check failed for %s; using cached version %s.",
                agent_name,
                cached_version,
            )
            return cached_version
        logger.error("Version check failed for %s: %s", agent_name, "; ".join(errors))
        raise RegistryError("; ".join(errors))
