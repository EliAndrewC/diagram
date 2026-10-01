"""Feature 294: what the settlement-review used to catch by eye, as rules over the shipped maps (plan B; research R3).

The GM (2026-10-01): *"if our settlement review is checking for anything which a properly implemented placement algorithm
would make impossible, then we should fix the placement algorithm and then stop checking for that thing in the settlement
review."* Each rule here is one of the review's recorded finding classes (`specs/294-settlement-review-rethink/research.md`
R1, R3), proved RED on a seeded fault of its recorded case first (the `test_*_fires_*` cases, plain inputs) and then held over
every shipped hamlet (the `test_*_pool` cases). The predicates are module-level so the seeded cases call them directly.

Thresholds and their sources (plan D11): footbridges 60 ft apart (GUESS; the placer spaces them 300 ft); house bearings
within +-33.75 deg of the common bearing (research homesteads/240: 87% of houses within the commonest compass point and the
two either side) with no pile-up at the limit; the brook crosses the view in one piece (map drawing convention); the wood shed
nearer its own house than any other building and turned with it (research homesteads/212 and 720; "nearest its own" a GUESS).
"""

from __future__ import annotations

import glob
import json
import os
import pathlib
from collections.abc import Mapping, Sequence
from typing import Any

import pytest
from shapely import affinity
from shapely.geometry import LineString, Point, Polygon, box
from shapely.ops import unary_union
from shapely.strtree import STRtree

_SKILL = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
_HAMLETS = sorted(glob.glob(os.path.join(_SKILL, "pool", "hamlets", "*", "*.gen.py")))

FOOTBRIDGE_GAP_FT = 60.0  # GUESS (plan D11): the recorded case was two decks side by side (feature 269, rounds 1-2)
BEARING_BAND_DEG = 33.75  # research homesteads/240: the commonest compass point and the two either side
PILE_AT_LIMIT = 2  # no more than two houses within a degree of the widest turn (the 9-of-16 pile, 269 E round 1)
PILE_FLOOR_DEG = 5.0  # a turn this small is the common bearing itself, not a clamp
SHED_TURN_TOL_DEG = 2.0
HIT_SHARE_FLOOR = 0.8  # GUESS (plan D11): a class answers the pointer over at least 80% of its own visible ink
HIT_MIN_PIXELS = 50  # a class with less visible ink than this is a few pixels of edge, not a region to hover
DRAWN_TO_ROLLED = 0.15  # GUESS (plan D11): a drawn size within 15% of its roll - a clump's canopy is the grain of a copse
RECORD_OFF_INK_FT = 3.0  # GUESS (plan D11): about one drawn ditch's width - a record is its drawing (map drawing convention)
POINT_ON_WATER_FT = 2.0  # GUESS: a sluice gate or weir stands on its water (the recorded case: a gate snapped 7 ft off)


def _manifest(gen: str) -> dict[str, Any]:
    from tests.gate import _pool

    with open(_pool.obtain(gen), encoding="utf-8") as fh:
        return json.load(fh)


def _ftpx(M: Mapping[str, Any]) -> float:
    return float((M.get("meta") or {}).get("ftpx") or 1.0)


# ---- B8: no two footbridges side by side ------------------------------------------------------------------


def bridges_too_close(bridges: Sequence[Mapping[str, Any]], ftpx: float, gap_ft: float = FOOTBRIDGE_GAP_FT) -> list[tuple[int, int, float]]:
    """(i, j, ft) for every pair of bridge decks closer than `gap_ft`, found through one STRtree over the deck centers."""
    pts = [Point(b["x"], b["y"]) for b in bridges]
    tree = STRtree(pts)
    out = []
    for i, p in enumerate(pts):
        for j in tree.query(p.buffer(gap_ft / ftpx)):
            j = int(j)
            if j > i and p.distance(pts[j]) * ftpx < gap_ft:
                out.append((i, j, round(p.distance(pts[j]) * ftpx, 1)))
    return out


def test_two_decks_side_by_side_fire() -> None:
    """Seeded: the recorded case, a second deck laid 15 ft along the same ditch."""
    assert bridges_too_close([{"x": 0, "y": 0}, {"x": 15, "y": 0}, {"x": 400, "y": 0}], 1.0) == [(0, 1, 15.0)]


# ---- B11: house bearings within the band, no pile at its limit --------------------------------------------


def _turn(rot: float, bearing: float) -> float:
    return (rot - bearing + 180.0) % 360.0 - 180.0


def bearing_faults(houses: Sequence[Mapping[str, Any]], bearing: float) -> list[str]:
    """Each way the houses' turns break the band: a house outside +-`BEARING_BAND_DEG`, or a pile of more than
    `PILE_AT_LIMIT` houses within a degree of the widest turn (a clamp, not a spread)."""
    turns = [_turn(float(h.get("rot") or 0.0), bearing) for h in houses]
    out = [f"house {i} turned {t:.1f} deg" for i, t in enumerate(turns) if abs(t) > BEARING_BAND_DEG]
    if turns:
        widest = max(abs(t) for t in turns)
        piled = sum(1 for t in turns if abs(abs(t) - widest) <= 1.0)
        if widest > PILE_FLOOR_DEG and piled > PILE_AT_LIMIT:
            out.append(f"{piled} houses piled at {widest:.1f} deg")
    return out


def test_a_pile_at_the_clamp_and_a_house_out_of_the_band_fire() -> None:
    """Seeded: Sawada's recorded case, 9 of 16 houses at +-30 deg; and one house turned 40 deg."""
    assert bearing_faults([{"rot": 30.0}] * 9 + [{"rot": 3.0}] * 7, 0.0) == ["9 houses piled at 30.0 deg"]
    assert bearing_faults([{"rot": 40.0}, {"rot": 0.0}], 0.0) == ["house 0 turned 40.0 deg"]
    assert bearing_faults([{"rot": 0.0}] * 10, 0.0) == [], "every house on the common bearing is no pile"


# ---- B12: the brook crosses the view as one piece ---------------------------------------------------------


def brook_pieces_in_view(stream: Mapping[str, Any], view: Sequence[float]) -> int:
    """How many separate runs of the brook's course lie inside the view (`meta.view` = x, y, w, h)."""
    x, y, w, h = view
    inside = LineString(stream["poly"]).intersection(box(x, y, x + w, y + h))
    return 0 if inside.is_empty else len(getattr(inside, "geoms", [inside]))


def test_a_brook_leaving_and_re_entering_the_view_fires() -> None:
    """Seeded: the recorded case (230 pass 3, Sawada's brook off the frame and back): out of the view and in again."""
    course = {"poly": [[-10, 50], [50, 50], [50, 150], [80, 150], [80, 50], [150, 50]]}
    assert brook_pieces_in_view(course, [0, 0, 100, 100]) == 2
    assert brook_pieces_in_view({"poly": [[-10, 50], [150, 50]]}, [0, 0, 100, 100]) == 1


# ---- B3: the wood shed on its own household's ground, turned with its house --------------------------------


def shed_faults(M: Mapping[str, Any]) -> list[str]:
    """Each wood shed (`farm_fixtures` kind `woodpile`) nearer another household's house than its own (`of`), or turned
    off its house's rake. Its own household's byre, shed or retirement house beside it is not a neighbor's gable."""
    houses = list(M.get("houses") or [])
    centers = [Point(h["x"], h["y"]) for h in houses]
    tree = STRtree(centers)
    out = []
    for f in M.get("farm_fixtures") or []:
        if f.get("kind") != "woodpile":
            continue
        here, own = Point(f["x"], f["y"]), Point(*f["of"])
        nearest = centers[int(tree.nearest(here))]
        if nearest.distance(own) > 1.0 and here.distance(nearest) < here.distance(own) - 1e-6:
            out.append(f"the shed at ({f['x']}, {f['y']}) stands nearer another household's house than its own")
        house = min(houses, key=lambda h: own.distance(Point(h["x"], h["y"])))
        off = abs(_turn(float(f.get("rot") or 0.0), float(house.get("rot") or 0.0))) % 90.0
        if min(off, 90.0 - off) > SHED_TURN_TOL_DEG:  # a quarter turn is the same rake
            out.append(f"the shed at ({f['x']}, {f['y']}) is turned off its house")
    return out


def test_a_shed_on_a_neighbors_gable_or_turned_off_its_house_fires() -> None:
    """Seeded: the recorded case (feature 269, a woodpile on the neighbor's gable), and a shed turned 45 deg."""
    houses = [{"x": 0, "y": 0, "rot": 0}, {"x": 60, "y": 0, "rot": 0}]
    on_gable = {"houses": houses, "farm_fixtures": [{"kind": "woodpile", "x": 50, "y": 0, "rot": 0, "of": [0, 0]}]}
    assert shed_faults(on_gable) and "nearer another household" in shed_faults(on_gable)[0]
    turned = {"houses": houses, "farm_fixtures": [{"kind": "woodpile", "x": 0, "y": 20, "rot": 45, "of": [0, 0]}]}
    assert shed_faults(turned) == ["the shed at (0, 20) is turned off its house"]


# ---- B1: a record lies on its own ink ---------------------------------------------------------------------


def water_ink(M: Mapping[str, Any]) -> Any:
    """The drawn water: every drawn channel and stream at its half-width plus a foot, and the reservoir's ellipse."""
    ink = [LineString(d["pts"]).buffer(max(float(d.get("w0") or 2), float(d.get("w1") or 2)) / 2 + 1) for d in M.get("drawn_channels") or [] if len(d.get("pts") or []) >= 2]
    ink += [LineString(s["poly"]).buffer(float(s.get("w") or 5) / 2 + 1) for s in M.get("streams") or [] if len(s.get("poly") or []) >= 2]
    pond = M.get("pond")
    if pond:
        ink.append(affinity.scale(Point(pond[0], pond[1]).buffer(1), pond[2] + 1, pond[3] + 1))
    return unary_union(ink)


def record_off_ink(M: Mapping[str, Any]) -> list[str]:
    """Where a record disagrees with its ink: a channel record's length off the drawn water beyond `RECORD_OFF_INK_FT`, a
    sluice gate or weir beyond `POINT_ON_WATER_FT` of it, a house standing on a marsh."""
    ftpx, water, out = _ftpx(M), water_ink(M), []
    for i, ch in enumerate(M.get("channels") or []):
        off = LineString(ch["poly"]).difference(water).length * ftpx
        if off > RECORD_OFF_INK_FT:
            out.append(f"channel {i} ({ch.get('frm', {}).get('kind')} -> {ch.get('to', {}).get('kind')}) runs {off:.1f} ft off its ink")
    for key in ("sluice_gates", "weirs"):
        for g in M.get(key) or []:
            gap = Point(g["x"], g["y"]).distance(water) * ftpx
            if gap > POINT_ON_WATER_FT:
                out.append(f"a {key[:-1]} at ({g['x']}, {g['y']}) stands {gap:.1f} ft off the water")
    marsh = unary_union([Polygon(m["poly"]).buffer(0) for m in M.get("marshes") or [] if len(m.get("poly") or []) >= 3])
    for h in M.get("houses") or []:
        if not marsh.is_empty and Point(h["x"], h["y"]).buffer(min(h["w"], h["h"]) / 2).intersects(marsh):
            out.append(f"a house at ({h['x']:.0f}, {h['y']:.0f}) stands on a marsh")
    return out


def test_a_record_off_its_ink_fires() -> None:
    """Seeded: the recorded cases - Kuwabata's feed record jogging off its stub (fixed here), a gate snapped 7 ft off."""
    M = {"drawn_channels": [{"pts": [[0, 0], [100, 0]], "w0": 2, "w1": 2}], "channels": [{"poly": [[0, 0], [100, 0]]}]}
    assert record_off_ink(M) == []
    M["channels"][0]["poly"] = [[0, 0], [50, 20], [100, 0]]
    assert record_off_ink(M) and "runs" in record_off_ink(M)[0]
    M["channels"] = []
    M["sluice_gates"] = [{"x": 50, "y": 9}]
    assert record_off_ink(M) == ["a sluice_gate at (50, 9) stands 7.0 ft off the water"]
    M2 = {"marshes": [{"poly": [[0, 0], [50, 0], [50, 50], [0, 50]]}], "houses": [{"x": 45, "y": 25, "w": 20, "h": 14}]}
    assert record_off_ink(M2) == ["a house at (45, 25) stands on a marsh"]


# ---- B10: what was rolled is drawn ----------------------------------------------------------------------


def undrawn_rolls(M: Mapping[str, Any]) -> list[str]:
    """Each roll the map declares and does not draw (the GM, 2026-08-24: a rolled knob is honored by what is drawn): a
    fixture kind short of its target or below its floor, the byres and retirement houses short of theirs, the settlement
    form drawn other than the one asked."""
    meta = M.get("meta") or {}
    drawn: dict[str, int] = {}
    for f in M.get("farm_fixtures") or []:
        drawn[f["kind"]] = drawn.get(f["kind"], 0) + 1
    drawn["persimmon"] = len(M.get("persimmons") or [])
    out = [f"{k}: {drawn.get(k, 0)} drawn of {n} rolled" for k, n in (meta.get("farm_fixtures_target") or {}).items() if drawn.get(k, 0) != n]
    out += [f"{k}: {drawn.get(k, 0)} drawn under its floor {n}" for k, n in (meta.get("farm_fixtures_min") or {}).items() if drawn.get(k, 0) < n]
    for key, rolled in (("byres", "byre_target"), ("retirement_houses", "retirement_target")):
        if meta.get(rolled) is not None and len(M.get(key) or []) != int(meta[rolled]):
            out.append(f"{key}: {len(M.get(key) or [])} drawn of {meta[rolled]} rolled")
    if meta.get("settlement_form_asked") and meta.get("settlement_form") != meta["settlement_form_asked"]:
        out.append(f"the settlement drawn {meta.get('settlement_form')}, asked {meta['settlement_form_asked']}")
    return out


def test_a_roll_drawn_short_fires() -> None:
    """Seeded: Kuwabata's recorded case - three households seated bare (privy 11 of 14, its household shrine 0 of 1)."""
    M = {"meta": {"farm_fixtures_target": {"privy": 14, "shrine": 1}, "farm_fixtures_min": {"shrine": 1}}, "farm_fixtures": [{"kind": "privy"}] * 11}
    assert undrawn_rolls(M) == ["privy: 11 drawn of 14 rolled", "shrine: 0 drawn of 1 rolled", "shrine: 0 drawn under its floor 1"]
    assert undrawn_rolls({"meta": {"byre_target": 2, "settlement_form": "dispersed", "settlement_form_asked": "nucleated"}, "byres": [{}]}) == [
        "byres: 1 drawn of 2 rolled",
        "the settlement drawn dispersed, asked nucleated",
    ]


# ---- B9: what is drawn is the size that was rolled -------------------------------------------------------


def drawn_off_roll(meta: Mapping[str, Any]) -> list[str]:
    """Every `meta` pair `{rolled, drawn}` whose drawn size is more than `DRAWN_TO_ROLLED` off its roll."""
    out = []
    for key, v in meta.items():
        if isinstance(v, Mapping) and {"rolled", "drawn"} <= set(v) and float(v["rolled"]) > 0:
            share = float(v["drawn"]) / float(v["rolled"])
            if abs(share - 1.0) > DRAWN_TO_ROLLED:
                out.append(f"{key}: drawn {v['drawn']} against {v['rolled']} rolled ({share:.0%})")
    return out


def test_a_size_drawn_off_its_roll_fires() -> None:
    """Seeded: Sawada's recorded case before feature 294, its homesteads' wood drawn at 60% of its roll."""
    assert drawn_off_roll({"homestead_wood_ft2": {"rolled": 17692, "drawn": 10672}}) == ["homestead_wood_ft2: drawn 10672 against 17692 rolled (60%)"]
    assert drawn_off_roll({"homestead_wood_ft2": {"rolled": 10109, "drawn": 10106}, "view": [0, 0, 1, 1]}) == []


# ---- B7: a lane's tread stands clear of a house wall ------------------------------------------------------


def treads_near_walls(M: Mapping[str, Any], clear_ft: float) -> list[str]:
    """Every lane whose tread EDGE comes within `clear_ft` of a farmhouse wall (the house's raked rectangle), found through one
    STRtree over the houses."""
    from l7r.diagram.settlement._geom import rot_rect

    ftpx = _ftpx(M)
    houses = [Polygon(rot_rect(h["x"], h["y"], h["w"], h["h"], float(h.get("rot") or 0.0))) for h in M.get("houses") or []]
    tree = STRtree(houses)
    out = []
    for i, ln in enumerate(M.get("lanes") or []):
        if len(ln.get("pts") or []) < 2:
            continue
        tread = LineString(ln["pts"])
        half = float(ln.get("w") or 3.0) / 2.0
        for j in tree.query(tread.buffer(half + clear_ft / ftpx)):
            gap = (tread.distance(houses[int(j)]) - half) * ftpx
            if gap < clear_ft:
                out.append(f"lane {i}'s tread runs {gap:.2f} ft from a house wall")
    return out


def test_a_tread_beside_a_wall_fires() -> None:
    """Seeded: the recorded case (feature 155), a tread 3.85 ft from a farmhouse wall."""
    M = {"houses": [{"x": 0.0, "y": 0.0, "w": 40.0, "h": 20.0, "rot": 0.0}], "lanes": [{"pts": [[-50.0, 15.35], [50.0, 15.35]], "w": 3.0}]}
    assert treads_near_walls(M, 4.0) == ["lane 0's tread runs 3.85 ft from a house wall"]
    M["lanes"][0]["pts"] = [[-50.0, 20.0], [50.0, 20.0]]
    assert treads_near_walls(M, 4.0) == []


# ---- the shipped hamlets ----------------------------------------------------------------------------------


@pytest.mark.parametrize("gen", _HAMLETS, ids=os.path.basename)
def test_the_shipped_hamlets_keep_the_rules_the_review_used_to_judge(gen: str) -> None:
    from l7r.diagram.hamletgen.ways import law

    M = _manifest(gen)
    meta = M.get("meta") or {}
    assert bridges_too_close(M.get("bridges") or [], _ftpx(M)) == [], "B8: two footbridges side by side"
    if meta.get("house_bearing_deg") is not None:
        assert bearing_faults(M.get("houses") or [], float(meta["house_bearing_deg"])) == [], "B11: house bearings"
    for stream in M.get("streams") or []:
        assert brook_pieces_in_view(stream, meta["view"]) <= 1, "B12: the brook leaves and re-enters the view"
    assert shed_faults(M) == [], "B3: wood shed seating"
    assert record_off_ink(M) == [], "B1: a record off its ink"
    assert undrawn_rolls(M) == [], "B10: a roll drawn short"
    assert drawn_off_roll(meta) == [], "B9: a size drawn off its roll"
    from l7r.diagram.settlement.houses import TREAD_WALL_FT

    assert treads_near_walls(M, TREAD_WALL_FT) == [], "B7: a tread beside a wall"
    from l7r.diagram.waterfields.twins import twins

    courses = [d["pts"] for d in M.get("drawn_channels") or [] if len(d.get("pts") or []) >= 2] + [s["poly"] for s in M.get("streams") or [] if len(s.get("poly") or []) >= 2]
    assert twins(courses, _ftpx(M)) == [], "B4: two watercourses side by side (the comb's own predicate, waterfields/twins.py)"
    from l7r.diagram.tools.see_through import broadleaf_over_conifer, crowns_in_paint_order
    from tests.gate import _pool

    with open(_pool.obtain(gen)[: -len(".json")] + ".svg", encoding="utf-8") as fh:
        crowns = crowns_in_paint_order(fh.read())
    assert crowns, "non-vacuity: the map's crowns were read off its ink"
    assert broadleaf_over_conifer(crowns) == [], "B5b: a broadleaf crown painted over a conifer"
    # B13: the lane law the placer guarantees, proved on what shipped
    assert law.needle_ends(M.get("lanes") or []) == [], "B13: a needle join"
    assert law.needle_loops(M) == [], "B13: a needle loop"
    assert law.lanes_that_kink(M) == [], "B13: a lane that doubles back or kinks"


# ---- B6: a class answers the pointer over its own ink ----------------------------------------------------


def hit_thefts(found: Mapping[str, tuple[float, str | None, int]], declared: frozenset[str]) -> list[str]:
    """Each class answering the pointer over less than `HIT_SHARE_FLOOR` of its own visible ink, where what answers instead is
    not one of the `declared` widened boxes (`interactive/page.HIT_WIDEN`: a thin mark's fat hit copy is meant to win the area
    fill beneath it, the GM's 2026-08-28 ruling)."""
    return [f"{k}: {share:.0%} of its {n} px, {thief} answers" for k, (share, thief, n) in found.items() if n >= HIT_MIN_PIXELS and share < HIT_SHARE_FLOOR and thief not in declared]


def test_a_region_taking_another_class_s_ink_fires() -> None:
    """Seeded: the recorded cases' shape - a lifted region over a pig sty (88%), a sluice box winning 42% of its own."""
    from l7r.diagram.interactive.page import HIT_WIDEN

    declared = frozenset(HIT_WIDEN)
    assert hit_thefts({"pig sty": (0.12, "pond sluice", 400), "paddy": (0.4, "bund", 9000), "edge": (0.1, "x", 3)}, declared) == ["pig sty: 12% of its 400 px, pond sluice answers"]


@pytest.mark.renders
@pytest.mark.parametrize("gen", _HAMLETS, ids=os.path.basename)
def test_every_class_answers_the_pointer_over_its_own_ink(gen: str) -> None:
    from l7r.diagram.interactive.page import HIT_WIDEN
    from l7r.diagram.pipeline import gencache
    from l7r.diagram.tools import hit_share
    from tests.gate import _pool

    _pool.obtain(gen)
    page = gencache.page_of(gen)  # the pool's page, or the vector page a skip-render roll filed (feature 294)
    assert page, "non-vacuity: the map's page is on disk or filed with its entry"
    with open(page, encoding="utf-8") as fh:
        svg = hit_share.page_svg(fh.read())
    assert svg, "non-vacuity: the page carries its map"
    found = hit_share.shares(svg)
    if found is None:
        pytest.skip("no resvg on this host")
    assert len(found) > 10, "non-vacuity: the classes on the map were measured"
    assert hit_thefts(found, frozenset(HIT_WIDEN)) == [], "B6: a class's ink answers as another"


# ---- B5: a see-through mark is declared, with its reason --------------------------------------------------


def undeclared_see_through(found: Mapping[str, float], table: Mapping[str, tuple[float, str]]) -> list[str]:
    """Each class drawn see-through that `table` does not declare, or drawn fainter than the floor it declares."""
    out = []
    for key, faintest in sorted(found.items()):
        if key not in table:
            out.append(f"{key}: drawn at {faintest} and declared nowhere")
        elif faintest < table[key][0] - 1e-6:
            out.append(f"{key}: drawn at {faintest}, under its declared {table[key][0]}")
    return out


def test_an_undeclared_see_through_mark_fires() -> None:
    """Seeded: the recorded cases - a field grave's mound at 0.9, the title placard at 0.94."""
    from l7r.diagram.settlement.see_through import SEE_THROUGH

    assert undeclared_see_through({"field grave": 0.9, "well": 0.55, "byre": 0.3}, SEE_THROUGH) == [
        "byre: drawn at 0.3, under its declared 0.6",
        "field grave: drawn at 0.9 and declared nowhere",
    ]


@pytest.mark.parametrize("gen", _HAMLETS, ids=os.path.basename)
def test_every_see_through_mark_is_declared(gen: str) -> None:
    from l7r.diagram.pipeline import gencache
    from l7r.diagram.settlement.see_through import SEE_THROUGH
    from l7r.diagram.tools import hit_share
    from l7r.diagram.tools.see_through import translucent_marks
    from tests.gate import _pool

    _pool.obtain(gen)
    page = gencache.page_of(gen)
    assert page, "non-vacuity: the map's page is on disk or filed with its entry"
    with open(page, encoding="utf-8") as fh:
        found = translucent_marks(hit_share.page_svg(fh.read()) or "")
    assert found, "non-vacuity: every map draws some mark see-through (the water's sheen at least)"
    assert undeclared_see_through(found, SEE_THROUGH) == [], "B5: a see-through mark nobody declared"


# ---- B2: a marsh's visible free edge is not ruled ----------------------------------------------------------

MARSH_AXIS_RUN_FT = 150.0  # GUESS (plan D11): a waved edge is level for a moment at each crest; the recorded ruled limits ran 450-590 ft


@pytest.mark.renders
@pytest.mark.parametrize("gen", _HAMLETS, ids=os.path.basename)
def test_no_marsh_meets_open_ground_on_a_ruled_line(gen: str) -> None:
    """B2: the brook's own straight-run rule (W03: `RULED_SHARE` of the visible edge once it is `RULED_MIN_LEN_FT`, at
    `RULED_TOL_FT`) and an axis-aligned stretch under `MARSH_AXIS_RUN_FT`, over each marsh's VISIBLE free edge
    (`tools/marsh_edges.py`; its unit tests carry the seeded ruled strip)."""
    from l7r.diagram.hamletgen.water.brook_rules import AXIS_EPS_DEG, RULED_MIN_LEN_FT, RULED_SHARE, RULED_TOL_FT
    from l7r.diagram.pipeline import gencache
    from l7r.diagram.tools import hit_share, marsh_edges

    M = _manifest(gen)
    rings = [m["poly"] for m in M.get("marshes") or [] if len(m.get("poly") or []) >= 3]
    page = gencache.page_of(gen)
    assert page and rings, "non-vacuity: every shipped hamlet draws a marsh, and its page is on disk or filed"
    with open(page, encoding="utf-8") as fh:
        runs = marsh_edges.free_runs(hit_share.page_svg(fh.read()) or "", rings, _ftpx(M))
    if runs is None:
        pytest.skip("no resvg on this host")
    rules = {"tol": RULED_TOL_FT, "share": RULED_SHARE, "min_len": RULED_MIN_LEN_FT, "eps_deg": AXIS_EPS_DEG, "axis_run": MARSH_AXIS_RUN_FT}
    assert [f for r in runs for f in marsh_edges.ruled_edges(r, _ftpx(M), rules)] == [], "B2: a marsh meets the open ground on a ruled line"


# ---- B15: every map folder carries its notes --------------------------------------------------------------


def folders_without_notes(root: str) -> list[str]:
    """Every map or sheet folder of both pool trees with no non-empty `<name>.notes.md`."""
    out = []
    for tree in ("pool", "legacy-hand-authored-pool"):
        for d in sorted(glob.glob(os.path.join(root, tree, "*", "*"))):
            name = os.path.basename(d)
            if not os.path.isdir(d) or not any(os.path.isfile(os.path.join(d, f"{name}{ext}")) for ext in (".gen.py", ".json", ".svg")):
                continue
            notes = os.path.join(d, f"{name}.notes.md")
            if not os.path.isfile(notes) or not pathlib.Path(notes).read_text(encoding="utf-8").strip():
                out.append(name)
    return out


def test_a_map_folder_with_no_notes_fires(tmp_path: Any) -> None:
    d = tmp_path / "pool" / "hamlets" / "bare"
    d.mkdir(parents=True)
    (d / "bare.gen.py").write_text("")
    assert folders_without_notes(str(tmp_path)) == ["bare"]
    (d / "bare.notes.md").write_text("# bare\n")
    assert folders_without_notes(str(tmp_path)) == []


def test_every_pool_and_legacy_map_folder_carries_its_notes() -> None:
    assert folders_without_notes(_SKILL) == []
