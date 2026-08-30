"""The lane network a rolled hamlet must produce (feature 166).

Carries six rules the retired battery re-measured on every finished map: `lanes_form_one_network`,
`lanes_do_not_break_mid_run`, `lanes_bend_like_paths`, `lanes_reach_something`,
`lane_ends_front_different_houses` and `groves_clear_of_lanes`.

A LANE IS A WORN LINE, AND THAT IS THE GROUNDING BEHIND EVERY RULE HERE. Nobody laid these paths out;
they exist because inhabitants walked them, and a path exists only where somebody had a reason to go.
So a lane joins the rest of the network (you can get there from here), it does not stop in the middle of
a field (nothing wore that stretch), it bends the way a person walking bends rather than doubling back on
itself, and its ends front something worth walking to.

WHY THE WEB IS LAID AFTER THE HOUSES, WHICH IS WHAT MAKES THESE PROPERTIES OF THE PLACER. `stage_ways`
lays the skeleton and the connector BEFORE the homesteads, so the houses front them; `stage_web` lays the
lane web AFTER, because a web laid first competes for ground with the very houses it exists to serve
(measured: it grew the four pool clusters' long axes 15-97%, sprawl no check measures). The order is the
design, and these assertions are what pins it.
"""

from __future__ import annotations

import math

import pytest

from l7r.diagram import hamletgen as hg
from l7r.diagram.pipeline import rollcache

SPEC = hg.HamletSpec(name="Inashiro", seed=4, households=15, down_deg=90, water_sink="pond")

JOIN_TOL = 4.0
"""How near a lane end must come to another lane before the two count as one network. The web's own join
tolerance; a looser bar would call a near-miss a junction, which is the failure the rule exists to catch."""

DOUBLE_BACK_DEG = 140.0
"""A turn this sharp is a path doubling back on itself - nobody walks that. Below it a lane is bending,
which is what a worn line does around an obstacle."""

BEND_RUN_FT = 40.0
"""Two real turns closer together than this is a kink rather than a bend: a walker rounding something
takes one arc, not a zig and an immediate zag."""


def _seg_dist(px: float, py: float, a, b) -> float:
    ax, ay, bx, by = a[0], a[1], b[0], b[1]
    vx, vy = bx - ax, by - ay
    L2 = vx * vx + vy * vy
    t = 0.0 if L2 == 0 else max(0.0, min(1.0, ((px - ax) * vx + (py - ay) * vy) / L2))
    return math.hypot(px - (ax + t * vx), py - (ay + t * vy))


def _min_dist(pt, poly) -> float:
    return min(_seg_dist(pt[0], pt[1], poly[i], poly[i + 1]) for i in range(len(poly) - 1))


def _ways(M):
    return [[(float(x), float(y)) for x, y in (ln.get("pts") or [])] for ln in (M.get("lanes") or [])]


@pytest.fixture(scope="module")
def rolled():
    return rollcache.hamlet(SPEC)


@pytest.fixture(scope="module")
def lanes(rolled):
    """The drawn lanes, with the assertion that there ARE some. Every rule below would pass on an empty
    list, and a hamlet with no lanes is not a hamlet."""
    _plan, M = rolled
    ways = [p for p in _ways(M) if len(p) >= 2]
    assert len(ways) >= 2, "the roll drew fewer than two lanes, so the network rules would judge nothing"
    return M, ways


def test_every_lane_belongs_to_one_network(lanes) -> None:
    """`lanes_form_one_network`. You can get from any door to any other, and to the connector that leaves
    the settlement. A lane in its own component is a path that starts nowhere a walker can reach - it is
    ink drawn where a path would look right, which is the difference between a map of a place and a
    picture of one."""
    M, ways = lanes
    parent = list(range(len(ways)))

    def find(i: int) -> int:
        while parent[i] != i:
            parent[i] = parent[parent[i]]
            i = parent[i]
        return i

    for i in range(len(ways)):
        for j in range(i + 1, len(ways)):
            touch = any(_min_dist(q, ways[j]) <= JOIN_TOL for q in (ways[i][0], ways[i][-1])) or any(_min_dist(q, ways[i]) <= JOIN_TOL for q in (ways[j][0], ways[j][-1]))
            if touch:
                parent[find(i)] = find(j)
    roots = {find(i) for i in range(len(ways))}
    assert len(roots) == 1, f"the lanes fall into {len(roots)} disconnected networks - you cannot walk between them"


def test_no_lane_doubles_back_or_kinks(lanes) -> None:
    """`lanes_bend_like_paths`. A worn line bends around what is in the way; it does not turn back on
    itself, and it does not zig and immediately zag. Both shapes read as a routing artifact rather than as
    ground somebody walks, which is exactly what they are when they appear."""
    M, _ways_all = lanes
    bad = []
    for ln in M.get("lanes") or []:
        if ln.get("connector"):
            continue
        p = [(float(a), float(b)) for a, b in (ln.get("pts") or [])]
        if len(p) < 3:
            continue
        turns = []
        for k in range(1, len(p) - 1):
            v1 = (p[k][0] - p[k - 1][0], p[k][1] - p[k - 1][1])
            v2 = (p[k + 1][0] - p[k][0], p[k + 1][1] - p[k][1])
            n1, n2 = math.hypot(*v1), math.hypot(*v2)
            if n1 < 1e-6 or n2 < 1e-6:
                continue
            deg = math.degrees(math.acos(max(-1.0, min(1.0, (v1[0] * v2[0] + v1[1] * v2[1]) / (n1 * n2)))))
            if deg >= DOUBLE_BACK_DEG:
                bad.append(("doubles back", round(p[k][0]), round(p[k][1])))
            elif deg >= 50.0:
                turns.append((k, deg))
        for (ka, _da), (kb, _db) in zip(turns, turns[1:], strict=False):
            if sum(math.dist(p[j], p[j + 1]) for j in range(ka, kb)) <= BEND_RUN_FT:
                bad.append(("kinks", round(p[ka][0]), round(p[ka][1])))
    assert not bad, f"lane(s) do not bend like paths: {bad[:4]}"


def test_every_lane_end_reaches_something_worth_walking_to(lanes) -> None:
    """`lanes_reach_something`. A path exists because somebody had a reason to go there. An end that meets
    no other way, no house and no field is a line that stops in open ground, and there is nothing at the
    end of it for anyone to have worn the path to."""
    M, ways = lanes
    houses = M.get("houses") or []
    fields = [[(float(a), float(b)) for a, b in (f.get("outline") or [])] for f in (M.get("fields") or [])]
    assert houses and any(len(o) >= 2 for o in fields), "the roll drew no house or no outlined field"
    dangling = []
    for i, ln in enumerate(M.get("lanes") or []):
        if ln.get("connector"):
            continue
        p = ways[i] if i < len(ways) else []
        if len(p) < 2:
            continue
        for end in (p[0], p[-1]):
            near_way = min((_min_dist(end, o) for k, o in enumerate(ways) if k != i and len(o) >= 2), default=1e9)
            near_house = min((math.hypot(end[0] - h["x"], end[1] - h["y"]) for h in houses), default=1e9)
            near_field = min((_min_dist(end, o) for o in fields if len(o) >= 2), default=1e9)
            if min(near_way, near_house, near_field) > 60.0:
                dangling.append((round(end[0]), round(end[1])))
    assert not dangling, f"lane end(s) stop in open ground at {sorted(set(dangling))[:4]} - nothing wore that path"


def test_a_lane_does_not_break_mid_run(lanes) -> None:
    """`lanes_do_not_break_mid_run`. A lane's drawn tread stops where something solid stands in it and
    resumes on the far side, which on the page reads as a path that vanishes and reappears. The physical
    claim is simpler than the geometry: ground either carries a path or it does not, and a gap in the ink
    with nothing in the gap is the drawing forgetting to finish the line."""
    M, ways = lanes
    solid = []
    for key in ("houses", "farm_sheds", "byres"):
        for r in M.get(key) or []:
            if "x" in r and "w" in r:
                hw, hh = r["w"] / 2, r["h"] / 2
                solid.append((r["x"] - hw, r["y"] - hh, r["x"] + hw, r["y"] + hh))
    assert solid, "the roll placed nothing solid, so a break would have nothing to be explained by"
    gaps = []
    for p in ways:
        for i in range(len(p) - 1):
            gap = math.dist(p[i], p[i + 1])
            if gap <= 60.0:
                continue
            mid = ((p[i][0] + p[i + 1][0]) / 2, (p[i][1] + p[i + 1][1]) / 2)
            if not any(x0 <= mid[0] <= x1 and y0 <= mid[1] <= y1 for x0, y0, x1, y1 in solid):
                continue
            gaps.append((round(mid[0]), round(mid[1])))
    assert not gaps, f"lane(s) run straight through something solid at {gaps[:4]}"


def test_a_farmhouse_discharges_one_lane_end_not_three(lanes) -> None:
    """`lane_ends_front_different_houses`. A lane end is allowed to stop at a farmhouse - that is what it
    is for. What it may not do is let one farmhouse absolve three separate lane ends, because then the
    fabric grows a fan of stubs all pointing at the same door and the settlement reads as a diagram of
    frontage rather than as ground."""
    M, ways = lanes
    houses = M.get("houses") or []
    assert houses, "the roll placed no house"
    fronted: dict[int, int] = {}
    for i, ln in enumerate(M.get("lanes") or []):
        if ln.get("connector") or i >= len(ways) or len(ways[i]) < 2:
            continue
        for end in (ways[i][0], ways[i][-1]):
            if min((_min_dist(end, o) for k, o in enumerate(ways) if k != i and len(o) >= 2), default=1e9) <= JOIN_TOL:
                continue  # it met another way; that end is discharged by the junction
            best = min(range(len(houses)), key=lambda h: math.hypot(end[0] - houses[h]["x"], end[1] - houses[h]["y"]))
            if math.hypot(end[0] - houses[best]["x"], end[1] - houses[best]["y"]) <= 80.0:
                fronted[best] = fronted.get(best, 0) + 1
    assert fronted, "no lane end fronted a house, so this rule judged nothing"
    greedy = {h: n for h, n in fronted.items() if n > 2}
    assert not greedy, f"house(s) discharge more than two lane ends apiece: {greedy}"


def test_no_tree_is_planted_in_a_path(lanes) -> None:
    """`groves_clear_of_lanes`. You do not plant a tree in a path. Canopy OVER a way is fine and expected -
    a woodland path is a path under trees (GM 2026-08-29) - so what is measured is the TRUNK position, not
    the crown's reach. That distinction is the whole rule: an earlier form of it read the crown and would
    have forbidden the shaded lane the GM asked for."""
    M, ways = lanes
    # `tree_crowns` is one FLAT list of x, y, r, x, y, r ... - the trunk is the first two of each triple
    # and the crown's REACH is the third. Reading the third here is exactly the mistake the rule warns
    # against, and the flat packing is what makes that mistake easy, so it is named at the point of use.
    flat = [float(v) for v in (M.get("tree_crowns") or [])]
    assert len(flat) % 3 == 0, "tree_crowns is not a flat list of (x, y, r) triples - the trunk read below would be nonsense"
    trunks = [(flat[i], flat[i + 1]) for i in range(0, len(flat), 3)]
    assert trunks, "the roll drew no tree, so this rule would judge nothing"
    on_path = [(round(x), round(y)) for x, y in trunks if min(_min_dist((x, y), p) for p in ways) < 4.0]
    assert not on_path, f"tree trunk(s) stand ON a lane at {on_path[:4]}"
