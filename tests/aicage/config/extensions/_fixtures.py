from pathlib import Path

from .._fixtures import join_yaml


def extension_definition(name: str, description: str, extra_lines: list[str] | None = None) -> str:
    lines = [f"name: \"{name}\"", f"description: \"{description}\""]
    if extra_lines:
        lines.extend(extra_lines)
    return join_yaml(lines)


def write_extension(
    path: Path,
    *,
    name: str,
    description: str,
    extra_lines: list[str] | None = None,
) -> None:
    scripts_dir = path / "scripts"
    scripts_dir.mkdir(parents=True, exist_ok=True)
    (path / "extension.yml").write_text(
        extension_definition(name, description, extra_lines=extra_lines),
        encoding="utf-8",
    )
    (scripts_dir / "01-install.sh").write_text(
        "#!/usr/bin/env bash\necho ok\n",
        encoding="utf-8",
    )
