"""The regen driver (`pipeline/regen.py`) - feature 174, when the GM ruled that every engine module
owes 100% coverage the day it lands and this one had never been measured at all.

It is `make`'s way into the generators, so its argv handling IS its contract: which files it accepts,
what it refuses under the scope lock, how many workers it takes, and that a worker's captured stdout
reaches the terminal in one piece rather than interleaved with its siblings'.

`tooling`, because it drives the cache and the process pool.
"""

from __future__ import annotations

import concurrent.futures
from typing import Any

import pytest

from l7r.diagram.pipeline import regen

pytestmark = pytest.mark.tooling


class _Cache:
    """Stands in for `gencache`. Records what it was asked so the test can assert the ORDER."""

    def __init__(self, hit: bool = False) -> None:
        self.hit, self.calls = hit, []

    def load(self, gen: str) -> bool:
        self.calls.append(("load", gen))
        return self.hit

    def run_and_record(self, gen: str) -> list[str]:
        self.calls.append(("run", gen))
        print(f"drawing {gen}")
        return ["dep.py"]

    def store(self, gen: str, deps: list[str]) -> None:
        self.calls.append(("store", gen, tuple(deps)))


def test_a_cache_HIT_reports_CACHED_and_never_runs_the_generator(monkeypatch: pytest.MonkeyPatch) -> None:
    """The whole point of the cache: a map whose inputs did not change is not redrawn. The assertion
    that matters is not the word CACHED but that `run_and_record` was never called."""
    cache = _Cache(hit=True)
    monkeypatch.setattr(regen, "gencache", cache)
    how, took = regen.regen("pool/hamlets/x/x.gen.py")
    assert how == "CACHED" and took >= 0.0
    assert cache.calls == [("load", "pool/hamlets/x/x.gen.py")], "no run, no store"


def test_a_MISS_runs_the_generator_and_then_stores_what_it_depended_on(monkeypatch: pytest.MonkeyPatch) -> None:
    """Store AFTER the run, with the deps the run reported - storing first would key the cache on a
    dependency set the map was not actually drawn from."""
    cache = _Cache(hit=False)
    monkeypatch.setattr(regen, "gencache", cache)
    how, _took = regen.regen("g.gen.py")
    assert how == "REGENERATED"
    assert [c[0] for c in cache.calls] == ["load", "run", "store"], cache.calls
    assert cache.calls[-1] == ("store", "g.gen.py", ("dep.py",))


def test_use_cache_False_skips_the_lookup_entirely(monkeypatch: pytest.MonkeyPatch) -> None:
    cache = _Cache(hit=True)
    monkeypatch.setattr(regen, "gencache", cache)
    assert regen.regen("g.gen.py", use_cache=False)[0] == "REGENERATED"
    assert [c[0] for c in cache.calls] == ["run", "store"], "the cache is not even asked"


def test_a_workers_stdout_is_CAPTURED_so_parallel_runs_cannot_interleave(monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> None:
    """Each worker's output is buffered and printed whole by the parent. Without this, two generators
    drawing at once produce a shuffled transcript that says nothing about either."""
    monkeypatch.setattr(regen, "gencache", _Cache(hit=False))
    how, _took, out = regen.regen_captured("g.gen.py", True)
    assert how == "REGENERATED"
    assert out == "drawing g.gen.py\n", "the gen's own print came back as a string"
    assert "drawing" not in capsys.readouterr().out, "and did NOT reach the terminal directly"


@pytest.fixture
def _driver(monkeypatch: pytest.MonkeyPatch) -> _Cache:
    """`main` with the cache stubbed and nothing frozen - the shape most argv tests want."""
    cache = _Cache(hit=False)
    monkeypatch.setattr(regen, "gencache", cache)
    monkeypatch.setattr(regen.poolmaps, "classify", lambda _g: "live")
    return cache


def test_no_arguments_prints_the_usage_and_refuses(_driver: _Cache, capsys: pytest.CaptureFixture[str]) -> None:
    """rc 2, not 0: `make` must be able to tell "you gave me nothing" from "nothing needed doing"."""
    assert regen.main(["--no-cache"]) == 2
    assert "regen" in capsys.readouterr().out.lower()


def test_a_path_that_is_not_a_gen_py_is_NAMED_and_skipped(_driver: _Cache, capsys: pytest.CaptureFixture[str]) -> None:
    """Silently ignoring it is the failure: a typo'd path would look like a successful no-op run."""
    assert regen.main(["notes.md"]) == 0
    assert "skipping notes.md" in capsys.readouterr().out


def test_a_FROZEN_map_is_refused_by_name_unless_forced(monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> None:
    """The legacy hand-authored maps are frozen (2026-08-16): regenerating one would overwrite an
    exhibit nobody can reproduce. It says so and carries on rather than failing the whole run."""
    cache = _Cache(hit=False)
    monkeypatch.setattr(regen, "gencache", cache)
    monkeypatch.setattr(regen.poolmaps, "classify", lambda _g: "legacy")
    assert regen.main(["old.gen.py"]) == 0
    out = capsys.readouterr().out
    assert "FROZEN" in out and "old" in out
    assert cache.calls == [], "and it was not drawn"

    assert regen.main(["old.gen.py", "--frozen-ok"]) == 0
    assert [c[0] for c in cache.calls] == ["load", "run", "store"], "--frozen-ok forces it"


def test_JOBS_is_parsed_off_argv_and_its_VALUE_is_not_mistaken_for_a_path(_driver: _Cache, capsys: pytest.CaptureFixture[str]) -> None:
    """`--jobs 4` is hand-parsed, so the 4 has to be removed from the positional list too - otherwise
    it lands in `args` and is reported as a skipped non-gen file."""
    assert regen.main(["a.gen.py", "--jobs", "4"]) == 0
    assert "skipping 4" not in capsys.readouterr().out


def test_a_MULTI_MAP_regen_is_refused_under_the_scope_lock(monkeypatch: pytest.MonkeyPatch) -> None:
    """A shell glob expands before `make` sees it, so this module is the ONLY place a whole-pool
    sweep can be caught (feature 132). One map is always allowed; more than one asks the switch."""
    monkeypatch.setattr(regen, "gencache", _Cache(hit=False))
    monkeypatch.setattr(regen.poolmaps, "classify", lambda _g: "live")
    from l7r.diagram import switches

    monkeypatch.setattr(switches, "locked_out", lambda _why: True)
    assert regen.main(["a.gen.py", "b.gen.py"]) == 2, "the sweep is refused"
    assert regen.main(["a.gen.py"]) == 0, "one map is never a sweep"


def test_several_maps_run_through_the_POOL_and_each_worker_s_output_is_printed_whole(monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> None:
    """The parallel path, with a pool that maps in-process so the test stays deterministic. What is
    asserted is the contract the real pool has to keep: one result per gen, in order, each with its
    own captured stdout printed before its status line."""
    monkeypatch.setattr(regen, "gencache", _Cache(hit=False))
    monkeypatch.setattr(regen.poolmaps, "classify", lambda _g: "live")
    from l7r.diagram import switches

    monkeypatch.setattr(switches, "locked_out", lambda _why: False)

    class _Pool:
        def __init__(self, max_workers: int) -> None:
            self.max_workers = max_workers

        def __enter__(self) -> _Pool:
            return self

        def __exit__(self, *_a: Any) -> None:
            return None

        def map(self, fn: Any, *iterables: Any) -> Any:
            return [fn(*args) for args in zip(*iterables, strict=True)]

    monkeypatch.setattr(concurrent.futures, "ProcessPoolExecutor", _Pool)
    assert regen.main(["a.gen.py", "b.gen.py", "--jobs", "2"]) == 0
    out = capsys.readouterr().out
    assert "drawing a.gen.py" in out and "drawing b.gen.py" in out, "each worker's own output"
    assert out.index("drawing a.gen.py") < out.index("drawing b.gen.py"), "in gen order, not shuffled"
    assert out.count("REGENERATED") == 2
