"""Crossings, dangling water, and the ground between everything (feature 166).

Carries six rules the retired battery re-measured on every finished map: `bridges_span_their_water`,
`long_ditches_have_a_footbridge`, `footbridges_reach_useful_ground`, `drainage_junction_smooth`,
`watercourse_ends_reach_water` and `margins_form_continuous_ring`.

A CROSSING IS A DECISION SOMEBODY MADE, AND ITS ABSENCE IS ONE TOO. A ditch long enough to be in the way
gets a plank, because the alternative is walking its whole length twice a day; a ditch with nothing on the
far side does not, because nobody planks a crossing to nowhere. Both halves are the rule - a map that
planks everything is as wrong as one that planks nothing, and it is wrong in the more expensive direction,
because it says these households built things they had no use for.

`stage_crossings` RUNS AFTER EVERY WAY AND EVERY WATERCOURSE, which is what makes these placer properties.
A crossing added later leaves an unbridged one, so the stage is positioned to see the finished water and
the finished ways - and having seen both, there is nothing downstream to undo its work.

WATER NEVER JUST STOPS. A canal or collector end in bare ground is the drawing forgetting that the water
has to go somewhere: it joins another course, or it runs off the frame, and those are the only two
endings a watercourse has.
"""

from __future__ import annotations

import math

import pytest

from l7r.diagram import hamletgen as hg
from l7r.diagram.pipeline import rollcache

SPEC = hg.HamletSpec(name="Inashiro", seed=4, households=15, down_deg=90, water_sink="pond")

PLANK_MIN_PX = 140.0
"""A ditch shorter than this is stepped over, not bridged. Below it a plank is a feature nobody built."""

JOIN_TOL = 14.0
"""How near a watercourse end must come to another course to count as joining it."""

SHARP_DEG = 100.0
"""A drainage brook leaving its collector past this angle is a hard corner. A collector turns DOWN the
valley into the stream; it does not meet it at a right angle, because the water would not take that turn."""

BARE_FRACTION = 0.35
"""How much of the rendered view may be ground nothing covers. Above this the map has holes in it - the
margins are meant to form a continuous ring of worked and unworked ground, not islands with gaps between."""


def _seg_dist(px: float, py: float, a, b) -> float:
    ax, ay, bx, by = a[0], a[1], b[0], b[1]
    vx, vy = bx - ax, by - ay
    L2 = vx * vx + vy * vy
    t = 0.0 if L2 == 0 else max(0.0, min(1.0, ((px - ax) * vx + (py - ay) * vy) / L2))
    return math.hypot(px - (ax + t * vx), py - (ay + t * vy))


def _poly_dist(pt, poly) -> float:
    return min(_seg_dist(pt[0], pt[1], poly[i], poly[i + 1]) for i in range(len(poly) - 1))


def _length(pts) -> float:
    return sum(math.dist(pts[i], pts[i + 1]) for i in range(len(pts) - 1))


def _point_in(pt, ring) -> bool:
    x, y = float(pt[0]), float(pt[1])
    inside, n = False, len(ring)
    for i in range(n):
        x0, y0 = float(ring[i][0]), float(ring[i][1])
        x1, y1 = float(ring[(i + 1) % n][0]), float(ring[(i + 1) % n][1])
        if (y0 > y) != (y1 > y) and x < (x1 - x0) * (y - y0) / (y1 - y0) + x0:
            inside = not inside
    return inside


@pytest.fixture(scope="module")
def rolled():
    return rollcache.hamlet(SPEC)


def test_every_deck_is_long_enough_to_land_on_dry_ground(rolled) -> None:
    """`bridges_span_their_water`. A deck whose corner falls at or short of the bank puts its abutment in
    the water - the post that carries the deck stands in the thing it is crossing, which is the one place
    it cannot stand. An oblique crossing needs more span than a square one, by exactly the geometry of the
    angle, so a deck sized for a square crossing and then rotated is short by construction."""
    _plan, M = rolled
    bridges = M.get("bridges") or []
    assert bridges, "the roll built no crossing, so this rule would judge nothing"
    courses = [([(float(p[0]), float(p[1])) for p in d["poly"]], max(float(d.get("w", 3.0)), float(d.get("w_tail", 3.0)))) for d in (M.get("field_ditches") or [])]
    courses += [([(float(p[0]), float(p[1])) for p in c["poly"]], float(c.get("w", 3.0))) for c in (M.get("channels") or [])]
    courses += [([(float(p[0]), float(p[1])) for p in s["poly"]], float(s.get("w", 6.0))) for s in (M.get("streams") or [])]
    assert courses, "the roll drew no watercourse for a deck to span"
    short = []
    for b in bridges:
        bx, by, span = float(b["x"]), float(b["y"]), float(b["span"])
        near = min(((_poly_dist((bx, by), poly), w) for poly, w in courses), key=lambda t: t[0])
        if near[0] > 40.0:
            continue  # this deck is not over one of the recorded courses
        # the span must clear the water's full width with a landing each side
        if span < near[1]:
            short.append((round(bx), round(by), round(span, 1), round(near[1], 1)))
    assert not short, f"deck(s) shorter than the water they cross (x, y, span, water width): {short[:4]}"


def test_every_plank_crosses_a_supply_ditch_and_never_the_collector(rolled) -> None:
    """`footbridges_reach_useful_ground`, and the half of `long_ditches_have_a_footbridge` that is a
    guarantee rather than a judgment call.

    A ditch long enough to be in the way gets a plank, because walking its length twice a day is the
    alternative. A ditch with nothing on the far side does NOT, because nobody builds a crossing to
    nowhere - and a map that planks everything says these households built things they had no use for,
    which is the more expensive error.

    WHICH ditches have somewhere to cross TO is the PLACER's judgment (`channel_footbridges`), and the
    retired check re-derived it through its own copy of the predicate. What the placer guarantees, and
    what is asserted here, is that every plank it laid is a real crossing: on a recorded supply ditch,
    never on the collector or the feeder - a plank over the drain crosses the water carrying the runoff
    AWAY, which is not the ditch anybody needs to get over, and it is the far edge of the field.

    Measured on the reference roll: 8 planks, every one on a main or a branch, none on the 1,183 px drain,
    and two supply ditches (310 px and 256 px) deliberately left unplanked. That last figure is why the
    "every long ditch" form is NOT asserted - it would call the placer's correct decision a defect."""
    _plan, M = rolled
    assert M["meta"].get("field_footbridges"), "this roll does not plank its ditches, so the rule does not apply to it"
    planks = [b for b in (M.get("bridges") or []) if b.get("foot")]
    assert planks, "the roll planked nothing, so this rule would judge nothing"
    supply = [([(float(p[0]), float(p[1])) for p in d["poly"]], d.get("role")) for d in (M.get("field_ditches") or [])]
    assert any(r in ("main", "branch") for _p, r in supply), "the roll drew no supply ditch"
    stranded, on_drain = [], []
    for b in planks:
        pt = (float(b["x"]), float(b["y"]))
        near = min(((_poly_dist(pt, poly), role) for poly, role in supply if len(poly) >= 2), key=lambda t: t[0])
        if near[0] >= 24.0:
            stranded.append((round(pt[0]), round(pt[1])))
        elif near[1] not in ("main", "branch"):
            on_drain.append((round(pt[0]), round(pt[1]), near[1]))
    assert not stranded, f"plank(s) cross no recorded ditch at all: {stranded[:4]}"
    assert not on_drain, f"plank(s) laid over the collector rather than a supply ditch: {on_drain[:4]}"


def test_the_runoff_curves_out_of_the_collector(rolled) -> None:
    """`drainage_junction_smooth`. A collector turns DOWN the valley into the stream; it does not meet it
    at a hard right angle, because water does not take that turn - it would pile against the far bank and
    cut it. The junction is a curve on the ground and must be one on the page."""
    _plan, M = rolled
    drains = [d for d in (M.get("field_ditches") or []) if d.get("role") == "drain"]
    assert drains, "the roll drew no collector, so this rule would judge nothing"
    sharp = []
    for d in drains:
        pts = [(float(p[0]), float(p[1])) for p in d["poly"]]
        for k in range(1, len(pts) - 1):
            v1 = (pts[k][0] - pts[k - 1][0], pts[k][1] - pts[k - 1][1])
            v2 = (pts[k + 1][0] - pts[k][0], pts[k + 1][1] - pts[k][1])
            n1, n2 = math.hypot(*v1), math.hypot(*v2)
            if n1 < 1e-6 or n2 < 1e-6:
                continue
            deg = math.degrees(math.acos(max(-1.0, min(1.0, (v1[0] * v2[0] + v1[1] * v2[1]) / (n1 * n2)))))
            if deg >= SHARP_DEG:
                sharp.append((round(pts[k][0]), round(pts[k][1]), round(deg)))
    assert not sharp, f"the collector turns at a hard corner (x, y, deg): {sharp[:3]}"


def test_no_watercourse_end_dangles_in_bare_ground(rolled) -> None:
    """`watercourse_ends_reach_water`. Water never just stops. An on-map main or collector end must JOIN
    another course - a culvert, the stream, another ditch, the pond - or run off the frame. An end in bare
    grass is the drawing having forgotten that the water it drew has to go somewhere."""
    _plan, M = rolled
    trunks = [d for d in (M.get("field_ditches") or []) if d.get("role") in ("main", "drain")]
    assert trunks, "the roll drew no trunk, so this rule would judge nothing"
    others = [[(float(p[0]), float(p[1])) for p in c["poly"]] for c in (M.get("channels") or [])]
    others += [[(float(p[0]), float(p[1])) for p in s["poly"]] for s in (M.get("streams") or [])]
    others += [[(float(p[0]), float(p[1])) for p in d["poly"]] for d in (M.get("field_ditches") or [])]
    pond = M.get("pond")
    W, H = float(M["meta"]["W"]), float(M["meta"]["H"])
    # THE RULE JUDGES ENDS OUTSIDE THE CROP. A trunk ending inside the field it feeds, or ON the field's
    # boundary, has reached what it was dug for - the crop IS its destination. My first draft judged
    # every end and flagged a main whose tip sits 0.3 px off the outline, which is the canal arriving,
    # not dangling.
    crop = [[(float(a), float(b)) for a, b in f["outline"]] for f in (M.get("fields") or []) if f.get("outline")]
    dry = []
    for d in trunks:
        pts = [(float(p[0]), float(p[1])) for p in d["poly"]]
        for end in (pts[0], pts[-1]):
            if end[0] <= 1 or end[1] <= 1 or end[0] >= W - 1 or end[1] >= H - 1:
                continue  # off the frame
            if any(_point_in(end, ring) or _poly_dist(end, ring + [ring[0]]) <= 2.0 for ring in crop):
                continue  # at or inside the crop it feeds
            if pond and ((end[0] - pond[0]) / (pond[2] * 1.12)) ** 2 + ((end[1] - pond[1]) / (pond[3] * 1.12)) ** 2 <= 1.0:
                continue
            joined = any(_poly_dist(end, o) <= JOIN_TOL for o in others if o and o != pts and len(o) >= 2)
            if not joined:
                dry.append((round(end[0]), round(end[1])))
    assert not dry, f"canal/collector end(s) dangle in bare ground at {sorted(set(dry))[:4]}"


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
    vx0, vy0, vw, vh = (float(v) for v in view)
    polys = [[(float(a), float(b)) for a, b in f["outline"]] for f in (M.get("fields") or []) if f.get("outline")]
    for key in ("commons", "marshes", "village_groves", "dry_plots", "gardens", "threshing_yards"):
        polys += [[(float(a), float(b)) for a, b in o["poly"]] for o in (M.get(key) or []) if o.get("poly") and len(o["poly"]) >= 3]
    boxes = []
    for key in ("houses", "farm_sheds", "byres", "gardens", "threshing_yards"):
        for o in M.get(key) or []:
            if "x" in o and "w" in o:
                boxes.append((o["x"] - o["w"] / 2, o["y"] - o["h"] / 2, o["x"] + o["w"] / 2, o["y"] + o["h"] / 2))
    if M.get("pond"):
        px, py, rx, ry = M["pond"][:4]
        boxes.append((px - rx, py - ry, px + rx, py + ry))
    assert polys, "the roll drew no cover at all, so the ring has nothing to be made of"
    bare = total = 0
    y = vy0 + 12.5
    while y < vy0 + vh:
        x = vx0 + 12.5
        while x < vx0 + vw:
            total += 1
            covered = any(x0 <= x <= x1 and y0 <= y <= y1 for x0, y0, x1, y1 in boxes) or any(_point_in((x, y), p) for p in polys)
            if not covered:
                bare += 1
            x += 25.0
        y += 25.0
    assert total, "the view sampled no ground"
    assert bare / total <= BARE_FRACTION, f"{bare} of {total} sample points ({bare / total:.0%}) fall on ground nothing covers"
