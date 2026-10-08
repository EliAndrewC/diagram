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
    (`pipeline/poolmaps.py`) and its gens are never run.

    NO ROLL OF ITS OWN (feature 215, FR-002): this used to regenerate the map to have something to store; the
    pool sweep has already produced or served exactly that map, and its entry's dependency record is on disk.
    The round trip is the assertion, and it runs over the same artifacts.

    ...AND NEVER ON THE POOL'S OWN FILES (2026-09-13, found by feature 245's gate). This used to delete the REAL
    manifest and restore it from the scratch cache a moment later, and the pool is shared by every xdist worker:
    a gate fixture in another worker was copying that same manifest through `gencache.load` at that moment and
    died in `copy2`'s `utime` with FileNotFoundError on it - one worker's `tests/gate/test_map_vocabulary.py`
    fixture, on the one run where the cache was cold enough for the timing to line up. So the round trip runs on
    a COPY of the map's directory under `tmp_path`: the same gen bytes (the key reads them), the same artifacts,
    a gen path the scratch cache alone knows, and nothing of the pool's is ever removed or rewritten. The
    `.svg` and `.png` are GITIGNORED renders a fresh clone may not have, so only what is on disk is copied.

    THE DELETE-AND-RESTORE WAS NOT THE ONLY WINDOW: `load` itself rewrites every output it restores, so even
    a restore that never removed the manifest would have raced the readers; a copy is the only form with none."""
    gen = os.path.join(HERE, "pool", "hamlets", "inashiro", "inashiro.gen.py")
    base = gen[: -len(".gen.py")]
    manifest = base + ".json"
    # THE SWEEP'S ENTRY, and its record: obtained under the run's per-gen lock (served warm, rolled cold - once)
    served = _pool.obtain(gen)
    assert served == manifest
    deps = json.loads((Path(gencache._entry_dir(gen)) / "meta.json").read_text(encoding="utf-8"))["deps"]
    assert any("/settlement/" in f for f, _ in deps["functions"]), "a real gen's record names engine deps"
    fresh = Path(manifest).read_bytes()
    # THE MAP UNDER TEST IS A COPY, and the cache under test is a scratch one (feature 214): the pool is only read
    copy_dir = tmp_path / "pool" / "hamlets" / "inashiro"
    copy_dir.mkdir(parents=True)
    for p in (gen, manifest, base + ".svg", base + ".png"):
        if os.path.isfile(p):
            (copy_dir / os.path.basename(p)).write_bytes(Path(p).read_bytes())
    gen_copy = str(copy_dir / "inashiro.gen.py")
    manifest_copy = copy_dir / "inashiro.json"
    monkeypatch.setattr(gencache, "CACHE_DIR", str(tmp_path / "gencache"))
    gencache.store(gen_copy, deps)
    manifest_copy.unlink()
    assert gencache.load(gen_copy) is True, "an unchanged pool map must hit"
    assert manifest_copy.read_bytes() == fresh
    assert Path(manifest).read_bytes() == fresh, "the pool's own manifest was never touched"
