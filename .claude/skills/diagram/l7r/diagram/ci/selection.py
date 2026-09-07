"""The pytest plugin of the incremental gate (feature 207), reached through `-p l7r.diagram.ci.gate_plugin`.

WHY TWO MODULES: `gate_plugin.py` is what `-p` loads, which happens before pytest-cov starts measuring, so its
import-time lines can never be covered; it is excluded with the reason at its top and holds two one-line delegates.
Everything real is here, imported lazily from those delegates once coverage is running.

Two jobs. (1) FIXTURE CONTEXTS: pytest-cov's `--cov-context=test` attributes a fixture's setup to whichever
test first asked for it, so a session fixture that rolls a hamlet is recorded under ONE test's `setup`
while forty tests read what it built. This plugin switches the coverage context to `fixture:<name>` around
every fixture setup and back to the test's phase after, so `incremental.py` can select every test whose
fixture closure touched a change. On the controller it also writes `tests.json` (nodeid -> fixture closure)
and the fixture dependency graph, which the merge uses to drop the contexts of fixtures affected
transitively. (2) SELECTION: when the plan says incremental, it keeps the affected tests, every test in a
changed test module, and every test the baseline never saw, and deselects the rest - identically on the
controller and every xdist worker, since the decision is a function of the same files. Above
`FULL_FRACTION` it keeps everything and marks the run FULL, so the Makefile saves a baseline from it.
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from typing import Any

import pytest

from l7r.diagram.ci import incremental

ENV = "L7R_GATE_SELECT"  # the baseline directory; set by the Makefile on a traced gate run


def _cov(config: pytest.Config) -> Any:
    plugin = config.pluginmanager.get_plugin("_cov")
    ctl = getattr(plugin, "cov_controller", None)
    return ctl.cov if ctl is not None and getattr(ctl, "started", False) else None


def switch(cov: Any, name: str) -> None:
    """Switch the coverage context AND RE-ARM THE FAST CORE'S EVENTS (spec D8, measured 2026-09-07). Python
    3.14's default `sys.monitoring` core disables a line's event after its first hit, so without this the
    second context to execute a line records nothing - four of eight contexts lost on the fixture project.
    `restart_events()` re-arms every disabled event, so each context records each line it executes once:
    the per-context line sets equal the C tracer's (12 of 12 rows), at one event per line per context
    instead of one per execution - the C tracer cost a full run 2.4x. Harmless under any other core."""
    cov.switch_context(name)
    sys.monitoring.restart_events()


class GateSelection:
    def __init__(self, bdir: Path, plan: dict[str, Any], closures: dict[str, list[str]]) -> None:
        self.bdir = bdir
        self.plan = plan
        self.closures = closures
        self.nodeid = ""
        self.phase = "setup"

    # ---- fixture contexts ----
    @pytest.hookimpl(hookwrapper=True, tryfirst=True)
    def pytest_runtest_setup(self, item: pytest.Item) -> Any:
        self.nodeid, self.phase = item.nodeid, "setup"
        cov = _cov(item.config)
        if cov is not None:
            switch(cov, f"{item.nodeid}|setup")  # pytest-cov switches to the same name after us; the re-arm is ours
        yield

    @pytest.hookimpl(hookwrapper=True, tryfirst=True)
    def pytest_runtest_call(self, item: pytest.Item) -> Any:
        self.nodeid, self.phase = item.nodeid, "run"
        cov = _cov(item.config)
        if cov is not None:
            switch(cov, f"{item.nodeid}|run")  # pytest-cov switches to the same name after us; the re-arm is ours
        yield

    @pytest.hookimpl(hookwrapper=True, tryfirst=True)
    def pytest_runtest_teardown(self, item: pytest.Item) -> Any:
        self.nodeid, self.phase = item.nodeid, "teardown"
        cov = _cov(item.config)
        if cov is not None:
            switch(cov, f"{item.nodeid}|teardown")  # pytest-cov switches to the same name after us; the re-arm is ours
        yield

    @pytest.hookimpl(hookwrapper=True)
    def pytest_fixture_setup(self, fixturedef: Any, request: Any) -> Any:
        cov = _cov(request.config)
        if cov is not None:
            switch(cov, f"fixture:{fixturedef.argname}")
        try:
            yield
        finally:
            if cov is not None:
                switch(cov, f"{self.nodeid}|{self.phase}")

    # ---- selection ----
    @pytest.hookimpl(trylast=True)
    def pytest_collection_modifyitems(self, session: pytest.Session, config: pytest.Config, items: list[pytest.Item]) -> None:
        pl = self.plan
        collected = [it.nodeid for it in items]
        graph = fixture_graph(items)
        mode, selected, reason = pl["mode"], collected, pl.get("reason", "")
        if pl["mode"] == "incremental":
            keep = keep_set(pl, collected, self.closures)
            fraction = float(pl.get("full_fraction", incremental.FULL_FRACTION))
            if len(keep) > fraction * len(items):
                mode, reason = "full", f"{len(keep)} of {len(items)} tests selected, over the {fraction:.0%} fraction - running everything and recording a baseline"
            else:
                selected = [n for n in collected if n in keep]
                dropped = [it for it in items if it.nodeid not in keep]
                items[:] = [it for it in items if it.nodeid in keep]
                config.hook.pytest_deselected(items=dropped)
        if _writer(config):
            self.bdir.mkdir(parents=True, exist_ok=True)
            (self.bdir / (incremental.TESTS + ".next")).write_text(json.dumps({it.nodeid: sorted(getattr(it, "fixturenames", ())) for it in _all_items(session, items)}, indent=0), encoding="utf-8")
            (self.bdir / incremental.RESULT).write_text(
                json.dumps({"mode": mode, "reason": reason, "selected": selected, "collected": collected, "fixture_dependents": graph}, indent=0), encoding="utf-8"
            )
            if pl["mode"] == "incremental":
                print(f"\ngate: {mode.upper()} - {len(selected)} of {len(collected)} tests selected ({reason})")


def _all_items(session: pytest.Session, kept: list[pytest.Item]) -> list[pytest.Item]:
    """Every collected item, deselected ones included - the baseline's `tests.json` must know them all."""
    seen = {it.nodeid for it in kept}
    return kept + [it for it in getattr(session, "_l7r_all_items", []) if it.nodeid not in seen]


def _writer(config: pytest.Config) -> bool:
    """Which process writes the result: the only one in a serial run, or worker `gw0` under xdist - the
    CONTROLLER never collects (it receives the workers' collections), so `pytest_collection_modifyitems`
    never fires there; every worker computes the same result from the same files, so one writer suffices."""
    info = getattr(config, "workerinput", None)
    return info is None or info.get("workerid") == "gw0"


def fixture_graph(items: list[pytest.Item]) -> dict[str, list[str]]:
    """fixture name -> the fixtures that request it (the REVERSE dependency edges the merge walks)."""
    dependents: dict[str, set[str]] = {}
    for it in items:
        info = getattr(it, "_fixtureinfo", None)
        if info is None:
            continue
        for name, defs in info.name2fixturedefs.items():
            for fd in defs:
                for dep in fd.argnames:
                    dependents.setdefault(dep, set()).add(name)
    return {k: sorted(v) for k, v in sorted(dependents.items())}


def keep_set(pl: dict[str, Any], collected: list[str], closures: dict[str, list[str]]) -> set[str]:
    """The tests to run: affected by their own contexts, by a fixture in their closure, by their module, or new."""
    affected = set(pl["affected_tests"])
    fixtures = set(pl["affected_fixtures"])
    modules = set(pl["changed_test_modules"])
    baseline = set(pl["baseline_tests"])
    out = set()
    for nodeid in collected:
        module = nodeid.split("::", 1)[0]
        if nodeid in affected or nodeid not in baseline or module in modules or fixtures and fixtures & set(closures.get(nodeid, ())):
            out.add(nodeid)
    return out


def configure(config: pytest.Config) -> None:
    """`gate_plugin.pytest_configure`'s body: read the plan and register the selection plugin."""
    bdir = Path(os.environ[ENV])
    plan_file, tests = bdir / incremental.PLAN, bdir / incremental.TESTS
    pl = json.loads(plan_file.read_text(encoding="utf-8")) if plan_file.is_file() else {"mode": "full", "reason": "no plan"}
    closures = json.loads(tests.read_text(encoding="utf-8")) if pl["mode"] == "incremental" and tests.is_file() else {}
    config.pluginmanager.register(GateSelection(bdir, pl, closures), "_l7r_gate_selection")


def remember_all(session: pytest.Session, items: list[pytest.Item]) -> None:
    """`gate_plugin.pytest_collection_modifyitems`'s body, which runs before any deselection (ours or `-m`'s):
    remember every collected item, so `tests.json` knows the deselected ones too."""
    session._l7r_all_items = list(items)  # type: ignore[attr-defined]
