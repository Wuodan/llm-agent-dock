import shutil
import sys
from dataclasses import dataclass
from typing import TextIO

_BAR_WIDTH: int = 24
_ELLIPSIS_WIDTH: int = 3
_MIN_RENDER_INTERVAL_SECONDS: float = 0.1
_SIZE_BASE: float = 1024.0
_CLEAR_LINE_PREFIX: str = "\r\033[2K"


@dataclass
class _LayerProgress:
    current: int = 0
    total: int = 0
    status: str = ""


class PullProgress:
    def __init__(self) -> None:
        self._layers: dict[str, _LayerProgress] = {}
        self._last_line: str = ""
        self._last_render_at: float = 0.0
        self._rendered: bool = False
        self._stream: TextIO | None = _progress_stream()

    def consume_event(self, event: object, now: float) -> None:
        layer_id = _layer_id(event)
        if layer_id is None:
            return

        status = _status(event)
        layer = self._layers.get(layer_id)
        if layer is None:
            layer = _LayerProgress()
            self._layers[layer_id] = layer
        progress_detail = _progress_detail(event)
        if progress_detail is not None and status == "Downloading":
            current = _progress_int(progress_detail, "current")
            total = _progress_int(progress_detail, "total")
            if current is not None:
                layer.current = current
            if total is not None:
                layer.total = total

        if status == "Download complete" and layer.total > 0:
            layer.current = layer.total
        if status == "Pull complete" and layer.total > 0:
            layer.current = layer.total
        layer.status = status

        if not _is_progress_status(status):
            return
        if not self._should_render():
            return
        if (
            now - self._last_render_at < _MIN_RENDER_INTERVAL_SECONDS
            and status != "Pull complete"
        ):
            return

        line = self._render_line()
        if line == self._last_line and status != "Pull complete":
            return

        print(f"{_CLEAR_LINE_PREFIX}{line}", end="", flush=True, file=self._stream)
        self._last_line = line
        self._last_render_at = now
        self._rendered = True

    def finish(self) -> None:
        if self._rendered:
            print(file=self._stream)

    def _should_render(self) -> bool:
        return self._stream is not None

    def progress_current(self) -> int | None:
        downloaded_bytes = sum(layer.current for layer in self._layers.values())
        return downloaded_bytes if downloaded_bytes > 0 else None

    def progress_total(self) -> int | None:
        total_bytes = sum(layer.total for layer in self._layers.values())
        return total_bytes if total_bytes > 0 else None

    def progress_status(self) -> str:
        summary = self._render_summary()
        if summary is None:
            return "Preparing pull"
        return summary

    def progress_details(self) -> str | None:
        if any(layer.status == "Pulling fs layer" for layer in self._layers.values()):
            return "[waiting for layer sizes...]"
        if not self._layers:
            return None

        downloaded_bytes = sum(layer.current for layer in self._layers.values())
        total_bytes = sum(layer.total for layer in self._layers.values())
        completed_layers = sum(
            1 for layer in self._layers.values() if _is_complete(layer)
        )
        downloading_layers = sum(
            1 for layer in self._layers.values() if layer.status == "Downloading"
        )
        extracting_layers = sum(
            1 for layer in self._layers.values() if layer.status == "Extracting"
        )
        known_layers = len(self._layers)

        details = (
            f"{_format_size(downloaded_bytes)}/{_format_size(total_bytes)} "
            f"layers {completed_layers}/{known_layers}"
        )
        if downloading_layers > 0:
            details += f" downloading {downloading_layers}"
        if extracting_layers > 0:
            details += f" extracting {extracting_layers}"
        return details

    def _render_line(self) -> str:
        summary = self._render_summary()
        if summary is None:
            return "[aicage] Pulling"
        return _truncate_to_terminal(f"[aicage] Pulling {summary}")

    def _render_summary(self) -> str | None:
        downloaded_bytes = sum(layer.current for layer in self._layers.values())
        total_bytes = sum(layer.total for layer in self._layers.values())
        percent = 0
        if total_bytes > 0:
            percent = min(100, int(downloaded_bytes * 100 / total_bytes))
        details = self.progress_details()
        if details is None:
            return None
        bar = _render_bar(percent)
        return f"{bar} {percent:>3}% {details}"


def _is_progress_status(status: str) -> bool:
    return status in {
        "Pulling fs layer",
        "Downloading",
        "Download complete",
        "Extracting",
        "Pull complete",
    }


def _layer_id(event: object) -> str | None:
    if not isinstance(event, dict):
        return None
    layer_id = event.get("id")
    if isinstance(layer_id, str) and layer_id:
        return layer_id
    return None


def _status(event: object) -> str:
    if not isinstance(event, dict):
        return ""
    status = event.get("status")
    if isinstance(status, str):
        return status
    return ""


def _progress_detail(event: object) -> dict[str, object] | None:
    if not isinstance(event, dict):
        return None
    progress_detail = event.get("progressDetail")
    if isinstance(progress_detail, dict):
        return progress_detail
    return None


def _progress_int(progress_detail: dict[str, object], key: str) -> int | None:
    value = progress_detail.get(key)
    if isinstance(value, int):
        return value
    return None


def _is_complete(layer: _LayerProgress) -> bool:
    return 0 < layer.total <= layer.current


def _render_bar(percent: int) -> str:
    filled = min(_BAR_WIDTH, int(percent * _BAR_WIDTH / 100))
    empty = _BAR_WIDTH - filled
    return f"[{'#' * filled}{'.' * empty}]"


def _format_size(size_bytes: int) -> str:
    if size_bytes <= 0:
        return "0 B"

    value = float(size_bytes)
    units = ("B", "KiB", "MiB", "GiB", "TiB")
    for unit in units:
        if value < _SIZE_BASE or unit == units[-1]:
            if unit == "B":
                return f"{int(value)} {unit}"
            return f"{value:.1f} {unit}"
        value /= _SIZE_BASE
    return "0 B"


def _truncate_to_terminal(line: str) -> str:
    columns = shutil.get_terminal_size(fallback=(120, 20)).columns
    if columns <= 0:
        return line
    if len(line) <= columns:
        return line
    if columns <= _ELLIPSIS_WIDTH:
        return line[:columns]
    return f"{line[: columns - _ELLIPSIS_WIDTH]}..."


def _progress_stream() -> TextIO | None:
    if sys.stdout.isatty():
        return sys.stdout
    if sys.stderr.isatty():
        return sys.stderr
    return None
