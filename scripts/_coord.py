#!/usr/bin/env python3
"""A coordination file read and written by line - `make lines` and `make append` (feature 274 D5, FR-002).

    _coord.py lines <file> <regex>     the matching lines, numbered, at most MAX, then how many were shown of how many
    _coord.py append <file>            appends $LINE as one line (the file made if needed); prints only where

WHY (feature 274, research R1). The research sessions re-read their coordination files whole: 619 reads of the
cross-session claims file across 172 sessions (about 30 M tokens carried), 418 of a group's handoff across 254 sessions
(about 20 M, though the briefs said "read only your own lines") and 388 of a checks report across 183 sessions (about
12 M), mostly to append one line - about 60 M in all, 5%. Every read stays in the session's context and is paid for
again on every later turn. So a session reads only its own lines and appends without reading.

The line to append comes from the ENVIRONMENT (`make` exports its command-line variables to the recipe), not from an
argument pasted into the recipe, so quotes and `$` in it survive. A relative FILE is taken from the directory `make`
ran in, else from the repository root, so the same command works from the clone root or the skill directory.
"""

from __future__ import annotations

import os
import pathlib
import re
import subprocess
import sys

MAX = 80  # lines shown at most: a KEY that matches more is too wide, and the count says so


def resolve(name: str, cwd: pathlib.Path | None = None) -> pathlib.Path:
    """FILE as given: absolute; else under the directory make ran in if it (or its parent directory) is there; else
    under the repository root."""
    p = pathlib.Path(name)
    if p.is_absolute():
        return p
    here = (cwd or pathlib.Path.cwd()) / p
    if here.exists() or here.parent.is_dir():
        return here
    top = subprocess.run(["git", "rev-parse", "--show-toplevel"], cwd=cwd, capture_output=True, text=True, check=False).stdout.strip()
    return pathlib.Path(top) / p if top else here


def lines(path: pathlib.Path, key: str) -> list[str]:
    """The output of `make lines`: each matching line as `<number>: <text>`, then the count line."""
    text = path.read_text(encoding="utf-8", errors="replace").splitlines()
    rx = re.compile(key)
    hits = [f"{n}: {ln}" for n, ln in enumerate(text, 1) if rx.search(ln)]
    out = hits[:MAX] + [f"({min(len(hits), MAX)} of {len(text)} lines shown)"]
    if len(hits) > MAX:
        out.append(f"({len(hits) - MAX} more matched - narrow KEY)")
    return out


def append(path: pathlib.Path, line: str) -> None:
    """Append ONE line, never reading the file; a newline first only if the file does not already end with one."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "ab+") as fh:
        fh.seek(0, os.SEEK_END)
        lead = b""
        if fh.tell():
            fh.seek(-1, os.SEEK_END)
            lead = b"" if fh.read(1) == b"\n" else b"\n"
        fh.write(lead + line.rstrip("\n").encode("utf-8") + b"\n")


def main(argv: list[str], env: dict[str, str] | None = None) -> int:
    env = dict(os.environ) if env is None else env
    if len(argv) == 3 and argv[0] == "lines":
        path = resolve(argv[1])
        if not path.is_file():
            print(f"make lines: no file {path}", file=sys.stderr)
            return 2
        try:
            print("\n".join(lines(path, argv[2])))
        except re.error as e:
            print(f"make lines: KEY is not a regular expression - {e}", file=sys.stderr)
            return 2
        return 0
    if len(argv) == 2 and argv[0] == "append":
        line = env.get("LINE", "")
        if not line.strip() or "\n" in line.strip("\n"):
            print("make append: LINE=<text> is required, and it is ONE line", file=sys.stderr)
            return 2
        path = resolve(argv[1])
        append(path, line)
        print(f"appended to {path}")
        return 0
    print("usage: _coord.py lines <file> <regex> | _coord.py append <file>  (the line in $LINE)", file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
