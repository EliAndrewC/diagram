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
    assert rollcache.obtain("toy", produce) == ({"value": 7}, "BYPASS")
    assert not Path(rollcache._entry("toy")).exists()
    monkeypatch.delenv(var)
    assert rollcache.obtain("toy", produce)[1] == "MISS", "a bypassed roll left nothing behind to serve"
