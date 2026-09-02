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
