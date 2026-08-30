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

import pytest

from l7r.diagram import hamletgen as hg
from l7r.diagram.overlap import matrix_extents, matrix_violations
from l7r.diagram.pipeline import rollcache

INASHIRO = hg.HamletSpec(name="Inashiro", seed=4, households=15, down_deg=90, water_sink="pond")
KUWABATA = hg.HamletSpec(name="Kuwabata", seed=21, households=16, down_deg=90, field_archetype="mulberry_dike_fishpond", pond_layout="mosaic", dike_crop="mulberry")


@pytest.fixture(scope="module")
def comb():
    return rollcache.hamlet(INASHIRO)


@pytest.fixture(scope="module")
def polder():
    return rollcache.hamlet(KUWABATA)


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
