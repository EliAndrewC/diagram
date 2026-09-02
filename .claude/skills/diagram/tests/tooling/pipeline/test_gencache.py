"""tooling tests split out of `tests.pipeline.test_gencache` (feature 133 T29, GM 2026-08-26): `make quick` collects
`tests/` minus the tier, gate and tooling trees, so these are neither imported nor collected while the scope is
locked to another tier; the gate collects everything. Helpers stay in the source module and are imported."""

from __future__ import annotations

import os
import subprocess
import sys

import pytest

from l7r.diagram.pipeline import gencache
from tests.pipeline.test_gencache import HERE, _fixture, _with_engine


@pytest.mark.tooling
def test_a_gen_that_ends_by_exiting_does_not_kill_the_sweep(tmp_path, monkeypatch):
    """Every Mode A gen ends `raise SystemExit(main())` - a normal successful return for a script,
    but `runpy` runs it in THIS interpreter, so it used to propagate straight out of regen.py and
    stop the batch dead at exit 0. `regen.py pool/*/*/*.gen.py` did the nine hamlets, hit the first
    magistracy, and reported success having skipped every town, village and city (2026-08-08)."""
    eng, gen, out = _fixture(tmp_path)
    _with_engine(monkeypatch, tmp_path, eng)
    gen.write_text(gen.read_text() + "\nraise SystemExit(0)\n")
    deps = gencache.run_and_record(str(gen))  # must RETURN, not raise
    assert out.read_text() == "7"  # ...and the gen still ran to completion
    assert deps["functions"], "the dep capture must survive the exit too"


@pytest.mark.tooling
def test_a_gen_that_exits_NONZERO_still_fails_loudly(tmp_path, monkeypatch):
    # the other direction: a real failure must not be swallowed by the tolerance above
    eng, gen, _ = _fixture(tmp_path)
    _with_engine(monkeypatch, tmp_path, eng)
    gen.write_text(gen.read_text() + "\nraise SystemExit(2)\n")
    with pytest.raises(SystemExit):
        gencache.run_and_record(str(gen))


@pytest.mark.tooling
def test_a_foreign_parallel_coverage_file_reaches_the_report(tmp_path):
    """R3 spike - THE load-bearing mechanism of the cache-backed gate (026): a parallel-mode
    coverage data file present beside the session's data file is merged by
    `coverage combine --append` (the Makefile line) and its lines count in the report. If this
    breaks, gate hits starve the coverage floors - so it is pinned in miniature: a pytest-cov run
    covers one function, a 'foreign' recorder covers the other, and the combined report must show
    the module at 100%."""
    (tmp_path / "spikemod.py").write_text("def by_pytest():\n    return 1\n\n\ndef by_replay():\n    return 2\n")
    (tmp_path / "test_spike.py").write_text("import spikemod\n\n\ndef test_covers():\n    assert spikemod.by_pytest() == 1\n")
    (tmp_path / "drive.py").write_text("import spikemod\n\nspikemod.by_replay()\n")
    env = {k: v for k, v in os.environ.items() if not k.startswith(("COV_CORE_", "COVERAGE_", "PYTEST_"))}

    def run(*cmd: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(list(cmd), cwd=tmp_path, env=env, capture_output=True, text=True)

    a = run(sys.executable, "-m", "pytest", "test_spike.py", "-q", "-p", "no:cacheprovider", "--cov=spikemod", "--cov-report=")
    assert a.returncode == 0, a.stdout + a.stderr
    b = run(sys.executable, "-m", "coverage", "run", "--parallel-mode", "drive.py")
    assert b.returncode == 0, b.stdout + b.stderr
    c = run(sys.executable, "-m", "coverage", "combine", "--append")
    assert c.returncode == 0, c.stdout + c.stderr
    d = run(sys.executable, "-m", "coverage", "report", "--include=spikemod.py", "--fail-under=100")
    assert d.returncode == 0, f"the foreign data file's lines must reach the combined report:\n{d.stdout}{d.stderr}"


@pytest.mark.tooling
def test_regen_skips_frozen_legacy_maps():
    """The 2026-08-16 legacy freeze, enforced at the ITERATION path: `regen.py pool/*/*/*.gen.py`
    must not rewrite a frozen exhibit - the engine drifts freely now, so a re-run would replace
    committed artifacts with output nobody reviewed. The skip happens BEFORE any cache or
    generation work, and the message carries the policy and the `--frozen-ok` override (tips live
    in the blocking output, not in docs the moment forgets)."""
    import contextlib
    import io

    from l7r.diagram.pipeline import regen

    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        rc = regen.main([os.path.join(HERE, "legacy-hand-authored-pool", "towns", "hoshizora", "hoshizora.gen.py")])
    out = buf.getvalue()
    assert rc == 0
    assert "FROZEN" in out and "--frozen-ok" in out and "migration-plan.md" in out
    assert "REGENERATED" not in out and "CACHED" not in out, out


# ---- feature 174: the defensive branches, under the GM's 2026-09-02 all-code rule ---------------
# Every one of these is a DEGRADATION path: the cache's job is to be invisible when it works and to
# get out of the way when it cannot. A cache that raised would take the whole map roll with it, so
# each of these answers "regenerate" rather than propagating.
import json
import pathlib
from typing import Any


def test_a_path_that_cannot_be_made_RELATIVE_is_recorded_absolute(monkeypatch: pytest.MonkeyPatch) -> None:
    """A different drive or an unresolvable pair. The key still has to be computable, so the absolute
    path is recorded rather than the dependency being dropped - dropping it would make two different
    trees hash identically."""

    def unrelatable(*_a: Any, **_kw: Any) -> str:
        raise ValueError("path is on mount 'C:', start on mount '/'")

    monkeypatch.setattr(os.path, "relpath", unrelatable)
    assert gencache._rel("/somewhere/else/x.py") == "/somewhere/else/x.py"


def test_source_that_does_not_PARSE_hashes_as_bytes_with_no_split(monkeypatch: pytest.MonkeyPatch) -> None:
    """Unparseable is still content: it gets a whole-file hash and contributes no per-function
    entries, so a syntactically broken engine file invalidates everything rather than nothing."""
    whole, funcs, names = gencache._split_sources(b"def broken(:\n")
    assert whole and funcs == {} and names == set()


def test_a_memo_that_cannot_be_WRITTEN_still_returns_its_answer(tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """A read-only tree loses the memo, never the answer - the same rule the module states for its
    other OSError. The split is recomputed next time; nothing is wrong except that it costs more."""
    src = tmp_path / "m.py"
    src.write_text("def f():\n    return 1\n")

    real = pathlib.Path.write_text

    def readonly(self: Any, *a: Any, **k: Any) -> Any:
        if self.suffix == ".tmp" or "split" in str(self):
            raise OSError("read-only file system")
        return real(self, *a, **k)

    monkeypatch.setattr(pathlib.Path, "write_text", readonly)
    whole, funcs, _names = gencache.split_sources(str(src))
    assert whole and funcs, "the answer came back regardless"


def test_an_ABSENT_renderer_is_recorded_as_absent_rather_than_crashing(monkeypatch: pytest.MonkeyPatch) -> None:
    """The renderer version is part of the key, because a resvg upgrade can change the PNG. When
    resvg is not installed the honest key component is the string "absent" - it still distinguishes
    that state from any installed version."""

    def no_resvg(*_a: Any, **_kw: Any) -> Any:
        raise OSError("no such binary")

    monkeypatch.setattr(subprocess, "run", no_resvg)
    assert gencache._renderer_version() == "absent"


def test_an_UNRESOLVABLE_dependency_state_forces_a_miss_every_time(monkeypatch: pytest.MonkeyPatch) -> None:
    """The one branch that deliberately returns a value that can never match: if the installed
    packages cannot be read, the safe answer is "this is a different environment from every other",
    which regenerates. Guessing "same as last time" would serve a map built against other libraries."""
    import glob as _glob

    def boom(*_a: Any, **_kw: Any) -> Any:
        raise RuntimeError("importlib.metadata is unhappy")

    monkeypatch.setattr(_glob, "glob", boom)
    gencache._deps_state.cache_clear()
    a = gencache._deps_state()
    gencache._deps_state.cache_clear()
    b = gencache._deps_state()
    assert a.startswith("unresolvable-") and b.startswith("unresolvable-")
    assert a != b, "and two resolutions never agree, so such a state can never hit"
    gencache._deps_state.cache_clear()


def test_load_MISSES_when_the_entry_has_no_metadata(tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """A half-written entry - killed mid-store, or hand-deleted - must miss rather than raise."""
    monkeypatch.setattr(gencache, "CACHE_DIR", str(tmp_path))
    (tmp_path / "x").mkdir()  # an entry directory with no meta.json in it
    assert gencache.load("x.gen.py") is False


def test_unreadable_stored_coverage_is_DOUBT_and_doubt_regenerates(tmp_path: pathlib.Path) -> None:
    """The comment says it outright: "unreadable stored coverage IS doubt, and doubt regenerates".
    A cache that resolved doubt in its own favour is the failure mode this whole module fears."""
    bad = tmp_path / "not-coverage.dat"
    bad.write_bytes(b"certainly not a coverage database")
    assert gencache._coverage_is_current(str(bad)) is False


def test_the_open_SPY_ignores_a_file_object_it_cannot_take_a_path_of(monkeypatch: pytest.MonkeyPatch) -> None:
    """The dependency recorder wraps `open` to note what a generator READ. `open` also accepts a file
    descriptor, and `os.path.abspath` on an int raises - so the spy must fall through to the real
    `open` rather than taking down the roll it is only observing."""
    seen: list[str] = []

    def run() -> None:
        fd = os.open(__file__, os.O_RDONLY)
        try:
            with open(fd, closefd=False) as fh:  # noqa: PTH123 - a file DESCRIPTOR, which is the point
                fh.read(1)
            seen.append("read through a descriptor")
        finally:
            os.close(fd)

    rec = gencache.record(run)
    assert seen == ["read through a descriptor"], "the read still happened"
    assert isinstance(rec, dict), "and the recorder returned a dependency record regardless"


def test_the_recorder_notes_which_ENGINE_FUNCTIONS_a_roll_executed() -> None:
    """The per-function half of the key: `record` watches starts through `sys.monitoring` and keeps
    the ones whose file is engine code. Nested qualnames carry `.<locals>.`, which the AST walk does
    not, so they are normalized to match - a mismatch there would make every key miss."""
    from l7r.diagram.settlement import Settlement

    def run() -> None:
        s = Settlement(200, 200, seed=1)
        s.meta(name="T", scale="village", ftpx=1)

    rec = gencache.record(run)
    funcs = rec.get("functions") or rec.get("funcs") or {}
    assert funcs, "the roll executed engine functions and they were recorded"
    assert not any(".<locals>" in str(name) for entry in [funcs] for name in (entry if isinstance(entry, (list, set, tuple)) else entry.keys())), "qualnames are normalized"


def test_load_DELETES_a_standing_output_the_cached_entry_does_not_carry(tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """The 2026-08-17 fix. A gate-built entry is stored with rendering skipped, so it has no PNG - and
    the stale PNG on disk was left in place and re-dated by the copy of its siblings. Nothing looked
    wrong (all three files carried the same mtime) and two review rounds judged the wrong image.
    "The key matched THIS entry's outputs; it says nothing about a file the entry does not contain."
    """
    monkeypatch.setattr(gencache, "CACHE_DIR", str(tmp_path / "cache"))
    gen = tmp_path / "m.gen.py"
    gen.write_text("x = 1\n")
    entry = tmp_path / "cache" / "m"
    entry.mkdir(parents=True)
    (entry / "m.json").write_bytes(b"{}")
    key = gencache.compute_key(str(gen), None)
    (entry / "meta.json").write_text(json.dumps({"key": key, "outputs": ["m.json"]}))
    stale_png = tmp_path / "m.png"
    stale_png.write_bytes(b"the PREVIOUS roll's picture")

    assert gencache.load(str(gen)) is True
    assert not stale_png.exists(), "the entry has no PNG, so the standing one is deleted to force a re-render"
    assert (tmp_path / "m.json").is_file(), "and what the entry DOES carry is restored"


def test_a_memo_whose_REPLACE_fails_still_answers(tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """The atomic rename at the end of the memo write. A read-only tree loses the memo, never the
    answer - the split is simply recomputed next time."""
    src = tmp_path / "mm.py"
    src.write_text("def f():\n    return 2\n")
    monkeypatch.setattr(gencache, "CACHE_DIR", str(tmp_path / "cache"))
    gencache._SPLIT_MEMO.clear()

    def no_replace(*_a: Any, **_kw: Any) -> Any:
        raise OSError("read-only file system")

    monkeypatch.setattr(os, "replace", no_replace)
    whole, funcs, _ = gencache.split_sources(str(src))
    assert whole and funcs, "the answer came back"


def test_store_EVICTS_a_stale_png_from_the_entry_rather_than_blessing_it(tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """ "EVICT, DO NOT SKIP." A `continue` alone leaves a PNG already sitting in the entry directory,
    and the meta.json written below then blesses that stale image as THIS key's output - so a later
    hit restores the previous roll's picture beside a current manifest. Four settlement-reviews on
    2026-08-23 each independently found the shipped PNG was the pre-feature-126 roll, on all four
    scripted hamlets, and reviewed the wrong image before noticing."""
    monkeypatch.setattr(gencache, "CACHE_DIR", str(tmp_path / "cache"))
    monkeypatch.setenv("DIAGRAM_SKIP_RENDER", "1")
    gen = tmp_path / "m.gen.py"
    gen.write_text("x = 1\n")
    (tmp_path / "m.json").write_bytes(b"{}")
    entry = tmp_path / "cache" / "m"
    entry.mkdir(parents=True)
    (entry / "m.png").write_bytes(b"the PREVIOUS roll's picture")

    gencache.store(str(gen), {})
    assert not (entry / "m.png").exists(), "the stale image is evicted, not blessed as this key's output"


def test_a_gate_regeneration_that_FAILS_raises_with_the_child_s_own_output(tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """The gate regenerates in a subprocess so the entry gains coverage data. When that child dies,
    the parent must raise carrying the CHILD's stdout and stderr - a bare "regeneration failed" would
    send a reader to run the generator by hand just to see the traceback the parent already had."""
    monkeypatch.setattr(gencache, "CACHE_DIR", str(tmp_path / "cache"))
    monkeypatch.setenv("GATE_NO_CACHE", "1")  # force the MISS path
    gen = tmp_path / "boom.gen.py"
    gen.write_text("raise SystemExit('the generator exploded')\n")

    def failed(*_a: Any, **_kw: Any) -> Any:
        return subprocess.CompletedProcess([], 1, "stdout: partway through", "stderr: the generator exploded")

    monkeypatch.setattr(subprocess, "run", failed)
    with pytest.raises(RuntimeError, match="gate regeneration failed for boom"):
        gencache.gate_obtain(str(gen))
    try:
        gencache.gate_obtain(str(gen))
    except RuntimeError as e:
        assert "the generator exploded" in str(e), "the child's own output travels with the failure"
        assert "exit 1" in str(e)
