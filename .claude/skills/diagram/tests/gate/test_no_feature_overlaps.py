"""No feature lies on another that may not carry it (feature 166).

Carries `features_do_not_overlap`, and with it `scatter_respects_swept_clearings`.

ONE CLASSIFICATION DECIDES EVERY PAIR, and that is the whole design. There is no per-pair rule and there
never was: each manifest key is classified once (`OVERLAP_CLASS`), and `matrix_policy` answers "may a
`ka` and a `kb` overlap, and on whose authority" for any two keys from that classification plus a short
list of named permissions - an annex on its OWN parent, two annexes of one household, a channel reaching
the field it feeds, a trade work's private well inside its own court. So a new footprint feature needs a
row in the taxonomy and nothing else: membership alone gates it off every hazard the matrix knows about.

THE TAXONOMY MOVED INTO THE ENGINE UNDER THIS FEATURE, and the move is the point rather than a side
effect. It lived in `check_village/common_01_geometry.py`, which meant the placer's own doctrine - which
features may share ground - was stored inside the thing that audited the placer. A placer needs that table
to decide where a thing may GO; the battery needed it to decide, afterwards, whether the thing had gone
somewhere allowed. Only the first is load-bearing, so the table now lives at `l7r/diagram/overlap/` and
the audit is this test, run once per code change instead of once per map generated.

DRAWN EXTENTS, NOT RECORDED ENVELOPES. `matrix_extents` is careful about a distinction that a naive
overlap test gets wrong in the expensive direction: several features record an ENVELOPE much larger than
the ink inside it - a grove's bounding box against its clumps, a commons parcel against its scatter - and
comparing envelopes reports overlaps the reader cannot see while missing ones they can.
"""

from __future__ import annotations

import math
import pytest

from l7r.diagram.overlap import matrix_extents, matrix_violations
from tests import rolls
from tests.gate import _pool

INASHIRO = rolls.REFERENCE  # the pool's brief (feature 215)
KUWABATA = rolls.KUWABATA


@pytest.fixture(scope="module")
def comb():
    return _pool.rolled_map(INASHIRO)


@pytest.fixture(scope="module")
def polder():
    return _pool.rolled_map(KUWABATA)


def test_the_comb_hamlet_draws_no_forbidden_overlap(comb) -> None:
    """`features_do_not_overlap` on the reference roll. The placer refuses an overlapping seat by
    construction, which is exactly why this is a property of the generator rather than an audit of its
    output - but the refusal only covers what the placer KNOWS about, and a feature drawn by a later stage
    over ground an earlier one claimed is the shape that gets through."""
    _plan, M = comb
    ext = matrix_extents(M)
    assert len(ext) > 100, f"the roll offered only {len(ext)} classified extents - too few for this rule to mean anything"
    bad = matrix_violations(M)
    assert not bad, f"overlapping feature(s) whose classes forbid it: {bad[:4]}"


def test_the_polder_hamlet_draws_no_forbidden_overlap(polder) -> None:
    """The same rule on the other archetype. The polder lays a dike, a ring canal, fishponds, sties and
    pens that the comb hamlet never draws, so it exercises rows of the taxonomy the reference roll cannot
    reach - and a classification is only as good as the pairs anything actually puts side by side."""
    _plan, M = polder
    ext = matrix_extents(M)
    assert len(ext) > 100, f"the polder roll offered only {len(ext)} classified extents"
    bad = matrix_violations(M)
    assert not bad, f"overlapping feature(s) whose classes forbid it: {bad[:4]}"


def test_the_ground_cover_scatter_respects_what_was_swept_before_it(comb) -> None:
    """`scatter_respects_swept_clearings`. The scrub and reed scatter skips the clearings that exist WHEN
    IT RUNS, so a clearing swept afterwards gets dotted over - the collar around a shrine or a graveyard
    fills with scrub that was drawn before anybody decided the collar was there.

    This is an ORDERING rule wearing an overlap rule's clothes, which is why it belongs with this one: the
    matrix is what notices, because a cover parcel lying over a reserved clearing is exactly a forbidden
    pair. The fix is never to make the scatter smarter - it is to reserve the ground BEFORE the cover
    draws, or to place the feature first."""
    _plan, M = comb
    cover = [c for c in (M.get("commons") or []) + (M.get("marshes") or []) if c.get("poly")]
    assert cover, "the roll laid no ground cover, so this rule would judge nothing"
    # every clearing the map reserved must still be clear of the cover drawn over it
    bad = [(a, b, x, y) for a, b, x, y in matrix_violations(M) if "clearings" in (a, b) or "commons" in (a, b) or "marshes" in (a, b)]
    assert not bad, f"ground cover drawn over a swept clearing: {bad[:3]}"


def _pond_stock_parts(M):
    """Every DRAWN part of every pig sty and duck pen on the map, as (outline, closed) pairs - the sty
    footprint, the pen's dry run, and the pen's fence arc, which is an open polyline and not a region."""
    from l7r.diagram.settlement._geom.overlap import rot_rect

    for s in M.get("pig_sties", []):
        yield rot_rect(s["x"], s["y"], s["w"], s["h"], s["rot"]), True
    for p in M.get("duck_pens", []):
        yield rot_rect(p["x"], p["y"], p["w"], p["h"], p["rot"]), True
        if p.get("wet"):
            yield [(float(q[0]), float(q[1])) for q in p["wet"]], False


def test_no_pond_fixture_stands_on_its_ponds_sluice(polder) -> None:
    """feature 233. The GM, reading this map, asked whether the pig sties would stand as close to the
    pond sluices as they did: three of seven had a feed culvert drawn THROUGH the shed and one duck
    pen's fence crossed one. The research says the shed belongs at the water - the manure is the pond's
    feed - so the fixtures were not moved back from it; they were moved off the culvert, because nobody
    builds over the opening they must reach to lift its boards."""
    from l7r.diagram.settlement._geom.primitives import poly_seg_dist
    from l7r.diagram.settlement.farm_fixtures import SLUICE_CLEAR_FT

    _plan, M = polder
    stubs = [((float(d["a"][0]), float(d["a"][1])), (float(d["b"][0]), float(d["b"][1]))) for d in M["dikepond_sluices"]]
    parts = list(_pond_stock_parts(M))
    assert stubs and parts, f"nothing to judge: {len(stubs)} stubs, {len(parts)} drawn parts"
    worst = min(poly_seg_dist(list(poly), a, b, closed) for poly, closed in parts for a, b in stubs)
    assert worst >= SLUICE_CLEAR_FT, f"a pond fixture stands {worst:.2f} ft from a sluice stub, inside the {SLUICE_CLEAR_FT} ft margin"


def test_every_pond_fixture_keeps_to_the_near_half_of_its_pond(polder) -> None:
    """feature 233, settlement-review. Ranking the bank seats without bounding the accept leaves the
    whole perimeter available, and this map's own geometry offers seats up to 288 ft further from the
    houses than the first choice - a shed on the far bank would read as belonging to no household, and
    nothing else here would say so. The bound is geometric: no further from the house cluster than the
    pond's own center."""
    _plan, M = polder
    houses = M["houses"]
    hc = (sum(h["x"] for h in houses) / len(houses), sum(h["y"] for h in houses) / len(houses))
    ponds = M["dikeponds"]
    for key in ("pig_sties", "duck_pens"):
        for f in M.get(key, []):
            par = ponds[f["pond"]]["parcel"]
            centre = (sum(float(q[0]) for q in par) / len(par), sum(float(q[1]) for q in par) / len(par))
            assert math.dist((f["x"], f["y"]), hc) <= math.dist(centre, hc), f"a {key[:-1]} sits on the far side of pond {f['pond']} from the houses"
