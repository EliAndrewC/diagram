"""Coordinate math on points, segments and rings - no map vocabulary in here at all.

Everything above this layer is built from these: a distance, a containment, a crossing, an
intersection. Nothing here reads a manifest or knows what a paddy is.

Split from settlement/_geom.py by feature 117 - see settlement/_geom/CLAUDE.md for the index.
"""

import math
from collections.abc import Sequence

from .base import Poly, Pt

FIELD_KEEPOUT_EPS = (
    3.0  # px: a field outline's chords may stray this far from it; the keep-out is pushed out by it (feature 140; 3 keeps the reference's lane web whole where 4-8 broke it - research R3)
)


def _signed_area(poly: Poly) -> float:
    a = 0.0
    n = len(poly)
    for i in range(n):
        x1, y1 = poly[i]
        x2, y2 = poly[(i + 1) % n]
        a += x1 * y2 - x2 * y1
    return a / 2


def point_in_poly(px: float, py: float, poly: Poly) -> bool:
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


def seg_closest(px: float, py: float, a: Pt, b: Pt) -> Pt:
    ax, ay, bx, by = a[0], a[1], b[0], b[1]
    dx, dy = bx - ax, by - ay
    if dx == dy == 0:
        return ax, ay
    t = max(0, min(1, ((px - ax) * dx + (py - ay) * dy) / (dx * dx + dy * dy)))
    return ax + t * dx, ay + t * dy


def seg_dist(px: float, py: float, a: Pt, b: Pt) -> float:
    cx, cy = seg_closest(px, py, a, b)
    return math.hypot(px - cx, py - cy)


def ring_meets_ellipse(ring: Sequence[Sequence[float]], cx: float, cy: float, rx: float, ry: float) -> bool:
    """Does any edge of the closed `ring` cross this ellipse's rim or run inside it - a bund through a field pond?

    THE ONE PREDICATE of the field pond's rule (feature 287, FR-003, water W29): `_plot_pond` shrinks a pond until no
    ring meets it, and `waterfields/ring_rules.crosses_pond_rim` - the finished-map test's call - is this function.
    They used to disagree: the placer asked `seg_in_ellipse_core`, a core shrunk 3 px inside the rim, while the test
    failed any ring with one vertex inside the full ellipse and the next outside. So the placer could let a bund cut
    the pond's outer 3 px and the test fail it, and the test could pass a bund chording the pond between two outside
    vertices that the placer, reading the core, would have refused.

    WHICH READING, AND WHY (the test's, as the water design W29 records). The research makes the pond "a low pocket"
    among the flat, flooded fields (`research/fields.html`, "In-field features"); the rule drawn from it is that the
    pocket is dug INTO one basin with the field tiling around it, because a bund running through open water reads as
    a flood rather than a pocket (the rule's own statement, `test_a_field_pond_is_sunk_into_one_plot`). A bund meeting
    the water at all - across the rim, chording it, or standing in it - is that flood, so the full ellipse is the
    rule and the 3 px inset was a placement tolerance that let the placer pass what the rule forbids. Exact: each
    edge's closest approach to the center, measured in the scaled space where the ellipse is the unit circle. A ring
    that only TOUCHES the rim (closest approach exactly 1) does not meet it."""
    n = len(ring)
    for i in range(n):
        ax, ay = (float(ring[i][0]) - cx) / rx, (float(ring[i][1]) - cy) / ry
        bx, by = (float(ring[(i + 1) % n][0]) - cx) / rx, (float(ring[(i + 1) % n][1]) - cy) / ry
        dx, dy = bx - ax, by - ay
        t = max(0.0, min(1.0, -(ax * dx + ay * dy) / max(1e-12, dx * dx + dy * dy)))
        if math.hypot(ax + t * dx, ay + t * dy) < 1.0:
            return True
    return False


def ring_touches(cx: float, cy: float, r: float, ring: Poly) -> bool:
    """Does a disc of radius r at (cx, cy) lap this ring - inside it, or within r of an edge?"""
    return point_in_poly(cx, cy, ring) or any(seg_dist(cx, cy, ring[i], ring[(i + 1) % len(ring)]) < r for i in range(len(ring)))


#                             fits INSIDE the empty court with air on both sides: at 11pt
#                             "Governor's Mansion" measures 123px in the render font against the
#                             145px-wide mansions of Tango and Nagahara, i.e. ~11px (~33 real ft)
#                             off each wall. At 14 it measured 157px and would not fit at all.


def segments_cross(a: Pt, b: Pt, c: Pt, d: Pt) -> bool:
    def ccw(p: Pt, q: Pt, r: Pt) -> bool:
        return (r[1] - p[1]) * (q[0] - p[0]) > (q[1] - p[1]) * (r[0] - p[0])

    return ccw(a, c, d) != ccw(b, c, d) and ccw(a, b, c) != ccw(a, b, d)


def seg_intersect(a: Pt, b: Pt, c: Pt, d: Pt) -> Pt | None:
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


def poly_seg_dist(poly: Poly, a: Pt, b: Pt, closed: bool = True) -> float:
    """Least distance between the segment `a`-`b` and a polygon (or an open polyline, `closed=False`),
    ZERO when the two actually MEET - the segment crossing an edge, or lying wholly inside a closed
    polygon.

    THE ZERO IS THE POINT (feature 233). A distance that cannot return zero reports an overlap as a
    narrow gap, and that is not hypothetical: this defect's first two measurements scored a shed with a
    culvert running through it at 0.13 ft, because they sampled the footprint's boundary and took the
    nearest sample with no intersection test. A clearance predicate built that way would have passed
    the very map it was written to fix. `specs/233-pigsty-clear-of-the-sluice/research.md` R1 records
    both measurements and how each understated; `measure_geom.py` beside it is the checked reference.
    """
    n = len(poly)
    best = math.inf
    for i in range(n if closed else n - 1):
        p, q = poly[i], poly[(i + 1) % n]
        if segments_cross(p, q, a, b):
            return 0.0
        best = min(best, seg_dist(a[0], a[1], p, q), seg_dist(b[0], b[1], p, q), seg_dist(p[0], p[1], a, b), seg_dist(q[0], q[1], a, b))
    # a segment wholly inside a closed polygon crosses no edge, so `segments_cross` alone cannot see it
    if closed and (point_in_poly(a[0], a[1], poly) or point_in_poly(b[0], b[1], poly)):
        return 0.0
    return best


def edge_dist(px: float, py: float, poly: Poly) -> float:
    return min(seg_dist(px, py, poly[i], poly[(i + 1) % len(poly)]) for i in range(len(poly)))


def convex_hull(pts: Sequence[Pt]) -> Poly:
    """Convex hull (monotone chain) of a point cloud, as a CCW vertex list. <3 unique points returns them
    as-is (a degenerate hull of zero area)."""
    ps = sorted(set((round(x, 3), round(y, 3)) for x, y in pts))
    if len(ps) < 3:
        return [(x, y) for x, y in ps]

    def cross(o: Pt, a: Pt, b: Pt) -> float:
        return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])

    lower: list[Pt] = []
    for p in ps:
        while len(lower) >= 2 and cross(lower[-2], lower[-1], p) <= 0:
            lower.pop()
        lower.append(p)
    upper: list[Pt] = []
    for p in reversed(ps):
        while len(upper) >= 2 and cross(upper[-2], upper[-1], p) <= 0:
            upper.pop()
        upper.append(p)
    return lower[:-1] + upper[:-1]


def ring_offset(ring: Sequence[Pt], out: float, inward: float) -> Poly:
    """A coarse keep-out around a closed centerline: each vertex pushed `out` along the outward normal (away
    from the centroid) and `inward` the other way, joined as one ring of 2n vertices (feature 140: the polder
    dike's 2,880-vertex smoothed band is replaced, for PLACEMENT only, by this ring around its crest)."""
    n = len(ring)
    # OUTWARD BY WINDING, never by a centroid test: in a concave pocket the edge that faces the centroid is the one
    # whose outward normal points AT it, and a centroid test turned that edge inside out (one chord vertex of a
    # wobbly test ring escaped its own keep-out). The ring's signed area fixes the orientation once.
    ccw = _signed_area(list(ring)) > 0
    outer: Poly = []
    inner: Poly = []

    def edge_normal(a: Pt, b: Pt) -> Pt:
        ex, ey = b[0] - a[0], b[1] - a[1]
        el = math.hypot(ex, ey) or 1.0
        return (ey / el, -ex / el) if ccw else (-ey / el, ex / el)

    for i in range(n):
        a, b, c = ring[(i - 1) % n], ring[i], ring[(i + 1) % n]
        n1, n2 = edge_normal(a, b), edge_normal(b, c)
        # MITERED: a band offset edge by edge reaches `out / cos(half the turn)` from a convex vertex, not
        # `out` - a vertex-normal ring fell 63 vertices short of the drawn band on a wobbly test ring.
        mx, my = n1[0] + n2[0], n1[1] + n2[1]
        ml = math.hypot(mx, my)
        if ml < 1e-9:  # a hairpin: fall back to the first edge's normal
            mx, my, ml = n1[0], n1[1], 1.0
        mx, my = mx / ml, my / ml
        # OUTWARD the miter is what makes the ring contain an edge-offset band (out / cos(half the turn)), capped at
        # 4x for a near-hairpin; INWARD a miter FOLDS the ring over itself at a reflex corner, so the inner edge uses
        # the plain vertex normal and the caller adds tolerance instead (`keepout_ring`).
        scale = 1.0 / max(0.25, mx * n1[0] + my * n1[1])
        outer.append((b[0] + mx * out * scale, b[1] + my * out * scale))
        inner.append((b[0] - mx * inward * min(scale, 1.5), b[1] - my * inward * min(scale, 1.5)))  # a gentler miter inward: enough for a drawn crest's corners, short of a fold
    # CLOSE THE ANNULUS THROUGH THE FIRST VERTEX: outer 0..n-1, back to outer 0, across to inner 0, inner n-1..0 - the
    # version that jumped from outer n-1 straight to inner n-1 left the LAST chord's sector out of the polygon, and
    # every containment escape in the tests sat in that sector.
    return [*outer, outer[0], inner[0], *reversed(inner)]


def simplify_ring(pts: Sequence[Pt], eps: float) -> Poly:
    """Douglas-Peucker on a CLOSED ring: the ring split at its two farthest-apart vertices, each half
    simplified so no dropped vertex lies farther than `eps` from the chord that replaces it. A 49-73-vertex
    field outline comes back as eight to sixteen chords that follow its bays (feature 140, GM 2026-08-28:
    *"three connected line segments ... maybe five or six ... just a few line segments running along the
    edge of the fields"*)."""
    ring = [(float(x), float(y)) for x, y in pts]
    n = len(ring)
    if n <= 4:
        return ring
    i0 = 0
    i1 = max(range(n), key=lambda j: math.hypot(ring[j][0] - ring[0][0], ring[j][1] - ring[0][1]))
    i0 = max(range(n), key=lambda j: math.hypot(ring[j][0] - ring[i1][0], ring[j][1] - ring[i1][1]))
    if i0 > i1:
        i0, i1 = i1, i0

    def dp(chain: list[Pt]) -> list[Pt]:
        if len(chain) <= 2:
            return list(chain)
        a, b = chain[0], chain[-1]
        far, fd = 0, -1.0
        for k in range(1, len(chain) - 1):
            d = seg_dist(chain[k][0], chain[k][1], a, b)
            if d > fd:
                far, fd = k, d
        if fd <= eps:
            return [a, b]
        left = dp(chain[: far + 1])
        right = dp(chain[far:])
        return left[:-1] + right

    first = dp(ring[i0 : i1 + 1])
    second = dp(ring[i1:] + ring[: i0 + 1])
    return first[:-1] + second[:-1]


def keepout_ring(chain: Sequence[Pt], covered: Sequence[Pt], eps: float, filled: bool = False) -> tuple[Poly, Poly]:
    """`(keepout, chords)`: `chain` simplified to a few chords, then pushed out on each side by as far as any
    point of `covered` lies from those chords (measured, not assumed) plus `eps` - so the keep-out CONTAINS
    every covered point by construction. For a field, `chain` and `covered` are both the outline (the
    keep-out is the outline's chords plus the simplification tolerance); for a dike, `chain` is the crest and
    `covered` the drawn band.

    AT MOST `KEEPOUT_CHORD_CAP` CHORDS (feature 287, homes H27; the GM's "a couple of dozen"): the simplification's
    tolerance grows by half again until the chain takes no more - containment is untouched, because the push is the
    MEASURED reach of every covered point from whatever chords result."""
    tol = eps
    chords = simplify_ring(chain, tol)
    while not filled and len(chords) > KEEPOUT_CHORD_CAP:  # the dike's band; a field is held by its facing chains' cap
        tol *= 1.5
        chords = simplify_ring(chain, tol)
    n = len(chords)
    if n < 3:
        return list(chords), list(chords)
    out_reach = in_reach = 0.0
    for x, y in covered:
        d = min(seg_dist(x, y, chords[i], chords[(i + 1) % n]) for i in range(n))
        if point_in_poly(x, y, chords):
            in_reach = max(in_reach, d)
        else:
            out_reach = max(out_reach, d)
    if filled:
        # A FIELD blocks its whole interior, so its keep-out is the outward offset alone - and the annulus's seam
        # (where the outer and inner rings join) is a zero-width slit that a chord vertex can land ON and be read as
        # outside; a filled ring has no seam.
        return ring_offset(chords, out_reach + eps, 0.0)[: len(chords)], chords
    # the inner edge is un-mitered (see ring_offset), so it starts with extra tolerance - AND IS THEN HELD TO CONTAIN THE BAND
    # (feature 287, homes wave 5): the tolerance was a heuristic, so the ring is asked of every covered point
    # (`point_in_poly`, the containment test's own reading) and the side a point escapes on is pushed a further `eps` until
    # none escapes. Each push only moves that edge away from the chords, so a point once inside stays inside.
    out_pad, in_pad = out_reach + eps, in_reach + eps * 3.0
    for _ in range(KEEPOUT_GROWTHS):
        keep = ring_offset(chords, out_pad, in_pad)
        escaped = [p for p in covered if not point_in_poly(p[0], p[1], keep)]
        if not escaped:
            return keep, chords
        inside = [point_in_poly(p[0], p[1], chords) for p in escaped]
        in_pad += eps if any(inside) else 0.0
        out_pad += eps if not all(inside) else 0.0
    raise ValueError(f"no keep-out of {n} chords contains its band within {KEEPOUT_GROWTHS} pushes of {eps}")


#: How many `eps` pushes `keepout_ring` gives a band's keep-out to contain it before refusing the band by name: far past what a
#: drawn dike's band ever asked (a band `w` wide about its crest needs no more than `w / eps`).
KEEPOUT_GROWTHS = 200


Chord = tuple[Pt, Pt, Pt]  # (a, b, outward normal): a pushed-out chord of a field outline and the side the houses are on


#: The most chords a dike's keep-out ring may have (homes H27): the GM's "a couple of dozen".
KEEPOUT_CHORD_CAP = 24
#: The most chords a field's facing chains may have (homes H27): half the ring's cap, since the chains are one side of it.
FACING_CHORD_CAP = 12


def facing_chains(outline: Sequence[Pt], seat: Pt, eps: float) -> list[list[Chord]]:
    """`_facing_chains` held to `FACING_CHORD_CAP` chords (feature 287, homes H27): where the outline simplifies to more,
    the tolerance - and with it the push that keeps the drawn outline behind every chord - grows by half again until
    the chains take no more. A cap reached only by a triangle's chains always holds."""
    tol = eps
    chains = _facing_chains(outline, seat, tol)
    while sum(len(c) for c in chains) > FACING_CHORD_CAP:
        tol *= 1.5
        chains = _facing_chains(outline, seat, tol)
    return chains


def _facing_chains(outline: Sequence[Pt], seat: Pt, eps: float) -> list[list[Chord]]:
    """THE OPEN CHAINS ON THE HOUSE SIDE (feature 140, GM 2026-08-28: *"just a few line segments on one side of
    the field that you are checking that you are on the correct side of ... not forming a closed shape"*):
    the outline simplified to chords, keeping only the runs of chords whose outward normal points toward
    `seat` (the planned cluster), each chord pushed out by `eps` along that normal so no part of the drawn
    outline lies on the house side of it. One open chain per run, each chord carrying its outward normal -
    the reference hamlet's field gives 5 chords / 6 vertices."""
    chords = simplify_ring(outline, eps)
    n = len(chords)
    if n < 3:
        return []
    ccw = _signed_area(list(chords)) > 0
    normals: list[Pt] = []
    faces: list[bool] = []
    for i in range(n):
        a, b = chords[i], chords[(i + 1) % n]
        ex, ey = b[0] - a[0], b[1] - a[1]
        el = math.hypot(ex, ey) or 1.0
        nx, ny = (ey / el, -ex / el) if ccw else (-ey / el, ex / el)  # outward by the ring's winding (see ring_offset)
        mx, my = (a[0] + b[0]) / 2, (a[1] + b[1]) / 2
        normals.append((nx, ny))
        faces.append(nx * (seat[0] - mx) + ny * (seat[1] - my) > 0)
    if not any(faces):
        return []
    # TWO GUARDS STOOD HERE AND BOTH WERE DEAD (removed with their proof, feature 146). An `if all(faces)`
    # arm handled a seat that faces EVERY edge, and an `if cur` after the loop handled a run still open at
    # the end. Neither can happen, and not by luck: the outward half-planes of a CLOSED ring have empty
    # intersection, so no seat is on the outward side of every edge (40,000 random 3-to-5-gons found none);
    # and the walk starts at a non-facing edge and ends on that same edge, so an open run is always flushed
    # by the `elif` on the last step. `next()` raising is the right answer if the geometry ever says
    # otherwise - a silent default would hand back a chain nothing verified.
    start = next(i for i in range(n) if not faces[i])
    runs = []
    cur: list[int] = []
    for k in range(1, n + 1):
        i = (start + k) % n
        if faces[i]:
            cur.append(i)
        elif cur:
            runs.append(cur)
            cur = []
    out: list[list[Chord]] = []
    for run in runs:
        chain: list[Chord] = []
        for i in run:
            a, b = chords[i], chords[(i + 1) % n]
            nx, ny = normals[i]
            chain.append(((a[0] + nx * eps, a[1] + ny * eps), (b[0] + nx * eps, b[1] + ny * eps), (nx, ny)))
        out.append(chain)
    return out


def chain_violated(px: float, py: float, chains: Sequence[Sequence[Chord]], gap: float) -> bool:
    """Is (px, py) on the field side of a chord it projects onto, or nearer than `gap` to a chord? The
    signed distance runs along the chord's outward normal, so the field side is negative - a point deep
    in the field fails by sign, a point too near the edge fails by distance; beyond a chord's ends only
    the distance to the end counts (the next chord, if any, projects it)."""
    for chain in chains:
        for (ax, ay), (bx, by), (nx, ny) in chain:
            ex, ey = bx - ax, by - ay
            el2 = ex * ex + ey * ey
            if el2 <= 1e-12:
                continue
            t = ((px - ax) * ex + (py - ay) * ey) / el2
            if 0.0 <= t <= 1.0:
                if (px - ax) * nx + (py - ay) * ny < gap:
                    return True
            else:
                qx, qy = (ax, ay) if t < 0.0 else (bx, by)
                if math.hypot(px - qx, py - qy) < gap:
                    return True
    return False


def chain_distance(px: float, py: float, chains: Sequence[Sequence[Chord]]) -> float:
    """The distance from (px, py) to the nearest chord (unsigned)."""
    best = float("inf")
    for chain in chains:
        for a, b, _n in chain:
            best = min(best, seg_dist(px, py, a, b))
    return best
