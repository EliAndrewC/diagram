#!/usr/bin/env python3
"""`make figures`: re-run every recorded measurement and report what moved (feature 239 FR-011).

    python3 scripts/figures.py specs/NNN-slug [...]

For each distinct `command` in a feature's `measurements.json` the command is re-run once, the values it
writes are compared with the recorded ones, and the ORIGINAL file is restored (plan P4): this reports,
it never records. A spec's figures are only as good as the commands behind them, and a command that no
longer reproduces its figure is the thing a reader would otherwise find by hand.

WHAT FAILS AND WHAT IS REPORTED (FR-011d). A moved COUNT fails - a count repeats exactly or the thing
counted changed. A TIMING is a property of the machine as well as the code, so a timing that moved
beyond its band (`varies: <fraction>`, 0.10 when written `true`, FR-011a) is reported and never fails:
a gate that failed on one would fail on correct work. A timing harness that REFUSES because the load
is high (FR-011c) is reported as not re-measured, never as moved.
"""

from __future__ import annotations

import json
import pathlib
import shlex
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
DEFAULT_BAND = 0.10


def band(entry: dict) -> float:
    varies = entry.get("varies")
    return DEFAULT_BAND if varies is True else float(varies)


def compare(recorded: dict[str, dict], fresh: dict[str, dict]) -> tuple[list[str], list[str]]:
    """(failures, reports) for the keys a re-run produced."""
    failures, reports = [], []
    for key, entry in sorted(recorded.items()):
        if key not in fresh:
            continue
        old, new = entry.get("value"), fresh[key].get("value")
        if old == new:
            continue
        if entry.get("varies"):
            limit = band(entry)
            try:
                moved = abs(float(new) - float(old)) / abs(float(old)) if float(old) else float(new != old)
            except (TypeError, ValueError):
                moved = 1.0
            if moved > limit:
                reports.append(f"  REPORT `{key}`: {old} -> {new}, outside its band of {limit:.0%} "
                               f"(a timing - reported, never failed; load {fresh[key].get('load', '?')})")
        else:
            failures.append(f"  FAIL   `{key}`: {old} -> {new} - a count that moved means the thing counted changed")
    return failures, reports


def rerun(spec_dir: pathlib.Path) -> tuple[list[str], list[str], list[str]]:
    """(failures, reports, not re-measured) for one feature, with its measurements file restored."""
    path = spec_dir / "measurements.json"
    original = path.read_text()
    recorded = json.loads(original)
    failures, reports, skipped = [], [], []
    try:
        for command in sorted({e["command"] for e in recorded.values() if e.get("command")}):
            path.write_text(original)
            run = subprocess.run(shlex.split(command), cwd=ROOT, capture_output=True, text=True)
            if run.returncode:
                reason = (run.stderr.strip().splitlines() or ["exit " + str(run.returncode)])[-1][:160]
                skipped.append(f"  NOT RE-MEASURED: {command}\n      {reason}")
                continue
            fail, report = compare(recorded, json.loads(path.read_text()))
            failures += fail
            reports += report
    finally:
        path.write_text(original)          # plan P4: `make figures` reports, it never records
    return failures, reports, skipped


def main(argv: list[str]) -> int:
    dirs = [pathlib.Path(a) for a in argv if not a.startswith("-")]
    if not dirs:
        dirs = sorted(p.parent for p in (ROOT / "specs").glob("*/measurements.json"))
    exit_code = 0
    for spec_dir in dirs:
        if not (spec_dir / "measurements.json").is_file():
            continue
        failures, reports, skipped = rerun(spec_dir)
        print(f"{spec_dir.name}: {len(failures)} moved count(s), {len(reports)} timing(s) outside their band, "
              f"{len(skipped)} command(s) not re-measured")
        for line in failures + reports + skipped:
            print(line)
        exit_code |= 1 if failures else 0
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
