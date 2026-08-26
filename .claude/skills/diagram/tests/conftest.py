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

import pytest

from l7r.diagram._invocation import assert_via_make

# At import of the suite's root conftest - once, before any test runs.
assert_via_make("the test suite", "quick   (~33 s)  or  make done   (~5.5 min, the full gate)")

pytest_plugins = ["pytester"]

TIERS = ("hamlet", "village", "town", "city", "capital")


def pytest_addoption(parser):  # type: ignore[no-untyped-def]
    parser.addoption(
        "--tier", default=None, choices=TIERS, help="run only tests relevant to this settlement tier (untagged tests always run); the Makefile passes the reference tier while scope is locked"
    )


def pytest_collection_modifyitems(config, items):  # type: ignore[no-untyped-def]
    """TIER RELEVANCE (GM 2026-08-26, feature 133 T17): while scope is locked to the reference hamlet,
    a test tagged `tiers("town", "city")` cannot say anything about the map on the sheet - skip it.
    A test with no `tiers` marker is relevant to every tier and always runs."""
    tier = config.getoption("--tier")
    if not tier:
        return
    keep, drop = [], []
    for item in items:
        m = item.get_closest_marker("tiers")
        (drop if m is not None and tier not in m.args else keep).append(item)
    if drop:
        config.hook.pytest_deselected(items=drop)
        items[:] = keep
        config._tier_dropped = len(drop)  # type: ignore[attr-defined]


_TIER_DIRS = {"hamlet": "hamlets", "village": "villages", "town": "towns", "city": "provincial-cities", "capital": "capitals"}


@pytest.fixture
def pool_tier_glob(request):  # type: ignore[no-untyped-def]
    """The pool subdirectory pattern a pool-wide test sweeps: the tier's own directory under
    `--tier X` (GM 2026-08-26: a hamlet run has no reason to parse every city's SVG), `*` otherwise."""
    tier = request.config.getoption("--tier")
    return _TIER_DIRS[tier] if tier else "*"


def pytest_report_header(config):  # type: ignore[no-untyped-def]
    tier = config.getoption("--tier")
    return f"tier: {tier} - tests tagged for other tiers only are deselected (scope locked to the reference settlement)" if tier else None
