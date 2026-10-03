"""One `<epoch> test` mark per failed test, for the run log's first and last failure times.

`make done` exports `L7R_GATE_FAILURES` (the clone's `gate-failures` file, read back by
`scripts/_runstats.py end`); unset, as under `make quick`, this does nothing. A failure appends one
short line, and a pass costs only the `report.failed` test.

TAKEN OUT OF THE ENVIRONMENT AT IMPORT. The tooling tests run make and pytest in fixture repositories,
some on purpose to watch a test fail; inheriting the variable, those would mark failures into a gate
that went green. Popping it when the suite's conftest loads keeps it from every process started after,
xdist's workers included (they also receive each report the controller does, and would count every
failure twice) - `PYTEST_XDIST_WORKER` is checked as well, in case a worker ever starts first.
"""

from __future__ import annotations

import os
import time

_PATH = os.environ.pop("L7R_GATE_FAILURES", None)


def mark(report, path: str | None) -> bool:  # type: ignore[no-untyped-def]
    """Append a mark for a failed report; say whether one was written."""
    if not (report.failed and path) or os.environ.get("PYTEST_XDIST_WORKER"):
        return False
    with open(path, "a") as f:
        f.write(f"{time.time():.3f} test\n")
    return True


def pytest_runtest_logreport(report) -> None:  # type: ignore[no-untyped-def]
    mark(report, _PATH)


def pytest_collectreport(report) -> None:  # type: ignore[no-untyped-def]
    mark(report, _PATH)
