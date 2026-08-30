"""The ground cover a rolled hamlet must produce (feature 166).

Carries six rules the retired battery re-measured on every finished map: `woodland_commons_on_dry_ground`,
`woodland_commons_visibly_stocked`, `woodland_commons_within_the_frame`, `village_groves_visibly_stocked`,
`copse_stands_clear_of_the_belt` and `canopy_clear_of_watercourses`.

A DECLARED FEATURE THE MAP DOES NOT DRAW IS THE FAILURE MOST OF THESE GUARD, and it is worse than a
missing feature. A commons parcel recording `role=woodland` with no crowns reads green to every other
grove rule while the dooryards it should have shaded stay bare - the record says wood, the page says
grass, and each rule downstream believes the record. So "it was drawn" is itself the assertion, stated
as a stocking density rather than as a boolean, because a parcel with two trees in it is not a wood.

THE PHYSICAL RULES ARE SIMPLER THAN THE RECORD-KEEPING ONES. Trees do not grow in a stream; a wood does
not stand in a marsh; a dooryard copse standing inside the windbreak's canopy is not a second stand of
trees but the same trees drawn twice. Each is a fact about the world rather than about the drawing, and
each has a placer that already knows it.
"""

from __future__ import annotations

import math

import pytest

from l7r.diagram import hamletgen as hg
from l7r.diagram.pipeline import rollcache

SPEC = hg.HamletSpec(name="Inashiro", seed=4, households=15, down_deg=90, water_sink="pond")

MIN_CROWNS = 5
"""Under five crowns a stand does not read as a wood at fit zoom - it reads as a few trees on grass."""

MIN_CLUMP_DENSITY = 1.5
"""Clumps per 100k square pixels. Below this the grove is a declared outline with almost nothing in it."""

FRAME_FRACTION = 0.7
"""How much of a woodland parcel's box must fall inside the rendered view. A commons may run off the
frame like any other countryside; what it may not do is be seated mostly outside the picture, because
then the map declares a wood the reader cannot see."""


def _seg_dist(px: float, py: float, a, b) -> float:
    ax, ay, bx, by = a[0], a[1], b[0], b[1]
    vx, vy = bx - ax, by - ay
    L2 = vx * vx + vy * vy
    t = 0.0 if L2 == 0 else max(0.0, min(1.0, ((px - ax) * vx + (py - ay) * vy) / L2))
    return math.hypot(px - (ax + t * vx), py - (ay + t * vy))


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


@pytest.fixture(scope="module")
def woodland(rolled):
    _plan, M = rolled
    parcels = [c for c in (M.get("commons") or []) if c.get("role") == "woodland" and c.get("poly")]
    assert parcels, "the roll seated no woodland commons, so every woodland rule would pass on nothing"
    return M, parcels


def test_a_woodland_commons_is_visibly_stocked(woodland) -> None:
    """`woodland_commons_visibly_stocked`. A parcel claiming a woodland must draw one and record its
    crowns. This is the record-keeping half of the rule and the reason it exists: without it a parcel
    reads as a wood to every other rule while the page shows bare ground."""
    _M, parcels = woodland
    bare = [(round(float(c.get("x", 0))), round(float(c.get("y", 0))), c.get("crowns")) for c in parcels if c.get("crowns") is None or int(c["crowns"]) < MIN_CROWNS]
    assert not bare, f"{len(bare)} woodland parcel(s) record no canopy (center, crowns; None = unrecorded): {bare[:4]}"


def test_a_woodland_commons_stands_on_dry_ground(woodland) -> None:
    """`woodland_commons_on_dry_ground`. A managed wood - the coppice a village cuts fuel and leaf-fodder
    from - is not a swamp forest. Standing water rots the stools, the cut cannot be carried out, and the
    species that make a satoyama coppice are not the species that grow in a marsh. Where the map has laid
    marsh, the wood goes somewhere else."""
    M, parcels = woodland
    marshes = [[(float(v[0]), float(v[1])) for v in (m.get("poly") or [])] for m in (M.get("marshes") or [])]
    marshes = [m for m in marshes if len(m) >= 3]
    assert marshes, "the roll laid no marsh, so this rule would judge nothing"
    wet = []
    for c in parcels:
        xs = [float(p[0]) for p in c["poly"]]
        ys = [float(p[1]) for p in c["poly"]]
        soaked = 0
        for i in range(5):
            for j in range(5):
                x = min(xs) + (max(xs) - min(xs)) * (i + 0.5) / 5
                y = min(ys) + (max(ys) - min(ys)) * (j + 0.5) / 5
                if any(_point_in((x, y), m) for m in marshes):
                    soaked += 1
        if soaked > 12:  # more than half the parcel's sample grid standing in water
            wet.append((round(float(c.get("x", 0))), round(float(c.get("y", 0))), soaked))
    assert not wet, f"woodland commons parcel(s) seated in marsh: {wet[:4]}"


def test_a_woodland_commons_is_mostly_inside_the_picture(woodland) -> None:
    """`woodland_commons_within_the_frame`. Countryside may run off the frame - that is what countryside
    does - but a parcel seated mostly outside the rendered view declares a wood the reader cannot see, and
    the sheet then shows a village whose fuel supply is off the page."""
    M, parcels = woodland
    view = M["meta"].get("view")
    assert view, "the roll records no view, so 'inside the picture' has no meaning"
    vx0, vy0, vw, vh = (float(v) for v in view)
    vx1, vy1 = vx0 + vw, vy0 + vh
    outside = []
    for c in parcels:
        xs = [float(p[0]) for p in c["poly"]]
        ys = [float(p[1]) for p in c["poly"]]
        box = max(1e-9, (max(xs) - min(xs)) * (max(ys) - min(ys)))
        inter = max(0.0, min(max(xs), vx1) - max(min(xs), vx0)) * max(0.0, min(max(ys), vy1) - max(min(ys), vy0))
        if inter / box < FRAME_FRACTION:
            outside.append((round(float(c.get("x", 0))), round(float(c.get("y", 0))), round(100 * inter / box)))
    assert not outside, f"woodland parcel(s) seated mostly outside the view (center, % inside): {outside[:4]}"


def test_every_recorded_grove_holds_trees(rolled) -> None:
    """`village_groves_visibly_stocked`. The same failure as the woodland rule, one feature over: a grove
    that DECLARES an outline and draws almost nothing in it leaves the dooryards it should have greened
    bare while every other grove rule reads green."""
    _plan, M = rolled
    groves = [g for g in (M.get("village_groves") or []) if float(g.get("w") or 0) * float(g.get("h") or 0) > 0]
    assert groves, "the roll recorded no grove, so this rule would judge nothing"
    bare = []
    for g in groves:
        area = float(g["w"]) * float(g["h"])
        n = len(g.get("clumps") or [])
        dens = n * 1e5 / area
        if dens < MIN_CLUMP_DENSITY:
            bare.append(f"{g.get('role') or 'grove'} {float(g['w']):.0f}x{float(g['h']):.0f}px holds {n} clump(s) ({dens:.2f}/100k)")
    assert not bare, f"{len(bare)} recorded grove(s) hold almost no trees: {bare[:3]}"


def test_a_dooryard_copse_stands_clear_of_the_windbreak(rolled) -> None:
    """`copse_stands_clear_of_the_belt`. A copse buried inside the windbreak's canopy is not a second
    stand of trees - it is the same trees drawn twice, and the map has spent a feature saying nothing. The
    copse is a dooryard feature and the belt is a field-edge one; they are different things standing in
    different places, so the one inside the other means a seat search that gave up."""
    _plan, M = rolled
    groves = M.get("village_groves") or []
    belts = [g for g in groves if g.get("role") in ("windbreak", "water_mouth")]
    copses = [g for g in groves if g.get("role") == "copse"]
    assert belts and copses, "the roll drew no belt or no copse, so this rule would judge nothing"
    buried = []
    for cp in copses:
        for cl in cp.get("clumps") or []:
            for b in belts:
                r = float(b.get("r") or 0.0)
                if any((float(cl[0]) - float(bc[0])) ** 2 + (float(cl[1]) - float(bc[1])) ** 2 < r * r for bc in (b.get("clumps") or [])):
                    buried.append((round(float(cl[0])), round(float(cl[1]))))
                    break
    assert not buried, f"{len(buried)} copse clump(s) stand INSIDE the windbreak's canopy at {buried[:4]}"


def test_no_canopy_stands_over_open_water(rolled) -> None:
    """`canopy_clear_of_watercourses`. Trees do not grow in a stream, a channel or a moat. A clump seated
    over open water is the scatter treating the watercourse as ground, and the reader sees a tree growing
    out of a canal."""
    _plan, M = rolled
    courses = [[(float(p[0]), float(p[1])) for p in c["poly"]] for c in (M.get("channels") or [])]
    courses += [[(float(p[0]), float(p[1])) for p in s["poly"]] for s in (M.get("streams") or [])]
    clumps = [(float(c[0]), float(c[1])) for g in (M.get("village_groves") or []) for c in (g.get("clumps") or [])]
    assert courses and clumps, "the roll drew no watercourse or no canopy, so this rule would judge nothing"
    wet = [(round(x), round(y)) for x, y in clumps if min(min(_seg_dist(x, y, p[i], p[i + 1]) for i in range(len(p) - 1)) for p in courses) < 4.0]
    assert not wet, f"grove canopy clump(s) stand over open water at {sorted(set(wet))[:4]}"
