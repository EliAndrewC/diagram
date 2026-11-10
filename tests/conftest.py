"""The test suite itself runs through make, or not at all (feature 127, FR-002).

WHY THE SUITE AND NOT JUST THE GENERATORS. `pytest` is the single most expensive thing in this
project that is not a map: the full suite is ~4.5 minutes, and it was reached for directly over and
over while `make quick` (~33 s) sat unused. The command-shape hook refuses a bare `pytest` before it
runs, and this is the layer beneath it - it catches the invocations the hook's patterns do not
anticipate, and it cannot be walked around by spelling the command differently.

IT IS A NO-OP ON THE LEGITIMATE PATH. Every make target that runs tests satisfies the determination,
and so does every pytest-xdist worker and every subprocess they spawn - ancestry is inherited
(verified in `test_invocation.py`). So this fires only when someone runs pytest by hand outside make,
which is the case it exists for.

THE REFUSAL NAMES THE TARGET, as every refusal in this feature must: a guard that blocks a legitimate
action without offering the route is a guard that gets worked around, which is not a theory - gating
bare pytest before `make durations` and `make test-file` existed left "why is this slow" and "re-run
the file I just changed" with no answer but the override.
"""

from __future__ import annotations

import os

import pytest

from l7r.diagram._invocation import assert_via_make

# TESTS DO NOT RENDER (feature 213, GM 2026-09-07: "Tests must not render real maps ... A suite-wide default, with the
# handful of tests that test rendering itself opting in"). The gate reads manifests; a PNG is resvg at 420 MB and the
# page's raster picture a 444 MB PIL child, and the census found both made by tests that never looked at them (the
# cache round-trip test regenerated a real map with its picture). So the switch `finish()` consults for both is set
# here for every test; a test OF rendering carries the `renders` marker and clears it itself, and the roll census
# fails the gate on a render from any other test (`ci/rollverdict.py`). `setdefault`, so a session that exports the
# variable for its own reasons is not overridden.
os.environ.setdefault("DIAGRAM_SKIP_RENDER", "1")

# THE ENGINE'S VERSION-KEYED CACHES CHECK THEMSELVES UNDER THE SUITE (feature 387, plan D4/D5): a cache keyed on a registry's
# own version is right only while every writer bumps it - so here every hit of the plots' sun boxes re-reads the plots, and the
# bamboo strip index re-reads what it filed, and each raises if they moved. A writer that forgot to bump fails a test instead of
# answering stale. Off outside the suite: the check costs what the cache saves.
os.environ.setdefault("L7R_CHECK_CACHES", "1")

# At import of the suite's root conftest - once, before any test runs.
# No durations in the message (2026-09-27): it said ~33 s and ~5.5 min long after both had moved, the stale
# figure test_guard_message_durations.py forbids - a literal handed to `assert_via_make` is printed, but
# that check reads only direct print/write calls in engine modules, so it could not see this one.
assert_via_make("the test suite", "quick   (lint, types, the unit tests)  or  make done   (the full gate)")

pytest_plugins = ["pytester"]

# The run log's first and last failure times (GM 2026-10-03): a mark per failed test, only when `make done`
# names the file. Re-exported so pytest finds the hooks here; the body is in `tests/_gate_failures.py`.
from tests._gate_failures import pytest_collectreport, pytest_runtest_logreport  # noqa: E402, F401

# A worker's freed heap goes back to the kernel after a test that grew it (2026-10-04): the body and the measurement
# are in `tests/_heap.py`.
from tests._heap import pytest_runtest_protocol  # noqa: E402, F401

TIERS = ("hamlet", "village", "town", "city", "capital")


def pytest_addoption(parser):  # type: ignore[no-untyped-def]
    parser.addoption(
        "--tier", default=None, choices=TIERS, help="run only tests relevant to this settlement tier (untagged tests always run); the Makefile passes the reference tier while scope is locked"
    )


@pytest.hookimpl(tryfirst=True)
def pytest_collection_modifyitems(config, items):  # type: ignore[no-untyped-def]
    """TIER RELEVANCE (GM 2026-08-26, feature 133 T17): a test tagged for other tiers cannot say anything about the map on the sheet."""
    tier = config.getoption("--tier")
    keep, drop = [], []
    for item in items:
        m = item.get_closest_marker("tiers")
        (drop if m is not None and tier and tier not in m.args else keep).append(item)
    if drop:
        config.hook.pytest_deselected(items=drop)
        items[:] = keep


_TIER_DIRS = {"hamlet": "hamlets", "village": "villages", "town": "towns", "city": "provincial-cities", "capital": "capitals"}


@pytest.fixture
def pool_tier_glob(request):  # type: ignore[no-untyped-def]
    """The pool subdirectory pattern a pool-wide test sweeps: the tier's own directory under
    `--tier X` (GM 2026-08-26: a hamlet run has no reason to parse every city's SVG), `*` otherwise."""
    tier = request.config.getoption("--tier")
    return _TIER_DIRS[tier] if tier else "*"


def pytest_report_header(config):  # type: ignore[no-untyped-def]
    from tests._scope import EXHAUSTIVE, FULL

    tier = config.getoption("--tier")
    lines = []
    if tier:
        lines.append(f"tier: {tier} - tests tagged for other tiers only are deselected (scope locked to the reference settlement)")
    lines.append("scope: EXHAUSTIVE - every sweep in full" if EXHAUSTIVE else "scope: quick - sweeps run their documented subset (EXHAUSTIVE=1 for the full form)")
    if FULL:
        lines.append("scope: FULL - the full tree is collected, the coverage floors are enforced, no cache serves a roll")
    return lines
