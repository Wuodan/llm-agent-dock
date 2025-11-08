#!/usr/bin/env python3
"""Validate commit subjects follow the T###/S###: short summary format."""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

PATTERN = re.compile(r"^T\d{3}/S\d{3}: .+")

def validate_subject(subject: str) -> int:
    subject = subject.rstrip("\n")
    if PATTERN.match(subject):
        return 0
    sys.stderr.write(
        "Commit subject must match 'T###/S###: short summary'.\n"
        f"Got: '{subject}'\n"
        "Examples:\n"
        "  T004/S001: Define branch workflow policy\n"
        "  T010/S000: Bootstrap task scaffolding (no subtask)\n"
    )
    return 1

def read_subject_from_file(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8").splitlines()[0]
    except FileNotFoundError:
        raise SystemExit(f"error: commit message file '{path}' not found")
    except IndexError:
        raise SystemExit("error: commit message is empty")


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Check commit message subject formatting",
    )
    parser.add_argument(
        "commit_message_file",
        nargs="?",
        type=Path,
        help="Path to the commit message file (supplied by git).",
    )
    parser.add_argument(
        "--message",
        dest="message",
        help="Optional subject string to validate directly.",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv or sys.argv[1:])
    subject = args.message
    if subject is None:
        if args.commit_message_file is None:
            raise SystemExit("error: provide --message or a commit message file")
        subject = read_subject_from_file(args.commit_message_file)
    return validate_subject(subject)


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
