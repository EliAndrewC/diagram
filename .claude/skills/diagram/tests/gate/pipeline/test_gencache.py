"""gate tests split out of `tests.pipeline.test_gencache` (feature 133 T29, GM 2026-08-26): `make quick` collects
`tests/` minus the tier, gate and tooling trees, so these are neither imported nor collected while the scope is
locked to another tier; the gate collects everything. Helpers stay in the source module and are imported."""

from __future__ import annotations

import glob
import json
import os
import subprocess
from pathlib import Path

import pytest

from l7r.diagram.pipeline import gencache
from tests.pipeline.test_gencache import (
    HERE,
    _fixture,
    _with_engine,  # fixtures the moved tests take as parameters
)


@pytest.mark.rolls_map
def test_gate_miss_scratch_files_stay_out_of_the_engine_tree(tmp_path, monkeypatch, clean_gatehit):
    """The other layer of the same defense: the miss subprocess's driver/record/raw-coverage files
    must live OUTSIDE the skill dir, where no key computation can ever see them."""
    eng, gen, _ = _fixture(tmp_path)
    _with_engine(monkeypatch, tmp_path, eng)
    monkeypatch.delenv(gencache.GATE_BYPASS, raising=False)
    seen: list[str] = []
    real_run = subprocess.run

    def spy_run(cmd, *a, **k):
        if isinstance(cmd, list) and cmd[-1].endswith("driver.py"):
            seen.append(cmd[-1])
        return real_run(cmd, *a, **k)

    monkeypatch.setattr(gencache.subprocess, "run", spy_run)
    _, how, _ = gencache.gate_obtain(str(gen))
    assert how == "REGENERATED" and seen, "the miss path must have spawned a driver"
    assert not seen[0].startswith(gencache.HERE + os.sep), f"scratch driver inside the engine tree: {seen[0]}"


@pytest.mark.tooling
@pytest.mark.rolls_map
def test_the_gate_reuses_a_verified_hit(tmp_path, monkeypatch, clean_gatehit):
    """026 guarantee 1: on a verified hit NO generation executes in any process - and a hit is
    only verified when the entry carries the coverage data a previous gate miss stored."""
    eng, gen, out = _fixture(tmp_path)
    _with_engine(monkeypatch, tmp_path, eng)
    monkeypatch.delenv(gencache.GATE_BYPASS, raising=False)
    manifest, how, cpu = gencache.gate_obtain(str(gen))
    assert (manifest, how) == (str(out), "REGENERATED") and cpu is not None
    entry = Path(gencache.CACHE_DIR, "toy")
    assert (entry / gencache.COVERAGE_NAME).is_file()
    assert json.loads((entry / "meta.json").read_text())["gen_cpu_s"] >= 0

    def boom(*a: object, **k: object) -> object:
        raise AssertionError("a verified hit must not spawn a generation subprocess")

    monkeypatch.setattr(gencache.subprocess, "run", boom)
    assert gencache.gate_obtain(str(gen)) == (str(out), "HIT", None)


@pytest.mark.tooling
@pytest.mark.rolls_map
def test_a_hit_still_runs_current_checks(tmp_path, monkeypatch, clean_gatehit):
    """026 guarantee 5: checking is never cached - the gate's caller judges whatever manifest the
    cache serves with the CURRENT battery, so a bad cached manifest cannot ride a hit through. The
    key hashes INPUTS, not outputs, so a tampered entry artifact is exactly the case where only
    the live check run stands between the cache and a green gate."""
    eng, gen, _ = _fixture(tmp_path)
    _with_engine(monkeypatch, tmp_path, eng)
    monkeypatch.delenv(gencache.GATE_BYPASS, raising=False)
    gencache.gate_obtain(str(gen))
    Path(gencache.CACHE_DIR, "toy", "toy.json").write_text('{"meta": {}}')
    manifest, how, _ = gencache.gate_obtain(str(gen))
    assert how == "HIT" and Path(manifest).read_text() == '{"meta": {}}'
    from l7r.diagram import check_village

    try:
        rc = check_village.main(manifest)
    except Exception:
        rc = 1
    assert rc != 0, "the current check battery must judge a served manifest - a hit is not a verdict"


@pytest.mark.tooling
@pytest.mark.rolls_map
def test_an_entry_without_coverage_data_is_a_gate_miss(tmp_path, monkeypatch, clean_gatehit):
    """026 guarantee 4: an iteration-path entry (regen.py stores no coverage) cannot satisfy the
    gate - the coverage floors would starve. The gate refreshes it instead, adding the coverage
    data, so the SECOND gate run hits."""
    eng, gen, _ = _fixture(tmp_path)
    _with_engine(monkeypatch, tmp_path, eng)
    monkeypatch.delenv(gencache.GATE_BYPASS, raising=False)
    deps = gencache.run_and_record(str(gen))
    gencache.store(str(gen), deps)
    assert gencache.load(str(gen)) is True, "the ITERATION path would hit this entry..."
    _, how, _ = gencache.gate_obtain(str(gen))
    assert how == "REGENERATED", "...but the GATE must not - it has no coverage to replay"
    assert Path(gencache.CACHE_DIR, "toy", gencache.COVERAGE_NAME).is_file()
    _, how2, _ = gencache.gate_obtain(str(gen))
    assert how2 == "HIT"


@pytest.mark.tooling
@pytest.mark.rolls_map
def test_gate_miss_stores_coverage_the_next_hit_replays(tmp_path, monkeypatch, clean_gatehit):
    """026 guarantees 1+2 composed: the coverage a miss stores is byte-for-byte the file a later
    hit drops into the run's combine."""
    eng, gen, _ = _fixture(tmp_path)
    _with_engine(monkeypatch, tmp_path, eng)
    monkeypatch.delenv(gencache.GATE_BYPASS, raising=False)
    gencache.gate_obtain(str(gen))
    stored = Path(gencache.CACHE_DIR, "toy", gencache.COVERAGE_NAME).read_bytes()
    mine = os.path.join(HERE, f".coverage.gatehit-toy-{os.getpid()}*")  # pid-scoped: xdist runs siblings concurrently
    before = set(glob.glob(mine))
    _, how, _ = gencache.gate_obtain(str(gen))
    new = set(glob.glob(mine)) - before
    assert how == "HIT" and len(new) == 1
    assert Path(new.pop()).read_bytes() == stored


@pytest.mark.tooling
@pytest.mark.rolls_map
def test_a_hit_is_refused_when_its_stored_coverage_names_a_file_that_is_gone(tmp_path, monkeypatch, clean_gatehit):
    """A stored coverage file that measures a DELETED module makes the entry unusable, so it is a
    miss - the cache's own "any doubt at all regenerates" rule, applied to the coverage half.

    THE INCIDENT (2026-08-17). A peer session's package split deleted `settlement/civic_grounds.py`;
    every cache entry built before that sync went on replaying coverage that measured it, the
    Makefile's `coverage combine --append` swept the replay in, and `coverage report` died with
    `No source for code` - which the Makefile reports as the settlement RATCHET FLOOR being breached.
    So a routine refactor in someone else's module surfaced, in a clone that had merely synced, as a
    coverage regression in code this session never touched. The key cannot see it: generation is
    perfectly valid, and the map it produces is correct. Only the replayed coverage is stale.

    Held here rather than in a doc because the recovery (`GATE_NO_CACHE=1 make done`) is exactly the
    kind of tip nobody recalls at the moment the gate goes red at a file they have never opened."""
    eng, gen, out = _fixture(tmp_path)
    _with_engine(monkeypatch, tmp_path, eng)
    monkeypatch.delenv(gencache.GATE_BYPASS, raising=False)
    assert gencache.gate_obtain(str(gen))[1] == "REGENERATED"
    assert gencache.gate_obtain(str(gen))[1] == "HIT", "baseline: this entry hits before we spoil it"

    from coverage import CoverageData  # noqa: PLC0415 - only this test needs the writer

    stored = Path(gencache.CACHE_DIR, "toy", gencache.COVERAGE_NAME)
    data = CoverageData(basename=str(stored))
    data.read()
    data.add_lines({str(tmp_path / "vanished_by_a_peer_session.py"): [1]})
    data.write()

    _, how, _ = gencache.gate_obtain(str(gen))
    assert how == "REGENERATED", "an entry whose coverage measures a vanished file must regenerate, not replay"


@pytest.mark.tooling
@pytest.mark.rolls_map
def test_gate_bypass_forces_regeneration(tmp_path, monkeypatch, clean_gatehit):
    """026 guarantee 3 - and the test OWNS the environment (the DIAGRAM_ALLOW_SLOW_GENS lesson,
    2026-08-03): delenv first, so an inherited bypass cannot silence the half that proves hits
    happen at all."""
    eng, gen, _ = _fixture(tmp_path)
    _with_engine(monkeypatch, tmp_path, eng)
    monkeypatch.delenv(gencache.GATE_BYPASS, raising=False)
    _, how, _ = gencache.gate_obtain(str(gen))
    assert how == "REGENERATED"
    _, how, _ = gencache.gate_obtain(str(gen))
    assert how == "HIT", "baseline: with the bypass unset, hits must happen"
    monkeypatch.setenv(gencache.GATE_BYPASS, "1")
    _, how, cpu = gencache.gate_obtain(str(gen))
    assert (how, cpu is not None) == ("REGENERATED", True), "the bypass must force regeneration"
