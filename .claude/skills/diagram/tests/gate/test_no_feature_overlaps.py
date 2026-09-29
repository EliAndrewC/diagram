"""No feature lies on another that may not carry it (feature 166).

Carries `features_do_not_overlap` - KEPT through feature 287 as a property no single placer owns: the matrix judges every
pair of layers, and until M8's registry (T83) refuses by it at every placer, the finished map is the only place every
pair meets. Feature 287 retired its siblings (specs/287-placer-guarantees/research.md R8): `scatter_respects_swept_clearings`
(`land/cover.py:_clear_ground` culls the cover in a swept clearing, and the test's filter was a subset of the matrix
test's own verdict), and the pond fixture off its sluice and on its pond's near half (`farm_fixtures.py:pond_fixture_fits`,
`hamletgen/pondstock.py:sty_on_near_half`) - each with a unit test on the violating case.

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
