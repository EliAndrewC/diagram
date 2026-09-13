#!/usr/bin/env python3
"""How much of each guard is a Python program inside a shell string.

    python3 specs/239-*/measure/guard_census.py [--tests] [--record]

THE CONVENTION, stated because the first hand count got it wrong in both directions: a BLOCK is the
text between an opening `python3 -c '` (or `python3 - <<DELIM`) and its closing delimiter; PROGRAM
LINES are the lines strictly between the delimiters, so a one-line program counts 1 and the quoting
lines count 0. A file may hold several blocks and the count is their sum. Test scripts are excluded
unless `--tests` is given, because a test driving a guard is not the guard.

`--record` writes the figures into the feature's `measurements.json`.
"""

from __future__ import annotations

import datetime
import json
import pathlib
import re
import sys

HERE = pathlib.Path(__file__).resolve()
SCRIPTS = HERE.parents[3] / "scripts"
MEASUREMENTS = HERE.parent.parent / "measurements.json"
# `python3 -c '...'` and `python3 - <<'DELIM' ... DELIM`, the two shapes the tree uses
# the closing quote may be followed by a newline OR by the `)` of a `$(...)` capture - the house-style
# hook writes the second form, and a pattern that demanded the first missed the largest program here
_QUOTED = re.compile(r"python3? +-c +'(?P<body>.*?)'(?=\s*[)\n])", re.S)
_HEREDOC = re.compile(r"python3? +-? *<<-? *['\"]?(?P<delim>\w+)['\"]?\n(?P<body>.*?)\n\s*(?P=delim)\b", re.S)


def program_lines(text: str) -> tuple[int, int]:
    """(program lines, blocks) for one shell file, by the convention in the docstring."""
    lines = blocks = 0
    for pattern in (_QUOTED, _HEREDOC):
        for m in pattern.finditer(text):
            body = m.group("body")
            lines += len(body.split("\n"))
            blocks += 1
    return lines, blocks


def census(include_tests: bool = False) -> list[tuple[str, int, int, int]]:
    rows = []
    for path in sorted(SCRIPTS.glob("*.sh")):
        if path.name.startswith("test-") and not include_tests:
            continue
        text = path.read_text(errors="replace")
        lines, blocks = program_lines(text)
        if lines:
            rows.append((path.name, lines, blocks, text.count("\n") + 1))
    return sorted(rows, key=lambda r: -r[1])


def record(entries: dict[str, dict]) -> None:
    now = datetime.date.today().isoformat()
    have = json.loads(MEASUREMENTS.read_text()) if MEASUREMENTS.is_file() else {}
    for key, entry in entries.items():
        have[key] = {**entry, "taken": now,
                     "command": "python3 specs/239-measurable-guards-and-derived-figures/measure/guard_census.py --record"}
    MEASUREMENTS.write_text(json.dumps(have, indent=1, sort_keys=True) + "\n")
    print(f"recorded {len(entries)} figures in {MEASUREMENTS.name}")


def main(argv: list[str]) -> int:
    rows = census("--tests" in argv)
    with_tests = census(True)
    print(f"{'guard':34} {'program lines':>13} {'blocks':>7} {'file lines':>11}")
    for name, lines, blocks, whole in rows:
        print(f"{name:34} {lines:13d} {blocks:7d} {whole:11d}")
    print(f"\n{len(rows)} guard scripts carry an inline Python program "
          f"({len(with_tests)} including the test scripts)")
    if "--record" in argv:
        top = rows[0]
        record({
            "guards-with-inline-python": {"value": len(rows), "unit": "files",
                                          "note": "non-test scripts/*.sh; the convention is in the harness docstring"},
            "guards-with-inline-python-including-tests": {"value": len(with_tests), "unit": "files"},
            "house-style-program-lines": {"value": dict((r[0], r[1]) for r in rows)["house-style-hooks.sh"],
                                          "unit": "lines", "note": "of the file's whole length, below"},
            "house-style-file-lines": {"value": dict((r[0], r[3]) for r in rows)["house-style-hooks.sh"], "unit": "lines"},
            "largest-inline-program": {"value": top[1], "unit": "lines", "note": f"in {top[0]}"},
        })
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
