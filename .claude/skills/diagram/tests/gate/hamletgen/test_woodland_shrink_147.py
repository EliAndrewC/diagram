"""THE WOODLAND SHRINK LADDER, WALKED ON PURPOSE - a COVERAGE CARRIER (features 147 and 149).

`hinterland.open_ground_patches` steps a coppice DOWN in size when the seat it picked will not hold a
full-sized parcel inside the crop window - *"a smaller coppice on the sheet beats a larger one the crop cuts
off. Only when even the floor-sized parcel fails is the seat genuinely unusable."*

WHY IT IS A CARRIER RATHER THAN AN ASSERTING TEST, stated plainly because a weak assertion usually means a
weak test. The ladder leaves nothing observable behind: when a shrunk rung fits, the parcel can still be
dropped by a later guard, so the caller cannot tell from the returned parcels whether the rung ran. What the
rung DOES leave is executed lines, and the hamlet-path floor is the thing that fails when they stop being
executed. That is the same bargain `tests/full/test_coverage_carriers.py` already makes, and it is the
honest description of this test: the floor is its assertion.

WHY IT NEEDS A REAL PLANNED SITE. The scan wants crop boxes, keep-outs and a seat lattice; every hand-built
settlement it was offered produced no candidate seat at all, so there is no cheap fixture. One build of one
cohort member is the smallest honest way in, and asking for oversized parcels is what forces the ladder.

WHICH MEMBER WALKS IT MOVES WITH THE ENGINE, and that is a maintenance cost worth naming: member 1 walked it
before feature 134's work landed and member 0 does after. If this test ever stops carrying the rung, the
floor goes red on `hinterland.py` and the fix is to re-aim it - `make cov-file FILE=<this file> MOD=x` names
the answer in seconds. Do NOT park the lines again; feature 149 removed that park after fixing the cause of
the floor's flicker, which was stale cached coverage rather than anything here.
"""

from __future__ import annotations

import pytest

from l7r.diagram import hamletgen as hg
from l7r.diagram.hamletgen.hinterland import open_ground_patches


@pytest.mark.rolls_map
def test_the_woodland_shrink_ladder_is_walked_on_a_real_site() -> None:
    spec = hg.driver.cohort_specs(8, first_seed=41)[0]
    plan = hg.plan_site(spec)
    s = hg.build(plan)
    for asked in (250.0, 380.0, 520.0):  # oversized for this map's open ground, so every rung is tried
        parcels = open_ground_patches(s, plan, 3, size=asked)
        assert isinstance(parcels, list)
        for poly in parcels:
            w = max(p[0] for p in poly) - min(p[0] for p in poly)
            h = max(p[1] for p in poly) - min(p[1] for p in poly)
            assert max(w, h) <= asked, "a parcel that came back is the shrunk one, never larger than asked"
