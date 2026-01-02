from __future__ import annotations

import logging
import os
from pathlib import Path

__all__ = ["get_logger"]

_LOGGER_NAME = "aicage"
_LOG_LEVEL_ENV = "AICAGE_LOG_LEVEL"
_DEFAULT_LEVEL = "INFO"
_LOG_PATH = "~/.aicage/logs/aicage.log"


def get_logger() -> logging.Logger:
    logger = logging.getLogger(_LOGGER_NAME)
    if logger.handlers:
        return logger

    log_path = Path(os.path.expanduser(_LOG_PATH))
    log_path.parent.mkdir(parents=True, exist_ok=True)

    level = _resolve_level(os.getenv(_LOG_LEVEL_ENV, _DEFAULT_LEVEL))
    logger.setLevel(level)
    logger.propagate = False

    handler = logging.FileHandler(log_path, encoding="utf-8")
    handler.setLevel(level)
    handler.setFormatter(
        logging.Formatter("%(asctime)s %(levelname)s %(name)s %(message)s")
    )
    logger.addHandler(handler)
    return logger


def _resolve_level(raw_level: str) -> int:
    normalized = raw_level.strip().upper()
    level = logging.getLevelName(normalized)
    if isinstance(level, int):
        return level
    return logging.INFO
