"""The roll cache (feature 135) is allowed to exist for the same reason the pool cache is: it is DEMONSTRABLY
safe. Every test asks the pool cache's question - can a change reach the payload without moving the key? - on a
toy engine, and the bypasses and the doubt rule are pinned so a served roll is never a stale one."""

from __future__ import annotations

import importlib
import json
import os
import sys
import textwrap
from pathlib import Path

import pytest

from l7r.diagram.pipeline import gencache, rollcache

# `keyed_to` through an alias: the marker guard (tests/test_markers.py) reads `rollcache.keyed_to` as a map roll, which
# it is everywhere but here - this file rolls a TOY engine in milliseconds and belongs to the quick tree.
keyed_to_toy = rollcache.keyed_to
hamlet_toy, report_toy = rollcache.hamlet, rollcache.report  # feature 219: the two views on a stood-in child, no map rolled

_ENGINE = """
CONSTANT = 3

def used(x):
    return x * CONSTANT + int(open({data!r}).read())

def unused(x):
    return x * 999
"""


def _toy(tmp_path, monkeypatch):
    """A toy engine + a `produce` that rolls through it; gencache pointed at the temp dir."""
    mod = "re_" + "".join(c if c.isalnum() else "_" for c in os.path.basename(str(tmp_path)))
    data = tmp_path / "grain.txt"
    data.write_text("1")
    eng = tmp_path / f"{mod}.py"
    eng.write_text(textwrap.dedent(_ENGINE).format(data=str(data)))
    monkeypatch.syspath_prepend(str(tmp_path))
    monkeypatch.setattr(gencache, "engine_files", lambda: [str(eng)])
    monkeypatch.setattr(gencache, "CACHE_DIR", str(tmp_path / "cache"))
    monkeypatch.setattr(gencache, "_renderer_version", lambda: "pinned")
    monkeypatch.delenv(gencache.GATE_BYPASS, raising=False)
    monkeypatch.delenv(rollcache.FULL_ENV, raising=False)
    # A RUN STORE OF ITS OWN (feature 214): `reset_shared()` removes the run share directory, and under the gate
    # these tests ran with the GATE'S xdist id - every reset wiped the payloads sibling workers had placed, and
    # the census showed the reference rolled twice by two workers seconds apart. A per-test id keeps the resets here.
    monkeypatch.setenv("PYTEST_XDIST_TESTRUNUID", "toy-" + os.path.basename(str(tmp_path)))

    def produce():
        m = importlib.reload(importlib.import_module(mod)) if mod in importlib.sys.modules else importlib.import_module(mod)
        return {"value": m.used(2)}

    return eng, data, produce


def test_a_miss_records_the_roll_and_the_next_call_hits_with_the_same_payload(tmp_path, monkeypatch):
    eng, _, produce = _toy(tmp_path, monkeypatch)
    first, how = rollcache.obtain("toy", produce)
    assert (first, how) == ({"value": 7}, "MISS")
    entry = Path(rollcache._entry("toy"))
    meta = json.loads((entry / "meta.json").read_text())
    assert any(q == "used" for _f, q in meta["deps"]["functions"]), "the roll's executed function is recorded"
    assert not any(q == "unused" for _f, q in meta["deps"]["functions"])
    assert rollcache.obtain("toy", lambda: pytest.fail("a hit must not produce")) == (first, "HIT")


def test_a_change_to_an_executed_function_rolls_again_and_an_unexecuted_one_does_not(tmp_path, monkeypatch):
    eng, _, produce = _toy(tmp_path, monkeypatch)
    rollcache.obtain("toy", produce)
    eng.write_text(eng.read_text().replace("return x * 999", "return x * 998"))
    assert rollcache.obtain("toy", produce)[1] == "HIT", "a function the roll never executed cannot reach the payload"
    eng.write_text(eng.read_text().replace("x * CONSTANT", "x * CONSTANT + 1"))
    assert rollcache.obtain("toy", produce) == ({"value": 8}, "MISS"), "a changed executed function rolls for real"


def test_a_data_file_the_roll_read_is_a_dependency(tmp_path, monkeypatch):
    _, data, produce = _toy(tmp_path, monkeypatch)
    rollcache.obtain("toy", produce)
    data.write_text("5")
    assert rollcache.obtain("toy", produce) == ({"value": 11}, "MISS")
    data.unlink()
    assert rollcache.obtain("toy", lambda: {"value": -1}) == ({"value": -1}, "MISS"), "a vanished data file is doubt, and doubt produces"


def test_a_half_written_or_foreign_entry_is_doubt(tmp_path, monkeypatch):
    _, _, produce = _toy(tmp_path, monkeypatch)
    rollcache.obtain("toy", produce)
    entry = Path(rollcache._entry("toy"))
    (entry / "payload.pickle").write_bytes(b"not a pickle")
    assert rollcache.obtain("toy", produce)[1] == "MISS"
    assert rollcache.obtain("toy", produce)[1] == "HIT", "...and the miss repaired the entry"
    meta = json.loads((entry / "meta.json").read_text())
    (entry / "meta.json").write_text(json.dumps({**meta, "subject": "someone else's"}))
    assert rollcache.obtain("toy", produce)[1] == "MISS", "a subject collision under one hash is never served"
    (entry / "meta.json").write_text("{")
    assert rollcache.obtain("toy", produce)[1] == "MISS"


def test_a_roll_keyed_to_a_test_is_remade_when_that_test_changes(tmp_path, monkeypatch):
    """`keyed_to` puts the test function's SOURCE in the key - the only place a monkeypatch can change."""
    _, _, produce = _toy(tmp_path, monkeypatch)

    def a_test():
        return 1

    def a_test_edited():
        return 2

    first = keyed_to_toy(a_test, produce)
    assert first == ({"value": 7}, "MISS")
    assert keyed_to_toy(a_test, produce) == ({"value": 7}, "HIT")
    assert keyed_to_toy(a_test, produce, label="other")[1] == "MISS", "a label is a different roll"
    assert keyed_to_toy(a_test_edited, produce)[1] == "MISS", "a different source is a different key"


@pytest.mark.parametrize("var", [gencache.GATE_BYPASS, rollcache.FULL_ENV])
def test_the_bypasses_produce_and_store_nothing(tmp_path, monkeypatch, var):
    # A SUBJECT NAME PER PARAMETER, because the shared store is shared ACROSS WORKERS (2026-09-12). Both
    # parameters used to roll `toy` and `shared-toy`, and `reset_shared()` clears the run store - but a
    # CONCURRENT worker running the other parameter can re-write it between the reset and the assert, so the
    # isolation held only while the scheduler happened to keep the two apart in time. It stopped holding the
    # day the gate moved from `worksteal` to `loadgroup` (which runs a module's tests closer together), and the
    # failure was the one `reset_shared`'s own docstring records from the last time this shape bit: the second
    # parameter saw `BYPASS-SHARED-RUN` where it asserted `BYPASS`. A unique subject removes the collision
    # instead of timing around it, and it is right under any scheduler.
    _subj, _shared = f"toy-{var.lower()}", f"shared-toy-{var.lower()}"
    _, _, produce = _toy(tmp_path, monkeypatch)
    monkeypatch.setenv(var, "1")
    rollcache.reset_shared()
    assert rollcache.obtain(_subj, produce) == ({"value": 7}, "BYPASS")
    assert rollcache.obtain(_subj, produce) == ({"value": 7}, "BYPASS"), "sharing is OPT-IN: a plain caller always produces"
    assert not Path(rollcache._entry(_subj)).exists()

    # ...AND A CALLER THAT OPTS IN DOES NOT ROLL TWICE (feature 147). The bypass exists so the coverage
    # floors watch real execution; one execution is all they can watch, and the 31 scripted fixtures share
    # two specs between them, so re-rolling per caller cost ~430 s of CPU to trace lines one roll traces.
    assert rollcache.obtain(_shared, produce, share=True) == ({"value": 7}, "BYPASS")
    again, how = rollcache.obtain(_shared, produce, share=True)
    assert (again, how) == ({"value": 7}, "BYPASS-SHARED")
    assert not Path(rollcache._entry(_shared)).exists(), "sharing still stores nothing on disk"

    monkeypatch.delenv(var)
    assert rollcache.obtain(_subj, produce)[1] == "MISS", "a bypassed roll left nothing behind to serve"


# FEATURE 192 SPLIT THIS PROPERTY IN TWO, and the split is the feature. The parametrized test above
# still holds for every subject it names - `toy` is not a `report:` roll - but the FULL bypass now
# RECORDS its `report:` rolls, because the floor that reads those records was re-rolling the same maps
# for a measured 401.6 s. `GATE_NO_CACHE` keeps its documented leave-nothing-behind contract, and these
# cases exist so a future edit cannot quietly merge the two again.
def test_the_FULL_bypass_records_a_roll_subject_and_a_later_run_can_serve_it(tmp_path, monkeypatch) -> None:  # type: ignore[no-untyped-def]
    _, _, produce = _toy(tmp_path, monkeypatch)
    monkeypatch.setenv(rollcache.FULL_ENV, "1")
    rollcache.reset_shared()
    assert rollcache.obtain("roll:toy", produce) == ({"value": 7}, "BYPASS-STORED")
    assert rollcache.obtain("roll:toy", produce)[1] == "BYPASS-STORED", "the FULL run still PRODUCES every time - never served"
    assert Path(rollcache._entry("roll:toy")).exists(), "the record the hamlet-path floor reads"
    monkeypatch.delenv(rollcache.FULL_ENV)
    assert rollcache.obtain("roll:toy", produce)[1] == "HIT", "a later non-FULL run serves what the FULL run recorded - the whole saving"


def test_GATE_NO_CACHE_still_stores_nothing_even_for_a_report_roll(tmp_path, monkeypatch) -> None:  # type: ignore[no-untyped-def]
    """`GATE_NO_CACHE=1` is the documented 'regenerate everything, leave nothing behind' escape
    (gencache.py). `bypassed()` is true for it AND for the FULL run, so the two are easy to conflate;
    feature 192 changed only the FULL one."""
    _, _, produce = _toy(tmp_path, monkeypatch)
    monkeypatch.setenv(gencache.GATE_BYPASS, "1")
    rollcache.reset_shared()
    assert rollcache.obtain("report:toy", produce) == ({"value": 7}, "BYPASS")
    assert not Path(rollcache._entry("report:toy")).exists()


def test_GATE_NO_CACHE_wins_when_both_are_set(tmp_path, monkeypatch) -> None:  # type: ignore[no-untyped-def]
    """`GATE_NO_CACHE=1 make done` is a real, documented recovery, so both variables are set together."""
    _, _, produce = _toy(tmp_path, monkeypatch)
    monkeypatch.setenv(gencache.GATE_BYPASS, "1")
    monkeypatch.setenv(rollcache.FULL_ENV, "1")
    rollcache.reset_shared()
    assert rollcache.obtain("report:toy", produce)[1] == "BYPASS"
    assert not Path(rollcache._entry("report:toy")).exists(), "the leave-nothing-behind escape must win"


def test_the_FULL_bypass_stores_nothing_for_a_NON_report_subject(tmp_path, monkeypatch) -> None:  # type: ignore[no-untyped-def]
    """Confinement (FR-004): only `report:` rolls feed the floor. `hamlet:` is the shared fixture path
    and `test:` rolls are monkeypatched; recording them would buy nothing and widen the blast radius."""
    _, _, produce = _toy(tmp_path, monkeypatch)
    monkeypatch.setenv(rollcache.FULL_ENV, "1")
    rollcache.reset_shared()
    assert rollcache.obtain("hamlet:toy", produce)[1] == "BYPASS"
    assert not Path(rollcache._entry("hamlet:toy")).exists()


def test_report_deps_records_once_and_then_reads_the_record(tmp_path, monkeypatch) -> None:  # type: ignore[no-untyped-def]
    """`report_deps` (feature 145, the hamlet-path floor): the first call rolls (in a child, feature 213) and records,
    the second returns the record without rolling - and it is never bypassed, unlike `obtain`. The record is the
    CHILD's (feature 210: the functions ran there), under the one `roll:` subject the tests' own roll uses (213)."""
    import os

    from l7r.diagram import hamletgen as hg
    from l7r.diagram.pipeline import rollcache

    calls: list[int] = []

    def fake_child(spec):  # type: ignore[no-untyped-def]
        calls.append(1)
        return (("plan", {"M": 1}, "report"), {"functions": [], "files": []})

    monkeypatch.setattr(rollcache, "_hamlet_in_child", fake_child)
    monkeypatch.setattr(rollcache, "_entry", lambda subject: str(tmp_path / "entry"))
    monkeypatch.setenv("L7R_TESTS_FULL", "1")  # bypass is for SERVING; recording still happens
    spec = hg.HamletSpec(name="Probe", seed=1, households=10)
    first = rollcache.report_deps(spec)
    assert calls == [1] and "functions" in first and os.path.isfile(tmp_path / "entry" / "meta.json")
    again = rollcache.report_deps(spec)
    assert calls == [1] and again == first


def test_a_shared_bypass_hands_out_copies_so_one_caller_cannot_break_another(tmp_path, monkeypatch):  # type: ignore[no-untyped-def]
    """THE WHOLE SAFETY ARGUMENT FOR SHARING (feature 147). The scripted negative fixtures each take a rolled
    manifest and DELIBERATELY break it; if they shared one object rather than one set of bytes, the first
    fixture's break would arrive in the next fixture's map and silently disarm it - a suite that still passes
    while proving nothing. A served HIT has always unpickled a fresh payload per caller, and the shared
    bypass keeps exactly that."""
    _, _, produce = _toy(tmp_path, monkeypatch)
    monkeypatch.setenv(rollcache.FULL_ENV, "1")
    rollcache.reset_shared()

    first, _ = rollcache.obtain("copies", produce, share=True)
    first["value"] = "BROKEN BY THE FIRST CALLER"
    second, how = rollcache.obtain("copies", produce, share=True)
    assert how == "BYPASS-SHARED"
    assert second == {"value": 7}, "the second caller gets the roll as it was produced, not as the first left it"
    assert second is not first


def test_two_different_producers_never_share_one_toy_subject(tmp_path, monkeypatch):  # type: ignore[no-untyped-def]
    """`subject` is contracted to determine the roll completely, and in the engine it does. A test may still
    hand two different callables the same short subject, and serving one of them the other's payload would be
    a worse bug than the re-rolling this replaces - so the producer's code object joins the share key."""
    _, _, produce = _toy(tmp_path, monkeypatch)
    monkeypatch.setenv(rollcache.FULL_ENV, "1")
    rollcache.reset_shared()

    def other() -> dict:
        return {"value": 99}

    assert rollcache.obtain("same-name", produce, share=True) == ({"value": 7}, "BYPASS")
    assert rollcache.obtain("same-name", other, share=True) == ({"value": 99}, "BYPASS"), "a different producer is a different roll"


def test_a_sibling_workers_payload_is_read_from_the_RUN_store(tmp_path, monkeypatch):  # type: ignore[no-untyped-def]
    """`BYPASS-SHARED-RUN` - the cross-worker read, covered DETERMINISTICALLY rather than by luck.

    THE DEFECT THIS CLOSES, and it was a live flake in the 100% floor. These five lines are reached only
    when one xdist worker finds a payload another worker of the same run has already written, so whether
    they execute depends on how the workers interleave. Two FULL builds of the SAME COMMIT on 2026-09-03
    disagreed about it: the cold one measured 22,544 statements at 100%, the warm one at 99% with
    `rollcache.py:180-184` missing - and since feature 174 made the floor a hard gate, that is a
    `make done` which goes red for nobody's mistake. Whoever hit it next would have gone looking for a
    change that was not there.

    The sibling is simulated exactly as the mechanism defines it: the RUN store is on disk (the first
    call put it there) while this process's own dict is empty, which is precisely what a second worker
    sees. Nothing about the timing is left to the scheduler."""
    _, _, produce = _toy(tmp_path, monkeypatch)
    monkeypatch.setenv(rollcache.FULL_ENV, "1")
    # a run to scope the store to, whether or not this suite is itself running under xdist
    monkeypatch.setenv("PYTEST_XDIST_TESTRUNUID", "feature-177-cross-worker")
    rollcache.reset_shared()

    first, how = rollcache.obtain("cross-worker", produce, share=True)
    assert how == "BYPASS", "the first caller produces it and writes the run store"

    rollcache._SHARED_BYPASS.clear()  # ...and now this process is the SIBLING: no dict, but a run store
    again, how = rollcache.obtain("cross-worker", produce, share=True)
    assert how == "BYPASS-SHARED-RUN", "a payload this RUN produced is read across the worker boundary"
    assert again == first and again is not first, "a fresh copy, exactly as a served HIT hands out"


def test_a_recorded_producer_stores_the_record_it_brings_and_the_next_call_hits(tmp_path, monkeypatch):  # type: ignore[no-untyped-def]
    """Feature 210: `obtain(recorded=)` is `produce` with its own dependency record - a roll made in a child
    records itself there. The MISS stores that record and the next call is a HIT with the same payload."""
    eng, data, produce = _toy(tmp_path, monkeypatch)

    def recorded():  # type: ignore[no-untyped-def]
        holder = []
        deps = gencache.record(lambda: holder.append(produce()))
        return holder[0], deps

    payload, how = rollcache.obtain("recorded-toy", produce, recorded=recorded)
    assert how == "MISS" and payload == {"value": 7}
    meta = json.loads(Path(rollcache._entry("recorded-toy"), "meta.json").read_text())
    assert str(eng) in json.dumps(meta["deps"]), "the record the producer brought is what was stored"
    assert rollcache.obtain("recorded-toy", produce, recorded=recorded) == ({"value": 7}, "HIT")


def test_a_failing_roll_child_raises_with_its_stderr(monkeypatch: pytest.MonkeyPatch) -> None:
    """Feature 210 FR-003: a child that dies is an error naming the failure, never a served roll."""
    monkeypatch.setattr(rollcache, "_CHILD_DRIVER", "import sys\nsys.stderr.write('no engine here')\nsys.exit(7)\n")
    monkeypatch.delenv("COV_CORE_SOURCE", raising=False)
    with pytest.raises(RuntimeError, match=r"(?s)exit 7.*no engine here"):
        rollcache._hamlet_in_child({"a": "toy spec"})  # type: ignore[arg-type]


# the template carries the coverage slots the real driver has (feature 213): a covered parent's child starts its own recorder
_TRIVIAL_CHILD = "{prelude}import pickle\nwith open({out_path!r}, 'wb') as fh:\n    pickle.dump((('plan', {{'M': 1}}), {{'functions': [], 'files': []}}), fh)\n{epilogue}"


def test_the_roll_child_records_coverage_only_under_a_covered_parent(monkeypatch: pytest.MonkeyPatch) -> None:
    """Feature 210 FR-003: with pytest-cov's `COV_CORE_SOURCE` in the parent's environment the child runs under
    `coverage run --parallel-mode` and publishes its data file into the skill directory's `.coverage.*` glob
    (what `coverage combine --append` sweeps, as for `gate_obtain`); without it the child runs plain and
    leaves none. The driver is a trivial template here - the real one rolls a hamlet."""
    monkeypatch.setattr(rollcache, "_CHILD_DRIVER", _TRIVIAL_CHILD)
    here = Path(gencache.HERE)
    before = set(here.glob(".coverage.rollchild-*"))
    monkeypatch.setattr(rollcache, "_parent_is_covered", lambda: False)
    payload, deps = rollcache._hamlet_in_child({"a": "toy spec"})  # type: ignore[arg-type]
    assert payload == ("plan", {"M": 1}) and deps == {"functions": [], "files": []}
    assert set(here.glob(".coverage.rollchild-*")) == before, "a plain parent gets a plain child"
    monkeypatch.setattr(rollcache, "_parent_is_covered", lambda: True)
    try:
        rollcache._hamlet_in_child({"a": "toy spec"})  # type: ignore[arg-type]
        rollcache._hamlet_in_child({"b": "another spec"})  # type: ignore[arg-type]
        published = set(here.glob(".coverage.rollchild-*")) - before
        assert len(published) == 2, "each child publishes its OWN data file - a name keyed on the worker alone lost a roll's coverage (the landing gate)"
    finally:
        for f in set(here.glob(".coverage.rollchild-*")) - before:
            f.unlink()


def test_the_parent_knows_when_it_is_covered_by_either_signal(monkeypatch: pytest.MonkeyPatch) -> None:
    """Feature 210: the gate that landed this feature lost three lines of `water.py` because the child took its
    cue from `COV_CORE_SOURCE` alone and this pytest-cov never sets it; the live `coverage.Coverage` in the
    worker is the signal that is actually there. Either suffices; neither means plain."""
    import types

    monkeypatch.delenv("COV_CORE_SOURCE", raising=False)

    class _Cov:
        current = staticmethod(lambda: None)

    monkeypatch.setitem(sys.modules, "coverage", types.SimpleNamespace(Coverage=_Cov))
    assert rollcache._parent_is_covered() is False, "no env, no live coverage: plain"
    monkeypatch.setitem(sys.modules, "coverage", types.SimpleNamespace(Coverage=types.SimpleNamespace(current=lambda: object())))
    assert rollcache._parent_is_covered() is True, "a live Coverage in this process"
    monkeypatch.setitem(sys.modules, "coverage", types.SimpleNamespace(Coverage=_Cov))
    monkeypatch.setenv("COV_CORE_SOURCE", "l7r")
    assert rollcache._parent_is_covered() is True, "pytest-cov's environment signal, where a version sets it"


def test_a_run_with_no_xdist_id_has_no_shared_store(monkeypatch: pytest.MonkeyPatch) -> None:
    """WITHOUT xdist there is no run to scope a shared payload to, so `_run_share_path` returns None
    and the per-process dict above it is the whole mechanism - exactly as it was before cross-worker
    sharing landed.

    This branch needs a test written FOR it because no suite run can reach it: the gate and the full
    run both use `-n 8`, where xdist sets `PYTEST_XDIST_TESTRUNUID` in every worker, so the id is
    always present and the early return is dead ground. It was the one line of the sharing change
    that the 100% floor caught (FULL, 2026-08-31) - and the floor only runs in FULL, so a green
    `make done` could not have seen it.
    """
    monkeypatch.delenv("PYTEST_XDIST_TESTRUNUID", raising=False)
    assert rollcache._run_share_path(("subject", "producer")) is None


def test_the_first_wave_waits_on_one_roll_instead_of_each_rolling(tmp_path, monkeypatch) -> None:  # type: ignore[no-untyped-def]
    """Feature 213 FR-002: two workers asking for the same shared subject at the same moment make ONE roll - the
    second waits on the first's lock and reads the payload it wrote. Threads stand in for workers (each `os.open`
    is its own file description, so `flock` separates them exactly as it separates processes); a fresh
    PYTEST_XDIST_TESTRUNUID gives them a run store of their own."""
    import threading
    import time as _time

    from l7r.diagram.pipeline import rollcache

    _toy(tmp_path, monkeypatch)
    monkeypatch.setenv(rollcache.FULL_ENV, "1")
    monkeypatch.setenv("PYTEST_XDIST_TESTRUNUID", "lock-test-" + tmp_path.name)
    monkeypatch.setattr(rollcache.tempfile, "gettempdir", lambda: str(tmp_path))
    rollcache.reset_shared()
    rolls: list[int] = []

    def slow_produce():  # type: ignore[no-untyped-def]
        rolls.append(1)
        _time.sleep(0.6)
        return {"value": 42}

    results: list[tuple[dict, str]] = []

    def worker() -> None:
        rollcache._SHARED_BYPASS.clear()  # each "worker" starts with an empty process dict, as a real one does
        results.append(rollcache.obtain("shared-lock-toy", slow_produce, share=True))

    threads = [threading.Thread(target=worker) for _ in range(3)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    assert rolls == [1], "three simultaneous requests, one roll"
    assert sorted(h for _p, h in results) == ["BYPASS", "BYPASS-SHARED-RUN", "BYPASS-SHARED-RUN"] and all(p == {"value": 42} for p, _h in results)
    rollcache.reset_shared()


def test_a_wedged_lock_holder_does_not_hang_the_run(tmp_path, monkeypatch) -> None:  # type: ignore[no-untyped-def]
    """FR-002's bound: past LOCK_WAIT_S a waiter proceeds and rolls itself - today's behavior, never a hang."""
    import fcntl
    import os

    from l7r.diagram.pipeline import rollcache

    run_path = str(tmp_path / "share" / "payload.pickle")
    os.makedirs(os.path.dirname(run_path))
    holder = os.open(run_path + ".lock", os.O_RDWR | os.O_CREAT)
    fcntl.flock(holder, fcntl.LOCK_EX)  # a holder that never releases
    monkeypatch.setattr(rollcache, "LOCK_WAIT_S", 0.4)
    entered = []
    with rollcache._share_lock(run_path):
        entered.append(1)
    assert entered == [1], "the waiter gave up waiting and went on"
    os.close(holder)
    with rollcache._share_lock(None):
        pass  # no run store: nothing to lock


def test_the_roll_slots_bound_how_many_child_rolls_run_at_once(tmp_path, monkeypatch) -> None:  # type: ignore[no-untyped-def]
    """Feature 213 FR-010: with one slot, two rolls serialize; the second starts only when the first releases."""
    import threading
    import time as _time

    from l7r.diagram.pipeline import rollcache

    monkeypatch.setenv(rollcache.ROLL_SLOTS_ENV, "1")
    monkeypatch.delenv("PYTEST_XDIST_TESTRUNUID", raising=False)
    monkeypatch.setattr(rollcache.tempfile, "gettempdir", lambda: str(tmp_path))
    spans: list[tuple[float, float]] = []

    def hold() -> None:
        with rollcache._roll_slot():
            t0 = _time.time()
            _time.sleep(0.3)
            spans.append((t0, _time.time()))

    a, b = threading.Thread(target=hold), threading.Thread(target=hold)
    a.start()
    b.start()
    a.join()
    b.join()
    (s0, e0), (s1, e1) = sorted(spans)
    assert s1 >= e0 - 0.01, f"the second roll started at {s1 - s0:.2f}s, before the first released at {e0 - s0:.2f}s"
    monkeypatch.setenv(rollcache.ROLL_SLOTS_ENV, "2")
    spans.clear()
    a, b = threading.Thread(target=hold), threading.Thread(target=hold)
    a.start()
    b.start()
    a.join()
    b.join()
    (s0, e0), (s1, e1) = sorted(spans)
    assert s1 < e0, "with two slots the two rolls overlap"


def test_a_covered_child_is_labeled_with_the_parent_s_coverage_context(tmp_path, monkeypatch) -> None:
    """Feature 213 (found on the polder-only run): the child's coverage data must carry its requester's context, or
    the incremental gate cannot select the test that rolls. Under a covered parent with a context exported the
    child runs `coverage run --context=<it>`; with no context exported, no flag; with no coverage, plain python."""
    import pickle
    import subprocess

    from l7r.diagram import _census
    from l7r.diagram.pipeline import gencache

    seen: list[list[str]] = []

    def fake_run(cmd, **kw):
        driver = Path(cmd[-1]).read_text()
        seen.append(driver)
        workdir = os.path.dirname(cmd[-1])
        with open(os.path.join(workdir, "out.pickle"), "wb") as fh:
            pickle.dump(("payload", {"functions": [], "files": []}), fh)
        if "_covmod.Coverage(" in driver:
            open(os.path.join(workdir, "cov.abc"), "w").close()  # the parallel-mode data file the child would leave
        return subprocess.CompletedProcess(cmd, 0, "", "")

    monkeypatch.setattr(subprocess, "run", fake_run)
    monkeypatch.setattr(gencache, "HERE", str(tmp_path))
    monkeypatch.setattr(rollcache, "_parent_is_covered", lambda: True)
    monkeypatch.setenv(_census.CONTEXT_ENV, "fixture:inashiro")
    assert rollcache._in_child("mod:fn", None)[0] == "payload"
    d = seen[-1]
    assert "_covmod.Coverage(" in d and "_cov.switch_context('fixture:inashiro')" in d and "_cov.save()" in d
    assert d.index("_cov.start()") < d.index("import l7r.diagram.hamletgen") < d.index("switch_context"), "coverage starts before the engine imports; the label applies only to the roll"
    assert [f for f in os.listdir(tmp_path) if f.startswith(".coverage.rollchild-")], "the child's data file is published for the combine"
    monkeypatch.delenv(_census.CONTEXT_ENV)
    rollcache._in_child("mod:fn", None)
    assert "_covmod.Coverage(" in seen[-1] and "switch_context" not in seen[-1]
    monkeypatch.setattr(rollcache, "_parent_is_covered", lambda: False)
    rollcache._in_child("mod:fn", None)
    assert "_covmod" not in seen[-1]


def test_a_child_roll_keyed_to_a_test_is_shared_across_workers_under_the_full_run(tmp_path, monkeypatch):  # type: ignore[no-untyped-def]
    """Feature 216: `keyed_to(..., child=)` shares like `hamlet()` does. Without `share=True` the FULL run's bypass
    stored the child's record and served nobody, so a module fixture reached from two xdist workers rolled the
    seatings twice - the census named both tests. Simulated as the sibling worker exactly as the test above."""
    _toy(tmp_path, monkeypatch)
    monkeypatch.setenv(rollcache.FULL_ENV, "1")
    monkeypatch.setenv("PYTEST_XDIST_TESTRUNUID", "feature-216-keyed-child")
    rollcache.reset_shared()
    calls: list[str] = []

    def in_child(child, arg):  # type: ignore[no-untyped-def]
        calls.append(child)
        return {"seated": 10}, {}

    monkeypatch.setattr(rollcache, "_in_child", in_child)

    def a_test() -> None:
        pass

    first, how = keyed_to_toy(a_test, lambda: {"seated": 10}, child="tests.x:roll")
    assert how == "BYPASS" and calls == ["tests.x:roll"], (how, calls)
    rollcache._SHARED_BYPASS.clear()  # the sibling worker: no dict, but this run's store
    again, how = keyed_to_toy(a_test, lambda: {"seated": 10}, child="tests.x:roll")
    assert how == "BYPASS-SHARED-RUN" and again == first, how
    assert calls == ["tests.x:roll"], "the child ran ONCE for the run"


def test_the_roll_payload_is_generate_s_plan_manifest_and_report(monkeypatch) -> None:  # type: ignore[no-untyped-def]
    """`_roll_payload` (feature 213), on a stood-in `generate`: the child's target returns the three views one roll
    serves. Feature 219: the gate rolls no spec of its own, so the machinery is proved here rather than by a polder."""
    from l7r.diagram import hamletgen as hg

    spec = hg.HamletSpec(name="Probe", seed=1, households=10)
    plan = hg.plan_site(spec)
    fake = hg.Report(plan=plan, failures=[], attempt=1, rerolled_after=[], manifest={"houses": []})
    monkeypatch.setattr(hg, "generate", lambda s, out_base=None, render=False: fake)
    got_plan, manifest, rep = rollcache._roll_payload(spec)
    assert got_plan is plan and manifest == {"houses": []} and rep is fake


def test_hamlet_and_report_are_two_views_of_the_one_child_roll(tmp_path, monkeypatch) -> None:  # type: ignore[no-untyped-def]
    """`hamlet()` and `report()` read the same `roll:<spec>` subject (feature 213 FR-001) - one child roll, shared;
    the second view is served from the run's share, never rolled again."""
    from l7r.diagram import hamletgen as hg

    calls: list[int] = []

    def fake_child(spec):  # type: ignore[no-untyped-def]
        calls.append(1)
        return (("plan", {"M": 1}, "report"), {"functions": [], "files": []})

    monkeypatch.setattr(rollcache, "_hamlet_in_child", fake_child)
    monkeypatch.setattr(rollcache, "_entry", lambda subject: str(tmp_path / "entry"))
    monkeypatch.setenv(rollcache.FULL_ENV, "1")
    monkeypatch.setenv("PYTEST_XDIST_TESTRUNUID", "feature-219-two-views-" + tmp_path.name)
    rollcache.reset_shared()
    spec = hg.HamletSpec(name="Probe", seed=2, households=10)
    assert hamlet_toy(spec) == ("plan", {"M": 1})
    rep, how = report_toy(spec)
    assert rep == "report" and how.startswith("BYPASS-SHARED"), how
    assert calls == [1], "one roll serves both views"


def test_the_childs_stderr_is_forwarded_under_the_stage_profile_flag(monkeypatch, capsys):
    """Feature 222 FR-005 (Principle XIV): `make map PROFILE=1` prints the stage profile again. The child
    writes it to its stderr; `_in_child` forwards that stream when `L7R_STAGE_PROFILE` is set and stays
    silent when it is not (a test roll's child is quiet by design)."""
    monkeypatch.setattr(
        rollcache, "_CHILD_DRIVER", "import pickle, sys\nsys.stderr.write('stage profile Toy seed 1: 0.1s total\\n')\nwith open({out_path!r}, 'wb') as fh:\n    pickle.dump(('payload', {{}}), fh)\n"
    )
    monkeypatch.delenv(rollcache.STAGE_PROFILE_ENV, raising=False)
    assert rollcache._in_child("x:y", None)[0] == "payload"
    assert "stage profile" not in capsys.readouterr().err
    monkeypatch.setenv(rollcache.STAGE_PROFILE_ENV, "1")
    assert rollcache._in_child("x:y", None)[0] == "payload"
    assert "stage profile Toy seed 1" in capsys.readouterr().err
