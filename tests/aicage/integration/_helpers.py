import os
import pty
import select
import stat
import subprocess
import sys
from pathlib import Path
from shutil import copytree


def run_cli_pty(args: list[str], env: dict[str, str], cwd: Path) -> tuple[int, str]:
    master_fd, slave_fd = pty.openpty()
    process = subprocess.Popen(
        [sys.executable, "-m", "aicage", *args],
        stdin=slave_fd,
        stdout=slave_fd,
        stderr=slave_fd,
        cwd=cwd,
        env=env,
        close_fds=True,
    )
    os.close(slave_fd)

    chunks: list[bytes] = []
    while True:
        read_ready, _, _ = select.select([master_fd], [], [], 0.2)
        if master_fd in read_ready:
            try:
                data = os.read(master_fd, 4096)
            except OSError:
                data = b""
            if data:
                chunks.append(data)
            elif process.poll() is not None:
                break
        elif process.poll() is not None:
            break

    process.wait()
    os.close(master_fd)
    output = b"".join(chunks).decode(errors="replace")
    return process.returncode, output


def build_cli_env(home_dir: Path) -> dict[str, str]:
    env = dict(os.environ)
    env["HOME"] = str(home_dir)
    repo_root = Path(__file__).resolve().parents[3]
    env["PYTHONPATH"] = str(repo_root / "src")
    for key in list(env):
        if key == "AGENT" or key.startswith("AICAGE_"):
            env.pop(key, None)
    return env


def copy_forge_sample(target_dir: Path) -> None:
    repo_root = Path(__file__).resolve().parents[3]
    source_dir = repo_root / "doc/sample/custom/agents/forge"
    copytree(source_dir, target_dir, dirs_exist_ok=True)
    _make_executable(target_dir / "install.sh")
    _make_executable(target_dir / "version.sh")


def _make_executable(path: Path) -> None:
    current = path.stat().st_mode
    path.chmod(current | stat.S_IEXEC)
