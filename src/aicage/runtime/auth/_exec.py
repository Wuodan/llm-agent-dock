import subprocess
from pathlib import Path
from typing import List

__all__ = ["capture_stdout"]


def capture_stdout(command: List[str], cwd: Path | None = None) -> str | None:
    try:
        result = subprocess.run(
            command, check=True, capture_output=True, text=True, cwd=str(cwd) if cwd else None
        )
    except (FileNotFoundError, subprocess.CalledProcessError):
        return None
    return result.stdout
