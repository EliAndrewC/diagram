"""The roll cache (feature 135) is allowed to exist for the same reason the pool cache is: it is DEMONSTRABLY
safe. Every test asks the pool cache's question - can a change reach the payload without moving the key? - on a
toy engine, and the bypasses and the doubt rule are pinned so a served roll is never a stale one."""

from __future__ import annotations

import importlib
import json
import os
import textwrap
from pathlib import Path

import pytest

from l7r.diagram.pipeline import gencache, rollcache

# `keyed_to` through an alias: the marker guard (tests/test_markers.py) reads `rollcache.keyed_to` as a map roll, which
# it is everywhere but here - this file rolls a TOY engine in milliseconds and belongs to the quick tree.
keyed_to_toy = rollcache.keyed_to

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
    _, _, produce = _toy(tmp_path, monkeypatch)
    monkeypatch.setenv(var, "1")
    rollcache.reset_shared()
    assert rollcache.obtain("toy", produce) == ({"value": 7}, "BYPASS")
    assert rollcache.obtain("toy", produce) == ({"value": 7}, "BYPASS"), "sharing is OPT-IN: a plain caller always produces"
    assert not Path(rollcache._entry("toy")).exists()

    # ...AND A CALLER THAT OPTS IN DOES NOT ROLL TWICE (feature 147). The bypass exists so the coverage
    # floors watch real execution; one execution is all they can watch, and the 31 scripted fixtures share
    # two specs between them, so re-rolling per caller cost ~430 s of CPU to trace lines one roll traces.
    assert rollcache.obtain("shared-toy", produce, share=True) == ({"value": 7}, "BYPASS")
    again, how = rollcache.obtain("shared-toy", produce, share=True)
    assert (again, how) == ({"value": 7}, "BYPASS-SHARED")
    assert not Path(rollcache._entry("shared-toy")).exists(), "sharing still stores nothing on disk"

    monkeypatch.delenv(var)
    assert rollcache.obtain("toy", produce)[1] == "MISS", "a bypassed roll left nothing behind to serve"


def test_report_deps_records_once_and_then_reads_the_record(tmp_path, monkeypatch) -> None:  # type: ignore[no-untyped-def]
    """`report_deps` (feature 145, the hamlet-path floor): the first call rolls and records, the second returns the
    record without rolling - and it is never bypassed, unlike `obtain`."""
    import os

    from l7r.diagram import hamletgen as hg
    from l7r.diagram.pipeline import rollcache

    calls: list[int] = []

    def fake_generate(spec, out_base=None, render=False):  # type: ignore[no-untyped-def]
        calls.append(1)
        return {"ok": True}

    monkeypatch.setattr(hg, "generate", fake_generate)
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
