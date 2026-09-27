"""The pool's hamlets after feature 261's amendment: the brook is crossed where the layout needs it, and what the
settlement-review found beside the wind is fixed on every map.

The GM, on the seats the brook used to refuse: *"if we find instead that our placement algorithm ends up not making
it possible to lay out a known-to-be-valid settlement configuration then we should fix the placement algorithm
instead"* - and then *"please add that to feature 261 and then do all of the work"*. These read the SHIPPED
manifests: properties of a finished map that no single placement owns (FR-011, FR-013 - FR-015, FR-017).
"""

from __future__ import annotations

import glob
import json
import math
import os

import pytest

from l7r.diagram.hamletgen.consts import BROOK_MAX_TURN_DEG, COPSE_BELT_REACH_FT, COPSE_HOUSE_REACH_FT
from l7r.diagram.settlement import segments_cross
from l7r.diagram.settlement.structures.fixtures import KOSATSUBA_ENTRANCE_REACH_FT, KOSATSUBA_HANDOVER_BAND_FT, departure_routes, kosatsuba_anchor, routes_missed
from l7r.diagram.settlement.structures.fixtures._helpers import KOSATSUBA_ANCHOR_BAND_FT

SKILL = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
GENS = sorted(glob.glob(os.path.join(SKILL, "pool", "hamlets", "*", "*.gen.py")))
IDS = [os.path.basename(g).removesuffix(".gen.py") for g in GENS]
PART_KEYS = ("gardens", "threshing_yards", "farm_fixtures", "byres", "farm_sheds", "persimmons", "bamboo_stands")


def _manifest(gen: str) -> dict:
    with open(gen.removesuffix(".gen.py") + ".json", encoding="utf-8") as fh:
        return json.load(fh)


def _brooks(m: dict) -> list[list[tuple[float, float]]]:
    return [[(float(p[0]), float(p[1])) for p in s["poly"]] for s in m.get("streams", []) if len(s.get("poly", ())) >= 2]


def _crossing(a: tuple[float, float], b: tuple[float, float], c: tuple[float, float], d: tuple[float, float]) -> tuple[float, float]:
    """Where segment a-b meets segment c-d (they are known to cross)."""
    den = (b[0] - a[0]) * (d[1] - c[1]) - (b[1] - a[1]) * (d[0] - c[0])
    t = ((c[0] - a[0]) * (d[1] - c[1]) - (c[1] - a[1]) * (d[0] - c[0])) / den
    return a[0] + t * (b[0] - a[0]), a[1] + t * (b[1] - a[1])


def test_the_pool_has_a_brook_to_cross() -> None:
    brooked = [g for g in GENS if _brooks(_manifest(g))]
    assert len(brooked) >= 3, "non-vacuity: most scripted hamlets carry a brook"


@pytest.mark.parametrize("gen", GENS, ids=IDS)
def test_every_way_across_the_brook_is_bridged(gen: str) -> None:
    """FR-011 / SC-008: a way that crosses the brook crosses on a drawn deck - a bridge within its own span of the
    crossing point."""
    m = _manifest(gen)
    for brook in _brooks(m):
        for lane in m.get("lanes", []):
            pts = [(float(p[0]), float(p[1])) for p in lane.get("pts") or []]
            for a, b in zip(pts, pts[1:], strict=False):
                for c, d in zip(brook, brook[1:], strict=False):
                    if not segments_cross(a, b, c, d):
                        continue
                    x, y = _crossing(a, b, c, d)
                    assert any(math.hypot(br["x"] - x, br["y"] - y) <= float(br.get("span", 20.0)) for br in m.get("bridges", [])), f"a way crosses the brook at ({x:.0f}, {y:.0f}) with no bridge"


@pytest.mark.parametrize("gen", GENS, ids=IDS)
def test_every_farmstead_part_stands_on_its_house_bank(gen: str) -> None:
    """FR-013 / SC-009: the line from a farmhouse to each part of its farmstead crosses no reach of the brook."""
    m = _manifest(gen)
    parts = [r for k in PART_KEYS for r in m.get(k) or [] if r.get("of")]
    assert parts or m.get("meta", {}).get("archetype") == "dikepond" or not m.get("houses"), "non-vacuity: parts name their house"
    for brook in _brooks(m):
        for r in parts:
            of = (float(r["of"][0]), float(r["of"][1]))
            across = any(segments_cross((float(r["x"]), float(r["y"])), of, c, d) for c, d in zip(brook, brook[1:], strict=False))
            assert not across, f"a farmstead part at ({r['x']:.0f}, {r['y']:.0f}) stands across the brook from its house"


@pytest.mark.parametrize("gen", GENS, ids=IDS)
def test_the_copse_stands_within_reach_of_what_it_is_named_for(gen: str) -> None:
    """FR-014 / SC-010: a dooryard copse among the houses (within 90 ft of a farmhouse), an against-the-belt copse at
    the belt's back (within 60 ft of a belt crown) - never spread over the cluster's bounding box."""
    m = _manifest(gen)
    groves = {g["role"]: g for g in m.get("village_groves", [])}
    if "copse" not in groves:
        pytest.skip("this map rolled no copse")
    clumps = groves["copse"]["clumps"]
    assert clumps, "non-vacuity: the copse has crowns"
    if m["meta"].get("copse_siting") == "against_the_belt":
        near, reach = groves["windbreak"]["clumps"] + groves["windbreak"].get("clumps_offpage", []), COPSE_BELT_REACH_FT  # the belt runs on off the page
    else:
        near, reach = [(h["x"], h["y"]) for h in m["houses"]], COPSE_HOUSE_REACH_FT
    far = [c for c in clumps if min(math.hypot(c[0] - q[0], c[1] - q[1]) for q in near) > reach + 1.0]
    assert not far, f"{len(far)} copse crowns stand beyond {reach:.0f} ft of what the copse is named for"


@pytest.mark.parametrize("gen", GENS, ids=IDS)
def test_an_entrance_board_stands_at_the_entrance(gen: str) -> None:
    """FR-015 / SC-011: a board the map seats at its entrance stands where the approach arrives - no further from the
    anchor than the entrance reach plus the board's siting band, and where every household's way out passes it. The
    settlement-review found Sawada's 669 ft from its anchor, deep among the houses, where no departure passed it."""
    m = _manifest(gen)
    seat = m["meta"].get("kosatsuba_seat")
    if seat != "entrance" or not m.get("kosatsuba"):
        pytest.skip(f"the board is seated {seat!r}")
    b = m["kosatsuba"][0]
    anchor = kosatsuba_anchor(m, seat)
    assert anchor is not None
    assert math.hypot(b["x"] - anchor[0], b["y"] - anchor[1]) <= KOSATSUBA_ENTRANCE_REACH_FT + KOSATSUBA_ANCHOR_BAND_FT
    # ...AND EVERY DEPARTURE PASSES IT (a settlement-review measured one or two households per map leaving by a lane that
    # never came near the board): each household's drawn way out, walked through the lanes and on along the connector
    routes = departure_routes(m)
    assert len(routes) >= len(m["houses"]) - 1, "non-vacuity: the households walk their ways out"
    assert routes_missed(routes, b["x"], b["y"], KOSATSUBA_HANDOVER_BAND_FT) == 0


@pytest.mark.parametrize("gen", GENS, ids=IDS)
def test_no_brook_folds_back_on_itself(gen: str) -> None:
    """FR-017 / SC-013: no vertex of a brook's course turns it more than the brook's own bend limit - Sawada's
    doubled back 123 degrees where it left the frame."""
    for brook in _brooks(_manifest(gen)):
        for p, q, r in zip(brook, brook[1:], brook[2:], strict=False):
            a, b = (q[0] - p[0], q[1] - p[1]), (r[0] - q[0], r[1] - q[1])
            na, nb = math.hypot(*a), math.hypot(*b)
            if na and nb:
                turn = math.degrees(math.acos(max(-1.0, min(1.0, (a[0] * b[0] + a[1] * b[1]) / (na * nb)))))
                assert turn <= BROOK_MAX_TURN_DEG + 1e-6, f"the brook turns {turn:.0f} deg at ({q[0]:.0f}, {q[1]:.0f})"


@pytest.mark.parametrize("gen", GENS, ids=IDS)
def test_a_way_reaches_the_field(gen: str) -> None:
    """FR-012 / SC-008: at least one of the hamlet's own ways (not the track out) comes within the 60 ft `lanes_reach_something`
    asks of the field - its paddy or its dry hem, which is the same worked ground. Inashiro, Kashikawa and Mizuguchi, whose
    houses stand across the brook from their rice, each lost that way at one step of this feature."""
    from l7r.diagram.settlement import seg_dist

    m = _manifest(gen)
    if not _brooks(m):
        pytest.skip("no brook stands between this hamlet and its field (FR-012 is about the crossing)")
    rings = [f["outline"] for f in m.get("fields", []) if f.get("outline")] + [d["poly"] for d in m.get("dry_plots") or [] if d.get("poly")]
    assert rings, "non-vacuity: the map has a field"
    pts = [(float(x), float(y)) for ln in m["lanes"] if not ln.get("connector") for x, y in ln["pts"]]
    near = min(seg_dist(p[0], p[1], r[i], r[(i + 1) % len(r)]) for p in pts for r in rings for i in range(len(r)))
    assert near <= 60.0, f"the nearest way stops {near:.0f} ft from the field"


@pytest.mark.parametrize("gen", GENS, ids=IDS)
def test_no_brook_runs_ruled_along_the_frame(gen: str) -> None:
    """FR-017: no stretch of brook within 80 ft of the view's edge runs level along that edge for more than 150 ft - the GM's
    ruling on Sawada (2026-08-26): a course that "appears to run exactly east to west parallel to the edge of the map ...
    makes it look like a mistake". The settlement-review measured 457 ft of it pinned against the frame box."""
    m = _manifest(gen)
    x0, y0, w, h = m["meta"]["view"]
    for brook in _brooks(m):
        for i in range(len(brook)):
            for axis, lo, hi in ((0, x0, x0 + w), (1, y0, y0 + h)):
                if min(abs(brook[i][axis] - lo), abs(brook[i][axis] - hi)) > 80.0:
                    continue
                j = i
                while j + 1 < len(brook) and abs(brook[j + 1][axis] - brook[i][axis]) <= 4.0:
                    j += 1
                run = sum(math.dist(brook[k], brook[k + 1]) for k in range(i, j))
                assert run <= 150.0, f"{run:.0f} ft of brook ruled along the frame from ({brook[i][0]:.0f}, {brook[i][1]:.0f})"


@pytest.mark.parametrize("gen", GENS, ids=IDS)
def test_no_farmhouse_stands_on_the_brook(gen: str) -> None:
    """FR-013: a farmstead stands whole on one bank, which begins with its house - no corner of a farmhouse within the brook's
    half-width plus 5 ft of its course. The settlement-review found a Mizuguchi house whose wall stood on the centerline."""
    from l7r.diagram.settlement import seg_dist

    m = _manifest(gen)
    for f in m.get("streams", []):
        poly, hw = f["poly"], float(f.get("w", 9.0)) / 2 + 5.0
        for h in m["houses"]:
            corners = [(h["x"] + sx * h["w"] / 2, h["y"] + sy * h["h"] / 2) for sx in (-1, 1) for sy in (-1, 1)]
            near = min(seg_dist(c[0], c[1], poly[k], poly[k + 1]) for c in corners for k in range(len(poly) - 1))
            assert near >= hw - 1.0, f"the farmhouse at ({h['x']:.0f}, {h['y']:.0f}) stands {near:.1f} ft from the brook's course"


@pytest.mark.parametrize("gen", GENS, ids=IDS)
def test_the_ways_cross_the_brook_only_at_fords_and_never_over_and_back(gen: str) -> None:
    """FR-011 (settlement-reviews of Kashikawa and Mizuguchi, feature 261): every crossing of the brook by a way stands at a
    ford, and no way crosses it an even number of times - out at one crossing and home at the next is two planks for
    nothing; and no lane record is an empty husk or a tail doubled along another way."""
    from l7r.diagram.hamletgen.ways.sweeps import _DOUBLED_DEG, along_tail
    from l7r.diagram.settlement import seg_intersect

    m = _manifest(gen)
    lanes = [[(float(x), float(y)) for x, y in ln.get("pts") or []] for ln in m["lanes"]]
    assert all(len(p) >= 2 and sum(math.dist(a, b) for a, b in zip(p, p[1:], strict=False)) >= 1.0 for p in lanes), "a lane record that draws nothing"
    for i, p in enumerate(lanes):
        if m["lanes"][i].get("connector"):
            continue
        assert not any(j != i and len(o) >= 2 and along_tail(p, o, deg=_DOUBLED_DEG) is not None for j, o in enumerate(lanes)), f"lane {i}'s end runs on beside another way"
    fords = m["meta"].get("brook_fords") or []
    for brook in _brooks(m):
        for p in lanes:
            hits = [seg_intersect(a, b, c, d) for a, b in zip(p, p[1:], strict=False) for c, d in zip(brook, brook[1:], strict=False) if segments_cross(a, b, c, d)]
            assert len(hits) < 2, f"a way crosses the brook {len(hits)} times"
            for x in hits:
                assert x is not None and min(math.dist(x, f) for f in fords) <= 45.0, f"a crossing at ({x[0]:.0f}, {x[1]:.0f}) stands off every ford"


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
def test_every_way_out_crosses_the_brook_at_most_once(gen: str) -> None:
    """A household's way OUT - its route through the lanes and along the connector - crosses the brook at most once: out
    over a plank and home over the next is two planks for nothing (settlement-review of Mizuguchi, feature 261: two
    north-bank farmsteads reached their own bank's lane 284 ft away by 1,010 ft over two planks). Asked per route, not per
    lane record: no single lane crossed twice."""
    from l7r.diagram.settlement.structures.fixtures._helpers import departure_routes

    m = _manifest(gen)
    routes = departure_routes(m)
    assert routes, "non-vacuity: the map has ways out"
    for brook in _brooks(m):
        for r in routes:
            n = sum(1 for a, b in zip(r, r[1:], strict=False) for c, d in zip(brook, brook[1:], strict=False) if segments_cross(a, b, c, d))
            assert n <= 1, f"the way out from ({r[0][0]:.0f}, {r[0][1]:.0f}) crosses the brook {n} times"


@pytest.mark.parametrize("gen", GENS, ids=IDS)
def test_no_lane_ends_in_a_hook(gen: str) -> None:
    """No lane ends in a hook - a last leg of `_HOOK_FT` or less turning back `_HOOK_DEG` or more (the GM, 2026-09-26; the
    settlement-review of Sawada, feature 261, found one drawn by the doubled-tail cut, after the pass that takes them off)."""
    from l7r.diagram.hamletgen.ways.joints import _HOOK_DEG, _HOOK_FT

    m = _manifest(gen)
    assert m["lanes"], "non-vacuity: the map has lanes"
    for ln in m["lanes"]:
        p = [(float(x), float(y)) for x, y in ln["pts"]]
        for a, b, c in ((p[-3], p[-2], p[-1]), (p[2], p[1], p[0])) if len(p) >= 3 else ():
            u, v = (b[0] - a[0], b[1] - a[1]), (c[0] - b[0], c[1] - b[1])
            nu, nv = math.hypot(*u), math.hypot(*v)
            turn = math.degrees(math.acos(max(-1.0, min(1.0, (u[0] * v[0] + u[1] * v[1]) / (nu * nv))))) if nu and nv else 0.0
            assert not (nv <= _HOOK_FT and turn >= _HOOK_DEG), f"a lane ends in a {nv:.1f} ft hook turning {turn:.0f} degrees at ({c[0]:.0f}, {c[1]:.0f})"


@pytest.mark.parametrize("gen", GENS, ids=IDS)
def test_every_lane_crosses_a_drawn_channel_square(gen: str) -> None:
    """A plank crosses its ditch square rather than obliquely (research ways/030) - the channels as well as the brook
    (settlement-review of Mizuguchi, feature 261: a lane over the head-race lay 44 degrees off square)."""
    from l7r.diagram.hamletgen.ways.checks import FORD_SQUARE_TOL_DEG

    m = _manifest(gen)
    for c in m.get("drawn_channels") or []:
        cp = [(float(q[0]), float(q[1])) for q in c["pts"]]
        for ln in m["lanes"]:
            p = [(float(x), float(y)) for x, y in ln["pts"]]
            for a, b in zip(p, p[1:], strict=False):
                for u, v in zip(cp, cp[1:], strict=False):
                    if segments_cross(a, b, u, v):
                        t = math.degrees(math.atan2(b[1] - a[1], b[0] - a[0]) - math.atan2(v[1] - u[1], v[0] - u[0])) % 180.0
                        assert abs(90.0 - t) <= FORD_SQUARE_TOL_DEG, f"a lane crosses a channel {abs(90.0 - t):.0f} degrees off square"


@pytest.mark.parametrize("gen", GENS, ids=IDS)
def test_the_board_caption_stands_at_the_boards_angle(gen: str) -> None:
    """The GM (2026-08-27): "the notice board is at an angle, therefore, the notice board label should be at exactly the
    same angle" (settlement-review of Kuwabata, feature 261: an upright fallback drew the caption level beside a board
    at 38.7 degrees)."""
    m = _manifest(gen)
    labs = [lab for lab in m.get("labels", []) if "notice" in str(lab[5]).lower()]
    assert labs and m.get("kosatsuba"), "non-vacuity: the board and its caption"
    tilt = float(labs[0][7]) if len(labs[0]) > 7 and labs[0][7] is not None else 0.0
    off = abs((tilt - float(m["kosatsuba"][0].get("rot") or 0.0) + 90.0) % 180.0 - 90.0)
    assert off <= 0.5, f"the caption stands {off:.1f} degrees off its board"


@pytest.mark.parametrize("gen", GENS, ids=IDS)
def test_no_three_woodland_parcels_stand_in_a_ruled_row(gen: str) -> None:
    """The coppice lots are not three stamps marching down one line (settlement-reviews of 2026-08-18, and of Inashiro in
    feature 261: 5 ft off one line over 1,104 ft)."""
    from l7r.diagram.hamletgen.hinterland.parcels import in_a_ruled_line

    m = _manifest(gen)
    w = [(float(o["x"]), float(o["y"])) for o in m.get("commons") or [] if o.get("role") == "woodland"]
    if len(w) < 3:
        pytest.skip(f"{len(w)} woodland parcel(s): a row needs three")
    assert not any(in_a_ruled_line(w[k], w[:k]) for k in range(2, len(w))), f"woodland parcels in a row: {w}"


@pytest.mark.parametrize("gen", GENS, ids=IDS)
def test_no_copse_clump_is_based_in_the_marsh(gen: str) -> None:
    """Woody cover stands on the dry ground above the marsh (research/vegetation.html; settlement-review of Kashikawa,
    feature 261: copse crowns 3-21 ft inside the toe marsh)."""
    from l7r.diagram.settlement._geom import point_in_poly

    m = _manifest(gen)
    copse = [c for g in m.get("village_groves") or [] if g.get("role") == "copse" for c in g.get("clumps") or []]
    assert copse, "non-vacuity: the map has a copse"
    for mk in m.get("marshes") or []:
        ring = [(float(q[0]), float(q[1])) for q in mk.get("poly") or []]
        if len(ring) >= 3:
            assert not any(point_in_poly(float(c[0]), float(c[1]), ring) for c in copse), "a copse clump stands in the marsh"


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
    # ...unless the map records that no seat the board could take offered a caption clear of the crowns (level 1): the GM
    # (2026-08-29) lets a board stand under a canopy while its label is visible, and the siter ranks a clear caption first
    assert not on or m["meta"].get("kosatsuba_caption_level") == 1, "the caption lies on a crown where the seat offered a clear one"


@pytest.mark.parametrize("gen", GENS, ids=IDS)
def test_every_copse_clump_stands_on_the_bank_of_a_house_within_reach(gen: str) -> None:
    """The dooryard copse is the trees in the gaps between the houses, so every clump has a house within the copse's reach
    on its own side of the brook (settlement-review of Kashikawa, feature 261: three clumps within reach only as the crow
    flies). Asked of a house within reach, not of the nearest: with houses on both banks a clump in the gap by its own
    house can stand a few feet nearer one across the water (Kashikawa, 81 against 77 ft)."""
    m = _manifest(gen)
    if m["meta"].get("copse_siting") == "against_the_belt":
        pytest.skip("the copse stands at the belt's back, named for the belt rather than a house")
    copse = [c for g in m.get("village_groves") or [] if g.get("role") == "copse" for c in g.get("clumps") or []]
    assert copse and m["houses"], "non-vacuity: a copse and its houses"
    for brook in _brooks(m):
        segs = list(zip(brook, brook[1:], strict=False))
        for c in copse:
            p = (float(c[0]), float(c[1]))
            mine = [h for h in m["houses"] if math.dist((h["x"], h["y"]), p) <= COPSE_HOUSE_REACH_FT and not any(segments_cross(p, (h["x"], h["y"]), a, b) for a, b in segs)]
            assert mine, f"a copse clump at ({p[0]:.0f}, {p[1]:.0f}) has no house within reach on its own bank"


def _straightest(pts: list[tuple[float, float]], tol: float) -> float:
    """The longest chord between two vertices of `pts` with every vertex between within `tol` ft of it."""
    best = 0.0
    for i in range(len(pts)):
        for j in range(i + 2, len(pts)):
            a, b = pts[i], pts[j]
            span = math.dist(a, b)
            if span > best and all(abs((b[0] - a[0]) * (a[1] - q[1]) - (a[0] - q[0]) * (b[1] - a[1])) / span <= tol for q in pts[i : j + 1]):
                best = span
    return best


@pytest.mark.parametrize("gen", GENS, ids=IDS)
def test_no_brook_runs_ruled_for_most_of_its_course_on_the_page(gen: str) -> None:
    """A natural brook does not run straight for most of the page (settlement-review of Sawada, round 0ae309f0: 872 ft
    within 3.1 ft of a line, 70% of the course on the page). No straight run - every vertex within 3.1 ft of the chord -
    covers more than 40% of the brook's length inside the view; the pool measured 17-31% once the walk swung across its
    band (specs/261 measurements)."""
    m = _manifest(gen)
    x0, y0, w, h = m["meta"]["view"]
    for brook in _brooks(m):
        on = [p for p in brook if x0 <= p[0] <= x0 + w and y0 <= p[1] <= y0 + h]
        length = sum(math.dist(a, b) for a, b in zip(on, on[1:], strict=False))
        if length < 300.0:
            continue
        run = _straightest(on, 3.1)
        assert run <= 0.4 * length, f"{run:.0f} of {length:.0f} ft of brook on the page runs straight"


@pytest.mark.parametrize("gen", GENS, ids=IDS)
def test_a_households_dry_ground_lies_by_its_house(gen: str) -> None:
    """A household's dry field lay first of all on the raised ground its house stood on (research/fields.html, "Where dry
    (hatake) crops go"; settlement-review of Inashiro, round 0ae309f0: every dry plot across the rice, a median walk of
    658 ft). The pool draws a homestead field against some steadings, and the median house stands within 150 ft of a dry
    plot - measured at 70-111 ft once the homestead fields were laid (specs/261 measurements)."""
    m = _manifest(gen)
    assert m["meta"].get("homestead_fields", 0) > 0, "no homestead field was laid"
    plots = [[(float(p[0]), float(p[1])) for p in d["poly"]] for d in m.get("dry_plots") or []]
    near = sorted(min(math.dist((h["x"], h["y"]), (sum(p[0] for p in q) / len(q), sum(p[1] for p in q) / len(q))) for q in plots) for h in m["houses"])
    assert near[len(near) // 2] <= 150.0, f"the median house stands {near[len(near) // 2]:.0f} ft from its nearest dry plot"


@pytest.mark.parametrize("gen", GENS, ids=IDS)
def test_a_belt_tree_in_the_marsh_is_alder(gen: str) -> None:
    """Woody cover at a reed edge is alder or willow, never pine (research/vegetation.html, the marsh margin): every belt
    clump seated inside a toe marsh is drawn as alder and counted so (settlement-review of Sawada, feature 261: 70 of
    its 201 belt clumps stood in the toe marsh, drawn as the belt's cedar and broadleaf)."""
    from l7r.diagram.settlement import point_in_poly

    m = _manifest(gen)
    toes = [[(float(a), float(b)) for a, b in mk["poly"]] for mk in m.get("marshes") or [] if mk.get("role") in ("toe", "waterside")]
    for g in m.get("village_groves") or []:
        if g.get("role") != "windbreak":
            continue
        wet = sum(1 for c in g["clumps"] if any(point_in_poly(c[0], c[1], t) for t in toes))
        assert g.get("alder", 0) == wet, f"{wet} belt clumps stand in the marsh, {g.get('alder', 0)} drawn as alder"


@pytest.mark.parametrize("gen", GENS, ids=IDS)
def test_no_brook_segment_lies_on_a_screen_axis_but_the_tap_run(gen: str) -> None:
    """A drawn watercourse runs on no screen axis (the GM, 2026-08-26: a course "exactly east to west parallel to the edge
    of the map ... makes it look like a mistake"), except the tap run, which lies on the fall by construction: the
    approach is five vertices, the sixth is the sluice, and the two segments from it are the run the head race's offtake
    angle is measured along. Sawada drew the segment leaving its tap run exactly vertical and Inashiro an approach leg
    1.2 degrees off one (settlement-review round 0ae309f0, feature 261)."""
    m = _manifest(gen)
    for brook in _brooks(m):
        for i, (a, b) in enumerate(zip(brook, brook[1:], strict=False)):
            if i in (5, 6) or math.dist(a, b) <= 1.0:
                continue
            deg = math.degrees(math.atan2(b[1] - a[1], b[0] - a[0])) % 90.0
            assert min(deg, 90.0 - deg) >= 1.6, f"brook segment {i} lies {min(deg, 90.0 - deg):.1f} degrees off a screen axis"
