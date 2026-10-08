"""The `-p` entry of the roll census (feature 213): `-p l7r.diagram.ci.rollcensus` on every floored gate run.

TINY, for the reason `gate_plugin.py` is tiny: a `-p` module is imported before pytest-cov starts measuring,
so anything at module level here is unmeasurable. The hooks delegate, one line each, to `rollverdict.py`,
which is imported lazily and measured like any other module.

What the plugin does: ATTRIBUTION. The census records are written by the engine at its chokepoints
(`_census.py`); the plugin puts the requesting test's id and a per-test request id into the environment
around each test, so every record - in the worker or in any child the test spawns - names the test that
caused it, and records this worker's pid so an in-process roll can be told from a child's. It also moves the
map-rolling tests to the front of collection (spec FR-010): the long rolls start at t=0 instead of four
minutes in.
"""

from __future__ import annotations

import os
from typing import Any


def pytest_configure(config: Any) -> None:
    if os.environ.get("L7R_ROLL_CENSUS"):
        from l7r.diagram.ci import rollverdict

        rollverdict.configure()


def pytest_collection_modifyitems(session: Any, config: Any, items: list[Any]) -> None:
    """Before `gate_plugin`'s trylast deselection, which keeps the order it is given."""
    if os.environ.get("L7R_ROLL_CENSUS"):
        from l7r.diagram.ci import rollverdict

        rollverdict.rolls_first(items)


def pytest_runtest_protocol(item: Any, nextitem: Any) -> None:
    """Not a hookwrapper: sets the environment for the test about to run; `pytest_runtest_logfinish` clears it."""
    if os.environ.get("L7R_ROLL_CENSUS"):
        from l7r.diagram.ci import rollverdict

        rollverdict.begin(item.nodeid)


def pytest_runtest_logfinish(nodeid: str, location: Any) -> None:
    if os.environ.get("L7R_ROLL_CENSUS"):
        from l7r.diagram.ci import rollverdict

        rollverdict.end()
