"""The `-p` entry of the incremental gate (feature 207): `-p l7r.diagram.ci.gate_plugin` on every traced gate run.

# pragma: exclude file

THIS FILE IS EXCLUDED FROM COVERAGE, AND THE REASON IS STRUCTURAL, NOT CONVENIENCE. A `-p` plugin is imported
while pytest parses its command line, BEFORE pytest-cov's `pytest_load_initial_conftests` starts measuring - so
every line executed at this module's import (the imports, the `def` lines) is invisible to coverage on every
worker, forever. The first draft loaded `selection.py` this way, and the gate reported its import-time lines,
`incremental.py`'s constants and `state.py`'s dataclass fields - 130 lines that no test could ever reach - as
uncovered. So this shim holds ONLY what pytest must see at load time: two hook functions whose bodies run
after coverage has started and delegate, one line each, to `selection.py`, which they import lazily and which
is measured like any other module. Nothing else may be added here; add it to `selection.py`.
"""

from __future__ import annotations

import os
from typing import Any


def pytest_configure(config: Any) -> None:
    if os.environ.get("L7R_GATE_SELECT"):
        from l7r.diagram.ci import selection

        selection.configure(config)


def pytest_collection_modifyitems(session: Any, config: Any, items: list[Any]) -> None:
    """Runs FIRST (this module's hook, `tryfirst` by registration order), before any deselection: remembers every collected item."""
    if os.environ.get("L7R_GATE_SELECT"):
        from l7r.diagram.ci import selection

        selection.remember_all(session, items)
