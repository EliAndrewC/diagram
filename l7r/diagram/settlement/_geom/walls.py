"""Every wall on a settlement map, what closes a ward against one, and the arches that must stand
clear of one.

The torii members are here rather than with settlement/shrines_wells/torii.py deliberately: at
THIS level an arch has exactly one geometric rule - it may not stand in a wall - and both
predicates are computed from wall_runs(). The arch glyph, the avenue count, the stride and the
threshold all live in shrines_wells/torii.py and are untouched by this module.

Split from settlement/_geom.py by feature 117 - see settlement/_geom/CLAUDE.md for the index.

Research: wall geometry - NONE: wall runs, ward closure and box-against-run tests
"""

from typing import Any

from .base import Manifest, Poly
from .overlap import _rect_ring
from .primitives import seg_dist, segments_cross

"""Research: torii avenue pitch - research/questions/0220-shrine-gateways-and-the-approach-to-the-hall-torii-sando.drawing.html: 12 ft stride and threshold"""


def torii_glyph_dims(ftpx: float, span_ft: float = 16.0) -> tuple[float, float, float, float]:
    """The PLAN-VIEW arch's drawn sizes in px at `ftpx`: (half span, beam depth, post side, post offset).

    A torii seen from above is its top beam (the kasagi, about 1.4 ft wide) with its two posts beneath it
    (feature 268, D3). The beam is drawn true size with the stroke floor (the SKILL's stroke convention);
    the posts are MARKED as squares standing just proud of the beam, a map drawing convention - real posts
    (about 1.2 ft) sit hidden under it - so the bar reads as an arch and not a plank. The drawn depth is
    the post side: at 1, 2 and 3 ft/px that is 2.6 px beside a pitch of 12, 6 and 4 px, so neighbors at the
    pitch never touch (the elevation glyph it replaces was about 10 ft deep on paper and could not stand at
    a 12 ft pitch).

    Research:
        torii span - UNRESEARCHED: 16 ft default
        top beam width - UNRESEARCHED: 1.4 ft, floored at 1.9 px
        posts proud of the beam - CONVENTION: 1.35x the beam, squares beside the bar
        post set-in - UNRESEARCHED: posts at 12/19 of the beam's half-span (the kasagi's overhang)"""
    s2 = (span_ft / ftpx) / 2
    beam = max(1.4 / ftpx, 1.9)
    post = beam * 1.35
    return s2, beam, post, s2 * 12.0 / 19.0


def torii_halfbox(ftpx: float, span_ft: float = 16.0) -> tuple[float, float, float]:
    """True drawn half-extents (x half-width, y-up, y-down) of a `_torii` glyph at scale `ftpx`, plus a small
    stroke pad - used to FRAME torii (`content_view`) and to keep captions and neighbors off them. Follows
    `torii_glyph_dims`: the beam spans +/-s2 and the glyph's depth is its post side, centered on the seat."""
    s2, _beam, post, _p2 = torii_glyph_dims(ftpx, span_ft)
    pad = 2.0  # stroke half-width + a hair, so the frame never clips the vermilion
    return s2 + pad, post / 2 + pad, post / 2 + pad


# Urban building kinds a SAMURAI WARD refuses (Settlement.ward / Settlement.building): the commoner
# dwellings and commerce the fence exists to keep out (GM 2026-08-02, on Minami: laborer houses in
# the middle of the samurai neighborhood, on the samurai side of the fence). servant is deliberately
# absent - samurai households' live-in domestics lodge inside the ward, and the city gens interleave
# them on purpose. So is monk_house: a temple may legitimately stand inside the ward (Tango's
# Bishamon precinct - the warrior fortune beside the garrison quarter) and its clergy row belongs
# with its temple, held to it by the temple-neighborhood checks. The zoning rule this encodes:
# research/questions/0161-the-samurai-quarter-where-a-citys-samurai-live-and-how-many-bukechi.drawing.html.
WARD_BARRED_KINDS = frozenset({"laborer", "laborer_large", "merchant", "merchant_house", "merchant_large", "burakumin", "shop", "inn"})
"""Research: samurai ward keeps commoners out - research/questions/0161-the-samurai-quarter-where-a-citys-samurai-live-and-how-many-bukechi.drawing.html: laborers, merchants, shops, inns, burakumin barred"""


def wall_runs(M: Manifest) -> list[tuple[str, Poly, float]]:
    """Every WALL on a settlement map as (label, polyline, half-width px): the city rampart, each
    ward fence (plus the short wall-stroke caps where it abuts the rampart), and the perimeter of
    every walled compound - manor, governor's mansion, merchant estate, mausoleum. The half-widths
    are the DRAWN stroke half-widths (city_wall's 11 px rampart, ward's 5 px fence and 11 px cap,
    each compound's recorded wall_w), so the test is against the ink actually on the page."""
    runs: list[tuple[str, Poly, float]] = []
    ring = M.get("wall")
    if ring:
        pts: Poly = [(float(p[0]), float(p[1])) for p in ring]
        runs.append(("the city wall", pts + [pts[0]], 5.5))
    for wd in M.get("wards", []):
        runs.append((f"the {wd.get('name', 'ward')} ward fence", [(float(p[0]), float(p[1])) for p in wd["boundary"]], 2.5))
        for cap in wd.get("wall_caps", []):
            runs.append(("a ward fence wall-cap", [(float(p[0]), float(p[1])) for p in cap.get("pts", [])], 5.5))
    walled: list[tuple[str, Any]] = [(lbl, c) for lbl, key in (("a manor wall", "manors"), ("a merchant estate wall", "merchant_estates"), ("a mausoleum wall", "mausoleums")) for c in M.get(key, [])]
    if M.get("governor_mansion"):
        walled.append(("the governor's mansion wall", M["governor_mansion"]))
    for lbl, c in walled:
        if not all(k in c for k in ("x", "y", "w", "h")):
            continue  # a synthetic fixture compound recorded for some other check's sake carries no footprint to wall
        runs.append((lbl, _rect_ring(c["x"], c["y"], c["w"], c["h"], float(c.get("rot", 0) or 0)), float(c.get("wall_w", 2.0)) / 2))
    return [(lbl, p, half) for lbl, p, half in runs if len(p) >= 2]


def _box_hits_run(box: tuple[float, float, float, float], pts: Poly, half: float) -> bool:
    """Does an axis-aligned box (x0, y0, x1, y1) reach a polyline drawn `2 * half` px thick? The
    wall's stroke is a THICK line, so the box must clear its EDGE, not its centerline - and a run
    that merely ends inside the box (crossing no edge) counts too."""
    x0, y0, x1, y1 = box
    edges = (((x0, y0), (x1, y0)), ((x1, y0), (x1, y1)), ((x1, y1), (x0, y1)), ((x0, y1), (x0, y0)))
    for i in range(len(pts) - 1):
        a, b = (pts[i][0], pts[i][1]), (pts[i + 1][0], pts[i + 1][1])
        if x0 <= a[0] <= x1 and y0 <= a[1] <= y1:
            return True
        for e0, e1 in edges:
            if segments_cross(a, b, e0, e1):
                return True
            if min(seg_dist(a[0], a[1], e0, e1), seg_dist(b[0], b[1], e0, e1), seg_dist(e0[0], e0[1], a, b), seg_dist(e1[0], e1[1], a, b)) < half:
                return True
    return False


# ---------------------------------------------------------------------------------------------
# A TORII STANDS CLEAR OF EVERY WALL (GM 2026-07-25, caught on Nagahara: the seventh arch of the
# Ebisu sando stood in the samurai ward fence). WHY: a torii is a FREESTANDING gateway - two posts
# in open ground that carry no load and close nothing, marking the threshold of sacred ground. A
# wall is its opposite: a continuous barrier whose whole purpose is that you cannot walk through
# it. So an arch drawn ON a wall run is impossible construction twice over - the posts stand inside
# the palisade, and the "gateway" opens onto a barrier. Where a way genuinely pierces a wall the
# opening is a GATE STRUCTURE (the city gate, a ward kido), never an arch. A torii over an ordinary
# street or lane stays legitimate: a sando arch spans its road, and a road is not a barrier.
#
# The rule is enforced from BOTH ends, because either feature may be drawn first (see CLAUDE.md
# "DRAW ORDER"): _torii refuses a seat standing in a wall already drawn (and shrine_hall shortens
# its avenue to fit rather than fail), while every wall-drawing method re-asks the question once
# its own run is on the page. check_village's torii_clear_of_walls is the manifest-level backstop,
# and all three read the SAME wall_runs() / torii_wall_conflicts() in this module.


def torii_seat_on_wall(M: Manifest, tx: float, ty: float, ftpx: float, runs: list[tuple[str, Poly, float]] | None = None) -> str | None:
    """The label of the wall an arch seated at (tx, ty) would stand in, or None if it stands clear.
    Asked of ONE candidate seat before it is drawn; `runs` caches wall_runs(M) across a sweep. The
    arch's extent is torii_halfbox - the same true-scale glyph box the crop and frame checks use.

    Research: torii stands clear of every wall - UNRESEARCHED: an arch's box may not reach a wall run"""
    txh, tyu, tyd = torii_halfbox(ftpx)
    for lbl, pts, half in wall_runs(M) if runs is None else runs:
        if _box_hits_run((tx - txh, ty - tyu, tx + txh, ty + tyd), pts, half):
            return lbl
    return None
