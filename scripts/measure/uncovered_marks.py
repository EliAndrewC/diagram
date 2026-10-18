"""Mark a coverage-floor failure's uncovered lines into the gate's failure file, so the run record names what a red gate failed on.

    python3 scripts/measure/uncovered_marks.py          (the coverage phase of `make done`, when the floor fails)

The round arbiter's tooling fix on red-gate@2026-10-18T11:42:39Z (feature 387): a gate red on the 100% floor left its run record
with no failed test and no name - "test-full, ? test(s) failed" - so the arbiter could not tell one red gate's cause from the
next. One `<epoch> uncovered <file>:<missing>` mark per module under 100%, read from `coverage report -m --skip-covered`, into
`L7R_GATE_FAILURES` (or the clone's `gate-failures`); `runstats.py end` puts them in the record's `failed_names`. Never fails.
"""

from __future__ import annotations

import os
import re
import subprocess
import sys
import time

#: a report row: the module, its statements, its misses, its percent, and the missing lines (`coverage report -m`)
ROW = re.compile(r"^(\S+\.py)\s+\d+\s+[1-9]\d*\s+\d+%\s+(.+)$")


def uncovered(report: str) -> list[str]:
    """`<file>:<missing>` for each module the report lists with a miss."""
    return [f"{m.group(1)}:{m.group(2).strip()}" for line in report.splitlines() if (m := ROW.match(line.strip()))]


#: what `coverage report` prints when it cannot report at all - a file the data names is gone (feature 388: a module the change
#: deleted, carried in from a baseline) - so the report lists no row and the record would say nothing
ERROR = re.compile(r"^(No source for code: .+|Couldn't parse .+|No data to report\.)$")


def errors(output: str) -> list[str]:
    """The report's own error lines, as `coverage-error <line>` marks."""
    return [f"coverage-error {m.group(1)}" for line in output.splitlines() if (m := ERROR.match(line.strip()))]


def main() -> int:
    path = os.environ.get("L7R_GATE_FAILURES")
    if not path:
        try:
            gitdir = subprocess.run(["git", "rev-parse", "--absolute-git-dir"], capture_output=True, text=True, check=True).stdout.strip()
        except OSError, subprocess.CalledProcessError:
            return 0
        path = os.path.join(gitdir, "gate-failures")
    run = subprocess.run([sys.executable, "-m", "coverage", "report", "-m", "--skip-covered"], capture_output=True, text=True)
    marks = errors(run.stdout + "\n" + run.stderr)
    report = run.stdout
    if marks:  # the report stopped at the error: ask it again past the error, for the rows it would have listed (the round
        # arbiter's tooling fix on red-gate@2026-10-18T21:00:44Z - a red that named nothing because the report itself failed)
        report = subprocess.run([sys.executable, "-m", "coverage", "report", "-m", "--skip-covered", "--ignore-errors"], capture_output=True, text=True).stdout
    marks += [f"uncovered {row}" for row in uncovered(report)]
    if marks:
        with open(path, "a") as f:
            f.writelines(f"{time.time():.3f} {mark}\n" for mark in marks)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
