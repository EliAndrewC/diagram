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
grain plot (its producer is gone). What is left is KEPT because no placer guarantees it yet, and each test says why:
- the brook's shape (fold, ruled run along the frame and on the page, the screen axis): `hamletgen/water/brook.py:feed_brook`
  returns its last candidate (round the field) unjudged, and the drawn course is rounded after it is judged;
- a way reaching the field: `settle.py:settle_reach` reports `field_unreached`, it does not refuse;
- a way out crossing the brook at most once: tree lanes are exempt from the last-resort drop, and `Lawful` judges one
  lane, not a route;
- the copse's reach and bank: a reserved wood seat is planted without the reach test, and a re-seated one is not asked
  its reach or bank again (and against_the_belt's reach is from the belt, which the reservation does not know);
- the board caption off the roofs, nearest its board and off the crowns: guaranteed except at plan D12's terminal, kept
  for the GM (`meta.kosatsuba_d12`).
"""

from __future__ import annotations

import glob
import json
import math
import os

import pytest

from l7r.diagram.hamletgen.consts import BROOK_MAX_TURN_DEG, BROOK_WANDER_STEP, COPSE_BELT_REACH_FT, COPSE_HOUSE_REACH_FT
from l7r.diagram.hamletgen.ways import law
from l7r.diagram.settlement import segments_cross

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
    m = _manifest(gen)
    if not _brooks(m):
        pytest.skip("no brook stands between this hamlet and its field (FR-012 is about the crossing)")
    assert [f for f in m.get("fields", []) if f.get("outline")] or [d for d in m.get("dry_plots") or [] if d.get("poly")], "non-vacuity: the map has a field"
    near = law.field_reach_ft(m)
    assert not law.field_unreached(m), f"the nearest way stops {near:.0f} ft from the field"


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
    twice = law.way_outs_crossing(m, routes)
    assert not twice, f"the way(s) out from {twice[:4]} (x, y, crossings) cross the brook more than once"


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
def test_no_brook_segment_lies_on_a_screen_axis_but_the_tap_run(gen: str) -> None:
    """A drawn watercourse runs on no screen axis (the GM, 2026-08-26: a course "exactly east to west parallel to the edge
    of the map ... makes it look like a mistake"), except the tap run, which lies on the fall by construction: the
    approach ends at the sluice, the vertex the head race leaves from, and the two segments from it are the run the head race's offtake
    angle is measured along. Sawada drew the segment leaving its tap run exactly vertical and Inashiro an approach leg
    1.2 degrees off one (settlement-review round 0ae309f0, feature 261)."""
    m = _manifest(gen)
    heads = [(float(c["poly"][0][0]), float(c["poly"][0][1])) for c in m.get("channels") or [] if (c.get("frm") or {}).get("kind") == "stream"]
    for brook in _brooks(m):
        # the tap is the vertex the head race leaves from - found by position, since the approach's bends are rounded
        tap = min(range(len(brook)), key=lambda k: min((math.dist(brook[k], h) for h in heads), default=0.0))
        for i, (a, b) in enumerate(zip(brook, brook[1:], strict=False)):
            # a chord of a rounded bend (`BROOK_BEND_FT`) is not a run: a curve that turns through an axis has one chord on
            # it, and the GM's objection is to a course that runs along one - so only runs of a wander stride or more count
            if i in (tap, tap + 1) or math.dist(a, b) < BROOK_WANDER_STEP:
                continue
            deg = math.degrees(math.atan2(b[1] - a[1], b[0] - a[0])) % 90.0
            assert min(deg, 90.0 - deg) >= 1.6, f"brook segment {i} lies {min(deg, 90.0 - deg):.1f} degrees off a screen axis"


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
