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
