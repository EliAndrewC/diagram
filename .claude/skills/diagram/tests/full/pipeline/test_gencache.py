"""THE FULL TREE (feature 135, GM 2026-08-27): the one cache test that regenerates a REAL scripted hamlet (58 s).
The eight toy-engine tests in tests/gate/pipeline/ prove the mechanics at every gate; this one proves them on
Inashiro at `make done FULL=1` and on AWS."""

import json
import os
from pathlib import Path

import pytest

from l7r.diagram.pipeline import gencache
from tests.gate import _pool
from tests.pipeline.test_gencache import HERE


@pytest.mark.rolls_map  # reads the pool's Inashiro through the gen cache (the sweep's own entry - no roll of its own since feature 215)
def test_the_real_pool_round_trips_through_the_cache(tmp_path, monkeypatch):
    """The end-to-end proof on a REAL map: the artifacts the sweep produced, stored into a scratch cache, wiped,
    restored, and the bytes must match. Uses the cheapest SCRIPTED hamlet - the hand-authored pool is FROZEN
    (`pipeline/poolmaps.py`) and its gens are never run - and restores the artifacts BYTE-FOR-BYTE afterwards.

    NO ROLL OF ITS OWN (feature 215, FR-002): this used to regenerate the map to have something to store; the
    pool sweep has already produced or served exactly that map, and its entry's dependency record is on disk.
    The round trip is the assertion, and it runs over the same artifacts.

    SNAPSHOT ONLY WHAT IS ON DISK. The `.json` manifest is tracked, but the `.svg` and `.png` renders are
    GITIGNORED derived files - render-sync rebuilds main's from main's own tip - so a freshly created clone has
    no render at all; reading the `.svg` unconditionally made this test die with FileNotFoundError in any
    clone where nothing had regenerated a map yet (confirmed 2026-08-16)."""
    gen = os.path.join(HERE, "pool", "hamlets", "inashiro", "inashiro.gen.py")
    base = gen[: -len(".gen.py")]
    manifest = base + ".json"
    committed = {p: Path(p).read_bytes() for p in (manifest, base + ".svg", base + ".png") if os.path.isfile(p)}
    # THE SWEEP'S ENTRY, and its record: obtained under the run's per-gen lock (served warm, rolled cold - once)
    served = _pool.obtain(gen)
    assert served == manifest
    deps = json.loads((Path(gencache._entry_dir(gen)) / "meta.json").read_text(encoding="utf-8"))["deps"]
    assert any("/settlement/" in f for f, _ in deps["functions"]), "a real gen's record names engine deps"
    fresh = Path(manifest).read_bytes()
    # THE CACHE UNDER TEST IS A SCRATCH ONE (feature 214): the real entry is never touched
    monkeypatch.setattr(gencache, "CACHE_DIR", str(tmp_path / "gencache"))
    try:
        gencache.store(gen, deps)
        os.remove(manifest)
        assert gencache.load(gen) is True, "an unchanged pool map must hit"
        assert Path(manifest).read_bytes() == fresh
    finally:
        for p, data in committed.items():
            Path(p).write_bytes(data)
