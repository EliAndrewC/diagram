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
controller and every xdist worker, since the decision is a function of the same files. It APPLIES the plan
it is given and no longer overrides it: the `FULL_FRACTION` decision moved into the planner in feature 237,
because the gate now narrows pytest's own arguments from the plan and a process given a few modules cannot
then decide to run everything (spec D8).
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from typing import Any

import pytest

from l7r.diagram import _census
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
    os.environ[_census.CONTEXT_ENV] = name  # a coverage child started under this context labels its data with it (feature 213, _census.py)


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
            switch(cov, f"fixture:{fixture_id(fixturedef)}")
        try:
            yield
        finally:
            if cov is not None:
                switch(cov, f"{self.nodeid}|{self.phase}")

    # ---- selection ----
    @pytest.hookimpl(trylast=True)
    def pytest_collection_modifyitems(self, session: pytest.Session, config: pytest.Config, items: list[pytest.Item]) -> None:
        pl = self.plan
        # RESTRICTED: an incremental plan gave pytest its own module list, so this process collected a SUBSET
        # of the tree on purpose (feature 237, FR-002), and nothing here may write a baseline from a partial
        # view - neither `tests.json` nor the fixture graph (FR-004, FR-005).
        #
        # AND THE FRACTION MOVED. Until feature 237 this hook could flip a run to FULL after collection when
        # the selection came out over `FULL_FRACTION` - run everything, record a baseline. That decision is
        # not available to a process whose ARGUMENTS were already narrowed: a run labeled full that collected
        # a subset would skip the merge and judge the 100% floor over that subset alone. So the planner makes
        # it instead, before the arguments are chosen, by projecting the same four rules over the baseline
        # (`incremental.plan`, `over_the_fraction`), and this hook simply applies the plan it is given.
        restricted = pl["mode"] == "incremental"
        collected = [it.nodeid for it in items]
        graph = merge_graphs(getattr(session, "_l7r_graph", {}), fixture_graph(items))
        mode, selected, reason = pl["mode"], collected, pl.get("reason", "")
        if pl["mode"] == "incremental":
            keep = keep_set(pl, collected, self.closures)
            selected = [n for n in collected if n in keep]
            dropped = [it for it in items if it.nodeid not in keep]
            items[:] = [it for it in items if it.nodeid in keep]
            config.hook.pytest_deselected(items=dropped)
        if _writer(config):
            self.bdir.mkdir(parents=True, exist_ok=True)
            if not restricted:  # only a run that collected the whole tree may offer the next baseline (FR-004)
                closures = {**getattr(session, "_l7r_closures", {}), **{it.nodeid: fixture_ids(it) for it in items}}
                (self.bdir / (incremental.TESTS + ".next")).write_text(json.dumps(closures, indent=0), encoding="utf-8")
                (self.bdir / (incremental.GRAPH + ".next")).write_text(json.dumps(graph, indent=0), encoding="utf-8")
            (self.bdir / incremental.RESULT).write_text(
                json.dumps({"mode": mode, "reason": reason, "selected": selected, "collected": collected, "fixture_dependents": graph}, indent=0), encoding="utf-8"
            )
            if pl["mode"] == "incremental":
                print(f"\ngate: {mode.upper()} - {len(selected)} of {len(collected)} tests selected ({reason})")

    @pytest.hookimpl(trylast=True)
    def pytest_sessionfinish(self, session: pytest.Session, exitstatus: int) -> None:
        """AN EMPTY SELECTION IS A GREEN RUN, NOT "NO TESTS RAN". When nothing the baseline exercised has changed
        the plan selects nothing, every test is deselected, and pytest (and xdist's controller) would exit 5 -
        which the Makefile reads as a failed phase. The merged floors are the verdict of such a run, and they
        judge the untouched baseline. Read from the result file, because on the xdist controller this hook runs
        but the collection hook never did."""
        if int(exitstatus) != 5 or self.plan.get("mode") != "incremental":
            return
        res = self.bdir / incremental.RESULT
        if res.is_file() and json.loads(res.read_text(encoding="utf-8")).get("selected") == []:
            session.exitstatus = 0


def merge_graphs(*graphs: dict[str, list[str]]) -> dict[str, list[str]]:
    """The union of several reverse-fixture-edge maps, each key's dependents deduplicated and sorted.

    The run's own graph covers the items that reached the selection hook; the one `remember_all` kept
    covers the marker-deselected ones as well, and `merge` needs both or a changed fixture's dependents
    keep stale contexts (feature 237, FR-005).
    """
    out: dict[str, set[str]] = {}
    for g in graphs:
        for key, dependents in g.items():
            out.setdefault(key, set()).update(dependents)
    return {k: sorted(v) for k, v in sorted(out.items())}


def _writer(config: pytest.Config) -> bool:
    """Which process writes the result: the only one in a serial run, or worker `gw0` under xdist - the
    CONTROLLER never collects (it receives the workers' collections), so `pytest_collection_modifyitems`
    never fires there; every worker computes the same result from the same files, so one writer suffices."""
    info = getattr(config, "workerinput", None)
    return info is None or info.get("workerid") == "gw0"


def fixture_id(fd: Any) -> str:
    """A fixture's identity for contexts and closures: WHERE it is defined plus its name - `tests/gate/test_x.py::rolled`
    for a module fixture, `tests/gate::rolled` for a conftest's, the bare name for the root conftest's (feature 213,
    the polder-only run of 2026-09-08). Feature 207 keyed on the argument name alone, and ten gate modules each define
    a `rolled` fixture of their own - one context name for all of them, so a change one of their rolls touched selected
    every test behind any of them: a polder-only edit re-rolled 18 specs in 297 s where 2 would do."""
    base = getattr(fd, "baseid", "") or ""
    return f"{base}::{fd.argname}" if base else str(fd.argname)


def fixture_ids(item: Any) -> list[str]:
    """The fixture ids in `item`'s closure - the definition each name resolves to for THIS item (the innermost)."""
    info = getattr(item, "_fixtureinfo", None)
    names = list(getattr(item, "fixturenames", ()))
    if info is None:
        return sorted(names)
    out = []
    for name in names:
        defs = info.name2fixturedefs.get(name)
        out.append(fixture_id(defs[-1]) if defs else name)
    return sorted(set(out))


def fixture_graph(items: list[pytest.Item]) -> dict[str, list[str]]:
    """fixture id -> the fixture ids that request it (the REVERSE dependency edges the merge walks)."""
    dependents: dict[str, set[str]] = {}
    for it in items:
        info = getattr(it, "_fixtureinfo", None)
        if info is None:
            continue
        for _name, defs in info.name2fixturedefs.items():
            for fd in defs:
                for dep in fd.argnames:
                    dep_defs = info.name2fixturedefs.get(dep)
                    dependents.setdefault(fixture_id(dep_defs[-1]) if dep_defs else str(dep), set()).add(fixture_id(fd))
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
    remember what the BASELINE needs from every collected item - its fixture closure, and the reverse
    fixture edges - so `tests.json` and `result.json` know the deselected ones too.

    WHY THIS EXISTS AT ALL, which the code never said: `ROLL_DESELECT` and `TIER_SELECT` deselect by MARKER
    even on a full run, and pytest's own mark hook runs before `GateSelection`'s, so the items list that
    reaches the writer is already short of what the next plan's `baseline_tests` must hold. A test missing
    from the baseline is treated as NEW by `keep_set`, so losing them would select every one of them on the
    next gate.

    WHY IT NO LONGER KEEPS THE ITEMS THEMSELVES (feature 237, FR-006): `list(items)` pinned every collected
    `Item` - each with its `__dict__`, its `NodeKeywords`, its `Stash` and its eagerly built request - on
    EVERY worker for the whole run, so nothing deselection freed could be reclaimed. These two derived maps
    are all the baseline ever read from them.
    """
    session._l7r_closures = {it.nodeid: fixture_ids(it) for it in items}  # type: ignore[attr-defined]
    session._l7r_graph = fixture_graph(items)  # type: ignore[attr-defined]
