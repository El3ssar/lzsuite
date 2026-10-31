"""Validate a Conventional Commit subject, from a message file or PR title."""

from __future__ import annotations

import os
import re
import sys
from pathlib import Path

PATTERN = re.compile(
    r"^(feat|fix|perf|refactor|docs|test|build|ci|chore|style|revert)"
    r"(\([^()\r\n]+\))?!?: \S.*$"
)


def main() -> int:
    if len(sys.argv) != 2:
        print("Usage: check_commit.py MESSAGE_FILE | --pr-title", file=sys.stderr)
        return 2
    message = (
        os.environ.get("PR_TITLE", "")
        if sys.argv[1] == "--pr-title"
        else Path(sys.argv[1]).read_text(encoding="utf-8")
    )
    subject = message.splitlines()[0] if message else ""
    if not PATTERN.fullmatch(subject):
        print("Use a Conventional Commit subject, e.g. feat: add quantile bins", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
