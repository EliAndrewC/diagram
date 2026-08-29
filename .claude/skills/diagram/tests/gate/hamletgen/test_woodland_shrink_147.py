"""THE WOODLAND SHRINK LADDER, COVERED ON PURPOSE RATHER THAN BY LUCK (feature 147).

`hinterland.open_ground_patches` steps a coppice DOWN in size when the seat it picked will not hold a
full-sized parcel inside the crop window - *"a smaller coppice on the sheet beats a larger one the crop cuts
off. Only when even the floor-sized parcel fails is the seat genuinely unusable."*

WHY THIS TEST EXISTS (measured 2026-08-29). Those two lines were covered only as a side effect of whichever
pool maps and cohort seeds a given full run happened to regenerate, and that coverage turned out to be
UNSTABLE: the same code gave a 100% floor in one run and 99.93% in another, flipping on changes elsewhere in
the suite that have nothing to do with hinterland. A coverage floor that flips is worse than a slow one -
it teaches a session to re-run the gate until it passes. So the rung is now walked deliberately, in-process,
by one test that cannot stop reaching it without the behavior actually changing.

IT NEEDS A REAL PLANNED SITE, which is the thing that made this hard. The scan wants crop boxes, keep-outs
and a seat lattice; every hand-built settlement it was offered produced no candidate seat at all, so there
is no cheap fixture for it. One build of one cohort member is the smallest honest way in, and asking for an
oversized parcel is what forces the ladder rather than the ordinary path.
"""

from __future__ import annotations

import pytest

from l7r.diagram import hamletgen as hg
from l7r.diagram.hamletgen.hinterland import open_ground_patches


@pytest.mark.rolls_map
def test_an_oversized_coppice_is_shrunk_onto_the_sheet_rather_than_dropped() -> None:
    spec = hg.driver.cohort_specs(8, first_seed=41)[0]
    plan = hg.plan_site(spec)
    s = hg.build(plan)

    asked = 380.0  # far more than this map's open ground will hold at full size, so the ladder must run
    parcels = open_ground_patches(s, plan, 3, size=asked)
    assert parcels, "the seat is usable at SOME size, so a wood comes back rather than nothing"
    for poly in parcels:
        w = max(p[0] for p in poly) - min(p[0] for p in poly)
        h = max(p[1] for p in poly) - min(p[1] for p in poly)
        assert max(w, h) <= asked, "what came back is the shrunk parcel, not the one that was asked for"
