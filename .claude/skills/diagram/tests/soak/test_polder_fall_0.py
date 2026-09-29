"""THE POLDER GRID, in the tier ABOVE the gate (feature 219, GM 2026-09-08; moved from tests/gate/).

Polder seed 12 was the gate's last roll of its own; its engine lines are unit tests (`tests/hamletgen/test_water.py`),
so under constitution VI the roll belongs here, where `make soak` makes it and no ordinary run does.

FEATURE 287 RETIRED FOUR OF THE FIVE TESTS THIS MODULE HELD, and with them the carve-out that excused the polder's "two
named gate failures" (FR-006: both closed on record, research R5; the battery that named them was retired by feature
166): the reservoir walking clear of the crop and uphill (`hamletgen/water/polder.py:walk_pond_uphill`), the grid solved
to its acreage or refused (`fit_polder`, `polder_acres_in_band`), every household seated or the site refused
(`homesteads/stages.py`, `SiteRefused`), a gate at every cut (`land/dikes.py:dike_gates`) and the lanes bending like paths
(`hamletgen/ways/settle.py:settle_the_web`) - each a placer decision with a unit test on the violating case
(specs/287-placer-guarantees/research.md R8).

What is left is the dike keep-out's CONTAINMENT on real geometry: the chord caps and the facing chains are `keepout_ring`'s and `facing_chains`'
by construction (`tests/settlement/test_keepouts.py`), but the dike keep-out's inner edge is padded by a heuristic and no
unit test holds a real polder band inside it.

SERVED FROM THE ROLL CACHE (feature 135): nothing here patches the engine, so `rollcache.hamlet` serves the plan and
finished manifest while every function the roll executed is unchanged, and rolls for real the moment one moves."""

import pytest

from l7r.diagram.settlement import point_in_poly
from tests import rolls
from tests.gate import _pool


@pytest.mark.rolls_map
def test_the_polder_dikes_keep_out_contains_its_drawn_band() -> None:
    """Feature 139 on REAL geometry: the dike's few-chord keep-out contains every vertex of the drawn band. (The GM's chord
    counts - a couple of dozen round the ring dike, under ten on the field's house side - and the field's facing chains
    never accepting a point the outline refuses are the keep-out builders' by construction since feature 287, unit-tested
    in `tests/settlement/test_keepouts.py`.)"""
    _plan, M = _pool.rolled_map(rolls.POLDER_FALL_0)  # Polder 12 since feature 216: seed 19 reached no line of its own (215 R1), and these assertions hold on either
    dk = M["dikes"][0]
    outside = [(x, y) for x, y in dk["outline"] if not point_in_poly(x, y, dk["keepout"])]
    assert not outside, f"{len(outside)} of {len(dk['outline'])} band vertices outside the keep-out, e.g. {outside[:3]}"
