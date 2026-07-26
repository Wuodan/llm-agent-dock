import json
import time
from pathlib import Path

from aicage._execution_cleanup import register_cleanup
from aicage._logging import get_logger
from aicage.docker._client import get_docker_pull_client
from aicage.docker._pull_progress import PullProgress
from aicage.docker.reporting import OperationReporter


def run_pull(
    image_ref: str,
    log_path: Path,
    reporter: OperationReporter | None = None,
) -> None:
    logger = get_logger()
    progress = PullProgress()
    log_path.parent.mkdir(parents=True, exist_ok=True)
    if reporter is None:
        print(f"[aicage] Pulling image {image_ref} (logs: {log_path})...")
    else:
        reporter.on_phase_started("pull", f"Pulling image {image_ref}", log_path)
    logger.info("Pulling image %s (logs: %s)", image_ref, log_path)

    client = get_docker_pull_client()
    register_cleanup(client.close)
    with log_path.open("w", encoding="utf-8") as log_handle:
        for event in client.api.pull(image_ref, stream=True, decode=True):
            line = _format_pull_event(event)
            log_handle.write(f"{line}\n")
            log_handle.flush()
            progress.consume_event(event, time.monotonic())
            if reporter is not None:
                reporter.on_phase_log("pull", line)
                _report_progress(reporter, progress, event)

    progress.finish()
    if reporter is not None:
        reporter.on_phase_finished("pull", f"Pull finished for {image_ref}")

    logger.info("Image pull succeeded for %s", image_ref)


def _format_pull_event(event: object) -> str:
    if isinstance(event, bytes):
        return event.decode("utf-8", errors="replace").rstrip("\n")
    if isinstance(event, str):
        return event.rstrip("\n")
    if isinstance(event, dict):
        return json.dumps(event, ensure_ascii=True)
    return str(event).rstrip("\n")


def _report_progress(
    reporter: OperationReporter, progress: PullProgress, event: object
) -> None:
    if not isinstance(event, dict):
        return
    status = event.get("status")
    if not isinstance(status, str):
        return
    reporter.on_phase_progress(
        "pull",
        progress.progress_details() or progress.progress_status(),
        progress.progress_current(),
        progress.progress_total(),
    )
