"""The roll census's WRITER (feature 213, GM 2026-09-07: "program our unit tests to never allow the same
hamlet to be rolled twice within the tests and also to have some required process around adding another
hamlet that gets rolled").

One function, `record`, appends one JSON line to the file named by `L7R_ROLL_CENSUS` - and does nothing
when the variable is unset, which is every run that is not a gate. It is called from the CHOKEPOINTS, not
from patched entry points: `hamletgen.driver.roll_scope` (every stage-running loop enters it - feature
210's static AST test proves that), `pipeline.rollcache` (served and rolled verdicts), `settlement.finish`'s
`render_png` and `interactive.raster.picture` (a render). The first census instrument (specs/213 census/)
patched six functions and missed the package's re-exported `build` on its first run; a record written at
the boundary itself cannot be short that way. The gate sets the variable and every child process inherits
it, so a roll in a test worker, in a roll child, in a pool-sweep child or in a cohort pool child is
recorded the same way. Two more variables ride along for attribution and are set by the pytest plugin
(`ci/rollcensus.py`): `L7R_ROLL_CENSUS_TEST`, the requesting test, and `L7R_ROLL_CENSUS_REQUEST`, one id per
test, so a `generate` that re-rolls three times inside one test is one roll with three attempts, and two
tests rolling the same spec are two rolls. The verdict is `ci/rollverdict.py`; the roster is
`tests/rolls.py`.
"""

from __future__ import annotations

import json
import os
import time
from typing import Any

ENV = "L7R_ROLL_CENSUS"
TEST_ENV = "L7R_ROLL_CENSUS_TEST"
REQUEST_ENV = "L7R_ROLL_CENSUS_REQUEST"
CONTEXT_ENV = "L7R_COV_CONTEXT"  # the parent's CURRENT coverage context, exported by ci/selection.switch so a coverage child labels its data with it (below)
# WHY A CHILD'S COVERAGE CARRIES ITS REQUESTER'S CONTEXT (feature 213, found on the polder-only run of 2026-09-08).
# Feature 207 selects the tests an engine change can reach from the baseline's per-test and per-fixture coverage
# contexts. A roll made IN a worker recorded the engine's lines under the rolling fixture's context; a roll made in
# a CHILD (210, 213) records them under no context at all - so a polder-only edit selected 46 unit tests and NOT
# ONE of the polder gate tests, and the hamlet floor re-rolled both polder subjects itself (207's D14 back again,
# by a different door). So every coverage child - the roll child, the pool sweep's gate_obtain child - runs
# starts coverage itself (gencache.child_coverage), imports the engine under NO context, and switches to the parent's
# context for the work alone - `coverage run --context=` labeled the imports too, and every roller then "touched" every
# engine file - so the baseline sees the roll where 207 expects it and nothing more.
WORKER_ENV = "L7R_ROLL_CENSUS_WORKER"  # the test worker's pid - a record from another pid came from a child


def spec_row(spec: Any) -> dict[str, Any] | None:
    """The fields of a `HamletSpec` the roster keys on and the verdict prints; None for no spec."""
    if spec is None:
        return None
    return {k: getattr(spec, k, None) for k in ("name", "seed", "households", "field_archetype", "down_deg", "water_sink", "settlement_form")}


def record(kind: str, **fields: Any) -> None:
    """Append one record - `kind` is `roll`, `served`, `rolled` or `render` - when a census is open. Never
    raises: a census that cannot be written must not turn a roll red; the verdict notices a short census
    because the roster's specs went unrolled."""
    path = os.environ.get(ENV)
    if not path:
        return
    row = {"kind": kind, "t": round(time.time(), 3), "pid": os.getpid(), "test": os.environ.get(TEST_ENV), "request": os.environ.get(REQUEST_ENV), "worker": os.environ.get(WORKER_ENV), **fields}
    try:
        with open(path, "a", encoding="utf-8") as fh:
            fh.write(json.dumps(row, default=str) + "\n")
    except OSError:
        pass
