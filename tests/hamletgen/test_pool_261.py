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
with the pool's brook non-vacuity that served it: on a brook map a field no way reaches is refused (`ways/last_resort.py`),
on the violating cases in `tests/hamletgen/ways/test_last_resort.py`. What is left is KEPT because no placer guarantees it yet, and each test says why:
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


def test_a_dwellings_nearest_sample_is_the_first_of_the_nearest() -> None:
    """`nearest_of` answers as `min(among, key=math.dist)` does: the nearest node, the FIRST of `among`'s order on a tie - the
    near-ties numpy finds asked again exactly (the perf-audit of feature 328 wave 4)."""
    from l7r.diagram.settlement.structures.fixtures._helpers import nearest_of, reached_at

    nodes = [(0.0, 0.0), (10.0, 0.0), (-10.0, 0.0), (0.0, 3.0), (0.1 + 0.2, 0.0)]
    for among in ([0, 1, 2, 3, 4], [2, 1, 0], [1, 2], [4, 3]):
        for q in ((0.0, 0.0), (5.0, 0.0), (0.0, 10.0), (0.15, 0.0)):
            assert nearest_of(nodes, among, reached_at(nodes, among), q) == min(among, key=lambda i: math.dist(nodes[i], q))


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


# THE ZIGZAG NO SMOOTHING STRAIGHTENS YET (feature 328 wave 52, bisected as the knots above): Sawada's lane 3 runs east to
# (4122.4, 2042.1) and turns back 27 ft to lane 1's door, where lane 1 leaves north-east - two turns past 50 degrees inside
# 40 ft across the joint. It waits on the found row specs/328-match-the-research/audit/found-wave54.jsonl ("a zigzag across a
# joint at a door"). STRICT: the day it is straightened this fails, and its name comes off the list.
_ZIGZAGS_WAITING = {"sawada"}


@pytest.mark.parametrize(
    "gen",
    [
        pytest.param(g, marks=pytest.mark.xfail(strict=True, reason="a zigzag at a door no smoothing straightens yet - ranked found row (feature 328)")) if i in _ZIGZAGS_WAITING else g
        for g, i in zip(GENS, IDS, strict=True)
    ],
    ids=IDS,
)
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


_KNOT_MARGIN = 1.0  # the page's own reach (feature 328); the slide the 1.5 caught is gone
"""Two junctions on one lane this many knot reaches apart still count as a knot: a foot slid along the lane to just past the
reach is the knot drawn, not gathered (glyph-check round 2 of feature 328 wave 4, Inashiro: lane 13's foot slid 16.7 ft along
lane 11 to 25.18 ft from lane 11's end, a walker turning 51, 91, 92 and 72 degrees within 45 ft)."""


def lane_knots(lanes: list[dict]) -> list[tuple[int, tuple[float, float], int, tuple[float, float], float]]:
    """The knots of a finished web, (lane, end, lane, end, ft): two lane ends within the knot reach (`_KNOT_FT`) of one another
    not standing at one point, and two JUNCTIONS (an end that meets another way: two or more ends at one point, or a T-foot on
    another lane's side) on the SAME lane within `_KNOT_MARGIN` reaches. Ends within `_JOINT_FT` are one point; a pair one lane
    runs between (its own two ends) is that lane, its join."""
    from l7r.diagram.hamletgen.ways.joints import _JOINT_FT
    from l7r.diagram.hamletgen.ways.smooth import _KNOT_FT
    from l7r.diagram.settlement._geom.primitives import seg_dist

    pts = [[(float(x), float(y)) for x, y in ln.get("pts") or []] for ln in lanes]
    ends = [(i, p[e]) for i, p in enumerate(pts) if len(p) >= 2 for e in (0, -1)]
    node = list(range(len(ends)))

    def root(a: int) -> int:
        while node[a] != a:
            a = node[a]
        return a

    for a in range(len(ends)):
        for b in range(a + 1, len(ends)):
            if math.dist(ends[a][1], ends[b][1]) <= _JOINT_FT:
                node[root(b)] = root(a)
    spans = {frozenset((root(2 * k), root(2 * k + 1))) for k in range(len(ends) // 2)}  # each lane's own two points

    def on(k: int, q: tuple[float, float]) -> bool:
        return any(seg_dist(q[0], q[1], u, v) <= _JOINT_FT for u, v in zip(pts[k], pts[k][1:], strict=False))

    def junction(a: int) -> bool:
        return sum(root(b) == root(a) for b in range(len(ends))) > 1 or any(k != ends[a][0] and len(pts[k]) >= 2 and on(k, ends[a][1]) for k in range(len(pts)))

    def one_lane(a: int, b: int) -> bool:
        return any(len(p) >= 2 and on(k, ends[a][1]) and on(k, ends[b][1]) for k, p in enumerate(pts))

    out = []
    for a in range(len(ends)):
        for b in range(a + 1, len(ends)):
            d = math.dist(ends[a][1], ends[b][1])
            if root(a) == root(b) or frozenset((root(a), root(b))) in spans or d > _KNOT_MARGIN * _KNOT_FT:
                continue
            if d <= _KNOT_FT or (junction(a) and junction(b) and one_lane(a, b)):
                out.append((ends[a][0], ends[a][1], ends[b][0], ends[b][1], round(d, 1)))
    return out


# THE KNOTS NO LAWFUL GATHER REACHES YET (feature 328 wave 4, measured): on these two maps every single-point gather of the
# remaining knots runs a way along another, through a yard, or off the network, so they wait for the ranked found row that
# re-lays the earlier household's way at seating (specs/328-match-the-research/ranking.json, "a knot no lawful gather
# reaches"). Main draws the same knots or more (Inashiro 7 end pairs within the reach on main and here, Sawada 3 -> 1). STRICT: the day a map's knots are gathered this fails, and its name comes off the list.
# Wave 9's re-seated homesteads left neither map a knot (feature 328, 2026-10-07): both names came off. Wave 10's field
# values (the rings' steps and the fork triangle) re-lay Sawada so it carries
# a knot again - one knot, as main has one there, at a different place (main: lanes 9/12, 21.9 ft; here: lanes 15/17, 8.2 ft;
# bisected with the berm still applied, the three together; the berm since held and the knot stands): Sawada waits again, Inashiro
# does not (main had one there too).
# Wave 52's fixture seats (the privy's barn share spread, the heap stepped along the privy's bearing) re-lay Inashiro and
# Kuwabata so each carries a knot again (bisected 2026-10-08: 013b667d5 passes, e4c99b277 and 19f69655c fail; probed in
# settle_knots' judge): Inashiro's field way starts on the spur 9.4 ft from where it leaves lane 10, 16.1 ft from that
# house's door, and every gather of the spur onto the door splits the web (the field way hangs on it); Kuwabata's lane 11
# foot T's onto lane 9 21.8 ft from its door, and the gather leaves a farmhouse unreached. Both wait on the same row.
_KNOTS_WAITING = {"sawada", "inashiro", "kuwabata"}


@pytest.mark.parametrize(
    "gen",
    [
        pytest.param(g, marks=pytest.mark.xfail(strict=True, reason="knots no lawful gather reaches yet - ranked found row (feature 328)")) if i in _KNOTS_WAITING else g
        for g, i in zip(GENS, IDS, strict=True)
    ],
    ids=IDS,
)
def test_no_lane_ends_knot_short_of_a_join(gen: str) -> None:
    """Lane ends that nearly meet are joined: ends within the knot reach (`_KNOT_FT`) of one another stand at ONE point
    (research/questions/0081-village-lanes.drawing.html: "Ends within 25 ft of one another are joined at a single point";
    feature 328 wave 4 glyph-check of Inashiro: lanes 7 and 3 T'd onto the track 6 ft apart, 18 and 24 ft down from its head
    where lane 1 arrives, and lanes 9 and 11 ended 19 ft apart). Every lane's end counts, a T-foot (an end on another lane's
    side) included - and two junctions on one lane within `_KNOT_MARGIN` reaches, so a foot slid to just past the reach is
    not read as gathered (`lane_knots`)."""
    from l7r.diagram.hamletgen.ways.smooth import _KNOT_FT

    lanes = _manifest(gen)["lanes"]
    assert any(len(ln.get("pts") or []) >= 2 for ln in lanes), "non-vacuity: the map has lanes"
    knots = lane_knots(lanes)
    assert not knots, f"lane ends within {_KNOT_FT:g} ft of one another (or junctions on one lane within {_KNOT_MARGIN * _KNOT_FT:g} ft) and not joined (lane, end, lane, end, ft): {knots}"


RANK_FT = {"footpath": 3.0, "spur": 5.0, "track": 6.0}
"""0081's widths by rank (research/questions/0081-village-lanes.drawing.html): "a footpath is drawn 3 ft wide, the cluster's
spine and its spur to the fields 5 ft, and the track out to the wider world 6 ft"."""


def lane_rank(ln: dict) -> str | None:
    """A lane's rank by its role: the track out (the connector), the field spur (the spur or the field way), a footpath (a
    household's way or a way target's). None for a lane with no role of rank (a web lane, a link, a street)."""
    if ln.get("connector"):
        return "track"
    if ln.get("spur") or ln.get("role") == "field way":
        return "spur"
    return "footpath" if ln.get("role") in ("access", "way target") else None


@pytest.mark.parametrize("gen", GENS, ids=IDS)
def test_every_lane_is_drawn_at_its_own_rank(gen: str) -> None:
    """A household's way is a 3 ft footpath, the field spur 5 ft and the track out 6 ft, whatever they meet end to end
    (glyph-check round 2 of feature 328 wave 4, Inashiro: the field route, lanes 7, 2 and 0, all drawn 6 ft - a household's
    way and the spur widened to the track's tread, a 6 ft lane hanging off a 3 ft footpath)."""
    lanes = _manifest(gen)["lanes"]
    ranked = [(i, r, float(ln["w"])) for i, ln in enumerate(lanes) if (r := lane_rank(ln))]
    assert any(r == "footpath" for _i, r, _w in ranked) or any(ln.get("role") == "touch" for ln in lanes), "non-vacuity: ranked lanes"
    off = [(i, r, w) for i, r, w in ranked if w != RANK_FT[r]]
    assert not off, f"lanes drawn off their rank (lane, rank, ft): {off}"


@pytest.mark.parametrize("gen", GENS, ids=IDS)
def test_every_bamboo_stand_is_on_the_sheet(gen: str) -> None:
    """A bamboo stand is drawn where a reader can see it (feature 293 round 3, settlement-review of Kashikawa: the thicket
    stood wholly above the view, every culm clipped, while the page offered its class)."""
    m = _manifest(gen)
    x, y, w, h = m["meta"]["view"]
    stands = [st for st in m.get("bamboo_stands", []) if st.get("poly") or st.get("outline")]
    # the knob is read of the THICKETS: a homestead strip (`role` "homestead") is what the "homestead" knob asks for, and Sawada
    # seated two once feature 302 moved its houses - the earlier form counted every stand and read them as a thicket
    thickets = [st for st in stands if st.get("role") == "thicket"]
    assert bool(thickets) == (m["meta"].get("bamboo") in ("thicket", "both")), "non-vacuity: a hamlet whose knob asks for a thicket has one, and no other"
    for st in stands:
        ring = st.get("poly") or st.get("outline")
        assert all(x <= q[0] <= x + w and y <= q[1] <= y + h for q in ring), f"a {st.get('role')} stand runs off the sheet"
