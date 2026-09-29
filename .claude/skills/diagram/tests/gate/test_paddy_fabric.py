"""The paddy fabric a rolled comb fan must produce (feature 166): what is left of it after feature 287.

Feature 166 carried eight rules here that the retired battery re-measured on every finished map. Feature 287 moved the
ring rules into the seam pass - `waterfields/seams/close.py:hold_ring_rules` asks `waterfields/ring_rules.py`'s one
predicate per rule and repairs or leaves bare what fails (`tests/waterfields/test_ring_guarantees.py`, each on the
violating ring) - and the floor and its overhang into the comb (`fields/comb.py:draw_comb_field`,
`waterfields/comb.py:_comb_floor_and_winding`), and retired the finished-map tests of them
(specs/287-placer-guarantees/research.md R8).

KEPT, because no placer guarantees them yet:
- `comb_supply_commands_both_flanks`: `hamletgen/water/fit.py:fit_field` RANKS aspects by it and keeps the least-bad
  fan when none is legal - no refusal, and no placer test with the violating case.
- the needle on a POLDER parcel: `waterfields/polder.py:unpoint_parcels` judges the unrounded ring, and the record is
  rounded afterwards (`fields/comb.py`), so the ring on the map is not the ring the placer judged. A comb fan's rings are
  judged as recorded, so only the fields without a fork (the polder's parcels) are read below.
"""

from __future__ import annotations

import glob
import math
import os

import pytest

from l7r.diagram.waterfields.ring_rules import NEEDLE_DEG, needle
from tests import rolls
from tests.gate import _pool

SPEC = rolls.REFERENCE  # the pool's brief (feature 215)


@pytest.fixture(scope="module")
def fan():
    """The comb fan itself - a paddy field carrying a fork, an outline, rings and a design cell.

    A map with no such field would make the test below vacuously true, so finding one is the first
    assertion rather than a silent `continue`."""
    _plan, M = _pool.rolled_map(SPEC)
    fans = [f for f in (M.get("fields") or []) if f.get("kind") == "paddy" and f.get("fork") and f.get("plot_rings")]
    assert fans, "the reference roll produced no comb paddy fan, so the rule in this module would pass on nothing"
    return M, fans[0]


def test_the_supply_commands_both_flanks_of_the_fan(fan) -> None:
    """`comb_supply_commands_both_flanks`. Water enters at the fork and must be able to reach BOTH sides
    of it; a fan whose delivery ditches all run to one side has half its plots painted as irrigated with
    nothing to irrigate them. Flank membership is the SIGN of a vertex's cross-slope offset from the fork -
    an aggregate bearing question, which is legitimate on vertices because every quantity here is an
    EXTENT, not a gap verdict."""
    M, f = fan
    ftpx = float(M["meta"].get("ftpx") or 1.0)
    fork = f.get("fork")
    down = float(f.get("down_deg", M["meta"].get("down_deg")))
    cross = (-math.sin(math.radians(down)), math.cos(math.radians(down)))

    def offset(v):
        return (v[0] - fork[0]) * cross[0] + (v[1] - fork[1]) * cross[1]

    extent = [0.0, 0.0]
    for ring in f.get("plot_rings") or []:
        for v in ring:
            s = offset(v)
            extent[0 if s >= 0 else 1] = max(extent[0 if s >= 0 else 1], abs(s))
    reach = [0.0, 0.0]
    for d in M.get("field_ditches") or []:
        if d.get("field") != f.get("name") or d.get("role") not in ("main", "branch"):
            continue
        for v in d["poly"]:
            s = offset(v)
            reach[0 if s >= 0 else 1] = max(reach[0 if s >= 0 else 1], abs(s))
    assert min(extent) > 150.0 / ftpx, f"the fan is one-sided ({extent}), so this rule would judge only one flank"
    for i in (0, 1):
        floor = max(80.0 / ftpx, 0.3 * extent[i])
        assert reach[i] >= floor, f"the {'+' if i == 0 else '-'}cross flank has {round(extent[i] * ftpx)} ft of plots and only {round(reach[i] * ftpx)} ft of supply"


_POOL_HAMLET_GENS = sorted(glob.glob(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "pool", "hamlets", "*", "*.gen.py")))


@pytest.mark.parametrize("gen", _POOL_HAMLET_GENS, ids=os.path.basename)
def test_no_shipped_polder_parcel_tapers_to_a_point(gen: str) -> None:
    """`paddy_plots_are_workable_basins` on every shipped hamlet's POLDER parcels (the fields with no fork), as recorded -
    the comb fans' half retired with feature 287 (the module docstring says why this half stays). Over every shipped
    manifest since the settlement-review of feature 230 pass 10. The fixture above reads the reference and Kuwabata, so a needle on
    Kashikawa - rings retracing their own edge at 0.9 degrees - reached a review before any test. Reading a manifest
    costs no roll when the cache is warm - and it is read THROUGH `_pool.obtain`, under the run's per-gen lock, like every
    other reader of a shipped generator: read straight off disk, it once caught the gate's own roll of the reference mid-write
    and parsed an empty file."""
    import json

    with open(_pool.obtain(gen), encoding="utf-8") as fh:
        M = json.load(fh)
    fields = [f for f in M.get("fields") or [] if f.get("plot_rings") and not f.get("fork")]
    if not fields:
        pytest.skip("no polder parcel on this map")
    needles = [(f.get("name"), i) for f in fields for i, r in enumerate(f["plot_rings"]) if len(r) >= 3 and needle(r)]
    assert not needles, f"{len(needles)} basin(s) taper below {NEEDLE_DEG} deg: {needles[:5]}"
