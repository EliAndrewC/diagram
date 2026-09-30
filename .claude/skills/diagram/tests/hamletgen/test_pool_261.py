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
on the violating cases in `tests/hamletgen/test_brook.py` and `test_sink.py`. Wave 5 retired a way reaching the field,
with the pool's brook non-vacuity that served it: the seating reserves the field's corridor with the exit strip, or seats no
one on the margin (`homesteads/stages.py:reserve_field_corridor`), and the web draws it first where no way reaches the field
(`ways/settle.py:settle_field`), on the violating cases in `tests/hamletgen/test_homesteads_287.py` and
`tests/hamletgen/ways/test_settle.py`. What is left is KEPT because no placer guarantees it yet, and each test says why:
- the board caption off the roofs, nearest its board and off the crowns: a PREFERENCE since the GM's ruling on plan D12
  (2026-09-30: *"It should sit clean when possible but it is okay for it to not sit clean"*). The siter takes a clean
  seat wherever one exists, and every pool map has one, so these hold of the pool; a map whose every roadside seat fouls
  its caption may fail them legitimately, and is then excused here by name.
"""

from __future__ import annotations

import glob
import json
import math
import os

import pytest

SKILL = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
GENS = sorted(glob.glob(os.path.join(SKILL, "pool", "hamlets", "*", "*.gen.py")))
IDS = [os.path.basename(g).removesuffix(".gen.py") for g in GENS]


def _manifest(gen: str) -> dict:
    with open(gen.removesuffix(".gen.py") + ".json", encoding="utf-8") as fh:
        return json.load(fh)


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
    board, the words named the byre). THE ONE PREDICATE (feature 287, labels L6): `stands_nearest`, which the board's
    siter asks of the caption and the board as they will be recorded (`board_seat.board_caption_seat`)."""
    from l7r.diagram.labels import Obstacle, ObstacleIndex
    from l7r.diagram.labels.obstacles import stands_nearest
    from l7r.diagram.labels.standard import WEIGHT_OBSTACLE
    from l7r.diagram.settlement._geom import label_quad, poly_gap
    from l7r.diagram.settlement.structures.captions import LABEL_GROUND_KEYS

    def quad(o: dict) -> list[tuple[float, float]]:
        a = math.radians(float(o.get("rot") or 0))
        ca, sa, hw, hh = math.cos(a), math.sin(a), float(o.get("vw") or o["w"]) / 2, float(o.get("vh") or o["h"]) / 2  # as drawn
        return [(o["x"] + dx * ca - dy * sa, o["y"] + dx * sa + dy * ca) for dx, dy in ((-hw, -hh), (hw, -hh), (hw, hh), (-hw, hh))]

    m = _manifest(gen)
    labs = [lab for lab in m.get("labels", []) if "notice" in str(lab[5]).lower()]
    assert labs and m.get("kosatsuba"), "non-vacuity: the board and its caption"
    q = label_quad(labs[0])
    own = poly_gap(q, quad(m["kosatsuba"][0]))
    others = [
        (quad(o), key)
        for key, recs in m.items()
        if key not in LABEL_GROUND_KEYS and key != "kosatsuba" and isinstance(recs, list)
        for o in recs
        if isinstance(o, dict) and all(isinstance(o.get(f), (int, float)) for f in ("x", "y", "w", "h"))
    ]
    assert others, "non-vacuity: built footprints to compare against"
    nearest = min((poly_gap(q, p), key) for p, key in others)
    index = ObstacleIndex([Obstacle(tuple(p), WEIGHT_OBSTACLE) for p, _key in others])
    assert stands_nearest(q, quad(m["kosatsuba"][0]), index), f"the caption stands {nearest[0]:.3f} ft from a {nearest[1]} record and {own:.3f} ft from its board"


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
    # of the crowns (`board_seat.py:board_caption_seat`) wherever a seat allows; where none does (plan D12, a preference
    # since 2026-09-30) the map is excused by name, and no pool map is.
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


def _sampled(p: list[tuple[float, float]], step: float = 4.0) -> list[tuple[float, float]]:
    """A way's points every `step` ft - the spacing `clear_runs` gives a web run before `_lay_web_lane` judges it."""
    out: list[tuple[float, float]] = []
    for a, b in zip(p, p[1:], strict=False):
        n = max(1, int(math.dist(a, b) // step))
        out += [(a[0] + (b[0] - a[0]) * k / n, a[1] + (b[1] - a[1]) * k / n) for k in range(n)]
    return [*out, p[-1]]


@pytest.mark.parametrize("gen", GENS, ids=IDS)
def test_no_two_ways_run_side_by_side_past_a_pitch(gen: str) -> None:
    """`WEB_SHADOW_FT` on the FINISHED web, way against way (feature 293, settlement-review of Sawada): two ways within 30
    ft of each other for more than a bundle pitch read as one way drawn twice. `_lay_web_lane` asks it of a web run as it is
    laid; the skeleton, the joins and the stragglers are never asked, and a re-packed Sawada shipped two lanes side by side
    for 244 ft. Way against way, not against the whole network: at a junction a lane runs within 30 ft of the ways it meets,
    and the shipped maps measure up to 124 ft that way with no way doubled."""
    from l7r.diagram.hamletgen.consts import BUNDLE_PITCH
    from l7r.diagram.hamletgen.ways.serve import shadow_measure

    m = _manifest(gen)
    lanes = [[(float(x), float(y)) for x, y in ln.get("pts") or []] for ln in m["lanes"]]
    assert sum(len(p) >= 2 for p in lanes) >= 5, "non-vacuity: a web to measure"
    for i, p in enumerate(lanes):
        if len(p) < 2 or m["lanes"][i].get("connector"):
            continue
        run = _sampled(p)
        for j, o in enumerate(lanes):
            if j != i and len(o) >= 2:
                stretch = shadow_measure(run, list(zip(o, o[1:], strict=False)))[1]
                assert stretch <= BUNDLE_PITCH, f"lane {i} runs within 30 ft of lane {j} for {stretch:.0f} ft"


@pytest.mark.parametrize("gen", GENS, ids=IDS)
def test_no_zigzag_straddles_a_joint(gen: str) -> None:
    """Two records meeting end to end are one way to the walker (joints.py, GM 2026-09-26), so the bend rule
    `lanes_bend_like_paths` asks of a record - no hairpin, no two 50-degree turns inside 40 ft - is asked of the two read
    as one (feature 293, settlement-reviews of Inashiro and Sawada: a Z with one turn each side of the joint passed every
    record-at-a-time check). The engine's own predicate and joint reading, not a restatement."""
    from l7r.diagram.hamletgen.ways.clearance import _bends_badly
    from l7r.diagram.hamletgen.ways.joints import joints, oriented

    lanes = _manifest(gen)["lanes"]
    for i, ei, j, ej in joints(lanes):
        x, y = oriented(lanes, i, ei, j, ej)
        assert _bends_badly(x) or _bends_badly(y) or not _bends_badly([*x, *y[1:]]), f"lanes {i} and {j} zigzag across their joint at {x[-1]}"


@pytest.mark.parametrize("gen", GENS, ids=IDS)
def test_every_bamboo_stand_is_on_the_sheet(gen: str) -> None:
    """A bamboo stand is drawn where a reader can see it (feature 293 round 3, settlement-review of Kashikawa: the thicket
    stood wholly above the view, every culm clipped, while the page offered its class)."""
    m = _manifest(gen)
    x, y, w, h = m["meta"]["view"]
    stands = [st for st in m.get("bamboo_stands", []) if st.get("poly") or st.get("outline")]
    assert bool(stands) == (m["meta"].get("bamboo") in ("thicket", "both")), "non-vacuity: a hamlet whose knob asks for a thicket has one, and no other"
    for st in stands:
        ring = st.get("poly") or st.get("outline")
        assert all(x <= q[0] <= x + w and y <= q[1] <= y + h for q in ring), f"a {st.get('role')} stand runs off the sheet"
