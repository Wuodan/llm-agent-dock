import subprocess  # nosec B404 -- subprocess is required here for controlled termination during setup cancellation.
import threading
from collections.abc import Callable, Iterator
from contextlib import contextmanager

_Cleanup = Callable[[], None]
_PROCESS_WAIT_TIMEOUT_SECONDS = 1.0
_lock = threading.Lock()


class _CurrentRegistry:
    def __init__(self) -> None:
        self.value: _CleanupRegistry | None = None


_current = _CurrentRegistry()


class _CleanupRegistry:
    def __init__(self) -> None:
        self._cleanups: list[_Cleanup] = []
        self._cancelled = False
        self._lock = threading.Lock()

    def add_cleanup(self, cleanup: _Cleanup) -> None:
        with self._lock:
            if self._cancelled:
                _run_cleanup(cleanup)
                return
            self._cleanups.append(cleanup)

    def cancel(self) -> None:
        with self._lock:
            if self._cancelled:
                return
            self._cancelled = True
            cleanups = list(reversed(self._cleanups))
            self._cleanups.clear()
        for cleanup in cleanups:
            _run_cleanup(cleanup)


@contextmanager
def current_execution_cleanup() -> Iterator[None]:
    registry = _CleanupRegistry()
    with _lock:
        previous = _current.value
        _current.value = registry
    try:
        yield
    finally:
        with _lock:
            if _current.value is registry:
                _current.value = previous


def register_cleanup(cleanup: _Cleanup) -> None:
    with _lock:
        registry = _current.value
    if registry is None:
        return
    registry.add_cleanup(cleanup)


def register_process(process: subprocess.Popen[str] | subprocess.Popen[bytes]) -> None:
    register_cleanup(lambda: _terminate_process(process))


def cancel_current_execution_cleanup() -> None:
    with _lock:
        registry = _current.value
    if registry is None:
        return
    registry.cancel()


def _terminate_process(
    process: subprocess.Popen[str] | subprocess.Popen[bytes],
) -> None:
    if process.poll() is not None:
        return
    try:
        process.terminate()
        process.wait(timeout=_PROCESS_WAIT_TIMEOUT_SECONDS)
    except subprocess.TimeoutExpired:
        process.kill()
        process.wait(timeout=_PROCESS_WAIT_TIMEOUT_SECONDS)
    except OSError:
        return


def _run_cleanup(cleanup: _Cleanup) -> None:
    try:
        cleanup()
    except Exception:
        return
