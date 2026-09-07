"""The `-p` entry of the incremental gate (feature 207): `-p l7r.diagram.ci.gate_plugin` on every traced gate run.

WHY THIS FILE IS TINY. A `-p` plugin is imported while pytest parses its command line, BEFORE pytest-cov's
`pytest_load_initial_conftests` starts measuring - so every line executed at this module's import (the imports,
the `def` lines) is invisible to coverage on every worker. The first draft loaded `selection.py` this way, and
the gate reported its import-time lines, `incremental.py`'s constants and `state.py`'s dataclass fields - 130
lines no test could ever reach - as uncovered. So this shim holds ONLY what pytest must see at load time: two
hook functions whose bodies run after coverage has started and delegate, one line each, to `selection.py`,
which they import lazily and which is measured like any other module. Its own five import-time lines are
measured by `tests/tooling/ci/test_incremental.py`, which RELOADS the module under coverage (a reload re-runs
the body; pluggy keeps the hook objects it registered, so the running gate is unaffected). Nothing else may be
added here; add it to `selection.py`. (`# pragma: exclude file` is NOT a coverage feature, whatever
coverage's own `pth_file.py` says - it was tried first and excluded nothing.)
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
