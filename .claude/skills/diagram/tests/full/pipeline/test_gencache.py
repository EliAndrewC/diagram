"""THE FULL TREE (feature 135, GM 2026-08-27): the one cache test that regenerates a REAL scripted hamlet (58 s).
The eight toy-engine tests in tests/gate/pipeline/ prove the mechanics at every gate; this one proves them on
Inashiro at `make done FULL=1` and on AWS."""

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

from l7r.diagram.pipeline import gencache
from tests.pipeline.test_gencache import HERE


@pytest.mark.rolls_map  # regenerates a REAL scripted hamlet: 58 s, the suite's single largest test
def test_the_real_pool_round_trips_through_the_cache():
    """The end-to-end proof on a REAL map: regenerate, cache, wipe, restore, and demand the bytes
    match. Uses the cheapest SCRIPTED hamlet - the hand-authored pool is FROZEN
    (`pipeline/poolmaps.py`) and its gens are never run - and restores the artifacts BYTE-FOR-BYTE
    afterwards rather than by re-running the gen: the engine is free to drift from what a live map
    was generated with, so a final re-run could leave the pool dirty.

    SNAPSHOT ONLY WHAT IS ON DISK. The `.json` manifest is tracked, but the `.svg` and `.png`
    renders are GITIGNORED derived files - render-sync rebuilds main's from main's own tip - so a
    freshly created clone has no render at all. Reading the `.svg` unconditionally made this test
    die with FileNotFoundError in any clone where nothing had regenerated a map yet, which is
    every new clone's first `make done`: a red gate whose cause has nothing to do with the change
    under test. The cache itself never had this problem - `store` and `load` both skip an output
    that is absent - so the dependency was this test's own bookkeeping, not the behavior it
    exercises. (Confirmed 2026-08-16 by running it in a fresh clone at the pre-reorganization
    commit: same failure, so it long predates the tests/ move.)"""
    gen = os.path.join(HERE, "pool", "hamlets", "inashiro", "inashiro.gen.py")  # feature 161 moved every map into a per-map folder; this literal kept the flat path and stopped matching SILENTLY (found by feature 166's FULL run, fixed on sight per constitution XIV)
    base = gen[: -len(".gen.py")]
    manifest = base + ".json"
    # nothing here creates a render (the gen runs under DIAGRAM_SKIP_RENDER), so restoring exactly
    # what was standing beforehand leaves the pool as it was found, render present or not
    committed = {p: Path(p).read_bytes() for p in (manifest, base + ".svg", base + ".png") if os.path.isfile(p)}
    env = {**os.environ, "DIAGRAM_SKIP_RENDER": "1"}
    try:
        subprocess.run([sys.executable, gen], check=True, capture_output=True, env=env, cwd=HERE)
        fresh = Path(manifest).read_bytes()
        deps = json.loads(json.dumps(gencache.run_and_record(gen)))  # round-trips through JSON like a stored entry
        assert any("/settlement/" in f for f, _ in deps["functions"]), "a real gen must record engine deps"
        gencache.store(gen, deps)
        os.remove(manifest)
        assert gencache.load(gen) is True, "an unchanged pool map must hit"
        assert Path(manifest).read_bytes() == fresh
    finally:
        shutil.rmtree(os.path.join(gencache.CACHE_DIR, "inashiro"), ignore_errors=True)
        for p, data in committed.items():
            Path(p).write_bytes(data)
