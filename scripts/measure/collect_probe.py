"""A pytest plugin `collect_cost.py` loads (`-p collect_probe`): in every process of a run - the controller and each xdist worker -
how many test modules were imported and how many tests were collected, written to `$L7R_COLLECT_PROBE/<process>.json`
(feature 383 amendment 3, plan D25: does a worker import the test files the run will not run?)."""

from __future__ import annotations

import json
import os
import sys


def pytest_collection_finish(session) -> None:  # noqa: ANN001
    out = os.environ.get("L7R_COLLECT_PROBE")
    if not out:
        return
    who = getattr(session.config, "workerinput", {}).get("workerid", "controller")
    modules = sorted(m for m in sys.modules if m.startswith("tests.") and m.rsplit(".", 1)[-1].startswith("test_"))
    with open(os.path.join(out, f"{who}.json"), "w", encoding="utf-8") as fh:
        json.dump({"test_modules_imported": len(modules), "items": len(session.items)}, fh)
