"""Split from settlement/homestead_parts.py by feature 173 - see this package's CLAUDE.md for the index."""

import math
from typing import TYPE_CHECKING, Any

from .._geom import edge_dist, point_in_poly, turn_about

if TYPE_CHECKING:
    from ..core import Settlement

# THE STRAW MAT, 3 x 6 ft (feature 282): the mushiro was woven about 3 shaku by 6 (90 x 180 cm; tobunken-mushiro), and a
# yard at harvest was a floor of them - "mats were spread to fill the yard" (Kitamoto). Laid long side across the yard's
# width, in rows (a GUESS: no page read says how they lay); what keeps the outer row off the floor's outline stroke is the
# edge clearance below (settlement-review, Kashikawa, 2026-09-28).
MAT_FT = (6.0, 3.0)
# ...and every mat corner at least this far inside the floor's DRAWN outline, which `_quad` pulls in at its corners: the
# rect inset alone left outer mats 0.1 ft off a pulled-in edge (measured on the pool's SVGs, 2026-09-28).
MAT_EDGE_CLEAR_FT = 1.0
MAT_SQ_FT = MAT_FT[0] * MAT_FT[1]
# THE GAP LEFT BETWEEN DRAWN MATS, widest first (feature 282, a CONVENTION): a real yard's mats lay edge to edge, and drawn
# so they read as a textured floor. A 2 ft gap on every side leaves each mat on its own - the 2 ft pitch alone is 45% of a
# full cover - and a yard too small or too clipped (by its pulled-in corners and the rack) to reach a third of one at that
# gap closes it a step at a time, never below 1 ft; a step that overshoots two thirds is thinned back evenly (FR-004).
MAT_GAPS_FT = (2.0, 1.5, 1.0)
# EACH MAT LAID BY HAND, NOT SET IN A PATTERN (settlement-reviews of 2026-09-28): every REGULAR layout read as paving - a
# checkered half as pavers meeting at their corners (Sawada), square rows as a tiled grid (Inashiro), rows set over by half
# a mat as brick bond (Kashikawa). So each mat is nudged off its row by up to this much and turned by up to this many
# degrees, a positional draw from its row and column (never the map's random stream), and kept at its row position
# wherever the nudge would carry it off the floor or onto the rack.
MAT_JITTER_FT = 0.4
MAT_SEARCH_STEP_FT = 0.25  # the grid the lattice's offset is searched on - every gap's pitch is a whole number of it
MAT_STROKE_FT = 0.2  # half the mat outline's drawn width (0.4 at a hamlet's 1 ft to the px)
MAT_INK_CLEAR_FT = 0.1  # bare ground left between two mats' drawn outlines, at the least
MAT_PROBE_FT = 1e-6  # how far off a crossing the exact solve probes a region cut by the rack (a hair: far above the 1e-9 test tolerance)
_PROBE_DIRS = tuple((math.cos(k * math.pi / 8), math.sin(k * math.pi / 8)) for k in range(16))
MAT_JITTER_DEG = 10.0  # up to 10 degrees where the neighbors leave room: at 6 a corner swung under half a pixel at map scale (settlement-review, Mizuguchi, round 7)


def _mat_hash(r: int, c: int, salt: float) -> float:
    """A deterministic draw in [0, 1) for the mat in row `r`, column `c` - positional, like `Settlement._hjit`."""
    v = math.sin(r * 12.9898 + c * 78.233 + salt * 37.719) * 43758.5453
    return v - math.floor(v)


def _mat_corners(x: float, y: float, mw: float, mh: float, a: float) -> list[tuple[float, float]]:
    """The four corners of a mat whose unturned rect is (x, y, mw, mh), turned `a` degrees about its center."""
    cx, cy, t = x + mw / 2.0, y + mh / 2.0, math.radians(a)
    return [(cx + dx * math.cos(t) - dy * math.sin(t), cy + dx * math.sin(t) + dy * math.cos(t)) for dx, dy in ((-mw / 2, -mh / 2), (mw / 2, -mh / 2), (mw / 2, mh / 2), (-mw / 2, mh / 2))]


# THE RACK BY THE HOUSE (feature 282): a line of posts and poles hung with sheaves, drawn 2.5 ft wide so it reads - a
# map drawing CONVENTION (the real poles are inches thick) - and inset 2 ft from the yard's front edge and 1 ft from its side. It is
# drawn as a straw-gold LINE of hung sheaves with dark post dots and no box: drawn first as an outlined box, it read as
# the woodpile beside the same houses (settlement-review, Sawada, 2026-09-28).
RACK_WIDTH_FT = 2.5
RACK_INSET_FT = 2.0  # from the yard's front (house-facing) edge
# ...but only 1 ft from its SIDE, so the rack stands in the slack the centered mat rows leave at the yard's flanks and does
# not take a column of mats: at 2 ft it cost the smallest yards a third of their floor (Sawada's 20 x 14 ft yard drew 4 mats
# of a floor of 6, the gate, 2026-09-28).
RACK_SIDE_INSET_FT = 1.0
RACK_MIN_FT = 4.0  # shorter than this and it is not drawn: a side clipped by the map-south rule to a stub reads as litter
RACK_CLEAR_FT = 0.25  # the rack stops this far north of the yard's midline (the manifest rounds to 0.1 px)
RACK_POST_FT = 6.0  # a post every ~6 ft (a GUESS within the attested racks: posts at even spacing, kotobank-hasa-nipponica)


def mat_cells(
    w: float, h: float, poly: list[tuple[float, float]], ftpx: float, keep_out: tuple[float, float, float, float] | None = None, salt: float = 0.0
) -> list[tuple[float, float, float, float, float]]:
    """The mats one yard draws, as (x, y, w, h, angle) in the yard's LOCAL, unturned frame (its center at 0,0): the
    unturned rect and the degrees it is turned about its own center.

    The real yard was covered edge to edge (40-60 mats), which at map scale reads as a textured floor rather than as mats,
    so the drawing lays them in rows across the whole yard with a gap around each, each nudged and turned a little as if
    laid by hand, a third to two thirds of a full cover - the GM's drawing convention (2026-09-28: "at this scale, we
    can't render dozens of mats and have that be legible. So our threshing yard glyphs show a smaller number to give the
    impression that there are many of them"). A mat is kept only if its four corners lie at least `MAT_EDGE_CLEAR_FT`
    inside the yard's quad `poly` (local coords) and miss `keep_out` (the rack's footprint, x0, y0, x1, y1). The count is
    held to at least a third of the yard's full cover (area / 18 sq ft; spec 282 FR-004) by closing the gap
    (`MAT_GAPS_FT`), at the widest gap that reaches it; where none does, the gap that holds the most. At each gap the
    lattice is tried as wide and as deep as the yard allows and one column and one row fewer, at every offset on a
    quarter-foot grid, and the one that seats the most is kept, of equals the one nearest the center - a centered lattice
    one column too wide lost both outer columns to the floor's pulled-in corners and drew half what fits
    (settlement-reviews of round 7, Sawada and Kashikawa, 2026-09-28).
    `salt` is the yard's own: the nudge and the turn are drawn per yard, not repeated from one to the next."""
    import numpy as np  # bound on first use: no heavy library at import time (feature 237)

    mw, mh, clear = MAT_FT[0] / ftpx, MAT_FT[1] / ftpx, MAT_EDGE_CLEAR_FT / ftpx
    floor = math.ceil((w * ftpx) * (h * ftpx) / MAT_SQ_FT / 3.0)

    def fits(corners: list[tuple[float, float]]) -> bool:
        if not all(point_in_poly(px, py, poly) and edge_dist(px, py, poly) >= clear for px, py in corners):
            return False
        xs, ys = [p[0] for p in corners], [p[1] for p in corners]
        return keep_out is None or not (min(xs) < keep_out[2] and max(xs) > keep_out[0] and min(ys) < keep_out[3] and max(ys) > keep_out[1])

    # WHICH MAT SPOTS FIT, ON A QUARTER-FOOT GRID, ONCE (spec-fidelity, amendment round 6, 2026-09-28): a lattice tried at a
    # few offsets missed the one that fits a yard in a 0.2 ft band and drew it a third short; every gap's pitch (7, 7.5 and
    # 8 ft across, 4, 4.5 and 5 ft down) is a whole number of quarter feet, so every lattice at every offset is a sum of
    # lookups in this one table - the whole search, asked of the geometry once.
    # THE FLOOR FILLED, NOT SEARCHED (feature 297, FR-003): the lattice is laid centered in the floor's inner box at each gap,
    # widest first, and the first that meets the third-of-cover floor is taken; the search below runs only where no gap's
    # fill does (a floor too irregular for its inner box), so the floor rule holds either way.
    filled = _filled_lattice(poly, clear, keep_out, mw, mh, ftpx, floor, fits)
    if filled is not None:
        return thin_evenly(_lay_by_hand(filled, mw, mh, ftpx, fits, salt), max(1, math.floor((w * ftpx) * (h * ftpx) / MAT_SQ_FT * 2.0 / 3.0)))
    q = MAT_SEARCH_STEP_FT / ftpx
    xs = [-w / 2.0 + i * q for i in range(int(w / q) + 1)]
    ys = [-h / 2.0 + j * q for j in range(int(h / q) + 1)]
    # each unturned mat's corners fall on the same grid (6 x 3 ft is 24 x 12 quarter feet), so the floor test is asked once
    # per grid point and a mat's fit is four lookups plus the rack's box
    cw, ch = round(MAT_FT[0] / MAT_SEARCH_STEP_FT), round(MAT_FT[1] / MAT_SEARCH_STEP_FT)
    # THE GRID AND THE SPOTS AS ARRAYS (feature 284, FR-011): each of a yard's ~19,000 grid points was asked `point_in_poly`
    # and `edge_dist` one at a time - 16 profiled seconds over three maps' 54 yards. `floor_grid` decides the same verdicts in
    # arrays; a spot is its four corners' verdicts and the rack's box, as slices.
    inside = floor_grid(xs, ys, poly, clear)
    ok = mat_spots(inside, np.asarray(xs), np.asarray(ys), cw, ch, mw, mh, keep_out)
    best: list[tuple[float, float, float, float, float]] = []
    for gap_ft in MAT_GAPS_FT:
        px, py = round((MAT_FT[0] + gap_ft) / MAT_SEARCH_STEP_FT), round((MAT_FT[1] + gap_ft) / MAT_SEARCH_STEP_FT)
        found = best_lattice(ok, xs, ys, px, py, mw, mh)
        _n, _o, i0, j0, nc, nr = found
        base = [(r, c, xs[i0 + c * px], ys[j0 + r * py]) for r in range(nr) for c in range(nc) if _n and ok[i0 + c * px][j0 + r * py]]
        if len(base) < floor and gap_ft == MAT_GAPS_FT[-1]:
            # THE LAST GAP IS SOLVED EXACTLY WHERE THE GRID FALLS SHORT (spec-fidelity, amendment round 7, 2026-09-28): a lattice
            # that fits in a window narrower than the quarter-foot grid was missed, and a yard that CAN hold a third drew one
            # short; so before a yard is let off with fewer, the lattice is solved exactly on the floor's own outline
            exact = _exact_lattice(poly, clear, keep_out, mw, mh, (MAT_FT[0] + gap_ft) / ftpx, (MAT_FT[1] + gap_ft) / ftpx, w, h, len(base))
            if len(exact) > len(base):
                base = [b for b in exact if fits(_mat_corners(b[2], b[3], mw, mh, 0.0))]
        mats = _lay_by_hand(base, mw, mh, ftpx, fits, salt)
        if len(mats) > len(best):
            best = mats
        if len(mats) >= floor:
            break
    # A YARD THAT CANNOT HOLD A THIRD WITH ROOM ROUND EVERY MAT DRAWS AS MANY AS FIT AT 1 FT (spec 282 FR-004, amended
    # 2026-09-28): the narrower steps were tried and each read as paving in the settlement-reviews - edge to edge (rounds 2
    # and 3), and 0.5 ft (rounds 4 to 6: no room to lay a mat askew, even thinned). At 1 ft every mat keeps bare ground and
    # room to lie askew; research.md R4 of spec 282 counts the pool's yards that still fall short.
    return thin_evenly(best, max(1, math.floor((w * ftpx) * (h * ftpx) / MAT_SQ_FT * 2.0 / 3.0)))


def _filled_lattice(
    poly: list[tuple[float, float]], clear: float, keep_out: tuple[float, float, float, float] | None, mw: float, mh: float, ftpx: float, floor: int, fits: Any
) -> list[tuple[int, int, float, float]] | None:
    """The mats' lattice (row, column, x, y of each mat's unturned origin) laid CENTERED in the floor's inner box - the box
    inside the floor moved in by `clear` (`inner_box`) - at the widest gap of `MAT_GAPS_FT` whose lattice seats `floor` mats,
    a spot dropped where its mat leaves the floor or meets the rack (`fits`); None where no gap's lattice seats `floor`."""
    box = inner_box(poly, clear)
    if box is None:
        return None
    x0, y0, x1, y1 = box
    for gap_ft in MAT_GAPS_FT:
        pw, ph = mw + gap_ft / ftpx, mh + gap_ft / ftpx
        nc, nr = int((x1 - x0 + gap_ft / ftpx) // pw), int((y1 - y0 + gap_ft / ftpx) // ph)
        if nc < 1 or nr < 1:
            continue
        ox = (x0 + x1) / 2.0 - (nc * pw - gap_ft / ftpx) / 2.0
        oy = (y0 + y1) / 2.0 - (nr * ph - gap_ft / ftpx) / 2.0
        base = [(r, c, ox + c * pw, oy + r * ph) for r in range(nr) for c in range(nc)]
        base = [b for b in base if fits(_mat_corners(b[2], b[3], mw, mh, 0.0))]
        if len(base) >= floor:
            return base
    return None


def inner_box(poly: list[tuple[float, float]], clear: float) -> tuple[float, float, float, float] | None:
    """An axis-aligned box inside the convex floor `poly` moved in by `clear`: bounded by the inner extreme of the moved-in
    floor's corners on each side - its left two corners' larger x, its right two's smaller, its top two's larger y, its bottom
    two's smaller. Inside for the floor's slightly irregular quad (each side a monotone edge); None where it is empty."""
    from shapely.geometry import Polygon

    g = Polygon(poly).buffer(-clear, join_style="mitre")
    if g.is_empty or g.geom_type != "Polygon":
        return None
    pts = list(g.exterior.coords)[:-1]
    if len(pts) < 4:
        return None
    xs = sorted(p[0] for p in pts)
    ys = sorted(p[1] for p in pts)
    x0, x1, y0, y1 = xs[1], xs[-2], ys[1], ys[-2]
    return (x0, y0, x1, y1) if x1 > x0 and y1 > y0 else None


def floor_grid(xs: list[float], ys: list[float], poly: list[tuple[float, float]], clear: float) -> Any:
    """`[[point_in_poly(x, y, poly) and edge_dist(x, y, poly) >= clear for y in ys] for x in xs]` as a boolean array, point
    for point (feature 284): a point inside the floor shrunk by `clear` plus a margin is surely clear, one outside it shrunk
    by `clear` minus the margin surely not, and a point between - within the margin of the line, where a buffer's chords and
    rounding could disagree with the exact test - is asked the exact test itself."""
    import numpy as np  # bound on first use: no heavy library at import time (feature 237)
    import shapely
    from shapely.geometry import Polygon

    gx, gy = np.meshgrid(np.asarray(xs, dtype=float), np.asarray(ys, dtype=float), indexing="ij")
    out = np.zeros(gx.shape, dtype=bool)
    if len(poly) < 3:
        return out
    floor = Polygon(poly)
    margin = max(1e-6, clear * 0.02)  # past the chord error of a buffer's arcs at a reflex corner (under 0.5% of `clear`)
    surely = floor.buffer(-(clear + margin))
    maybe = floor.buffer(-(clear - margin)) if clear > margin else floor.buffer(0)
    if not surely.is_empty:
        out = shapely.contains_xy(surely, gx, gy)
    band = ~out & (shapely.intersects_xy(maybe, gx, gy) if not maybe.is_empty else np.zeros(gx.shape, dtype=bool))
    for i, j in zip(*np.nonzero(band), strict=True):
        x, y = xs[i], ys[j]
        out[i, j] = point_in_poly(x, y, poly) and edge_dist(x, y, poly) >= clear
    return out


def mat_spots(inside: Any, xs: Any, ys: Any, cw: int, ch: int, mw: float, mh: float, keep_out: tuple[float, float, float, float] | None) -> Any:
    """`mat_cells`' old `spot(i, j)` for every grid point at once: the four corners of the mat whose origin is the point all
    on the floor (`inside`), and its box clear of the rack's (`keep_out`) - the same comparisons."""
    import numpy as np  # bound on first use: no heavy library at import time (feature 237)

    nx, ny = inside.shape
    ok = np.zeros((nx, ny), dtype=bool)
    if nx > cw and ny > ch:
        ok[: nx - cw, : ny - ch] = inside[: nx - cw, : ny - ch] & inside[cw:, : ny - ch] & inside[: nx - cw, ch:] & inside[cw:, ch:]
    if keep_out is not None:
        x, y = xs[:, None], ys[None, :]
        ok &= ~((x < keep_out[2]) & (x + mw > keep_out[0]) & (y < keep_out[3]) & (y + mh > keep_out[1]))
    return ok


def best_lattice(ok: Any, xs: list[float], ys: list[float], px: int, py: int, mw: float, mh: float) -> tuple[int, float, int, int, int, int]:
    """The lattice `mat_cells` seats at one gap: (count, -off-center, i0, j0, cols, rows) - the most mats seated, of equals the
    one whose seated mats sit nearest the yard's center (settlement-reviews of round 9: scored on the whole lattice tried, a
    lattice with a row hanging off the floor won and its real mats sat hard against the other side), the first met on a tie.

    THE COUNTS AS ARRAY SUMS (feature 284, FR-011): every offset of every lattice was walked in Python, its seated mats listed
    one by one. The count at every offset of an `nc x nr` lattice is the sum of `nc * nr` strided slices of `ok`. The old walk
    kept the lexicographic best of (count, -off-center) in (cols, rows, i0, j0) order with strict improvement, so it ends on
    the first offset, in that order, holding the GLOBAL best count and the least off-center among those: only those offsets
    are walked here, with the old `_off_center`, in the old order."""
    import numpy as np  # bound on first use: no heavy library at import time (feature 237)

    nx, ny = ok.shape
    mc, mr = (nx - 1) // px + 1, (ny - 1) // py + 1  # the most columns and rows the yard's span allows
    counts: list[tuple[int, int, Any]] = []
    top = 0
    for nc in (mc, mc - 1):
        for nr in (mr, mr - 1):
            ni, nj = nx - (nc - 1) * px, ny - (nr - 1) * py
            if nc < 1 or nr < 1 or ni < 1 or nj < 1:
                continue
            c = np.zeros((ni, nj), dtype=np.int64)
            for ci in range(nc):
                for rj in range(nr):
                    c += ok[ci * px : ci * px + ni, rj * py : rj * py + nj]
            counts.append((nc, nr, c))
            top = max(top, int(c.max()))
    found: tuple[int, float, int, int, int, int] = (0, 0.0, 0, 0, 0, 0)
    if top == 0:
        return found
    for nc, nr, c in counts:
        for i0, j0 in np.argwhere(c == top).tolist():
            seated = [(xs[i0 + ci * px], ys[j0 + rj * py]) for ci in range(nc) for rj in range(nr) if ok[i0 + ci * px, j0 + rj * py]]
            cand = (len(seated), -_off_center(seated, mw, mh), i0, j0, nc, nr)
            if cand[:2] > found[:2]:
                found = cand
    return found


def _off_center(seated: list[tuple[float, float]], mw: float, mh: float) -> float:
    """How far the box round the seated mats (their unturned origins, each `mw` x `mh`) sits off the yard's center."""
    x0, x1 = min(p[0] for p in seated), max(p[0] for p in seated) + mw
    y0, y1 = min(p[1] for p in seated), max(p[1] for p in seated) + mh
    return abs((x0 + x1) / 2.0) + abs((y0 + y1) / 2.0)


def _exact_lattice(
    poly: list[tuple[float, float]], clear: float, keep: tuple[float, float, float, float] | None, mw: float, mh: float, pw: float, ph: float, w: float, h: float, beat: int
) -> list[tuple[int, int, float, float]]:
    """The lattice (pitch `pw` x `ph`) seating the most unturned `mw` x `mh` mats, found EXACTLY - no step anywhere
    (spec-fidelity, amendment round 8, 2026-09-28: a y grid of 0.02 ft missed a lattice that fits in a band thinner than
    that, just below a rack's end). Whether a lattice spot seats is a set of linear conditions on the lattice's origin:
    each corner stays `clear` inside the convex `poly` (a corner is `clear` inside a convex polygon exactly where it is
    inside the polygon every edge of which is moved in by `clear`), and the mat misses `keep`. The seated count is
    constant between those conditions' lines, so its largest value is reached at a crossing of two of them; every
    crossing, and a hair to each side of it, is tried. Returns [] unless it seats more than `beat`; of equals, the lattice
    whose seated mats sit nearest the yard's center."""
    import numpy as np

    area = sum(poly[i][0] * poly[(i + 1) % len(poly)][1] - poly[(i + 1) % len(poly)][0] * poly[i][1] for i in range(len(poly)))
    sign = 1.0 if area > 0 else -1.0
    edges = []
    for i in range(len(poly)):
        (ax, ay), (bx, by) = poly[i], poly[(i + 1) % len(poly)]
        ln = math.hypot(bx - ax, by - ay)
        nx, ny = sign * (by - ay) / ln, -sign * (bx - ax) / ln  # the outward normal
        edges.append((nx, ny, nx * ax + ny * ay - clear))  # inside, moved in: nx*x + ny*y <= c
    corners = ((0.0, 0.0), (mw, 0.0), (0.0, mh), (mw, mh))
    best: tuple[int, float, list[tuple[int, int, float, float]]] = (beat, 0.0, [])
    for nr in range(1, int(h // ph) + 2):
        for nc in range(1, int(w // pw) + 2):
            if nc * nr <= best[0]:
                continue
            spots = [(r, c, c * pw, r * ph) for r in range(nr) for c in range(nc)]
            # every condition as a line a*ox + b*oy = k on the origin (ox, oy)
            lines = [(nx, ny, ce - nx * (tx + dx) - ny * (ty + dy)) for _r, _c, tx, ty in spots for dx, dy in corners for nx, ny, ce in edges]
            if keep is not None:
                for _r, _c, tx, ty in spots:
                    lines += [(1.0, 0.0, keep[2] - tx), (1.0, 0.0, keep[0] - mw - tx), (0.0, 1.0, keep[3] - ty), (0.0, 1.0, keep[1] - mh - ty)]
            lines += [(1.0, 0.0, -w / 2.0), (1.0, 0.0, w / 2.0), (0.0, 1.0, -h / 2.0), (0.0, 1.0, h / 2.0)]
            A = np.array(lines)
            a1, a2 = np.triu_indices(len(A), 1)
            det = A[a1, 0] * A[a2, 1] - A[a1, 1] * A[a2, 0]
            ok = np.abs(det) > 1e-12
            a1, a2, det = a1[ok], a2[ok], det[ok]
            ox = (A[a1, 2] * A[a2, 1] - A[a1, 1] * A[a2, 2]) / det
            oy = (A[a1, 0] * A[a2, 2] - A[a1, 2] * A[a2, 0]) / det
            inbox = (ox >= -w / 2.0 - 1e-9) & (ox <= w / 2.0 + 1e-9) & (oy >= -h / 2.0 - 1e-9) & (oy <= h / 2.0 + 1e-9)
            ox, oy = ox[inbox], oy[inbox]

            def seats(ox: Any, oy: Any, tol: float, spots: list[tuple[int, int, float, float]] = spots) -> Any:
                # which spots seat at each origin; `tol` > 0 counts a spot on its boundary (closed), < 0 only well inside
                seat = np.ones((len(spots), len(ox)), bool)
                for k, (_r, _c, tx, ty) in enumerate(spots):
                    for dx, dy in corners:
                        for nx, ny, ce in edges:
                            seat[k] &= nx * (ox + tx + dx) + ny * (oy + ty + dy) <= ce + tol
                    if keep is not None:
                        x, y = ox + tx, oy + ty
                        seat[k] &= ~((x < keep[2] - tol) & (x + mw > keep[0] + tol) & (y < keep[3] - tol) & (y + mh > keep[1] + tol))
                return seat

            # each region where one set of spots seats is convex, and its corners are crossings; the crossings are grouped
            # by the set they seat on its closed boundary, and each group's centroid - inside its region - is where the
            # set is confirmed with every spot well inside, so a region however thin is found and none is claimed falsely
            closed = seats(ox, oy, 1e-9)
            live = closed.sum(axis=0) > best[0]
            if not live.any():
                continue
            _sets, which = np.unique(closed[:, live].T, axis=0, return_inverse=True)
            which = which.ravel()
            size = np.bincount(which)
            cx = np.bincount(which, weights=ox[live]) / size
            cy = np.bincount(which, weights=oy[live]) / size
            if keep is not None:
                # missing the rack is a union of four half-planes, so a region can be an L whose centroid lies in the
                # cut-out corner (spec-fidelity, amendment round 9: a 10 x 7 ft yard drew 0 where 1 fits); a hair to
                # each side of every crossing lies inside each region meeting it, however it is cut
                hx, hy = ox[live], oy[live]
                cx = np.concatenate([cx] + [hx + MAT_PROBE_FT * dx for dx, dy in _PROBE_DIRS])
                cy = np.concatenate([cy] + [hy + MAT_PROBE_FT * dy for dx, dy in _PROBE_DIRS])
            strict = seats(cx, cy, -1e-9)
            for q in range(len(cx)):
                n = int(strict[:, q].sum())
                if n > best[0] or (n == best[0] and best[2]):
                    seated = [(r, c, float(cx[q]) + tx, float(cy[q]) + ty) for k, (r, c, tx, ty) in enumerate(spots) if strict[k, q]]
                    off = _off_center([(sx, sy) for _r, _c, sx, sy in seated], mw, mh)
                    if n > best[0] or off < best[1]:
                        best = (n, off, seated)
    return best[2]


def _quad_gap(a: list[tuple[float, float]], b: list[tuple[float, float]]) -> float:
    """The gap between two convex quads: the least corner-to-edge distance either way, 0 where a corner of one is inside
    the other."""
    if any(point_in_poly(px, py, b) for px, py in a) or any(point_in_poly(px, py, a) for px, py in b):
        return 0.0
    return min(min(edge_dist(px, py, b) for px, py in a), min(edge_dist(px, py, a) for px, py in b))


def _boxes_within(a: list[tuple[float, float]], b: list[tuple[float, float]], need: float) -> bool:
    """Could the two quads be nearer than `need`? False when their boxes are `need` or more apart - every point of one then
    stands at least that far from every point of the other, so `_quad_gap` is at least `need` (feature 284: each mat was
    measured against every other mat of its yard)."""
    dx = max(0.0, min(p[0] for p in b) - max(p[0] for p in a), min(p[0] for p in a) - max(p[0] for p in b))
    dy = max(0.0, min(p[1] for p in b) - max(p[1] for p in a), min(p[1] for p in a) - max(p[1] for p in b))
    return math.hypot(dx, dy) < need


def _lay_by_hand(base: list[tuple[int, int, float, float]], mw: float, mh: float, ftpx: float, fits: Any, salt: float = 0.0) -> list[tuple[float, float, float, float, float]]:
    """Set each mat of the lattice `base` (row, column, x, y) down by hand: nudged up to `MAT_JITTER_FT` and turned up to
    `MAT_JITTER_DEG` by a positional draw, and kept so only where its corners still fit the floor (`fits`) and its drawn
    outline stays `MAT_INK_CLEAR_FT` clear of every neighbor's - the mats already laid and the lattice spots still to come.
    Where the full draw does not fit, the same turn with no nudge, then half the turn, then the lattice spot unturned.

    ONE BUDGET PER MAT, NOT A FORMULA PER GAP (settlement-reviews of round 6, 2026-09-28): a turn limit derived from the
    gap and the nudge fell to nothing at the 1 ft step as well as the 0.5 ft one, and six to eleven yards a map drew a rigid
    grid again; asking each mat whether its own turn fits beside its own neighbors keeps the turn wherever there is room."""
    need = (MAT_INK_CLEAR_FT + 2 * MAT_STROKE_FT) / ftpx
    laid: list[tuple[float, float, float, float, float]] = []
    lattice = [_mat_corners(bx, by, mw, mh, 0.0) for _r, _c, bx, by in base]  # each spot's unturned mat, made once
    # ITS NEIGHBORS, NOT EVERY MAT (feature 297): a mat can come within `need` only of a mat in an adjacent row or column of the
    # lattice - the next one over stands a whole mat and gap away - so each spot is measured against those, laid or to come
    at: dict[tuple[int, int], int] = {(r, c): k for k, (r, c, _x, _y) in enumerate(base)}
    placed: dict[int, list[tuple[float, float]]] = {}
    for k, (r, c, x, y) in enumerate(base):
        dx, dy = (2 * _mat_hash(r, c, salt + 1.0) - 1) * MAT_JITTER_FT / ftpx, (2 * _mat_hash(r, c, salt + 2.0) - 1) * MAT_JITTER_FT / ftpx
        a = (2 * _mat_hash(r, c, salt + 3.0) - 1) * MAT_JITTER_DEG
        near = [m for dr in (-1, 0, 1) for dc in (-1, 0, 1) if (dr or dc) and (m := at.get((r + dr, c + dc))) is not None]
        others = [placed[m] if m in placed else lattice[m] for m in near if m in placed or m > k]
        for jx, jy, ja in ((x + dx, y + dy, a), (x, y, a), (x, y, a / 2.0), (x, y, 0.0)):
            q = _mat_corners(jx, jy, mw, mh, ja)
            if ja == 0.0 or (fits(q) and all(_quad_gap(q, o) >= need for o in others if _boxes_within(q, o, need))):
                laid.append((jx, jy, mw, mh, ja))
                placed[k] = q
                break
    return laid


def thin_evenly(items: list[Any], cap: int) -> list[Any]:
    """`items` cut to `cap`, dropping evenly across the list rather than from one end (centered picks, so the drops fall
    mid-yard). The mats' two-thirds ceiling (spec 282 FR-004): a step that closes the gap can more than double a small
    yard's count, and this is what holds it under two thirds whatever the step."""
    if len(items) <= cap:
        return items
    step = len(items) / cap
    return [items[int((i + 0.5) * step)] for i in range(cap)]


def rack_segment(w: float, h: float, rot: float, ftpx: float, side: int) -> tuple[float, float, float, float] | None:
    """The rack by the house, as (x, y0, y1, half width) in the yard's LOCAL frame, or None where no side takes one.

    It runs along one of the yard's two side edges (local x = +/-), from the edge facing the house (local north) toward
    the middle, and never past it: the half nearest the house (505's GUESS - the sources are silent on the side). It must
    also stay out of the yard's MAP-south half, because the drying floor needs the sun from the south (entry 030) - and
    that is solved in MAP coordinates, after the house's rake `rot`, so it holds for any turn (a quarter-turned homestead
    included): a local point (x, y) lies map-south of the yard's center by x sin(rot) + y cos(rot), and every corner of the
    rack's footprint must keep that at or below zero. `side` (+1 east, -1 west, in the local frame) is tried first.

    THE HALF NEAREST THE HOUSE YIELDS BEFORE THE KNOB DOES (plan review, 2026-09-28): it is our guess, while the knob is
    the research's - where the weather is changeable EVERY farmstead gathers its rack by the house - so where neither side's
    near half leaves `RACK_MIN_FT`, the whole side is tried, still held off the map-south half. Some part of one side edge
    always lies map-north of the center, so a yard of the sizes the roll makes always takes a rack."""
    th = math.radians(rot)
    s, c = math.sin(th), math.cos(th)
    hw, inset, minlen = RACK_WIDTH_FT / 2.0 / ftpx, RACK_INSET_FT / ftpx, RACK_MIN_FT / ftpx
    for far, sd in ((0.0, side), (0.0, -side), (h / 2.0 - inset, side), (h / 2.0 - inset, -side)):
        x = sd * (w / 2.0 - RACK_SIDE_INSET_FT / ftpx - hw)
        lo, hi = -h / 2.0 + inset, far
        for xp in (x - hw, x + hw):  # each long edge of the footprint: y * c <= -xp * s
            k = -xp * s - RACK_CLEAR_FT / ftpx  # a hair north of the midline, so the manifest's rounding cannot carry it over
            if abs(c) < 1e-9:
                if k < 0.0:
                    hi = lo - 1.0  # this side lies map-south of the center along its whole length
            elif c > 0.0:
                hi = min(hi, k / c)
            else:
                lo = max(lo, k / c)
        if hi - lo >= minlen:
            return (x, lo, hi, hw)
    return None


def house_facing_edge(ox: float, oy: float, hx: float, hy: float, rot: float) -> str:
    """Which edge of a yard centered at (ox, oy) faces its house at (hx, hy), in the HOUSE'S frame (turned by `rot`): N, S,
    E or W of the yard's unturned quad (feature 287, homes H07). `_attach_yard` levels exactly this edge and its test reads
    exactly this edge - the test once read the quad's north edge whatever side the house stood on."""
    th = math.radians(rot)
    mx, my = ox - hx, oy - hy
    dx, dy = mx * math.cos(th) + my * math.sin(th), -mx * math.sin(th) + my * math.cos(th)
    return ("N" if dy >= 0 else "S") if abs(dy) >= abs(dx) else ("W" if dx > 0 else "E")


class ThreshingYardsMixin:
    def _draw_threshing_yard(self: Settlement, cx: float, cy: float, w: float, h: float, poly: Any, rot: float = 0.0) -> dict[str, Any]:  # type: ignore[misc]
        """Draw one tamped earthen threshing yard as the harvest leaves it (feature 282): a floor of straw mats, and a
        rack by the house where the settlement's harvest weather is changeable. The outer footprint is a
        slightly-irregular quad (`poly`, absolute corner coords, UNTURNED); the interior is laid out in the local (w,h)
        frame and the whole group turned by `rot`, its farmhouse's rake. Returns what it drew for the manifest: `mats`
        (the count) and, with a rack, `rack` (its footprint's four corners in MAP coordinates)."""
        g = [f'<g transform="translate({cx:.1f},{cy:.1f}) rotate({rot:.2f})">']
        local = [(px - cx, py - cy) for px, py in poly]
        pts = " ".join(f"{px:.1f},{py:.1f}" for px, py in local)
        g.append(f'<polygon points="{pts}" fill="#D2BE94" stroke="#A98E54" stroke-width="1.5"/>')  # tamped earthen floor
        rack = rack_segment(w, h, rot, self.ftpx, 1 if self._hjit(cx, cy, 53.0) < 0.5 else -1) if self._house_racks else None
        pad = 0.25 / self.ftpx  # the mats keep a quarter foot off the rack - a wider margin cost the smallest yards a column
        keep = (rack[0] - rack[3] - pad, rack[1] - pad, rack[0] + rack[3] + pad, rack[2] + pad) if rack else None
        mats = mat_cells(w, h, local, self.ftpx, keep, salt=round(self._hjit(cx, cy, 61.0) * 997.0, 3))  # the yard's own draw
        for mx, my, mw, mh, ma in mats:  # straw mats (mushiro), a third to two thirds of those that covered the floor, each laid by hand - a CONVENTION
            turn = f' transform="rotate({ma:.1f} {mx + mw / 2:.2f} {my + mh / 2:.2f})"' if ma else ""
            g.append(f'<rect x="{mx:.2f}" y="{my:.2f}" width="{mw:.2f}" height="{mh:.2f}"{turn} fill="#E4CC86" stroke="#C4A45E" stroke-width="0.4"/>')
        out: dict[str, Any] = {"mats": len(mats)}
        if rack:
            x, y0, y1, hw = rack
            g.append(f'<line x1="{x:.2f}" y1="{y0:.2f}" x2="{x:.2f}" y2="{y1:.2f}" stroke="#D9B64A" stroke-width="{2 * hw:.2f}"/>')  # hung sheaves
            g.append(f'<line x1="{x:.2f}" y1="{y0:.2f}" x2="{x:.2f}" y2="{y1:.2f}" stroke="#6B4A22" stroke-width="0.5"/>')  # the pole
            n = max(1, round((y1 - y0) * self.ftpx / RACK_POST_FT))
            for i in range(n + 1):  # the posts, as dots
                g.append(f'<circle cx="{x:.2f}" cy="{y0 + (y1 - y0) * i / n:.2f}" r="{hw * 0.55:.2f}" fill="#5A3F1E"/>')
            th = math.radians(rot)
            out["rack"] = [
                [round(cx + px * math.cos(th) - py * math.sin(th), 2), round(cy + px * math.sin(th) + py * math.cos(th), 2)] for px, py in ((x - hw, y0), (x + hw, y0), (x + hw, y1), (x - hw, y1))
            ]
        g.append('</g>')
        self.add(''.join(g), cls="threshing yard")
        return out

    def _yard_fits(self: Settlement, x: float, y: float, w: float, h: float, hx: float, hy: float) -> bool:  # type: ignore[misc]
        """A threshing yard fits where it is in-bounds, on DRY ground (clear of paddies / blocks),
        off any lane, and clear of every placed footprint EXCEPT its own farmhouse (it abuts that)."""
        if x < 55 or x > self.W - 55 or y < 88 or y > self.H - 26:
            return False
        if self.bound and not point_in_poly(x, y, self.bound):
            return False
        if self._in_blocked(x, y) or self._near_corridor(x, y):
            return False
        if self._rect_hits((x, y, w, h), self.dry_polys):  # hem strips / garden tracts are cropland too -
            return False  # the yard footprint stays off them, same as the house test in _fits (GM, Tango hems)
        r = math.hypot(w, h) / 2
        for poly in self.field_polys:  # keep the whole DRY footprint out of every paddy
            if point_in_poly(x, y, poly) or edge_dist(x, y, poly) < r + 4:
                return False
        # ...AND ASK THE QUESTION THE CHECK ASKS, OF THE SOURCE THE CHECK READS (cohort seed 31,
        # 2026-08-18). The loop above is a CENTRE-and-circle test against `field_polys`, which holds
        # the smoothed ENVELOPE; `harvest_yards_clear_of_paddies` is a CORNER test against each
        # paddy's own recorded `outline`. Two sources and two geometries, so they can disagree - and
        # on seed 31 they did: a yard cleared the envelope by its circle and still put a corner at
        # (2024, 1908) inside a drawn basin. This is the same defect shape as the woodland scan
        # mirroring its check's formula but not its window, fixed earlier the same day; the standing
        # rule is that placement and its check read ONE source.
        _fo = [f["outline"] for f in self.M.get("fields", []) if f.get("kind") == "paddy" and f.get("outline")]
        if _fo:
            _cn = [(x + sx * w / 2, y + sy * h / 2) for sx in (-1.0, 1.0) for sy in (-1.0, 1.0)]
            for _ol in _fo:
                if any(point_in_poly(_px, _py, _ol) for _px, _py in _cn):
                    return False
                if any(-w / 2 <= _vx - x <= w / 2 and -h / 2 <= _vy - y <= h / 2 for _vx, _vy in _ol):
                    return False  # ...and the other direction: a basin vertex inside the yard, which the check also tests
        for px, py, pw, ph, *_ in self.placed:
            if px == hx and py == hy:  # the yard abuts its OWN farmhouse - allowed
                continue
            if math.hypot(x - px, y - py) < r + math.hypot(pw, ph) / 2 + 2:
                return False
        return True

    # THE WORK YARD IS ROLLED FROM A LOGNORMAL, CORRELATED WITH THE HOUSEHOLD (GM 2026-08-28, feature
    # 134 T49; research/homesteads.html "Threshing and drying yards at farmhouses (niwa)").
    #
    # The record, in one line: Kitamoto's households stated their yard in straw mats - 40-60 mats
    # usually, over 100 for a few, two mats to the tsubo - so 20-30 tsubo (66-99 sq m) ordinarily and
    # past 50 tsubo (165 sq m) at the top. No survey tabulates yards, so the SHAPE comes from what the
    # cadastres do tabulate, and every one of those is right-skewed: Kamikanai 1771's 31 commoner main
    # houses fit a lognormal of median 22.5 tsubo, sigma_ln 0.46, its headman detached at 3.1x; Kikoba's
    # lots run 15-100 bu about a mode of 30. Kitamoto's own band-and-tail implies sigma 0.35-0.45 - that
    # convergence is what these numbers rest on. Hence median 25 tsubo, sigma_ln 0.40, floored at 8.
    #
    # CORRELATED, NOT PROPORTIONAL (the GM: "overwhelmingly likely that a large household has a large
    # threshing yard", a mismatch "possible but rare"). Kamikanai measures the coupling as ADDITIVE -
    # five more koku of holding buys about ten more tsubo of built area - so a 20x holder does not get a
    # 20x yard. The household enters as its house footprint's deviation from the map's ordinary minka,
    # damped by YARD_HOUSE_BETA; an independent positional draw supplies the rest of the spread.
    # THE MEDIAN IS THE WET-RICE FIGURE, THE SHAPE IS KITAMOTO'S (GM 2026-08-28, option 2). Kitamoto's
    # 20-30 tsubo is the one directly-stated yard size, but it is a BARLEY district - its yard is sized
    # by the mugi crop the household spreads whole. Wet rice is field-dried on hazakake racks for 10-14
    # days before it reaches the yard, and is threshed in batches over days, so a paddy household needs
    # less standing floor: the crop derivation (1.3 koku/tan -> 247 kg momi -> mats at a 2.5 cm spread,
    # batched) gives 55-100 sq m for a full cho, 35-65 for five tan. That derivation gave 18 tsubo
    # (59.5 sq m) for a rice hamlet until feature 280 retired its modern spreading depth (below); Kitamoto's 25 tsubo is
    # YARD_MEDIAN_TSUBO_DRYFIELD, and a rice hamlet now takes the same median. The SHAPE - lognormal, sigma 0.40 - is Kitamoto's
    # and Kamikanai's and applies to both.
    # FEATURE 280 M16 (research/homesteads/020): the crop derivation behind 18 tsubo spread the momi at IRRI's 2.5 cm, modern
    # tropical extension advice and the only depth found, so it is retired; the one rice-district figure is the Okayama museum's
    # ~50 mats a farm for sun-drying momi, about 25 tsubo, the middle of Kitamoto's band - so a rice hamlet's yards are centered
    # at 25 like the dry-field yard. Both are undated records of remembered practice, a calibration the GM may re-sort.
    YARD_MEDIAN_TSUBO = 25.0  # wet rice as the dry field: the Okayama ~50 mats; the map's `yard_sizes` knob may name the dry-field figure instead
    YARD_SIGMA_LN = 0.40  # Kamikanai 0.46; Kitamoto's band-and-tail 0.35-0.45
    YARD_MEDIAN_TSUBO_DRYFIELD = 25.0  # Kitamoto's 50 mats - a barley/wheat household spreads the whole crop
    YARD_MIN_TSUBO = 8.0  # nobody is yardless - this project's choice, so every farm can thresh; no source gives the smallest yard (research/rendering/homesteads.html, 'How our maps draw threshing and drying yards (niwa)'; the old reason, "by Genroku every peasant held a homestead", rests on no source read)
    YARD_HOUSE_BETA = 2.2  # how much of the household's own deviation the yard inherits (the drawn house varies only ~+-15% about the ordinary minka, so the household needs this much amplification to dominate the roll - measured on Inashiro: r = 0.17 at 0.55, r = 0.6-0.7 here, which is the GM's "overwhelmingly likely" without making it a rigid ratio)
    YARD_ASPECT = 1.45  # a work apron is near-square, a little wider than deep (the drawn ratio, unchanged)
    TSUBO_FT2 = 35.583  # 1 tsubo = 3.306 sq m

    def _yard_area_ft2(self: Settlement, hx: float, hy: float, hw: float, hh: float) -> float:  # type: ignore[misc]
        """This household's work-yard area in square FEET - the lognormal roll above, correlated with the
        house. Position-seeded like every other homestead attribute, so it never ripples placement."""
        import math as _m

        base = self.px(46.0) * self.px(28.0)  # the ordinary minka footprint in this map's pixels
        house = max(hw * hh, 1.0)
        # the household's own deviation, in log space, damped: a house 1.5x the ordinary lifts the yard
        # 1.5**0.55 = 1.25x before the independent draw - a strong correlation, not a rigid ratio
        tilt = _m.log(house / base) * self.YARD_HOUSE_BETA
        # THE NORMAL DRAW IS A SUM OF SIX POSITIONAL DRAWS, not Box-Muller (measured 2026-08-28): the two
        # salted `_hjit` values a Box-Muller pair needs are not independent enough - one salt pair gave a
        # population mean of -0.93 sigma across Inashiro's fifteen houses, dragging every yard a full sigma
        # small, and a different pair gave +0.28. Six draws summed (Irwin-Hall, standardized) is
        # near-normal by the central limit theorem, stable across salt choices, and has no runaway tail.
        z = (sum(self._hjit(hx, hy, k) for k in (23.0, 29.0, 31.0, 37.0, 43.0, 47.0)) - 3.0) / _m.sqrt(0.5)
        median = self.YARD_MEDIAN_TSUBO_DRYFIELD if self.M["meta"].get("yard_sizes") == "dryfield" else self.YARD_MEDIAN_TSUBO
        tsubo = median * _m.exp(tilt + self.YARD_SIGMA_LN * z)
        if self.M["meta"].get("yard_sizes") == "allotted":
            # THE PLANNED-COLONY FORM, the second attested shape: a shinden colony issued every settler
            # an identical homestead (Santome 1696), so its yards are uniform. Principle XII's knob rule:
            # two attested forms become a per-settlement knob, never a preference.
            tsubo = median
        return max(tsubo, self.YARD_MIN_TSUBO) * self.TSUBO_FT2

    def _yard_dims(self: Settlement, hw: float, hh: float, hx: float = 0.0, hy: float = 0.0) -> tuple[float, float]:  # type: ignore[misc]
        """The yard's drawn width and depth: the rolled area at the apron's near-square aspect.
        PREVIEW AND PLACEMENT MUST AGREE - `rolling/bundle.py` reserves what this returns, so changing
        one without the other makes the placer clear a different rect than the map draws."""
        import math as _m

        area_px = self._yard_area_ft2(hx, hy, hw, hh) / (self.ftpx * self.ftpx)  # sq ft -> sq px
        depth = _m.sqrt(area_px / self.YARD_ASPECT)
        return depth * self.YARD_ASPECT, depth

    def _find_yard_spot(self: Settlement, hx: float, hy: float, hw: float, hh: float) -> tuple[float, float, float, float] | None:  # type: ignore[misc]
        """The first fitting threshing-yard position for a farmhouse: the sunny SOUTH/front side (+y) is
        the maeniwa; fall back to the E/W sides if the paddy blocks due-south, but NEVER the shady north
        back. Returns (ox, oy, yw, yh) or None if the farmstead is boxed in on all three sides."""
        yw, yh = self._yard_dims(hw, hh, hx, hy)
        for dx, dy in ((0, 1), (1, 0), (-1, 0)):
            ox = hx + dx * (hw / 2 + yw / 2 - 2)
            oy = hy + dy * (hh / 2 + yh / 2 - 2)
            if self._yard_fits(ox, oy, yw, yh, hx, hy):
                return ox, oy, yw, yh
        return None

    def _attach_yard(self: Settlement, hx: float, hy: float, spot: Any, rot: float = 0.0) -> None:  # type: ignore[misc]
        """Draw a farmstead's threshing/drying yard (it is drawn BEFORE its house, so the house renders on
        top of the overlap) and record it. The work yard was UNIVERSAL, so every farmhouse gets one. Its
        footprint is a SLIGHTLY-irregular quad (a swept work surface stays near-square: small jitter),
        inscribed in the reserved rect.

        THE YARD TAKES ITS HOUSE'S RAKE (`rot`, GM 2026-09-26: the yards sat square to the map while the
        houses were turned up to 5 degrees, *"I think that they would always be in [line] with the
        farmhouses because that's just how they would be naturally laid out"*). The maeniwa is the ground
        before the house's front, so its edges run with the front wall. The homestead turns as ONE piece:
        `_rake_parts` has already carried the yard's center round the house's center, and the placer
        cleared the ground there, so this turns the yard in place about that center. Turning it about its
        own center alone, as first shipped, slid it up to 3 ft along the front wall."""
        ox, oy, yw, yh = spot
        # THE EDGE THAT FACES THE HOUSE IS LEVEL (GM 2026-09-26): north on every bundled homestead, where the yard
        # is the south front; the legacy fallback may seat it east or west, and the facing edge follows it. Read in the
        # HOUSE'S frame (269 B18): the flat quad is turned by `rot` below, so a quarter-turned homestead's yard, west of its
        # house on the map, still has its house-facing edge on the quad's north
        _facing = house_facing_edge(ox, oy, hx, hy, rot)
        flat = self._quad(ox, oy, yw, yh, 0.10, 41.0, level=_facing)
        poly = turn_about(flat, ox, oy, rot)
        # A NO-RICE HAMLET DRAWS NO THRESHING FLOOR (feature 150, GM 2026-08-28: "thrashing yards on a
        # no-rice hamlet seem bad and should be eliminated"). The ground is still RECORDED, as a
        # `forecourt`: the open ground before a farmhouse is what the lane web threads around, what
        # trees, scrub and wells keep out of, and what a silk-and-fish household works its leaf and
        # nets on - dropping the record (measured) re-packed the web and the belt, which was not the
        # ask. Only the ink goes: no swept floor, no bordered frame. `harvest_yards_present` reads
        # `meta.work_yards` and stands aside; the interactive class `threshing yard` has no ink here.
        _fore = not getattr(self, "_work_yards", True)
        drawn = {} if _fore else self._draw_threshing_yard(ox, oy, yw, yh, flat, rot)  # its mats and rack, for the manifest (feature 282)
        self.M["threshing_yards"].append(
            {
                "x": round(ox, 1),
                "y": round(oy, 1),
                "w": yw,
                "h": yh,
                "rot": round(rot, 2),
                "of": [hx, hy],
                "poly": [[round(px, 3), round(py, 3)] for px, py in poly],  # to a thousandth, so a check can re-derive the mats (feature 282)
                **({"kind": "forecourt"} if _fore else {}),
                **drawn,
            }
        )
        self.placed.append((ox, oy, yw, yh))
