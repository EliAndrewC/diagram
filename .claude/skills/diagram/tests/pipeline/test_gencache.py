#!/usr/bin/env python3
"""The cache is only allowed to exist because it is DEMONSTRABLY safe (GM 2026-08-08: "if both the
coarse and fine grained version are demonstrably safe"). These are that demonstration.

Every test below is about one question: can a change reach a map's output WITHOUT moving its key?
The failure direction that matters is only ever "served a stale map"; regenerating unnecessarily is
free correctness. So each test that asserts a HIT also proves the hit was RIGHT, by regenerating
and comparing bytes - an assertion that the key did not move is worth nothing on its own.

Since feature 026 the gate RIDES the cache (`gate_obtain`), so the second half of this file pins
that contract: a verified hit skips generation only, checking is never cached, the bypass and any
incomplete entry force regeneration, and a miss stores the coverage data the next hit replays.
"""

from __future__ import annotations

import glob
import json
import os
import shutil
import sys
import textwrap
from pathlib import Path

import pytest

from l7r.diagram.pipeline import gencache

HERE = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))  # the skill root; this test lives in tests/pipeline/

_ENGINE = '''
CONSTANT = 3

def used(x):
    return x * CONSTANT

def unused(x):
    return x * 999

class Thing:
    def method(self, x):
        return used(x) + 1
'''

_GEN = '''
import sys
sys.path.insert(0, {here!r})
import {mod} as fakeengine
open({out!r}, "w").write(str(fakeengine.Thing().method(2)))
'''


def _fixture(tmp_path, engine=_ENGINE):
    """A miniature engine + gen, wired so gencache treats the temp dir as the engine.

    The module name is UNIQUE PER TEST on purpose. With a shared name, `sys.modules` served the
    first test's module to every later one - so the engine file a test edited was not the module
    its gen actually imported, and the tests quietly stopped testing anything (found 2026-08-08,
    when only the test that happened to run first behaved)."""
    mod = "fe_" + "".join(c if c.isalnum() else "_" for c in os.path.basename(str(tmp_path)))
    eng = tmp_path / f"{mod}.py"
    eng.write_text(textwrap.dedent(engine))
    out = tmp_path / "toy.json"
    gen = tmp_path / "toy.gen.py"
    gen.write_text(textwrap.dedent(_GEN).format(here=str(tmp_path), out=str(out), mod=mod))
    return eng, gen, out


def _with_engine(monkeypatch, tmp_path, eng):
    monkeypatch.setattr(gencache, "engine_files", lambda: [str(eng)])
    monkeypatch.setattr(gencache, "CACHE_DIR", str(tmp_path / "cache"))
    monkeypatch.setattr(gencache, "_renderer_version", lambda: "pinned")


def test_a_change_to_an_executed_function_invalidates(tmp_path, monkeypatch):
    eng, gen, _ = _fixture(tmp_path)
    _with_engine(monkeypatch, tmp_path, eng)
    deps = gencache.run_and_record(str(gen))
    before = gencache.compute_key(str(gen), deps)
    eng.write_text(eng.read_text().replace("return x * CONSTANT", "return x * CONSTANT + 1"))
    assert gencache.compute_key(str(gen), deps) != before, "a changed function the map RAN must move the key"


def test_a_change_outside_the_dep_set_is_a_hit_AND_the_hit_is_correct(tmp_path, monkeypatch):
    """The whole point of the fine-grained key - and the assertion that makes it honest is the
    second one: regenerate anyway and prove the bytes really are identical, so serving the cache
    was not merely permitted but RIGHT."""
    eng, gen, out = _fixture(tmp_path)
    _with_engine(monkeypatch, tmp_path, eng)
    deps = gencache.run_and_record(str(gen))
    before, fresh = gencache.compute_key(str(gen), deps), out.read_bytes()
    eng.write_text(eng.read_text().replace("return x * 999", "return x * 12345"))
    assert gencache.compute_key(str(gen), deps) == before, "a function the map never ran must NOT move the key"
    out.unlink()
    gencache.run_and_record(str(gen))
    assert out.read_bytes() == fresh, "the cache would have served this - so it must be what regeneration produces"


def test_a_module_level_change_invalidates_even_though_no_function_moved(tmp_path, monkeypatch):
    # the hole a per-function key would leave: a constant read by an executed function
    eng, gen, _ = _fixture(tmp_path)
    _with_engine(monkeypatch, tmp_path, eng)
    deps = gencache.run_and_record(str(gen))
    before = gencache.compute_key(str(gen), deps)
    eng.write_text(eng.read_text().replace("CONSTANT = 3", "CONSTANT = 4"))
    assert gencache.compute_key(str(gen), deps) != before


def test_a_renamed_dep_falls_back_to_the_whole_file_rather_than_being_ignored(tmp_path, monkeypatch):
    # an unresolvable dep must degrade CONSERVATIVELY - the direction of failure is everything
    eng, gen, _ = _fixture(tmp_path)
    _with_engine(monkeypatch, tmp_path, eng)
    deps = gencache.run_and_record(str(gen))
    eng.write_text(eng.read_text().replace("def used(", "def renamed("))
    key_after_rename = gencache.compute_key(str(gen), deps)
    eng.write_text(eng.read_text() + "\n# an edit nothing in the dep set can see\n")
    assert gencache.compute_key(str(gen), deps) != key_after_rename, "with a dep unresolved the file must hash WHOLE"


def test_the_gen_file_itself_is_part_of_the_key(tmp_path, monkeypatch):
    eng, gen, _ = _fixture(tmp_path)
    _with_engine(monkeypatch, tmp_path, eng)
    deps = gencache.run_and_record(str(gen))
    before = gencache.compute_key(str(gen), deps)
    gen.write_text(gen.read_text() + "\n# touched\n")
    assert gencache.compute_key(str(gen), deps) != before


def test_a_data_file_the_run_read_is_part_of_the_key(tmp_path, monkeypatch):
    """A gen that READS a data file has an input no source hash covers. `open` is spied during the
    recorded run so that input tracks itself, instead of someone having to remember it."""
    eng, gen, out = _fixture(tmp_path)
    data = tmp_path / "table.txt"
    data.write_text("7")
    gen.write_text(gen.read_text().replace("fakeengine.Thing().method(2)", f"fakeengine.Thing().method(int(open({str(data)!r}).read()))"))
    _with_engine(monkeypatch, tmp_path, eng)
    deps = gencache.run_and_record(str(gen))
    assert str(data) in deps["files"], "the spied open() must record a data input"
    before = gencache.compute_key(str(gen), deps)
    data.write_text("9")
    assert gencache.compute_key(str(gen), deps) != before


def test_round_trip_restores_byte_identical_outputs(tmp_path, monkeypatch):
    eng, gen, out = _fixture(tmp_path)
    _with_engine(monkeypatch, tmp_path, eng)
    deps = gencache.run_and_record(str(gen))
    fresh = out.read_bytes()
    gencache.store(str(gen), deps)
    out.unlink()
    assert gencache.load(str(gen)) is True
    assert out.read_bytes() == fresh
    # and a moved key is a MISS, not a silently-served stale entry
    stored = json.loads(Path(gencache.CACHE_DIR, "toy", "meta.json").read_text())
    eng.write_text(eng.read_text().replace("return x * CONSTANT", "return x * CONSTANT + 1"))
    assert gencache.compute_key(str(gen), stored["deps"]) != stored["key"], "a changed dep must not still match the stored key"


def test_no_recorded_deps_falls_back_to_the_coarse_whole_engine_key(tmp_path, monkeypatch):
    eng, gen, _ = _fixture(tmp_path)
    _with_engine(monkeypatch, tmp_path, eng)
    before = gencache.compute_key(str(gen), None)
    eng.write_text(eng.read_text().replace("return x * 999", "return x * 12345"))  # an UNUSED function
    assert gencache.compute_key(str(gen), None) != before, "with no dep set every engine byte counts"


def test_a_second_gen_in_the_same_process_records_its_own_full_dep_set(tmp_path, monkeypatch):
    """`sys.monitoring`'s DISABLE is permanent per code object, and that is what makes capture free
    - but without `restart_events()` the SECOND map traced in one process records only what the
    first did not already touch. A whole-pool sweep gave map #1 473 deps and nagahara 3, leaving it
    keyed on so little that almost any engine change would still have read as a hit.

    The unit tests could not catch this: each builds a FRESH engine module whose code objects were
    never disabled. It took an end-to-end "change one algorithm and see what regenerates" sweep, so
    the lesson gets pinned here where it is cheap to re-check.
    """
    eng, gen1, out1 = _fixture(tmp_path)
    mod = eng.stem
    out2 = tmp_path / "toy2.json"
    gen2 = tmp_path / "toy2.gen.py"
    gen2.write_text(textwrap.dedent(_GEN).format(here=str(tmp_path), out=str(out2), mod=mod))
    _with_engine(monkeypatch, tmp_path, eng)
    first = gencache.run_and_record(str(gen1))
    second = gencache.run_and_record(str(gen2))
    quals = {q for _, q in second["functions"]}
    assert "used" in quals and "Thing.method" in quals, f"the second gen recorded only {quals} - DISABLE leaked across runs"
    # every real FUNCTION the first run saw must be seen again; module and class BODIES
    # legitimately are not, because a second import of an already-imported module does not
    # re-execute them (and both are covered by the module-level hash anyway)
    bodies = {"<module>", "Thing"}
    assert {q for _, q in first["functions"]} - bodies <= quals, (first["functions"], sorted(quals))


def test_the_environment_is_part_of_the_key(tmp_path, monkeypatch):
    """A container rebuild changes the interpreter or the renderer, and both change what a map
    comes out as - the PIL layout-engine incident already rewrote 16 manifests with no code change
    behind it. All three environment inputs are asserted here rather than trusted, because none of
    them is exercised by an ordinary run: they only move when the box underneath you does."""
    eng, gen, _ = _fixture(tmp_path)
    _with_engine(monkeypatch, tmp_path, eng)
    deps = gencache.run_and_record(str(gen))
    before = gencache.compute_key(str(gen), deps)
    monkeypatch.setattr(gencache, "_renderer_version", lambda: "resvg 9.9.9")
    assert gencache.compute_key(str(gen), deps) != before, "a new renderer must invalidate - it draws the PNG"
    monkeypatch.setattr(gencache, "_renderer_version", lambda: "pinned")
    monkeypatch.setattr(sys, "version", "3.99.0 (fake)")
    assert gencache.compute_key(str(gen), deps) != before, "a new interpreter must invalidate"
    monkeypatch.undo()
    _with_engine(monkeypatch, tmp_path, eng)
    monkeypatch.setattr(gencache, "FORMAT_VERSION", "99")
    assert gencache.compute_key(str(gen), deps) != before, "bumping FORMAT_VERSION must invalidate every entry"


def test_an_entry_is_written_atomically_and_declared_valid_last(tmp_path, monkeypatch):
    """Concurrency safety, asserted as the two properties it rests on rather than by racing threads
    and hoping to hit the window.

    (1) Nothing is written in place - every artifact lands via a temp file and os.replace - so a
    reader mid-write sees the old bytes or the new bytes, never half a file. (2) meta.json, the
    only thing `load` trusts, is written LAST, so an entry is never declared valid before the
    artifacts it describes exist. Together those mean a concurrent reader either misses (no meta,
    or a stale key) or hits on a complete, self-consistent entry."""
    eng, gen, out = _fixture(tmp_path)
    _with_engine(monkeypatch, tmp_path, eng)
    deps = gencache.run_and_record(str(gen))

    order: list[str] = []
    real_replace = os.replace

    def spy_replace(src, dst, *a, **k):
        order.append(os.path.basename(str(dst)))
        return real_replace(src, dst, *a, **k)

    real_write = Path.write_bytes

    def no_direct_write(self, data):  # any write must go to a .tmp path, never to the live name
        assert ".tmp" in self.name, f"{self.name} was written in place - a reader could see it half-made"
        return real_write(self, data)

    monkeypatch.setattr(os, "replace", spy_replace)
    monkeypatch.setattr(Path, "write_bytes", no_direct_write)
    gencache.store(str(gen), deps)
    monkeypatch.undo()

    assert order, "store wrote nothing"
    assert order[-1] == "meta.json", f"meta.json must be published LAST, got order {order}"
    assert "toy.json" in order


@pytest.fixture
def clean_gatehit():
    """Remove THIS test's toy replay/recording files from the skill dir afterwards - they are
    near-empty (the toy engine is outside the coverage source list) but there is no reason to
    leave them for the session's combine. PID-scoped, because under xdist several of these tests
    run at once and all share the `toy` stem: an unscoped glob deletes a CONCURRENT test's
    in-flight driver file (found on this suite's first parallel run)."""
    pid = os.getpid()
    yield
    for f in glob.glob(os.path.join(HERE, f".coverage.gatehit-toy-{pid}*")) + glob.glob(os.path.join(HERE, f".gatecov-toy-{pid}*")):
        os.remove(f)


def test_a_dependency_change_invalidates_every_entry(tmp_path, monkeypatch):
    """Feature 026 R1: the key covers the dependency surface BELOW the Python-source horizon -
    installed distributions plus renderer font bytes - so a pip-level change (the PIL
    layout-engine incident class) invalidates automatically instead of relying on someone
    remembering to run a bypassed sweep."""
    eng, gen, _ = _fixture(tmp_path)
    _with_engine(monkeypatch, tmp_path, eng)
    deps = gencache.run_and_record(str(gen))
    gencache.store(str(gen), deps)
    assert gencache.load(str(gen)) is True
    monkeypatch.setattr(gencache, "_deps_state", lambda: "a different installed world")
    assert gencache.load(str(gen)) is False, "a dependency-state change must miss every entry"
    monkeypatch.undo()
    _with_engine(monkeypatch, tmp_path, eng)
    assert gencache.load(str(gen)) is True, "restoring the dependency state must restore the hit"


def test_engine_files_ignores_dotfiles(tmp_path, monkeypatch):
    """A hidden .py is never an engine module - it is a transient (an editor swap, a scratch
    driver). Pinned because the gate's own miss drivers used to land in the skill dir as
    `.gatecov-*-driver.py` and every concurrent key computation counted them as engine modules,
    so a parallel sweep poisoned every other map's key and NOTHING ever hit - found because
    feature 026's first warm-gate measurement came out slower than the cold one."""
    (tmp_path / "real.py").write_text("A = 1\n")
    (tmp_path / ".transient-driver.py").write_text("B = 2\n")
    monkeypatch.setattr(gencache, "HERE", str(tmp_path))
    assert [os.path.basename(f) for f in gencache.engine_files()] == ["real.py"]


def test_engine_files_prunes_the_tests_tree(tmp_path, monkeypatch):
    """The tests/ tree is not an engine input, and its files do NOT start with `test_`.

    Before the 2026-08-16 reorg every test file sat at the skill root named `test_*.py`, so the
    `test_`-prefix filter covered them all. Under tests/ the helpers (`_builders.py`, `__init__.py`)
    match no filter, and counting them as engine modules would invalidate every map in the pool on
    any edit to a test helper - the same silent-never-hits failure the dotfile filter exists for."""
    (tmp_path / "real.py").write_text("A = 1\n")
    (tmp_path / "tests" / "pipeline").mkdir(parents=True)
    (tmp_path / "tests" / "__init__.py").write_text("B = 2\n")
    (tmp_path / "tests" / "pipeline" / "_builders.py").write_text("C = 3\n")
    monkeypatch.setattr(gencache, "HERE", str(tmp_path))
    assert [os.path.basename(f) for f in gencache.engine_files()] == ["real.py"]


def test_the_deps_state_is_stable_within_a_process():
    first = gencache._deps_state()
    assert first == gencache._deps_state(), "the deps input must not wobble between key computations"
    assert first and not first.startswith("unresolvable-")


def test_an_entry_never_keeps_coverage_it_did_not_just_record(tmp_path, monkeypatch):
    """THE FLICKERING FLOOR (feature 149; feature 147 parked two `hinterland.py` lines over this).

    `store` publishes a FRESH key at the end of every call. A caller that regenerates WITHOUT measuring
    coverage - `make maps`, the iteration regen path, anything but the gate's miss path - used to leave the
    old `coverage.data` beside that new key, and `gate_obtain` replayed it on the next hit. Coverage data is
    a set of LINE NUMBERS, so a replay after the source moved marks the wrong lines: the hamlet-path floor
    then gave 100% on one full run and 99.93% on the next, from the same code, depending on which entries had
    last been written by a path that records coverage and which by a path that does not.

    `_coverage_is_current` cannot catch it - it asks whether the measured files still EXIST, and here they
    all do; they have simply moved. So the rule is the blunt one: no coverage unless it was just recorded."""
    eng, gen, out = _fixture(tmp_path)
    _with_engine(monkeypatch, tmp_path, eng)
    deps = gencache.run_and_record(str(gen))
    cov = tmp_path / "some.coverage"
    cov.write_bytes(b"not really coverage, but this test is about the FILE's lifetime")
    gencache.store(str(gen), deps, coverage_data=str(cov))
    stored = Path(gencache.CACHE_DIR, "toy", gencache.COVERAGE_NAME)
    assert stored.is_file(), "the gate's miss path stores the coverage the next hit would replay"

    stamp = Path(gencache.CACHE_DIR, "toy", gencache.COVERAGE_KEY_NAME)
    assert stamp.read_text().strip() == json.loads(Path(gencache.CACHE_DIR, "toy", "meta.json").read_text())["key"]
    assert gencache._coverage_stamp_matches(str(gen)), "freshly recorded coverage is replayable"

    # ...and a re-store WITHOUT coverage drops it, rather than pairing it with the new key
    gencache.store(str(gen), deps)
    assert not stored.exists(), "stale coverage must not survive beside a freshly written key"
    assert not stamp.exists(), "and the stamp goes with it"

    # AN ENTRY POISONED BEFORE THIS LANDED heals itself: coverage present, no stamp, so it is not replayed.
    # Every clone in existence held some of these, and nothing in the entry said so.
    gencache.store(str(gen), deps, coverage_data=str(cov))
    stamp.unlink()
    assert not gencache._coverage_stamp_matches(str(gen)), "an unstamped entry is regenerated, never replayed"


_REAL_ENGINE_RELS = [gencache._rel(p) for p in gencache.engine_files()]


# ---- FEATURE 167: A CACHE ONE CLONE BUILDS IS USABLE BY ANOTHER --------------------------------
#
# WHY (GM 2026-08-30). A fresh clone paid about two minutes re-rolling maps a sibling had already
# rolled from identical source - 30 s for the reference settlement and 122 s for the map-rolling gate
# tests, against 1 s and 21 s warm. The cause was that a dependency was recorded as an ABSOLUTE path
# and `key_for` looked it up while walking this tree's own files, so across roots every per-function
# part silently dropped out of the key and a copied cache could never match.
#
# The direction of failure is what these tests really guard. A key that wrongly MATCHES would let the
# gate serve a roll produced by different code - the only failure here that could pass a map the suite
# never checked. So each test below pins a MISS as firmly as it pins a hit.


def test_a_dependency_inside_the_skill_is_recorded_relative_and_outside_it_absolute():
    inside = os.path.join(gencache.HERE, "l7r/diagram/settlement/houses.py")
    assert gencache._rel(inside) == "l7r/diagram/settlement/houses.py"
    assert gencache._abs(gencache._rel(inside)) == inside
    # a font, an installed package, the GM's notes mount: no meaningful root-relative form, and the
    # same file for every clone on this machine, so it stays absolute
    for outside in ("/usr/share/fonts/x.ttf", "/host-l7r-repo/setting/l7r.md", "/usr/lib/python3/x.py"):
        assert gencache._rel(outside) == outside
        assert gencache._abs(outside) == outside


def test_the_key_survives_a_change_of_ROOT_but_not_a_change_of_SOURCE(monkeypatch, tmp_path):
    """The whole feature, in one assertion pair: same sources under a different root key the same;
    a changed source keys differently."""
    real = os.path.join(gencache.HERE, "l7r/diagram/settlement/houses.py")
    deps = {"functions": [[gencache._rel(real), "place_houses"]], "files": []}
    here_key = gencache.key_for(b"subject", deps)

    # a second "clone": the same engine sources, reachable at a different absolute path
    other = tmp_path / "elsewhere"
    shutil.copytree(os.path.join(gencache.HERE, "l7r"), other / "l7r")
    monkeypatch.setattr(gencache, "HERE", str(other))
    monkeypatch.setattr(gencache, "engine_files", lambda: [str(other / rel) for rel in _REAL_ENGINE_RELS])
    assert gencache.key_for(b"subject", deps) == here_key, "the same sources under another root must key the same"

    # ...and the safe direction: change one recorded function's source and the key must move
    target = other / "l7r/diagram/settlement/houses.py"
    target.write_text(target.read_text() + "\n\ndef place_houses_extra() -> None:\n    pass\n", encoding="utf-8")
    assert gencache.key_for(b"subject", deps) != here_key, "a changed engine source must NOT key the same"


def test_an_old_absolute_format_entry_cannot_be_re_keyed_under_the_new_rule():
    """Format 1 recorded absolute paths. Re-reading one under the new lookup would silently drop its
    per-function parts, which is the shape that could serve a stale roll - so it must key differently,
    and FORMAT_VERSION is bumped so it is discarded outright."""
    real = os.path.join(gencache.HERE, "l7r/diagram/settlement/houses.py")
    relative = {"functions": [[gencache._rel(real), "place_houses"]], "files": []}
    absolute = {"functions": [[real, "place_houses"]], "files": []}
    assert gencache.key_for(b"s", absolute) != gencache.key_for(b"s", relative)
    assert gencache.FORMAT_VERSION != "1"


def test_a_data_file_is_hashed_from_THIS_tree_not_from_the_recorded_path(monkeypatch, tmp_path):
    """The one way this change could have turned a safe miss into a wrong hit: hashing the recorded
    path would read the PRODUCING clone's copy of a data file rather than this clone's."""
    data = tmp_path / "root" / "sub" / "d.json"
    data.parent.mkdir(parents=True)
    data.write_text("one", encoding="utf-8")
    monkeypatch.setattr(gencache, "HERE", str(tmp_path / "root"))
    monkeypatch.setattr(gencache, "engine_files", lambda: [])
    deps = {"functions": [], "files": ["sub/d.json"]}
    before = gencache.key_for(b"s", deps)
    data.write_text("two", encoding="utf-8")
    assert gencache.key_for(b"s", deps) != before, "the key must follow THIS tree's data file"
