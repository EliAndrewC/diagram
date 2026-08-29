"""THE WOODLAND SHRINK RUNG, COVERED ON PURPOSE RATHER THAN BY LUCK (feature 147).

`hinterland.open_ground_patches` steps a coppice DOWN in size when the seat it picked will not hold a
full-sized parcel inside the crop window - "a smaller coppice on the sheet beats a larger one the crop cuts
off". Two lines, and until this test they were covered only as a side effect of whichever cohort seeds the
full run happened to roll.

WHY THAT WAS NOT GOOD ENOUGH (measured 2026-08-29). The hamlet-path floor is 100% or the gate is red, and
those two lines went uncovered in a WARM full run while a COLD one covered them - identical code, opposite
verdicts, which made the floor a coin flip nobody had noticed. Every cohort member rolls through the rung
when rolled by itself, so the rung is not seed-specific at all; what varied was whether the coverage of
those rolls survived the run. Rolling one member here, deliberately, takes the question off luck.

It costs one roll. The alternative - reaching the rung from a synthetic fixture - was tried and does not
work: the scan wants a fully planned site (crop boxes, keep-outs, a real seat lattice), and every hand-built
settlement it was offered yielded no seat at all.
"""

from __future__ import annotations

import pytest

from l7r.diagram import hamletgen as hg
from l7r.diagram.pipeline import rollcache


@pytest.mark.rolls_map
def test_a_rolled_hamlet_walks_the_woodland_shrink_ladder() -> None:
    spec = hg.driver.cohort_specs(8, first_seed=41)[0]
    report, _how = rollcache.report(spec)
    assert report is not None, "the member rolls"
