"""Crossings, dangling water, and the ground between everything (feature 166): what is left of it after feature 287.

Feature 166 carried six rules here that the retired battery re-measured on every finished map. Feature 287 moved the
crossing and watercourse rules into their placers, each with a unit test on the violating case, and retired their
finished-map tests (specs/287-placer-guarantees/research.md R8): the deck long enough to land dry
(`hamletgen/ways/settle.py:_crossing_fault`, `city/bridges.py` raising `UndeckableCrossing`), the plank on a supply ditch
only (`city/bridges.py:channel_footbridges`, `plank_on_supply`), the runoff curving out of the collector
(`waterfields/comb.py:_comb_drain`) and no watercourse end dangling (`waterfields/trunks.py:anchor_trunk_ends`).

KEPT, because no placer guarantees it yet: `margins_form_continuous_ring`. `land/cover.py:fill_the_holes` clothes the
decided view to the rule's share, but the finish grows `meta.view` by the title band AFTER the fill
(`settlement/finish.py:_title_band`), and the band's blank canvas is counted by the rule and refilled by nothing.
"""

from __future__ import annotations

import pytest

from tests import rolls
from tests.gate import _pool

SPEC = rolls.REFERENCE  # the pool's brief (feature 215)


@pytest.fixture(scope="module")
def rolled():
    return _pool.rolled_map(SPEC)


def test_the_countryside_has_no_holes_in_it(rolled) -> None:
    """`margins_form_continuous_ring`. Between the fields and the settlement there is always SOMETHING -
    margin grass, scrub, a grazing common, a marsh, a wood, a yard. Real countryside has no blank ground;
    a hole in the cover is the map admitting it has not decided what is there, and the reader sees bare
    parchment where a place should be.

    Sampled on a grid over the rendered view, which is the reader's own window - ground outside it is
    somebody else's countryside."""
    _plan, M = rolled
    view = M["meta"].get("view")
    assert view, "the roll records no view, so 'the picture' has no extent"
    from l7r.diagram.settlement.land.cover import BARE_SHARE_CAP, bare_cells

    assert any(c.get("poly") for c in M.get("commons") or []), "the roll drew no cover at all, so the ring has nothing to be made of"
    # THE ENGINE'S OWN PREDICATE (feature 287, FR-003, plan D6): every recorded footprint and tread is decided ground
    holes, total = bare_cells(M, view)
    bare = len(holes)
    assert total, "the view sampled no ground"
    assert bare / total <= BARE_SHARE_CAP, f"{bare} of {total} sample points ({bare / total:.0%}) fall on ground nothing covers"
