"""Coordinate math on points, segments and rings - no map vocabulary in here at all.

Everything above this layer is built from these: a distance, a containment, a crossing, an
intersection. Nothing here reads a manifest or knows what a paddy is.

Split from settlement/_geom.py by feature 117 - see settlement/_geom/CLAUDE.md for the index.
"""

import math
from collections.abc import Sequence

from .base import Poly, Pt

FIELD_KEEPOUT_EPS = (
    3.0  # px: a field outline's chords may stray this far from it; the keep-out is pushed out by it (feature 139; 3 keeps the reference's lane web whole where 4-8 broke it - research R3)
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


def seg_in_ellipse_core(a: Pt, b: Pt, cx: float, cy: float, rx: float, ry: float, inset: float = 4.0) -> bool:
    """Does segment a-b pass through the CORE of this ellipse - the water inside its rim?

    The shared predicate of the feature-012 field pond's containment rule: `_plot_pond` (placement)
    and `field_ponds_sunk_into_one_plot` (the verdict) both call this one function, so the siter and
    the check cannot disagree - the same discipline as `paddy_wet_rings` in extents.py. The core is the
    ellipse shrunk by `inset` px (rim stroke + reed fringe): a bund may TOUCH the shore - the host
    plot's own ring does - but a bund running through open water means the pond spans plots.
    Computed in the scaled space where the core is the unit circle, so one segment-to-center
    distance answers it for any ellipse."""
    crx, cry = max(1.0, rx - inset), max(1.0, ry - inset)
    ax, ay = (float(a[0]) - cx) / crx, (float(a[1]) - cy) / cry
    bx, by = (float(b[0]) - cx) / crx, (float(b[1]) - cy) / cry
    dx, dy = bx - ax, by - ay
    t = max(0.0, min(1.0, -(ax * dx + ay * dy) / max(1e-12, dx * dx + dy * dy)))
    return math.hypot(ax + t * dx, ay + t * dy) < 1.0


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
    """The (x, y) where segments ab and cd cross, or None if parallel. Call only when they cross."""
    den = (a[0] - b[0]) * (c[1] - d[1]) - (a[1] - b[1]) * (c[0] - d[0])
    if abs(den) < 1e-9:
        return None
    t = ((a[0] - c[0]) * (c[1] - d[1]) - (a[1] - c[1]) * (c[0] - d[0])) / den
    return (a[0] + t * (b[0] - a[0]), a[1] + t * (b[1] - a[1]))


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
    from the centroid) and `inward` the other way, joined as one ring of 2n vertices (feature 139: the polder
    dike's 2,880-vertex smoothed band is replaced, for PLACEMENT only, by this ring around its crest)."""
    n = len(ring)
    # OUTWARD BY WINDING, never by a centroid test: in a concave pocket the edge that faces the centroid is the one
    # whose outward normal points AT it, and a centroid test turned that edge inside out (one chord vertex of a
    # wobbly test ring escaped its own keep-out). The ring's signed area fixes the orientation once.
    ccw = _signed_area(ring) > 0
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
        inner.append((b[0] - mx * inward, b[1] - my * inward))
    return [*outer, *reversed(inner)]


def simplify_ring(pts: Sequence[Pt], eps: float) -> Poly:
    """Douglas-Peucker on a CLOSED ring: the ring split at its two farthest-apart vertices, each half
    simplified so no dropped vertex lies farther than `eps` from the chord that replaces it. A 49-73-vertex
    field outline comes back as eight to sixteen chords that follow its bays (feature 139, GM 2026-08-28:
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


def keepout_ring(chain: Sequence[Pt], covered: Sequence[Pt], eps: float) -> tuple[Poly, Poly]:
    """`(keepout, chords)`: `chain` simplified to a few chords, then pushed out on each side by as far as any
    point of `covered` lies from those chords (measured, not assumed) plus `eps` - so the keep-out CONTAINS
    every covered point by construction. For a field, `chain` and `covered` are both the outline (the
    keep-out is the outline's chords plus the simplification tolerance); for a dike, `chain` is the crest and
    `covered` the drawn band."""
    chords = simplify_ring(chain, eps)
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
    return ring_offset(chords, out_reach + eps, in_reach + eps * 3.0), chords  # the inner edge is un-mitered (see ring_offset), so it carries extra tolerance


Chord = tuple[Pt, Pt, Pt]  # (a, b, outward normal): a pushed-out chord of a field outline and the side the houses are on


def facing_chains(outline: Sequence[Pt], seat: Pt, eps: float) -> list[list[Chord]]:
    """THE OPEN CHAINS ON THE HOUSE SIDE (feature 139, GM 2026-08-28: *"just a few line segments on one side of
    the field that you are checking that you are on the correct side of ... not forming a closed shape"*):
    the outline simplified to chords, keeping only the runs of chords whose outward normal points toward
    `seat` (the planned cluster), each chord pushed out by `eps` along that normal so no part of the drawn
    outline lies on the house side of it. One open chain per run, each chord carrying its outward normal -
    the reference hamlet's field gives 5 chords / 6 vertices."""
    chords = simplify_ring(outline, eps)
    n = len(chords)
    if n < 3:
        return []
    ccw = _signed_area(chords) > 0
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
    if all(faces):
        runs = [list(range(n))]
    else:
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
        if cur:
            runs.append(cur)
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
