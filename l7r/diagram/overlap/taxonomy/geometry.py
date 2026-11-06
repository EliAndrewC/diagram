"""The overlap taxonomy's geometry: the manifest's types, its loader, and the polygon and gap measures every matrix verdict reads
(was the top and the tail of `overlap/taxonomy.py`, split as a package at 1,000 lines - feature 444, the Rust stage gate's seed 802010).

Research: geometry and bookkeeping - NONE: types, loaders and polygon measures
"""

import json
import math
from collections.abc import Callable, Mapping, Sequence
from typing import Any

from l7r.diagram.settlement import _assert_not_main_tree, sat_overlap
from l7r.diagram.settlement._geom.primitives import convex_hull as convex_hull  # re-exported: the hull lives in the geometry package since feature 140

_assert_not_main_tree(__file__)  # standalone gate runs must also happen in a session clone, never in main (CLAUDE.md "Session clones"; settlement's own import-time guard backstops this)

Manifest = dict[str, Any]  # the JSON settlement manifest the generator emits

Pt = Sequence[float]  # an (x, y) point (list from JSON, or a tuple)

Poly = Sequence[Sequence[float]]  # a polyline / polygon

Check = Callable[..., None]  # the check(name, passed, message) sink passed into the check functions


def load(path: str) -> Manifest:
    with open(path) as f:
        result: Manifest = json.load(f)
        return result


def rect_corners(h: dict[str, Any]) -> list[tuple[float, float]]:
    a = math.radians(h["rot"])
    ca, sa = math.cos(a), math.sin(a)
    w, ht = h["w"], h["h"]
    return [(h["x"] + dx * ca - dy * sa, h["y"] + dx * sa + dy * ca) for dx, dy in [(-w / 2, -ht / 2), (w / 2, -ht / 2), (w / 2, ht / 2), (-w / 2, ht / 2)]]


def _struct_rect(s: dict[str, Any]) -> dict[str, Any]:
    """Normalize a solid footprint feature to a rect for the overlap tests. Every solid feature now
    carries w/h(/rot). A LOCATION MARKER (a feature whose true footprint is sub-glyph, so it draws
    at a legibility floor - the kosatsuba; see Settlement.kosatsuba) also carries vw/vh, the box it
    actually occupies on the map: overlap is about DRAWN pixels colliding, so the marker's visual
    box is what the checks must clear, exactly as the wells' clearance uses `vr` over `r`."""
    return {"x": s["x"], "y": s["y"], "w": s.get("vw", s["w"]), "h": s.get("vh", s["h"]), "rot": s.get("rot", 0)}


def _box_hits_poly(box: tuple[float, float, float, float], poly: Poly) -> bool:
    """Whether an axis-aligned box (x0,y0,x1,y1) overlaps a polygon (corner-in, vertex-in, or edge-cross)."""
    x0, y0, x1, y1 = box
    bc = [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]
    n = len(poly)
    return (
        any(point_in_poly(cx, cy, poly) for cx, cy in bc)
        or any(x0 <= vx <= x1 and y0 <= vy <= y1 for vx, vy in poly)
        or any(segments_cross(bc[e], bc[(e + 1) % 4], poly[k], poly[(k + 1) % n]) for e in range(4) for k in range(n))
    )


def poly_area(pts: Poly) -> float:
    """Absolute polygon area (shoelace) of a list of (x, y) vertices."""
    n = len(pts)
    s = 0.0
    for i in range(n):
        x0, y0 = pts[i]
        x1, y1 = pts[(i + 1) % n]
        s += x0 * y1 - x1 * y0
    return abs(s) / 2.0


# ---- overlap classification registry ---------------------------------------------------------------
# Every footprint feature (a manifest key holding a list of dicts with positional geometry) must be
# classified below. The DEFAULT is "must not overlap anything": a SOLID feature joins `structs`, which
# the no_structure_* checks clear against each other and against the walls / water / roads / fields it
# should not sit on. Overlaps are OPT-IN - a feature that is meant to overlap something (a label, a
# bridge over water, a guard tower on the wall) is named in _OVERLAP_EXEMPT with its reason. The
# `every_feature_classified_for_overlap` check fires when a NEW feature key appears in none of these
# sets, forcing whoever adds it to declare its overlap behavior rather than silently skipping it.


def _mx_rect(o: Mapping[str, Any]) -> list[tuple[float, float]]:
    """A record's DRAWN box: `vw`/`vh` where a marker draws above its true size, else w/h."""
    hw = float(o.get("vw", o.get("w", 0))) / 2
    hh = float(o.get("vh", o.get("h", 0))) / 2
    th = math.radians(float(o.get("rot") or 0.0))
    c, s_ = math.cos(th), math.sin(th)
    return [(o["x"] + dx * c - dy * s_, o["y"] + dx * s_ + dy * c) for dx, dy in ((-hw, -hh), (hw, -hh), (hw, hh), (-hw, hh))]


def _mx_stroke(pts: Sequence[Any], hw: float) -> list[list[tuple[float, float]]]:
    """One quad per segment of a linear feature at its TRUE half-width - never the ink width, since a
    hairline stroke floor draws a 1 ft ditch 4 px wide and that slop must not manufacture a defect."""
    quads: list[list[tuple[float, float]]] = []
    for i in range(len(pts) - 1):
        ax, ay = float(pts[i][0]), float(pts[i][1])
        bx, by = float(pts[i + 1][0]), float(pts[i + 1][1])
        ln = math.hypot(bx - ax, by - ay) or 1.0
        nx, ny = -(by - ay) / ln * hw, (bx - ax) / ln * hw
        quads.append([(ax + nx, ay + ny), (bx + nx, by + ny), (bx - nx, by - ny), (ax - nx, ay - ny)])
    return quads


# a fixture's DRAWN box, in its own record's vocabulary (see matrix_extents)
_MX_FIXTURE_BOX: dict[str, Any] = {
    "bridges": lambda o: (float(o["span"]), float(o["w"])),  # the deck: span along the way, deck width across
    "jetties": lambda o: (float(o["len"]), 6.4),  # the planked finger, at the width the glyph draws
    "sluice_gates": lambda o: (float(o.get("span") or 10.8), 8.4),  # post to post across the channel (bank to bank where a span is recorded), the beam and drum to the posts along it
    "weirs": lambda o: (float(o["len"]), float(o["w"])),  # the oblique bar: its length across the brook, its thickness along it
    "washing_places": lambda o: (float(o["w"]), float(o["h"])),  # the footing: its width along the bank, its depth down it
}
"""Research: drawn fixture box - NONE: mirrors each glyph's drawn size"""

_MX_LINE_W = {"streams": 9.0, "channels": 2.5, "field_ditches": 1.5, "canals": 14.0, "town_streets": 20.0, "alleys": 6.0, "lanes": 6.0, "roads": 26.0, "towpaths": 2.4, "aqueducts": 4.0, "quays": 3.4}
"""Research: fallback line widths - NONE: used only where a record carries no width"""


def seg_closest(px: float, py: float, a: Pt, b: Pt) -> tuple[float, float]:
    ax, ay = a
    bx, by = b
    dx, dy = bx - ax, by - ay
    if dx == dy == 0:
        return ax, ay
    t = max(0, min(1, ((px - ax) * dx + (py - ay) * dy) / (dx * dx + dy * dy)))
    return ax + t * dx, ay + t * dy


def seg_dist(px: float, py: float, a: Pt, b: Pt) -> float:
    cx, cy = seg_closest(px, py, a, b)
    return math.hypot(px - cx, py - cy)


# the 2 patron fortunes of each Great Clan - a town defaults to one monastery for each
# The recognized justifications for a city carrying MORE than two major temples
# (research/contents.json#religion-and-the-dead). A fixed vocabulary rather than free text: the doctrine
# enumerates the exceptions, so an unrecognized reason must FAIL rather than pass by virtue of
# being non-empty - otherwise the declaration stops meaning anything and becomes a rubber stamp.
#   large         - an especially large city
#   pious         - a pilgrimage destination (the monzen-machi inversion)
#   changed_hands - kept the old ruler's temple after passing between clans (Tango)
#   fox_structure - the Fox seven-temple structure: many modest precincts, each an economic house
#                   holding forest usufruct, rather than two great complexes (Minami; l7r.md
#                   "Fox Temples", research/contents.json#religion-and-the-dead)
TEMPLE_EXCEPTIONS = {"large", "pious", "changed_hands", "fox_structure"}
"""Research: temple exceptions - research/questions/0234-how-many-temples-a-city-keeps-and-its-temple-quarter-teramachi.drawing.html: more than two only for a declared reason"""

CLAN_FORTUNES = {
    "crab": {"Bishamon", "Ebisu"},
    "crane": {"Benten", "Daikoku"},
    "dragon": {"Hotei", "Ebisu"},
    "lion": {"Bishamon", "Daikoku"},
    "phoenix": {"Fukurokujin", "Hotei"},
    "scorpion": {"Benten", "Jurojin"},
    "unicorn": {"Fukurokujin", "Jurojin"},
}
"""Research: patron Fortunes - research/questions/0228-town-monasteries.drawing.html: one monastery for each of the clan's two"""


def segments_cross(a: Pt, b: Pt, c: Pt, d: Pt) -> bool:
    def ccw(p: Pt, q: Pt, r: Pt) -> bool:
        return (r[1] - p[1]) * (q[0] - p[0]) > (q[1] - p[1]) * (r[0] - p[0])

    return ccw(a, c, d) != ccw(b, c, d) and ccw(a, b, c) != ccw(a, b, d)


def seg_intersect(a: Pt, b: Pt, c: Pt, d: Pt) -> tuple[float, float] | None:
    """The (x, y) where SEGMENTS ab and cd cross, or None if they do not (parallel, or apart).

    BOUNDED ON BOTH SEGMENTS (feature 276, a defect found while profiling the track stage). This returned the
    intersection of the two infinite LINES for any non-parallel pair, under a docstring asking callers to "call
    only when they cross" - and seven callers did not: `path_violations`' brook, double-bridge, shallow-crossing
    and crop-landing tests counted a path segment against every non-parallel water segment on the map (Inashiro's
    candidate paths scored 3,847 to 8,773 "violations" with no real crossing among them), a cluster's way-crossing
    finder and its spur trim met ways that never touched, and a homestead's brook-cut test counted a brook it did not
    cross. A caller that checked `segments_cross` first gets the same point as before."""
    den = (a[0] - b[0]) * (c[1] - d[1]) - (a[1] - b[1]) * (c[0] - d[0])
    if abs(den) < 1e-9:
        return None
    t = ((a[0] - c[0]) * (c[1] - d[1]) - (a[1] - c[1]) * (c[0] - d[0])) / den
    u = -((a[0] - b[0]) * (a[1] - c[1]) - (a[1] - b[1]) * (a[0] - c[0])) / den
    if not (0.0 <= t <= 1.0 and 0.0 <= u <= 1.0):
        return None
    return (a[0] + t * (b[0] - a[0]), a[1] + t * (b[1] - a[1]))


def point_in_poly(px: float, py: float, poly: Any) -> bool:
    inside = False
    n = len(poly)
    j = n - 1
    for i in range(n):
        xi, yi = poly[i]
        xj, yj = poly[j]
        if ((yi > py) != (yj > py)) and (px < (xj - xi) * (py - yi) / (yj - yi + 1e-9) + xi):
            inside = not inside
        j = i
    return inside


def poly_dist(px: float, py: float, poly: Poly) -> float:
    if point_in_poly(px, py, poly):
        return 0.0
    return min(seg_dist(px, py, poly[i], poly[(i + 1) % len(poly)]) for i in range(len(poly)))


def edge_gap(a: Mapping[str, Any], b: Mapping[str, Any]) -> float:
    """The TRUE gap in px between two rotated footprints - the distance you could measure on the
    ground between the nearest points of two buildings. 0.0 if they overlap or touch.

    THE ONE MEASUREMENT ANY GAP VERDICT USES (GM, 2026-07-26). Before this there were THREE
    conventions in the file for the same question, and all three were wrong in different ways:

      - raw center-to-center (`math.hypot(a["x"] - b["x"], ...)`) understates the real clearance by
        the sum of both half-extents, so a rule promising 120 ft delivered as little as ~60 at town
        scale. Two live defects shipped this way: an execution ground and a boundary stone both
        sited inside the line they were supposed to be outside of.
      - the circumscribed radius (`0.5 * math.hypot(w, h)`) is the half-DIAGONAL, which exceeds the
        true half-extent by up to 41% on a square and more on an elongated rect;
      - `max(w, h) / 2` is the same error, differently sized.

    And the approximations' error FLIPS SIGN with the rule: subtracting too much makes a
    "must be far" rule strict and a "must be near" rule lenient, so they cannot even be reasoned
    about as a uniform safety margin. Since the closest pair of two convex polygons is always a
    vertex of one against an edge of the other, the exact answer costs a few `poly_dist` calls -
    there was never a reason to approximate it.

    Centers remain correct for CLASSIFICATION ("which ward is this in" - a building belongs to one
    ward, not 0.6 of one), for ASSOCIATION/REACH whose tolerance dwarfs the footprints, and for
    PREFILTERS. See the dev-loop doc, "Centers, footprints, and aggregates"."""
    da, db = _gap_disc(a), _gap_disc(b)
    if da is not None and db is not None:
        return max(0.0, math.hypot(da[0] - db[0], da[1] - db[1]) - da[2] - db[2])
    if da is not None:
        return max(0.0, poly_dist(da[0], da[1], rect_corners(_struct_rect(dict(b)))) - da[2])
    if db is not None:
        return max(0.0, poly_dist(db[0], db[1], rect_corners(_struct_rect(dict(a)))) - db[2])
    ca, cb = rect_corners(_struct_rect(dict(a))), rect_corners(_struct_rect(dict(b)))
    if sat_overlap(ca, cb):
        return 0.0
    return min(min(poly_dist(px, py, cb) for px, py in ca), min(poly_dist(px, py, ca) for px, py in cb))


def _gap_disc(o: Mapping[str, Any]) -> tuple[float, float, float] | None:
    """(x, y, radius) if this feature is drawn as a DISC rather than a rect, else None.

    A wellhead is the case: it records `r` (clearance) and `vr` (the drawn head) and carries no
    w/h at all, so treating every feature as a rect is not merely imprecise here, it raises
    KeyError. Found the hard way on 2026-07-27, and the way it was found is worth more than the
    bug: a crashing gate prints no FAIL lines, so a pool scan that greps for FAIL read the crash
    as CLEAN - the file's own "a check that never RUNS looks exactly like a check that passes",
    committed by the person who had just written it down. Scan for the exit code, not for FAIL.

    `vr` over `r` for the same reason `_struct_rect` prefers vw/vh: a clearance rule is about the
    ink on the map, and the drawn head is what a reader sees."""
    if "w" in o:
        return None
    return float(o["x"]), float(o["y"]), float(o.get("vr", o.get("r", 0.0)))


def _gap_reach(o: Mapping[str, Any]) -> float:
    """A circumscribed radius for the pair prefilter - deliberately generous (see within_edge_gap)."""
    d = _gap_disc(o)
    return d[2] if d is not None else math.hypot(o.get("vw", o["w"]), o.get("vh", o["h"])) / 2


def within_edge_gap(a: Mapping[str, Any], b: Mapping[str, Any], lim: float) -> bool:
    """Is the true gap between two footprints at most `lim` px? Center-distance prefiltered, so a
    check may ask it of every pair on a city without the exact test running on all of them - the
    index-prunes-never-decides rule applied to a pair test. The prefilter uses circumscribed radii
    deliberately: over-estimating an extent can only admit a pair the exact test then rejects."""
    if math.hypot(a["x"] - b["x"], a["y"] - b["y"]) > lim + _gap_reach(a) + _gap_reach(b):
        return False
    return edge_gap(a, b) <= lim
