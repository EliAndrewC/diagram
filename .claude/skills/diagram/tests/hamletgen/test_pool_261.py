"""The pool's hamlets after feature 261's amendment: the brook is crossed where the layout needs it, and what the
settlement-review found beside the wind is fixed on every map.

The GM, on the seats the brook used to refuse: *"if we find instead that our placement algorithm ends up not making
it possible to lay out a known-to-be-valid settlement configuration then we should fix the placement algorithm
instead"* - and then *"please add that to feature 261 and then do all of the work"*. These read the SHIPPED
manifests: properties of a finished map that no single placement owns (FR-011, FR-013 - FR-015, FR-017).

FEATURE 287 RETIRED FOURTEEN OF THESE (specs/287-placer-guarantees/research.md R8): the placer now decides each rule, with
a unit test on the violating case - the brook bridged and crossed only at fords, square and at most once out and back
(`hamletgen/ways/settle.py`, `city/bridges.py`), no hook and no end served only by its own way (`settle.py`), a farmstead
part on its house's bank and no farmhouse on the brook (`settlement/rolling/fit.py`), the entrance board
(`structures/fixtures/siting.py`), the board caption at the board's angle (`board_seat.py`), the ruled row of woodland
(`hinterland/parcels.py`), the copse off the marsh and the belt's alder (`homestead_parts/stands.py`) and no household
grain plot (its producer is gone). Wave 5 also retired the copse's reach and bank: every clump `village_grove` plants is
asked its reach and bank where it is seated and again where it is re-seated - a household's reserved seat its dooryard's
(`seat_near`), every other clump its siting's (`near`) - on the violating cases in `tests/settlement/test_woods_287.py`. Wave 5 retired a fifteenth, a way out crossing the brook at most once: the tree lanes
carrying such a way out are taken away too, `Lawful` asks the route (`law.adds_a_way_out_crossing`) before a tree lane is
laid, and the connector crosses a brook at most once (`track.connector_keeps_the_law`). Wave 5 retired the brook's shape
too (fold, ruled run along the frame and on the page, the screen axis): `hamletgen/water/brook.py:feed_brook` judges every
candidate, the routes round the field included, on the course as drawn (`drawn_course`) and refuses the site past the last
(`BrookRefused`), and the sink judges each confluence it adds with the brook as drawn (`sink.confluence_keeps_the_brook`),
on the violating cases in `tests/hamletgen/test_brook.py` and `test_sink.py`; the pool's brook non-vacuity stays, for the
way that reaches the field across it. What is left is KEPT because no
placer guarantees it yet, and each test says why:
- a way reaching the field: `settle.py:settle_reach` reports `field_unreached`, it does not refuse;
- the board caption off the roofs, nearest its board and off the crowns: guaranteed except at plan D12's terminal, kept
  for the GM (`meta.kosatsuba_d12`).
"""

from __future__ import annotations

import glob
import json
import math
import os

import pytest

from l7r.diagram.hamletgen.ways import law

SKILL = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
GENS = sorted(glob.glob(os.path.join(SKILL, "pool", "hamlets", "*", "*.gen.py")))
IDS = [os.path.basename(g).removesuffix(".gen.py") for g in GENS]


def _manifest(gen: str) -> dict:
    with open(gen.removesuffix(".gen.py") + ".json", encoding="utf-8") as fh:
        return json.load(fh)


def _brooks(m: dict) -> list[list[tuple[float, float]]]:
    return [[(float(p[0]), float(p[1])) for p in s["poly"]] for s in m.get("streams", []) if len(s.get("poly", ())) >= 2]


def test_the_pool_has_a_brook_to_cross() -> None:
    brooked = [g for g in GENS if _brooks(_manifest(g))]
    assert len(brooked) >= 3, "non-vacuity: most scripted hamlets carry a brook"


@pytest.mark.parametrize("gen", GENS, ids=IDS)
def test_a_way_reaches_the_field(gen: str) -> None:
    """FR-012 / SC-008: at least one of the hamlet's own ways (not the track out) comes within the 60 ft `lanes_reach_something`
    asks of the field - its paddy or its dry hem, which is the same worked ground. Inashiro, Kashikawa and Mizuguchi, whose
    houses stand across the brook from their rice, each lost that way at one step of this feature."""
    m = _manifest(gen)
    if not _brooks(m):
        pytest.skip("no brook stands between this hamlet and its field (FR-012 is about the crossing)")
    assert [f for f in m.get("fields", []) if f.get("outline")] or [d for d in m.get("dry_plots") or [] if d.get("poly")], "non-vacuity: the map has a field"
    near = law.field_reach_ft(m)
    assert not law.field_unreached(m), f"the nearest way stops {near:.0f} ft from the field"


@pytest.mark.parametrize("gen", GENS, ids=IDS)
def test_the_board_caption_names_the_board_only(gen: str) -> None:
    """The notice board's caption, as DRAWN (the tilted quad), stands on no farmhouse roof and across no lane (settlement-
    reviews of Kashikawa and Kuwabata, feature 261: a caption across a roof named the farmhouse; one across a lane's
    tread cut the lane at "notice")."""
    from l7r.diagram.settlement._geom import label_quad, point_in_poly, poly_gap, poly_seg_dist

    m = _manifest(gen)
    labs = [lab for lab in m.get("labels", []) if "notice" in str(lab[5]).lower()]
    assert labs, "non-vacuity: the board has its caption"
    q = label_quad(labs[0])
    for h in m["houses"]:
        roof = [(h["x"] + sx * h["w"] / 2, h["y"] + sy * h["h"] / 2) for sx, sy in ((-1, -1), (1, -1), (1, 1), (-1, 1))]
        assert poly_gap(q, roof) > 0.0 and not point_in_poly(h["x"], h["y"], q), f"the caption lies on the roof at ({h['x']:.0f}, {h['y']:.0f})"
    for ln in m["lanes"]:
        p = ln["pts"]
        for a, b in zip(p, p[1:], strict=False):
            assert poly_seg_dist(q, tuple(a), tuple(b)) - float(ln.get("w", 3)) / 2 >= 2.0, "the caption lies across a lane's tread"


@pytest.mark.parametrize("gen", GENS, ids=IDS)
def test_the_board_caption_stands_nearest_its_own_board(gen: str) -> None:
    """The reader pairs a caption with the nearest glyph, so the notice board's caption stands nearer the board AS DRAWN
    than any other built footprint (settlement-review of Kuwabata, feature 261: 4.9 ft off a byre and 24.6 ft off its
    board, the words named the byre)."""
    from l7r.diagram.settlement._geom import label_quad, poly_gap
    from l7r.diagram.settlement.structures.captions import LABEL_GROUND_KEYS

    def quad(o: dict) -> list[tuple[float, float]]:
        a = math.radians(float(o.get("rot") or 0))
        ca, sa, hw, hh = math.cos(a), math.sin(a), float(o["w"]) / 2, float(o["h"]) / 2
        return [(o["x"] + dx * ca - dy * sa, o["y"] + dx * sa + dy * ca) for dx, dy in ((-hw, -hh), (hw, -hh), (hw, hh), (-hw, hh))]

    m = _manifest(gen)
    labs = [lab for lab in m.get("labels", []) if "notice" in str(lab[5]).lower()]
    assert labs and m.get("kosatsuba"), "non-vacuity: the board and its caption"
    q = label_quad(labs[0])
    own = poly_gap(q, quad(m["kosatsuba"][0]))
    others = [
        (poly_gap(q, quad(o)), key)
        for key, recs in m.items()
        if key not in LABEL_GROUND_KEYS and key != "kosatsuba" and isinstance(recs, list)
        for o in recs
        if isinstance(o, dict) and all(isinstance(o.get(f), (int, float)) for f in ("x", "y", "w", "h"))
    ]
    assert others, "non-vacuity: built footprints to compare against"
    nearest = min(others)
    assert nearest[0] > own, f"the caption stands {nearest[0]:.1f} ft from a {nearest[1]} record and {own:.1f} ft from its board"


@pytest.mark.parametrize("gen", GENS, ids=IDS)
def test_the_board_caption_notches_no_crown(gen: str) -> None:
    """The caption's halo does not cut a notch out of a tree crown (settlement-review of Kuwabata, feature 230 pass 13 and
    again in feature 261, once the caption stood at its board's angle in the windbreak)."""
    from l7r.diagram.settlement._geom import label_quad
    from l7r.diagram.settlement.structures.fixtures._helpers import quad_on_canopy
    from l7r.diagram.settlement.structures.fixtures.siting import canopy_index

    m = _manifest(gen)
    labs = [lab for lab in m.get("labels", []) if "notice" in str(lab[5]).lower()]
    assert labs, "non-vacuity: the board has its caption"
    on = quad_on_canopy(label_quad(labs[0]), canopy_index(m).near)
    # no excuse since feature 287 (FR-006): the level-1 seat is gone - the board is sited only where its caption proves clear
    # of the crowns (`board_seat.py:board_caption_seat`). Plan D12's terminal (no verge takes a clean caption) is not
    # excused either: it is the gap this test is kept for.
    assert not on, "the board's caption lies on a crown"


def test_a_house_beyond_the_reach_of_every_lane_has_no_way_out() -> None:
    """`departure_routes` walks each dwelling from its nearest lane sample within `reach`; a house farther than that from
    every lane is left out rather than routed from a far-off sample (feature 278: the branch Sawada's stranded house used to
    take, stated directly)."""
    from l7r.diagram.settlement.structures.fixtures._helpers import departure_routes

    m = {
        "houses": [{"x": 210.0, "y": 100.0}, {"x": 1000.0, "y": 1000.0}],
        "lanes": [{"pts": [[0.0, 0.0], [200.0, 0.0]], "connector": True}, {"pts": [[200.0, 0.0], [200.0, 200.0]]}],
    }
    routes = departure_routes(m)
    assert len(routes) == 1 and routes[0][0][0] == 200.0, "the near house walks out; the far one is not routed"
