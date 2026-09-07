"""A pytest plugin that records EVERY hamlet roll a full run makes (PYTEST_ADDOPTS=-p rollcensus).

Patches the entry points: `driver.build` (every in-process roll, with its spec), `driver.roll_scope` (the
three tools' stage loops too), `rollcache._hamlet_in_child` (the child rolls), `gencache.gate_obtain` (the
pool sweep: HIT or REGENERATED, in a subprocess) and `gencache.run_and_record` (a gen run in-process, e.g.
the immune test). Each record carries the test that caused it. One JSONL per worker in $ROLLCENSUS_DIR."""

from __future__ import annotations

import json
import os
import time

import pytest

OUT = os.environ["ROLLCENSUS_DIR"]
_rows: list[dict] = []
_current = {"test": None}
_t0 = time.time()


def _spec_row(spec) -> dict:
    return {k: getattr(spec, k, None) for k in ("name", "seed", "households", "field_archetype", "down_deg", "water_sink", "pond_layout", "dike_crop", "settlement_form", "windward")}


def pytest_configure(config: pytest.Config) -> None:
    from l7r.diagram.hamletgen import driver
    from l7r.diagram.pipeline import gencache, rollcache

    real_build = driver.build

    def build(plan, avoid=()):
        t = time.time()
        try:
            return real_build(plan, avoid)
        finally:
            _rows.append({"kind": "build", "test": _current["test"], "spec": _spec_row(plan.spec), "dt": round(time.time() - t, 1), "t": round(time.time() - _t0)})

    driver.build = build

    real_scope = driver.roll_scope

    def roll_scope():
        _rows.append({"kind": "scope", "test": _current["test"], "t": round(time.time() - _t0)})
        return real_scope()

    driver.roll_scope = roll_scope

    real_child = rollcache._hamlet_in_child

    def child(spec):
        t = time.time()
        try:
            return real_child(spec)
        finally:
            _rows.append({"kind": "child", "test": _current["test"], "spec": _spec_row(spec), "dt": round(time.time() - t, 1), "t": round(time.time() - _t0)})

    rollcache._hamlet_in_child = child

    real_obtain = rollcache.obtain

    def obtain(subject, produce, share=False, recorded=None):
        out = real_obtain(subject, produce, share, recorded)
        _rows.append({"kind": "obtain", "test": _current["test"], "subject": subject[:90], "how": out[1], "t": round(time.time() - _t0)})
        return out

    rollcache.obtain = obtain

    real_gate = gencache.gate_obtain

    def gate_obtain(gen):
        t = time.time()
        out = real_gate(gen)
        _rows.append({"kind": "gate_obtain", "test": _current["test"], "gen": os.path.basename(gen), "how": out[1], "dt": round(time.time() - t, 1), "t": round(time.time() - _t0)})
        return out

    gencache.gate_obtain = gate_obtain

    real_rar = gencache.run_and_record

    def run_and_record(gen):
        t = time.time()
        try:
            return real_rar(gen)
        finally:
            _rows.append({"kind": "run_and_record", "test": _current["test"], "gen": os.path.basename(gen), "dt": round(time.time() - t, 1), "t": round(time.time() - _t0)})

    gencache.run_and_record = run_and_record


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_protocol(item: pytest.Item, nextitem: pytest.Item | None):
    _current["test"] = item.nodeid
    yield
    _current["test"] = None


def pytest_sessionfinish(session: pytest.Session, exitstatus: int) -> None:
    worker = os.environ.get("PYTEST_XDIST_WORKER", "controller")
    os.makedirs(OUT, exist_ok=True)
    with open(os.path.join(OUT, f"{worker}-{os.getpid()}.jsonl"), "w") as fh:
        for r in _rows:
            fh.write(json.dumps(r) + "\n")
