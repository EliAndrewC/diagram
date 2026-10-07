"""Split from hamletgen/hinterland.py by feature 173 - see this package's CLAUDE.md for the index.

Research: woodland scan plumbing - NONE: lattices, indexes, measures and ring geometry
"""

from __future__ import annotations

import math
from collections.abc import Sequence
from typing import Any

from l7r.diagram.settlement import Settlement, point_in_poly, seg_dist, segments_cross
from l7r.diagram.settlement._geom import PointGrid, RingIndex, seg_reach_index
from l7r.diagram.settlement.land.cover import WOODLAND_MIN_CROWNS, ring_center
from l7r.diagram.settlement.land.wet import marsh_ground

from ..consts import Poly, Pt
from ..plan import SitePlan
from .frame import content_box, frame_bounds, title_pocket

CROP_MARGIN = 48.0  # the one crop margin, shared by stage_frame's crop_to_content call and the
# predicted-kept-window math in open_ground_patches - two hardcoded 48s would drift
"""Research: crop margin - CONVENTION: 48 px round the framed content"""

# How much of a woodland parcel's ROTATED bbox must fall inside the predicted kept window for the
# scan to seat it. Module-level so the attribution census can drive it - a floor buried in a closure
# cannot be measured against, and this one had to be measured twice before it was right.
#
# 0.72 sits 2 points above `woodland_commons_within_the_frame`'s own 0.7, which is all the cushion
# the prediction needs: instrumenting cohort seed 33 showed the window is byte-identical at all 16
# `_crop_boxes` calls of a build AND equal to the final `meta.view`, because everything that sets the
# frame is placed before the woodland scan runs. The neighboring square test's 0.8 exists for drift
# that measurement says does not happen; carrying 0.8 over to the rotated bbox cost seed 33 its
# woodland outright. See future-work/, "the woodland scan vetted a SQUARE".
WOODLAND_BBOX_FLOOR = 0.72
"""Research: woods on the page - CONVENTION: 72% of a parcel's box inside the predicted view"""

_COMMONS_REACH = 1.49
"""How much further a rotated parcel reaches than the equal-AREA square, worst case.

`open_ground_patches` rolls an aspect up to 2.2:1 while holding area, so the long half-axis grows by
sqrt(2.2) = 1.483 and the short one shrinks to match. Every keep-out test is done at this reach, so
a parcel that rotates cannot end up nearer a crop, a lane or the marsh than the square it replaced -
rotating a footprint must never buy ground the square could not have had."""

_COMMONS_FLOOR_FT = 120.0
"""The smallest square a woodland COMMONS may be drawn as, in feet.

Not a historical minimum - `research/contents.json#fields` is clear that coppice lots were "whatever odd corner
the village spared", and there is no attested floor. This is a LEGIBILITY floor, and it exists
because the size-variance machinery above can compound its way under one: a per-map ladder scale
times a per-parcel band multiplier took Kashikawa to 103 ft. The number is our own recorded
judgment - when the first (shrink-only) size roll produced a 116 ft parcel on Mizuguchi the reading
was "a copse, not a commons", which is what made the roll two-sided - so 120 ft is just above the
size we have already said does not read. A settlement whose ground genuinely cannot hold one draws
FEWER parcels rather than smaller ones.

Research: commons legibility floor - CONVENTION: no woodland parcel under 120 ft"""


def parcel_bbox_ok(x: float, y: float, hw: float, hh: float, bc: float, bs: float, frame: tuple[float, float, float, float]) -> bool:
    """Does a ROTATED parcel keep enough of its own bbox inside the frame? The check's own rule.

    ROTATING A BOX GROWS ITS AXIS-ALIGNED BBOX - by up to sqrt(2), at 45 degrees, even for a square -
    and `woodland_commons_within_the_frame` measures that grown bbox. Testing the unrotated square
    instead let a seat pass the ladder at 0.8 and draw a parcel 0.67 inside the window, which is what
    cohort seed 33 did the moment the cluster change walked it to the edge: a check and the thing it
    checks measuring different quantities.

    `WOODLAND_BBOX_FLOOR` is 0.72, NOT the 0.8 the square test uses, and the difference is measured
    rather than taste. The 0.8 elsewhere buys slack because that window is called a PREDICTION of the
    crop - but instrumenting seed 33 showed the window is byte-identical at all 16 `_crop_boxes` calls
    across the build AND equal to the final `meta.view`, because everything that sets the frame is
    already placed when the woodland scan runs. The prediction does not drift, so paying 10 points of
    slack for drift that does not happen just deletes coppices: at 0.8 on the rotated bbox seed 33 lost
    its woodland outright, a worse map than the 67%-clipped parcel this rule set out to stop. 0.72
    keeps a 2-point cushion over the gate for float ordering.

    Lifted out of `open_ground_patches` so it can be asked with plain numbers (GM 2026-08-28).

    Research: woods on the page - CONVENTION: WOODLAND_BBOX_FLOOR of the rotated box inside the frame
    """
    fx0, fy0, fx1, fy1 = frame
    bw, bh = abs(hw * bc) + abs(hh * bs), abs(hw * bs) + abs(hh * bc)
    inside = max(0.0, min(x + bw, fx1) - max(x - bw, fx0)) * max(0.0, min(y + bh, fy1) - max(y - bh, fy0))
    return inside >= WOODLAND_BBOX_FLOOR * (2.0 * bw) * (2.0 * bh)


def parcel_inside_share(ring: Sequence[Pt], frame: tuple[float, float, float, float]) -> float:
    """The share of a parcel's DRAWN ring's bounding box inside `frame` (x0, y0, x1, y1) - the gate's own measure
    (`test_a_woodland_commons_is_mostly_inside_the_picture`, over the view). ONE PREDICATE (feature 287, FR-003; woods
    W14): `parcel_bbox_ok` measures the rotated RECTANGLE the ring is drawn inside, whose box is not the ring's, so the
    scan asks this of the ring it is about to draw as well.

    Research: woods on the page - CONVENTION: the drawn ring's box share inside the frame
    """
    xs = [float(p[0]) for p in ring]
    ys = [float(p[1]) for p in ring]
    box = max(1e-9, (max(xs) - min(xs)) * (max(ys) - min(ys)))
    inter = max(0.0, min(max(xs), frame[2]) - max(min(xs), frame[0])) * max(0.0, min(max(ys), frame[3]) - max(min(ys), frame[1]))
    return inter / box


def fit_square_parcel(half: float, floor_half: float, fits: Any) -> float | None:
    """Shrink a square parcel down the ladder until it fits, or return None.

    SHRINK BEFORE DROPPING - the same principle as the outer aspect ladder, applied to the rotated
    bbox. A seat whose square will not fit the window is usually a seat near the edge that a slightly
    smaller square clears, and a smaller coppice on the sheet beats a larger one the crop cuts off.
    Only when even the floor-sized parcel fails is the seat genuinely unusable.

    The floor is a FLOOR, not a rung: every rung is clamped up to it, so a parcel already at the
    minimum is offered once rather than shrunk below the size at which a commons is still legible.

    Lifted out of `open_ground_patches` (GM 2026-08-28). Feature 147 parked its two lines behind a
    coverage pragma while the floor's verdict on them flickered; feature 149 found the cause - an
    entry's stored coverage outliving the key it was recorded under - and the park came off. This is
    what should have happened instead of the park: the ladder is a decision about numbers, and it can
    be asked about numbers.

    Research: shrink before dropping - UNRESEARCHED: a square parcel tried at 0.9-0.6 of its size, never under the floor
    """
    for sh in (0.9, 0.8, 0.7, 0.6):
        cand = max(half * sh, floor_half)
        if fits(cand):
            return cand
    return None


WET_SHARE_CAP = 0.0
"""The most of a woodland parcel that may stand in marsh: none of its sample grid (`woodland_commons_on_dry_ground`). A
managed coppice is not a swamp forest - standing water rots the stools and the cut cannot be carried out - and 0077's
drawing page leaves low ground by a river or marsh to grass, not wood (feature 328: the cap was half a parcel).

Research: woods mostly on dry ground - research/questions/0077-village-fuel-woods-and-their-coppice-satoyama.drawing.html: no part of a parcel in marsh"""


def parcel_wet_share(ring: Sequence[Pt], marshes: Sequence[list[Pt]]) -> float:
    """The share of a parcel's 5 x 5 sample grid, over its DRAWN ring's bounding box, that stands in a marsh ring.

    ONE PREDICATE (feature 287, FR-003; woods W12), read by `open_ground_patches` on the ring it is about to draw and by
    the gate's `test_a_woodland_commons_stands_on_dry_ground`. They used to disagree: the scan probed 3 x 3 points of the
    circumscribing square while the gate sampled 5 x 5 over the drawn ring's box, so a marsh finger between the probes
    could pass the scan and fail the rule. `marshes` is `marsh_ground(M)` - the drawn marsh (M7)."""
    if not marshes or len(ring) < 3:
        return 0.0
    xs = [float(p[0]) for p in ring]
    ys = [float(p[1]) for p in ring]
    x0, x1, y0, y1 = min(xs), max(xs), min(ys), max(ys)
    soaked = 0
    for i in range(5):
        for j in range(5):
            x = x0 + (x1 - x0) * (i + 0.5) / 5
            y = y0 + (y1 - y0) * (j + 0.5) / 5
            if any(point_in_poly(x, y, m) for m in marshes):
                soaked += 1
    return soaked / 25.0


_EDGE_SAMPLE = 30.0  # px between the samples `crop_edge_points` takes along a field edge: a third of the scan's 90 px lattice


def crop_edge_points(crops: Sequence[Poly], every: float = _EDGE_SAMPLE) -> PointGrid:
    """The edges of the field ground, sampled every `every` px and filed in a grid, so the height of the field nearest a
    seat is one grid read (269 B27; a paddy envelope's vertices can stand hundreds of px apart, so the vertices alone
    would measure the wrong stretch of edge)."""
    grid = PointGrid(128.0)
    for ring in crops:
        for (ax, ay), (bx, by) in zip(ring, [*ring[1:], ring[0]], strict=False):
            n = max(1, math.ceil(math.dist((ax, ay), (bx, by)) / every))
            grid.extend([(ax + (bx - ax) * k / n, ay + (by - ay) * k / n, ax + (bx - ax) * k / n, ay + (by - ay) * k / n, ax + (bx - ax) * k / n, ay + (by - ay) * k / n) for k in range(n)])
    return grid


def field_height_near(p: Pt, fall: Pt, grid: PointGrid) -> float:
    """The height (up the fall, -p.fall) of the field ground nearest `p` - the field a wood at `p` would adjoin. The grid
    is asked at a widening pad until it answers; with no field ground at all, -inf (every seat stands above it)."""
    pad = 128.0
    while pad <= 8192.0:
        near = [(math.dist(p, (q[0], q[1])), q) for q in grid.near(p[0], p[1], pad)]
        near = [t for t in near if t[0] <= pad]
        if near:
            q = min(near)[1]
            return -(float(q[0]) * fall[0] + float(q[1]) * fall[1])
        pad *= 2.0
    return -math.inf


def woodland_tier(p: Pt, fall: Pt, house_floor: float, field_height: float) -> int:
    """Where the record puts a village's fuel wood, as a rank (269 B27, research/questions/0077-village-fuel-woods-and-their-coppice-satoyama.html): 0 - higher than the field
    it adjoins and not below the lowest house (the nearest hill ground beyond the fields); 1 - not below the houses but
    not above that field (the level beside the fields, the record's fallback); 2 - downslope of every house, where the
    record puts the grass and riverbank commons, never the wood. Heights run up the fall: -p.fall.

    Research: where the fuel wood stands - research/questions/0077-village-fuel-woods-and-their-coppice-satoyama.drawing.html: higher ground beyond the fields first, the level next, never below the houses
    """
    h = -(p[0] * fall[0] + p[1] * fall[1])
    if h < house_floor:
        return 2
    return 0 if h > field_height else 1


_CHAIN_OFF = 0.2  # a third parcel within this fraction of the span off the line through two others stands in their row
"""Research: woods not in a ruled line - UNRESEARCHED: a third parcel within 0.2 of the span off two others' line"""


def in_a_ruled_line(p: tuple[float, float], centers: Sequence[tuple[float, ...]], frac: float = _CHAIN_OFF) -> bool:
    """Would a parcel at `p` stand in a ruled line with two parcels already placed - off the line through them by less
    than `frac` of the three's span (settlement-review of Inashiro, feature 261)? Varying the stride did not break the
    CHAIN the 2026-08-18 reviews recorded: the monotone score still seats each parcel on the first legal ground along the
    crop's keep-out edge, and Inashiro's three stood 5 ft off one line over 1,104 ft, Kashikawa's in a column.

    Research: woods not in a ruled line - UNRESEARCHED: three parcels off one line by less than 0.2 of their span refused
    """
    for i in range(len(centers)):
        for j in range(i + 1, len(centers)):
            a, b = (float(centers[i][0]), float(centers[i][1])), (float(centers[j][0]), float(centers[j][1]))
            span = max(math.dist(a, b), math.dist(a, p), math.dist(b, p))
            ab = math.dist(a, b)
            if span and ab and abs((b[0] - a[0]) * (a[1] - p[1]) - (a[0] - p[0]) * (b[1] - a[1])) / ab < frac * span:
                return True
    return False


def off_the_row(p: tuple[float, float], centers: Sequence[tuple[float, ...]], frac: float = _CHAIN_OFF) -> list[tuple[float, float]]:
    """Seats stepped sideways off the row `p` would stand in, nearest first: along the normal of the first row it joins,
    by 1, 1.5 and 2 times the off-line distance `in_a_ruled_line` asks for, each side (settlement-review of Inashiro,
    feature 261: the open ground there is a narrow band along the field's keep-out, every qualifying seat in the row)."""
    for i in range(len(centers)):
        for j in range(i + 1, len(centers)):
            a, b = (float(centers[i][0]), float(centers[i][1])), (float(centers[j][0]), float(centers[j][1]))
            if not in_a_ruled_line(p, [a, b], frac):
                continue
            ab = math.dist(a, b)
            nx, ny = -(b[1] - a[1]) / ab, (b[0] - a[0]) / ab
            span = max(ab, math.dist(a, p), math.dist(b, p))
            return [(p[0] + sgn * k * frac * span * nx, p[1] + sgn * k * frac * span * ny) for k in (1.05, 1.5, 2.0) for sgn in (1.0, -1.0)]
    return []


def seat_off_the_row(p: tuple[float, float], centers: Sequence[tuple[float, ...]], ok: Any) -> tuple[float, float] | None:
    """`p` itself when it stands in no row with two placed parcels; otherwise the nearest sideways step off the row that
    `ok` admits and that stands in no row either; otherwise None (feature 261)."""
    if not in_a_ruled_line(p, centers):
        return p
    return next((q for q in off_the_row(p, centers) if ok(q) and not in_a_ruled_line(q, centers)), None)


def reached_across(field: Poly, frm: Pt, to: Pt) -> bool:
    """Whether the straight walk `frm` -> `to` crosses the field's outline - the seat lies across the field (feature 261)."""
    return any(segments_cross(frm, to, a, b) for a, b in zip(field, list(field[1:]) + list(field[:1]), strict=False))


def open_ground_patches(s: Settlement, plan: SitePlan, count: int, size: float = 250.0) -> list[Poly]:
    """Find `count` patches of ground still open enough for a managed woodland - by SCANNING.

    Woodland (coppice, bamboo, tung-oil - the "economic forest") is a few discrete patches on the
    higher, farther ground, set back from the sun-needing crops by the scrub between. Ikegami places
    three by hand. The script cannot hand-place, so it scans a coarse lattice over the canvas and
    scores each candidate square on the two things that actually decide the answer:

      - it must be CLEAR of the crops by a real margin, and clear by MORE on the crop's sunny side,
        because a canopy south of a field shades it (this mirrors `woodland_clear_of_crops`, whose
        set-back is bigger to the south for exactly that reason);
      - it must be clear of the settlement, its lanes, its grove and its water.

    Among the candidates that qualify it prefers the ones furthest from the crop and highest up the
    slope, and it keeps them apart from each other so three patches read as three woods rather than
    one ragged mass. This is the stage that most obviously could not be done by pinning coordinates:
    "where is there still room" is a question about the map as it stands at that moment.

    Research:
        parcel count and size - UNRESEARCHED: `count` parcels from 250 ft, the ladder scaled 0.9-1.1 per map, rungs 0.8, 0.64, 0.5
        crop set-back - UNRESEARCHED: 80 px, 180 px on the crop's sunny side, relaxed to 40 and 100
        keep-outs - UNRESEARCHED: 150 px from houses, 90 from wells, 120 past the pond, 70 from lanes, 60 from streams, 110 round the belt and the houses
        where the fuel wood stands - research/questions/0077-village-fuel-woods-and-their-coppice-satoyama.drawing.html: ranked by `woodland_tier`, below-the-houses seats dropped
        near side of the field preferred - research/questions/0077-village-fuel-woods-and-their-coppice-satoyama.drawing.html: seats not across the field from the houses taken first
        parcels kept apart - UNRESEARCHED: each one's exclusion 1.15-2.5 of the size
        aspect and bearing - UNRESEARCHED: up to 2.2:1, laid across the fall within 20 deg
        line follows its bounds - research/questions/0077-village-fuel-woods-and-their-coppice-satoyama.drawing.html: within LOT_BOUND_REACH of a lane, brook or field the line runs alongside
        mostly dry - research/questions/0077-village-fuel-woods-and-their-coppice-satoyama.drawing.html: no sample of the parcel in marsh (WET_SHARE_CAP 0)
        on the page - CONVENTION: WOODLAND_BBOX_FLOOR of the ring inside the view
        woods not in a ruled line - UNRESEARCHED
        nearest seat preferred - research/questions/0077-village-fuel-woods-and-their-coppice-satoyama.drawing.html: the nearest slope beyond the fields
        per-parcel size bands - UNRESEARCHED: 0.82-1.18 of the half-size by band, then a 0.84 smaller try
        scan reach - UNRESEARCHED: confined to 210 px past the content box
    """
    dx, dy = plan.fall
    keep: list[tuple[float, float, float]] = []  # (x, y, radius) of everything to stay clear of
    for h in s.M.get("houses", []):
        keep.append((h["x"], h["y"], 150.0))
    for wl in s.M.get("wells", []):
        keep.append((wl["x"], wl["y"], 90.0))
    pond = s.M.get("pond")
    if pond:
        keep.append((pond[0], pond[1], max(pond[2], pond[3]) + 120.0))
    lanes: list[tuple[Poly, float]] = [(ln["pts"], 70.0) for ln in s.M.get("lanes", [])]
    # THE COPPICE IS A DISTINCT WOOD from the fengshui grove, and must not merge into it
    # (`woodland_clear_of_grove`, which measures to each grove CLUMP, not to the belt outline - so a
    # patch merely touching the belt's edge already fails). Both groves count: the windbreak belt
    # behind the cluster, and the copse scattered through the gaps among the houses, whose footprint
    # is the house bbox. The margin is generous because a clump's drawn canopy overhangs its
    # recorded radius, and because two woods that nearly touch read as one ragged mass anyway.
    # Kept clear by RECTANGLE, not by a circle around the bounding box. A belt is a long thin band
    # and a cluster is usually longer than it is deep, so a circle sized to the LONG side leaves the
    # short side hugely over-reserved while a circle sized any tighter under-covers the ends - and
    # the ends are exactly where a patch slips in and merges with the grove.
    keep_rects: list[tuple[float, float, float, float]] = [title_pocket(s, plan)]
    if plan.belt:
        keep_rects.append((min(p[0] for p in plan.belt) - 110.0, min(p[1] for p in plan.belt) - 110.0, max(p[0] for p in plan.belt) + 110.0, max(p[1] for p in plan.belt) + 110.0))
    hxs = [h["x"] for h in s.M.get("houses", [])]
    hys = [h["y"] for h in s.M.get("houses", [])]
    if hxs:  # the copse's ground, which is the house cloud
        keep_rects.append((min(hxs) - 110.0, min(hys) - 110.0, max(hxs) + 110.0, max(hys) + 110.0))
    streams: list[tuple[Poly, float]] = [(st["poly"], 60.0) for st in s.M.get("streams", [])]
    # ...AND THE MARSH IS NOT OPEN GROUND (settlement-review x3, 2026-08-16: the kept-window
    # confinement pushed parcels onto the wet toe - Inashiro seated one 100% inside the marsh
    # with zero crowns, Sawada 97%, Mizuguchi ~60%; the crown filter refuses wet ground, so a
    # wet seat renders as a claimed woodland with almost no trees). "Still open" is not "dry":
    # a candidate square must keep every sample point out of every recorded marsh poly.
    # `woodland_commons_on_dry_ground` gates the result.
    marshes: list[Poly] = marsh_ground(s.M)  # the drawn marsh (feature 287, M7)

    # ...each marsh's y-span taken once (feature 287 perf): a ray test counts an edge only where `(yi > py) != (yj > py)`, so a
    # sample outside a ring's [lowest, highest) y is outside it without the walk - the same verdict
    crops: list[Poly] = [list(plan.envelope)] + [[(float(v[0]), float(v[1])) for v in d["poly"]] for d in s.M.get("dry_plots", [])]
    crop_pts = crop_edge_points(crops)  # the field ground's edge, sampled and indexed once, for `field_height_near` (269 B27)
    _hx = [h["x"] for h in s.M.get("houses", [])] or [plan.W / 2]
    _hy = [h["y"] for h in s.M.get("houses", [])] or [plan.H / 2]
    ccx, ccy = sum(_hx) / len(_hx), sum(_hy) / len(_hy)

    # THE PATCHES MUST NOT STRETCH THE FRAME. `crop_to_content` frames the map to its HARD features,
    # and a woodland patch is one - so a patch parked in a far corner of the working canvas drags the
    # crop out with it, leaving a band of empty scrub on one side and (worse) putting the map edge
    # beyond the reach of the drain brook, which then no longer runs off the frame. That is three
    # gate failures from one badly-sited wood: `crop_not_held_open_by_one_feature`,
    # `stream_runs_off_edge` and `stream_end_anchored`. So the scan is confined to the ground the
    # map already occupies, expanded by a margin - a coppice stands on the settlement's own high
    # ground, not a quarter mile out in nowhere.
    cbx0, cby0, cbx1, cby1 = content_box(s, plan, pad=210.0)
    step = 90.0

    # ...AND CONFINED TO THE PREDICTED KEPT WINDOW (known-open ledger 2026-08-16, Sawada: two of
    # three parcels wholly above the frame, the third half-cropped under the title; Kashikawa and
    # Mizuguchi the same shape). The commons never set the frame (crop_to_content: woods bleed at
    # the edge), so a parcel the keep-outs push past the future crop simply vanishes from the
    # sheet. The decision, over "let the crop admit them": the frame stays tight to the working
    # settlement - the documented reason commons do not set the frame at all - and a coppice is
    # walked-to-daily ground that belongs ON the sheet, so it is the coppice that moves. The
    # window is computed from the SAME source the crop will read (`_crop_boxes` -> hull + the
    # shared CROP_MARGIN), and at this stage it is final except for features that only GROW it -
    # so a parcel held inside it now is inside the kept view later.
    # `woodland_commons_within_the_frame` gates the result.
    # SINCE FEATURE 287 (M6) the window IS the view function: `frame_bounds`, the crop's own body over the crop's boxes and
    # the ground the frame reserves (an outside pocket, the confluence, the brook beside the field), which the view decided
    # at the end of this stage contains - a frame only GROWS after the scan (the belt's face), and a parcel's share inside a
    # larger frame is never smaller.
    _fx0, _fy0, _fx1, _fy1 = frame_bounds(s, plan)

    chosen: list[Poly] = []
    centers: list[tuple[float, float, float]] = []  # (x, y, this parcel's OWN exclusion radius - see the stride roll)
    # THE LADDER ITSELF IS ROLLED PER MAP (settlement-review x2, 2026-08-18). The shrink ladder's
    # rungs were the same four numbers on every map, so every tight composition fell to the SAME
    # bottom rung and produced the same wood: Kashikawa shipped a 121.7 ft stand with 18 crowns and
    # Sawada a 127.2 ft stand with 19 - two different hamlets, effectively one wood, and the
    # per-parcel size roll could not separate them because it only spans +/-15% of a rung they
    # SHARED. Scaling the whole ladder by a per-map factor moves the rungs themselves apart, so two
    # tight maps land on different sizes before the per-parcel roll even runs.
    _ladder = 0.90 + 0.20 * s._hjit(plan.W, plan.H, 76.0)
    # ...AND THE PARCEL SIZES ARE STRATIFIED, one per band, rather than drawn independently. A
    # continuous roll clusters near its own middle, which is exactly the reading being fixed:
    # Mizuguchi's four came out 292 / 294 / 290 / 269 ft - three of them inside 1.4% of each other,
    # perceptually one wood drawn three times, from a roll that was already +/-18% wide. Independent
    # draws will keep doing that (with four samples a near-tie somewhere is the NORMAL outcome, not
    # bad luck), so each accepted parcel instead TAKES a band and removes it from the pool: with
    # four parcels the multipliers are 0.865 / 0.955 / 1.045 / 1.135 and no two woods can land
    # within 9% of each other. Which parcel gets which band is still rolled from its own position,
    # so the sizes are not ordered by seating order.
    _bands = list(range(max(2, count)))
    # SHRINK BEFORE GIVING UP (settlement-review round 2, 2026-08-16): with the kept window and
    # the marsh both closed to it, a tight composition can offer no full-size seat at all - the
    # first dry pass seated ZERO parcels on Kashikawa, the map NAMED for its oaks. A smaller
    # woodlot (200 ft, then 160 ft) is historically ordinary - coppice lots were whatever odd
    # corner the village spared - while an absent one on a name-story map is not. Unfilled slots
    # re-scan at the smaller sizes; a slot no size can seat is honestly dropped.
    # ...AND THE SET-BACK RELAXES BEFORE THE MAP GOES WOODLESS (Kashikawa round 3, 2026-08-16:
    # after the wells realigned, the generous 80/180 px crop set-backs plus the marsh closed the
    # whole kept window at every rung - zero parcels on the map NAMED for its oaks). The scan's
    # defaults are deliberately far above the gate's own floors (`woodland_clear_of_crops`:
    # CLEAR 14 px overhang, SHADE 69 px sunny-side at 1 ft/px), so a second pass at 40/100 px
    # still clears them - and the satoyama mosaic genuinely puts the woodlot on the margin
    # beside the field. ONE trap, found by the 48-seed sweep (Audit-24): `_clear_gap` measures
    # center-to-crop minus HALF, which overstates the true polygon gap by up to 0.414*half when
    # the crop lies diagonal to the square - the generous profile absorbed that slack, the
    # relaxed one shipped a parcel the check called shading. So the relaxed thresholds carry
    # the diagonal slack EXPLICITLY, per parcel size (the measured-gap floor then implies a
    # true-gap floor of 40/100, both above the check's 14/69). The generous profile always runs
    # first, so a roomy composition is byte-identical; only one that would otherwise draw NO
    # woodland tightens.
    for _sb_normal, _sb_sunny in ((80.0, 180.0), (40.0, 100.0)):
        if len(chosen) >= count:
            break
        for size_try in (size * _ladder, size * 0.8 * _ladder, size * 0.64 * _ladder, size * 0.5 * _ladder):
            if len(chosen) >= count:
                break
            # A RUNG UNDER THE LEGIBILITY FLOOR IS NOT OFFERED AT ALL. The first cut clamped each
            # candidate up to the floor and then dropped the parcel when the clamped size did not
            # fit, which needed a fall-through nobody could reach in a test; skipping the rung says
            # the same thing in one line and leaves `half_used = half` unconditionally safe, because
            # every rung that survives to the accept block is already above the floor. Either way a
            # settlement whose ground cannot hold a legible commons draws FEWER, never smaller.
            if size_try < _COMMONS_FLOOR_FT:
                continue
            half = size_try / 2.0
            _sb_pad = 0.415 * half if _sb_normal < 80.0 else 0.0  # the diagonal slack (see above); the generous profile keeps its historical thresholds exactly
            _sb_n, _sb_s = _sb_normal + _sb_pad, _sb_sunny + _sb_pad
            # MIRROR THE CHECK'S WINDOW, NOT JUST ITS FORMULA (2026-08-18). The kept-window
            # confinement above and `woodland_commons_within_the_frame` are meant to be the same
            # rule, and they were not: the check asks for **70% of the parcel's bbox** inside the
            # view and says in as many words that a parcel clipping at the edge "reads as 'more wood
            # that way' and is fine", while the scan demanded the whole square inside the window
            # plus a further 16 px. Being stricter than your own gate sounds safe and is not - it
            # cost two of the four hamlets their woodland outright. Measured before the fix: at
            # EVERY rung of the shrink ladder and BOTH set-back profiles, Kashikawa - the map named
            # 樫川, "oak river" - had ZERO qualifying seats out of a 231-286 point lattice and Sawada
            # exactly one, with the crop clause alone refusing 93-97% and the best achievable
            # clearance NEGATIVE (the square overlapped a paddy). Neither the shrink ladder nor the
            # set-back relaxation, both added FOR Kashikawa, could ever have worked: the binding
            # constraint was never the set-back, it was that a 20-household hamlet's field fills its
            # own frame and the scan would not let a wood touch the edge of it.
            #
            # So the seat is judged the way the check judges it, by AREA. The center may now sit up
            # to 0.6*half outside the kept window and the exact bbox-overlap fraction is tested in
            # `_ok` - which is what makes the both-axes corner case safe, where a per-axis box test
            # would pass two 0.4*half overhangs at 0.64 inside and ship a check failure. The floor
            # is 0.8 rather than the check's 0.7 because this window is a PREDICTION of the crop:
            # the margin absorbs the features that may still grow it.
            sx0, sy0 = max(cbx0 + 16.0, _fx0 - 0.6 * half), max(cby0 + 16.0, _fy0 - 0.6 * half)
            sx1, sy1 = min(cbx1 - 16.0, _fx1 + 0.6 * half), min(cby1 - 16.0, _fy1 + 0.6 * half)
            # the lines a lot's outline may follow (woods W26): the lanes and brooks at their keep-outs, the fields at this rung's set-back
            _lot_bounds = lot_bounds([ln for ln, _ in lanes], [st for st, _ in streams], crops, _sb_n)

            # THE QUALIFICATION IS ONE PREDICATE, so a seat can be re-asked after it is nudged. It
            # used to be an inline `if` that only the lattice scan could evaluate, which is why the
            # jitter below could not exist: there was no way to check that a moved seat was still
            # legal. Same shape as every other "placement and its check read one source" fix here.
            # ONE REGION PER SIZE ASKED (feature 297; the trap feature 284 recorded): `_ok` is re-asked with a different `half`
            # when the size roll re-tests a seat, and every keep-out is grown by `half`, so each size paints its own.
            regions: dict[tuple[float, float, float], Any] = {}

            def _ok(
                x: float,
                y: float,
                half: float = half,
                n: float = _sb_n,
                sn: float = _sb_s,
                sx0: float = sx0,
                sy0: float = sy0,
                sx1: float = sx1,
                sy1: float = sy1,
                regions: dict[tuple[float, float, float], Any] = regions,
            ) -> bool:
                # ONE guard clause, deliberately: the window bounds and the kept-window AREA are the
                # same question asked of a seat that may have been MOVED since the scan offered it
                # (the jitter and the size roll both re-ask). Split into two statements the bounds
                # half is unreachable in the corpus - no pool map or cohort seed happens to jitter a
                # seat past the edge - and an untested line in a predicate whose whole job is
                # re-asking is exactly what rots.
                if (
                    not (max(half + 40.0, sx0) <= x <= min(plan.W - half - 40.0, sx1) and max(half + 40.0, sy0) <= y <= min(plan.H - half - 40.0, sy1))
                    or (max(0.0, min(x + half, _fx1) - max(x - half, _fx0)) * max(0.0, min(y + half, _fy1) - max(y - half, _fy0))) < 0.8 * (2.0 * half) ** 2
                ):
                    return False  # off the window, or under the check's own 70%-of-bbox rule (0.8 here, for prediction slack)
                # EVERY KEEP-OUT A SQUARE'S CENTER IS ASKED OF, PAINTED ONCE PER SIZE (feature 297, FR-004, plan B4 - the GM:
                # "drawing a box and then filling it in"): the crops grown by their set-back (the sunny side's deeper south of each),
                # the keep circles and rectangles, the lanes and streams at their reach and the marsh, each grown by the square's
                # half, so a center is one raster read (`open_ground_region`)
                return bool(crops) and not open_ground_region(regions, half, n, sn, crops, keep, keep_rects, lanes + streams, marshes, (sx0, sy0, sx1, sy1)).taken(x, y)

            scored: list[tuple[float, float, float]] = []
            y = max(half + 40.0, sy0)
            while y <= min(plan.H - half - 40.0, sy1):
                x = max(half + 40.0, sx0)
                while x <= min(plan.W - half - 40.0, sx1):
                    if _ok(x, y):
                        # PREFER THE NEAREST QUALIFYING GROUND. The first version of this maximized distance from
                        # the crop instead, which drove every patch to the canvas's far upslope margin and the crop
                        # then cut three of four off the sheet. A settlement's coppice is walked to daily for fuel and
                        # fodder: the satoyama is the NEAREST hill ground (research/questions/0077-village-fuel-woods-and-their-coppice-satoyama.html), so within the
                        # ground the height rule below admits, nearer wins outright. The keep-outs above are what make
                        # it far ENOUGH. Height is no longer a term in this score (269 B27): it is `woodland_tier`.
                        scored.append((-math.hypot(x - ccx, y - ccy), x, y))
                    x += step
                y += step
            # THE WOOD STANDS BEYOND THE FIELDS, ON GROUND HIGHER THAN THE FIELDS IT ADJOINS (269 B27; research/questions/0077-village-fuel-woods-and-their-coppice-satoyama.html,
            # "Village fuel woods and their coppice (satoyama)" - houses, then fields, then the hill and wild land beyond; the
            # nearest hill slope round the settlement; the Musashino upland's groves, fields, then the konara wood on the
            # outer edge). The scorer used to ADD `0.35 * upslope` to nearness, and nearness outbid it: a 90 px step toward
            # the cluster was worth 257 px of height, so Kashikawa drew a stand 886 ft down the fan and 75 ft off the reed
            # marsh. A cross-slope preference (the along/cross ratio, 2026-08-18) narrowed that and still admitted ground
            # below the houses. The record's rule is a ranking, so it is one here (`woodland_tier`): a seat higher than the
            # nearest field ground and not below the lowest house first; then, where the map has no such ground, a seat on
            # the level beside the fields - not below the houses; a seat downslope of every house is never offered. Low wet
            # ground by a marsh or a river is left to grass and reeds: the marsh and stream keep-outs above refuse it, and it
            # lies below the houses on a fan. Reading "beyond the fields" as "higher than the field next to it" where the
            # ground slopes is the entry's own reading of "the slopes around the settlement".
            _fall = (dx, dy)
            _house_floor = min((-(float(h["x"]) * dx + float(h["y"]) * dy) for h in s.M.get("houses", [])), default=-math.inf)
            _tiers = [woodland_tier((t[1], t[2]), _fall, _house_floor, field_height_near((t[1], t[2]), _fall, crop_pts)) for t in scored]
            # a RANK, not a filter, below the downslope refusal: every tier-0 seat outranks every tier-1 one (the 1e9 dwarfs any
            # distance on a canvas), so the level is taken only once the ground above the fields is used up - "where the map
            # has no such ground" read per parcel, as the count is a target the scan meets only where there is open ground
            scored = [(t[0] - 1e9 * k, t[1], t[2]) for t, k in zip(scored, _tiers, strict=True) if k < 2]
            # ...AND ON THE HOUSES' SIDE OF THEIR FIELD (settlement-review of Inashiro, feature 261): a coppice walked to daily
            # for fuel and fodder stands on the hillside the settlement backs onto, and with the houses seated against the
            # wind Inashiro's parcels went up across the paddy from every house. A preference as the one above: where no seat
            # is reached from the cluster without crossing the field, the rest are still offered.
            _near_side = [t for t in scored if not reached_across(plan.envelope, (ccx, ccy), (t[1], t[2]))]
            if _near_side:
                scored = _near_side
            # ...NOT IN A ROW: a seat in line with two placed parcels is stepped sideways off the row where the ground allows,
            # and refused where it does not - the count is a target the scan already meets only where there is open ground
            # (a map with one parcel is common), and a ruled chain is the defect two reviews recorded (Inashiro's band lies
            # between the field's keep-out and the frame's corner: its third parcel had nowhere off the line)
            for _, x, y in sorted(scored, reverse=True):
                if len(chosen) >= count:
                    break
                if any(math.hypot(x - cx0, y - cy0) < _ex0 for cx0, cy0, _ex0 in centers):
                    continue
                _off = seat_off_the_row((x, y), centers, lambda q: _ok(*q) and not any(math.hypot(q[0] - cx0, q[1] - cy0) < _ex0 for cx0, cy0, _ex0 in centers))
                if _off is None:
                    continue  # the stride varied and the line did not; with no ground off the row, no parcel here
                x, y = _off
                # OFF THE LATTICE, AND NOT ALL ONE SIZE (settlement-review, Mizuguchi 2026-08-18).
                # The scan samples a uniform 90 px lattice, scores every seat by one monotone
                # function (near the cluster, leaning upslope) and then takes the best remaining seat
                # outside a FIXED separation radius. Those three together do not merely tend to
                # produce an even chain - they produce one by construction, and Mizuguchi shipped the
                # proof: three identical 250 x 250 ft squares at (456,967), (726,697), (996,427),
                # offsets of exactly (+270,-270) and (+270,-270), reading as three stamps of one wood
                # marching up a ruled diagonal. The fourth parcel, seated off the ladder at a
                # different size, reads fine and is the control.
                #
                # So the LATTICE is a sampling artifact and must not survive into the output. The
                # accepted seat is nudged up to half a step off it and the parcel's size rolled down
                # by up to a fifth, both from `_hjit` - positional, so a map is unchanged by
                # regeneration and two maps differ from each other. Every nudge is re-asked through
                # `_ok`, and a nudge that would not qualify is simply not taken: this can only move a
                # legal seat to another legal seat, never widen what the scan admits.
                # VARY THE STRIDE, NOT JUST THE SEAT (settlement-review x2, 2026-08-18 - the FIRST
                # version of this fix did not work and this is why). Jittering the accepted seat off
                # the lattice killed the identical-STAMP reading, and left the CHAIN: Mizuguchi still
                # stepped 379.7 ft then 361.9 ft up one axis with the middle parcel 3.1% off the
                # straight line, and Inashiro independently stepped 366 / 371 / 392 ft. Measured, and
                # the cause is not the lattice at all - it is that a MONOTONE score plus a FIXED
                # `size * 1.5` exclusion radius means each parcel is by construction the nearest
                # qualifying seat just outside the last one's circle, so the stride is pinned at
                # ~375 ft however the seats are dithered. A +/-45 px jitter is +/-12% of that stride:
                # far too small to break a rhythm it does not touch. So each parcel now carries its
                # OWN exclusion radius, rolled 1.15x-2.50x its size from its own position, and the
                # spacing varies because the generative rule varies rather than because the output
                # is dithered.
                jx = x + (s._hjit(x, y, 71.0) - 0.5) * step
                jy = y + (s._hjit(x, y, 72.0) - 0.5) * step
                # ...and the size roll is wider than it was, for the reason recorded at `_ladder`:
                # +/-15% of a shared rung left two maps' stands 1.8% apart. This is a DEGREE on a
                # continuum (calibrated liberty), not a knob - `research/questions/0077-village-fuel-woods-and-their-coppice-satoyama.html` treats a lot's size as whatever ground the village spared, not
                # a surveyed figure, so a narrow roll was narrower than our own doctrine.
                # TRY THE MIRRORED SIZE BEFORE FALLING BACK TO THE RUNG. Widening the roll upward
                # made it WORSE at first, in a way only the artifact showed: a grown parcel often
                # fails `_ok` (it is asking for ground the rung already fitted snugly), the ladder
                # fell straight back to `half`, and Mizuguchi shipped three parcels at 292 / 294 /
                # 290 ft - the exact rung, three times, more identical than before the roll existed.
                # Reflecting the factor about 1.0 gives a distinctly SMALLER parcel to try before
                # surrendering to the rung, so a refused growth becomes variety instead of a twin.
                _bi = min(int(s._hjit(x, y, 73.0) * len(_bands)), len(_bands) - 1) if _bands else 0
                _f = 0.82 + 0.36 * (((_bands[_bi] if _bands else 0) + 0.5) / max(2, count))
                # The band first; then one distinctly SMALLER try, because a grown parcel is asking
                # for ground the rung only just fitted and the plain fallback to `half` is what
                # produced the near-identical trio above.
                # ...BUT NEVER BELOW A COMMONS' OWN FLOOR. The band multipliers compound with the
                # per-map ladder, and at the ladder's bottom rung that took Kashikawa's smaller
                # parcel to 103 ft - under the ~116 ft that THIS change already judged "a copse, not
                # a commons" when it made the size roll two-sided. A floor is the honest guard: a
                # parcel too small to read as a managed wood should not be drawn smaller to satisfy
                # a variance rule. If the floor does not fit, the rung fallback still applies, so
                # this can only ever make a parcel larger or leave it alone.
                half_used = half  # the rung: the scan already tested this seat at REACH, so the rotated parcel fits
                # the reach a rotated parcel needs is its circumscribing half - a 2.2:1 parcel of the
                # same AREA reaches sqrt(2.2) further along its long axis than the square did, so the
                # candidate is tested at that reach and the rotation cannot buy ground.
                for _cand in (max(half * _f, _COMMONS_FLOOR_FT / 2.0), max(half * 0.84, _COMMONS_FLOOR_FT / 2.0)):
                    # the jitter moves a seat off the row check it passed, so the moved seat is asked the row rule too (woods W04)
                    if _ok(jx, jy, _cand) and not in_a_ruled_line((jx, jy), centers):
                        x, y, half_used = jx, jy, _cand
                        break
                    if _ok(x, y, _cand):
                        half_used = _cand
                        break
                # THE FLOOR WAS NOT A FLOOR (settlement-review, Kashikawa 2026-08-18 round 2). Both
                # candidates are clamped to `_COMMONS_FLOOR_FT`, but when neither fitted, control fell
                # through to `half_used = half` - the UNCLAMPED rung - and Kashikawa shipped a 116.6 ft
                # parcel, under the floor, at the very size this file's own docstring calls "a copse,
                # not a commons". The comment above claimed the clamp "can only ever make a parcel
                # larger or leave it alone" and the fall-through did the one thing it forbade.
                #
                # The rung is now only taken if the rung itself clears the floor; otherwise the parcel
                # is DROPPED, which is what `_COMMONS_FLOOR_FT`'s docstring says should happen - "a
                # settlement whose ground genuinely cannot hold one draws FEWER parcels rather than
                # smaller ones". The band is returned to the pool by not popping it until acceptance,
                # so a dropped parcel does not silently consume a size band the next one could use.
                if _bands:
                    _bands.pop(_bi)
                # ...AND IT IS NOT A SQUARE (settlement-review x2, 2026-08-18 round 2). Every woodland
                # parcel the engine had ever drawn was `rot: 0` with `w == h` - 12 of 12 across the
                # four hamlets - and the reviewers' point was that the size work made this MORE
                # conspicuous, not less: four identical squares read as one repeated stamp, but four
                # differently-sized perfect squares read as a lattice with a size knob bolted on,
                # because the varying dimension proves the constant one was a choice.
                #
                # The record is decisive rather than two-sided, so this is calibrated liberty and not
                # a knob between forms: an *iriai* wood's edge was a line the villages agreed or were
                # given, and it bent (research/questions/0077-village-fuel-woods-and-their-coppice-satoyama.html: a 1612 ruling map sealed along the line at
                # its ends and bends); that it ran by ridge, stream and path is a GUESS - no page read
                # says so (269 B27; the Yamaguni study cited for it says nothing of boundaries), and satoyama
                # coppice sits on the slope break - there is no attested rectilinear woodlot. Aspect and bearing therefore roll per parcel from its
                # own position, AREA HELD (hw*hh is unchanged, so every size rule above still means
                # what it says), and the bearing is taken off the fall line because a hillside wood
                # runs with the contour rather than with the page.
                #
                # The keep-out tests keep using the CIRCUMSCRIBING half, so a rotated parcel clears
                # everything a square of the same reach would have: rotating a footprint must not be
                # able to buy ground the square could not have had.
                # THE ASPECT ADAPTS TO THE ROOM, it does not demand it. Testing every seat at the
                # worst-case circumscribing reach was the first cut and it was far too strict: it
                # left Kashikawa - the oak map - woodless again, undoing the morning's fix, because
                # that map's ground is genuinely tight and a 1.49x reach requirement refuses nearly
                # all of it. So the rolled aspect is a TARGET, stepped down to whatever this seat
                # actually supports, with the square as the floor. A roomy seat gets a long wood, a
                # tight one still gets its square, and no map loses a parcel to the shape roll.
                # The ladder steps DOWN from the rolled target toward the square. The first cut wrote
                # the rungs as literals (target, 1.6, 1.3) and so could step UP - a seat that rolled
                # 1.2 was then offered 1.6, a LONGER parcel than the roll asked for - and it needed a
                # guard clause to stop that, which was itself unreachable. Scaling the rolled excess
                # says what was meant in one expression: at the last rung the excess is 45% of the
                # roll, and if even that will not fit the square always does, because the seat was
                # accepted at exactly this half.
                # THE LADDER MUST VET THE SHAPE THAT GETS DRAWN, NOT A SQUARE STAND-IN FOR IT
                # (2026-08-19). `_ok` tests an axis-aligned square of the LONG half, which sounds
                # conservative and is not: the parcel is drawn as a rotated rectangle, and rotating a
                # box GROWS its axis-aligned bbox - by up to sqrt(2), at 45 degrees, even for a
                # square. `woodland_commons_within_the_frame` measures that bbox. So a seat could
                # pass the ladder at 0.8 of a square and draw a parcel 0.67 inside the window, which
                # is exactly what cohort seed 33 did the moment the cluster change walked it to the
                # edge: a check and the thing it checks measuring different quantities, the same
                # defect as the drawn-vs-band aspect confusion in `CLUSTER_DRAWN_ASPECT`.
                #
                # The bearing is therefore computed BEFORE the ladder (it never depended on the
                # aspect - only on the fall direction and the seat), and each rung is tested on the
                # true rotated bbox. The line this replaced carried the comment "the scan already
                # tested this seat at REACH, so the rotated parcel fits", which was an assumption
                # stated as a fact; it is now the thing being checked.
                _bear = math.radians(math.degrees(math.atan2(dy, dx)) + 90.0 + 40.0 * (s._hjit(x, y, 78.0) - 0.5))
                _bc, _bs = math.cos(_bear), math.sin(_bear)  # not `_cb` - that name is the crop-boxes list above

                def _bbox_ok(hw: float, hh: float, x: float = x, y: float = y, _bc: float = _bc, _bs: float = _bs) -> bool:
                    """This seat's rotated-bbox test - see `parcel_bbox_ok`, which holds the body."""
                    return parcel_bbox_ok(x, y, hw, hh, _bc, _bs, (_fx0, _fy0, _fx1, _fy1))

                _excess = 1.2 * s._hjit(x, y, 77.0)
                _asp = 0.0  # 0.0 means "no rung fitted" - distinct from the square, which is 1.0
                for _step in (1.0, 0.72, 0.45, 0.0):
                    _try = 1.0 + _excess * _step
                    if _ok(x, y, half_used * math.sqrt(_try)) and _bbox_ok(half_used * math.sqrt(_try), half_used / math.sqrt(_try)):
                        _asp = _try
                        break
                if not _asp:
                    # SHRINK BEFORE DROPPING - see `fit_square_parcel`, which holds the ladder and is
                    # unit-tested over plain numbers. Written as one expression rather than an `if`
                    # on purpose: the DECISION is tested in that function, so a separate branch here
                    # is plumbing that only a real site can execute, and pinning a cohort member to
                    # execute it is what made `test_woodland_shrink_147` rot twice (features 147 and
                    # 149) before it was re-aimed a third time.
                    _cand_half = fit_square_parcel(half_used, _COMMONS_FLOOR_FT / 2.0, lambda _h, _x=x, _y=y: _ok(_x, _y, _h) and _bbox_ok(_h, _h))
                    half_used, _asp = (_cand_half, 1.0) if _cand_half is not None else (half_used, _asp)
                if not _asp:
                    # Nothing fits. Drop the parcel rather than draw one the crop will cut off: a
                    # settlement whose ground cannot hold a legible commons draws FEWER, never one
                    # that is half off the sheet.
                    #
                    # The size band popped above is NOT put back. Restoring it would mean pushing
                    # `_bi` - an INDEX into a list that has since been mutated - back as a VALUE,
                    # which silently corrupts the size distribution; and a consumed band costs only a
                    # little size variety on a map that just declined to seat a parcel anyway.
                    continue
                _hw, _hh = half_used * math.sqrt(_asp), half_used / math.sqrt(_asp)
                _ring = _parcel_outline(s, x, y, _hw, _hh, _bc, _bs)
                # ...AND ITS LINE FOLLOWS WHAT BOUNDS IT (feature 287, woods W26 - a GUESS, research/questions/0077-village-fuel-woods-and-their-coppice-satoyama.html: no page
                # read says a lot's line followed stream, path or field): within `LOT_BOUND_REACH` of a brook, a lane or the
                # field edge the ring is cut to run parallel to it (`follow_the_bounds`, pulled in only, so every keep-out
                # above still holds) and asked `lot_follows_its_bounds`; the rules below are then asked of the cut ring. A cut
                # takes ground, so the cut ring is held to the legibility floor too (`_COMMONS_FLOOR_FT`, its widest extent):
                # a lot the cut leaves under it is not drawn - FEWER, never smaller
                _bounds = bounds_near(_lot_bounds, (x, y), _hw)
                _ring = follow_the_bounds(_ring, (x, y), _bounds)
                if not lot_follows_its_bounds(_ring, _bounds) or ring_span(_ring) < _COMMONS_FLOOR_FT:
                    continue
                # ...AND THE RING THAT IS DRAWN STANDS ON DRY GROUND, by the rule's own measure (feature 287, FR-003; woods
                # W12): the 3x3 probe above samples the circumscribing SQUARE, and a marsh finger threading between its
                # probes can still put most of the drawn ring in the wet - so the ring is asked `parcel_wet_share`, the one
                # predicate the gate reads too, and a wet ring is refused for the next scored seat
                if parcel_wet_share(_ring, marshes) > WET_SHARE_CAP:
                    continue
                # ...AND THE RING THAT IS DRAWN IS ON THE PAGE, by the rule's own measure (woods W14): the rotated rectangle's box
                # passed above, and the ring inside it has a box of its own. The frame is the view as it stands (`frame_bounds`),
                # which the decided view contains - only the belt's face is added after this - so the share can only grow
                if parcel_inside_share(_ring, (_fx0, _fy0, _fx1, _fy1)) < WOODLAND_BBOX_FLOOR:
                    continue
                # ...AND IT HAS ROOM FOR A WOOD (woods W13): the crowns the ring is sure of on the commons' own keep-outs, as
                # `commons` will stock it (`woodland_room`) - a ring mostly over the padded crop is not offered as a wood
                if len(s.woodland_room(_ring)) < WOODLAND_MIN_CROWNS:
                    continue
                # ...AND THE POINT THE RECORD CARRIES STANDS IN NO ROW (feature 287, woods W04). The seat above was asked the row
                # rule, but the commons record carries the drawn RING's box center (`ring_center`), which the ring's wander moves
                # off the seat - a third point nobody had asked. So the rule is asked of exactly that point against the points
                # the parcels already chosen will carry, in the order they are drawn and recorded; a ring in a row is refused
                # for the next scored seat, and a map whose ground offers none draws fewer parcels (the count is a target).
                if in_a_ruled_line(ring_center(_ring), [ring_center(c) for c in chosen]):
                    continue
                chosen.append(_ring)
                centers.append((x, y, size * (1.15 + 1.35 * s._hjit(x, y, 74.0))))
    return chosen


def _parcel_outline(s: Settlement, x: float, y: float, hw: float, hh: float, bc: float, bs: float, n: int = 12) -> Poly:
    """A coppice parcel's outline: an IRREGULAR ring inside the rolled ellipse, never a rectangle.

    THE RESEARCHED RULING WAS ONLY HALF DRAWN (GM 2026-08-27, feature 133 T36: *"those coppice
    Patches. basically it looked like little squares ... I want to make sure that that is intentional
    and based on research rather than just happenstance"*). It was happenstance. The 2026-08-18
    review pass had already found the record decisive - *iriai* commons boundaries were customary (it
    said "described by ridge, stream and path", which is a GUESS: research/questions/0077-village-fuel-woods-and-their-coppice-satoyama.html finds a line
    the villages agreed or were given, bent to the ground, and no page on what it followed), satoyama coppice sits on the slope break, and there is no
    attested rectilinear woodlot - and implemented it as a ROTATED RECTANGLE with the plain square as
    the fallback for a tight seat. A rotated rectangle is still rectilinear, and on Inashiro all three
    parcels took the fallback: `rot 0`, `w == h`, twelve of twelve across the pool before that. So the
    outline is now what the ruling says: a ring that follows no page axis, its radius wandering the
    way a boundary bent to the ground does (whether by ridge, stream and path is a GUESS - 0077).

    Built INSIDE the tested reach, on purpose. Every keep-out test in `open_ground_patches` was made
    at the ellipse's circumscribing half, so a vertex that never leaves the ellipse can never buy
    ground the square could not have had. The radius runs 0.80-1.00 of the ellipse's, on two low
    harmonics seeded from the parcel's own position (`_hjit`), so the ring is smooth rather than
    spiky - a wood's edge wanders, it does not serrate - and the AREA comes out at ~85% of the
    ellipse's: the size rules above still bound it, from above. Recorded in research/questions/0077-village-fuel-woods-and-their-coppice-satoyama.html, with the one form deliberately NOT drawn here: the strip
    holdings of a shinden dry-upland village, which are a settlement form, not a woodlot knob.

    Research: wandering edge - research/questions/0077-village-fuel-woods-and-their-coppice-satoyama.drawing.html: radius 0.80-1.00 of the ellipse on two low harmonics, never a rectangle
    """
    p1, p2 = 2 * math.pi * s._hjit(x, y, 79.0), 2 * math.pi * s._hjit(x, y, 80.0)
    ring: Poly = []
    for i in range(n):
        t = 2 * math.pi * (i + 0.35 * (s._hjit(x + i, y, 81.0) - 0.5)) / n
        re = hw * hh / math.hypot(hh * math.cos(t), hw * math.sin(t))
        f = 0.80 + 0.20 * (0.5 + 0.25 * math.sin(2 * t + p1) + 0.25 * math.sin(3 * t + p2))
        lx, ly = re * f * math.cos(t), re * f * math.sin(t)
        ring.append((x + lx * bc - ly * bs, y + lx * bs + ly * bc))
    return ring


# ---- woods W26: a lot's line follows what bounds it on the ground ---------------------------------------------------
# GUESS (research/questions/0077-village-fuel-woods-and-their-coppice-satoyama.html, 0077): a wood's edge was a line the villages agreed or were
# given, and it bent; "whether it followed ridges, streams and paths is a GUESS: no page read says so." This builds that
# working answer: where a lot's outline comes within a small reach of a brook, a lane or a field's edge, its line keeps off
# that feature and runs parallel to it, rather than wandering near it or across it as a stamped disc would. The one form
# the record does attest as rectilinear (the Musashino strip holdings) is a settlement form and is not drawn here.

LANE_LOT_LINE = 70.0  # px from a lane's centerline: the scan's own lane keep-out (`open_ground_patches`), the lot's line along it
"""Research: lot line along a lane - UNRESEARCHED: 70 px from its centerline"""
STREAM_LOT_LINE = 60.0  # px from a brook's centerline: the scan's own stream keep-out, the lot's line along it
"""Research: lot line along a brook - UNRESEARCHED: 60 px from its centerline"""
LOT_BOUND_REACH = 45.0
"""How near (px, 1 ft at the hamlet scale) a lot's outline must come to a feature's line before the line bounds it.

GUESS, a calibrated degree (research/questions/0077-village-fuel-woods-and-their-coppice-satoyama.html is silent on any distance): half the scan's 90 px lattice step, so a
seat the lattice put within one half-step of a keep-out has its facing side drawn along that keep-out, while a lot a whole
step or more away keeps its free wandering edge. A larger reach would bound more lots and cut more of their ground.

Research: lot line reach - research/questions/0077-village-fuel-woods-and-their-coppice-satoyama.drawing.html: 45 ft"""

Bound = tuple[list[tuple[Pt, Pt]], float, "Poly | None"]  # (segments, the lot's line distance, the ring when closed)


def lot_bounds(lanes: Sequence[Sequence[Pt]], streams: Sequence[Sequence[Pt]], crops: Sequence[Poly], crop_setback: float) -> list[Bound]:
    """The features a coppice lot's line may follow (woods W26): each lane and brook as its segments at the scan's keep-out,
    each field ring as its closed edge at the set-back the scan seated the lot with (a point inside a field is on the wrong
    side of its line)."""

    def _segs(pts: Sequence[Pt], closed: bool) -> list[tuple[Pt, Pt]]:
        ps = [(float(p[0]), float(p[1])) for p in pts]
        return list(zip(ps, ps[1:] + ps[:1] if closed else ps[1:], strict=False))

    return [
        *((_segs(ln, False), LANE_LOT_LINE, None) for ln in lanes if len(ln) >= 2),
        *((_segs(st, False), STREAM_LOT_LINE, None) for st in streams if len(st) >= 2),
        *((_segs(c, True), crop_setback, [(float(p[0]), float(p[1])) for p in c]) for c in crops if len(c) >= 3),
    ]


def _bound_margin(p: Pt, bound: Bound) -> float:
    """How far `p` stands off `bound`'s feature, signed: negative inside a field's ring."""
    segs, _line, ring = bound
    d = min(seg_dist(p[0], p[1], a, b) for a, b in segs)
    return -d if ring is not None and point_in_poly(p[0], p[1], ring) else d


def _follows(p: Pt, bounds: Sequence[Bound], reach: float, tol: float = 1.0) -> bool:
    """One vertex of the lot's line: for every bound, either ON its line (within `tol`) or beyond `reach` of it."""
    return all(abs((d := _bound_margin(p, b)) - b[1]) <= tol or d >= b[1] + reach - tol for b in bounds)


def lot_follows_its_bounds(ring: Sequence[Pt], bounds: Sequence[Bound], reach: float = LOT_BOUND_REACH) -> bool:
    """THE ONE PREDICATE (feature 287, woods W26 - GUESS, research/questions/0077-village-fuel-woods-and-their-coppice-satoyama.html): does a coppice lot's line follow what
    bounds it? Where a vertex comes within `reach` of a brook's, a lane's or a field's line it lies on that line or keeps
    off it by the reach - a ragged wander near a feature, or a vertex over its line, is refused; and no edge of the lot
    crosses a feature. `open_ground_patches` draws only rings this admits, cut by `follow_the_bounds`.

    Research: line follows its bounds - research/questions/0077-village-fuel-woods-and-their-coppice-satoyama.drawing.html: on the feature's line or clear of it by the reach, never across it
    """
    edges = list(zip(ring, [*ring[1:], ring[0]], strict=False))
    for b in bounds:
        if any(segments_cross(a, c, s0, s1) for a, c in edges for s0, s1 in b[0]):
            return False
    return all(_follows(p, bounds, reach) for p in ring)


def ring_span(ring: Sequence[Pt]) -> float:
    """A ring's widest axis-aligned extent - the measure the commons floor is held on."""
    xs, ys = [float(p[0]) for p in ring], [float(p[1]) for p in ring]
    return max(max(xs) - min(xs), max(ys) - min(ys))


def bounds_near(bounds: Sequence[Bound], center: Pt, radius: float) -> list[Bound]:
    """Only the segments of each bound that could come within `radius` of `center` (a field ring keeps its whole ring for
    the inside test) - a prefilter: a segment farther than that can bound no vertex of a lot of that radius."""
    out: list[Bound] = []
    for segs, line, ring in bounds:
        near = [(a, b) for a, b in segs if seg_dist(center[0], center[1], a, b) < radius + line + LOT_BOUND_REACH]
        if near:
            out.append((near, line, ring))
    return out


def follow_the_bounds(ring: Sequence[Pt], center: Pt, bounds: Sequence[Bound], reach: float = LOT_BOUND_REACH) -> Poly:
    """The lot's line cut to follow its bounds (woods W26 - GUESS, research/questions/0077-village-fuel-woods-and-their-coppice-satoyama.html): each vertex that
    `lot_follows_its_bounds` would refuse is pulled in along its ray toward the lot's own `center` until it keeps off
    every bound by that bound's line plus the reach - so the lot's facing side runs parallel to the brook, lane or field
    edge. Only ever pulled IN: the ring stays inside the reach the scan tested, so no keep-out can be crossed by the cut.
    A vertex no point of its ray can clear (the center itself too near) is left, and the predicate refuses the ring.

    Research: line follows its bounds - research/questions/0077-village-fuel-woods-and-their-coppice-satoyama.drawing.html: vertices pulled in until they run alongside the feature
    """
    out: Poly = []
    cx, cy = center
    for p in ring:
        if _follows(p, bounds, reach):
            out.append(p)
            continue

        def _at(f: float, p: Pt = p) -> Pt:
            return (cx + (p[0] - cx) * f, cy + (p[1] - cy) * f)

        def _clear(f: float) -> bool:
            q = _at(f)
            return all(_bound_margin(q, b) >= b[1] + reach for b in bounds)

        lo = next((k / 20.0 for k in range(19, -1, -1) if _clear(k / 20.0)), None)
        if lo is None:
            out.append(p)
            continue
        hi = lo + 0.05
        for _ in range(20):
            mid = (lo + hi) / 2.0
            lo, hi = (mid, hi) if _clear(mid) else (lo, mid)
        out.append(_at(lo))
    return out


def open_ground_region(
    cache: dict[tuple[float, float, float], Any],
    half: float,
    normal: float,
    sunny: float,
    crops: Sequence[Poly],
    keep: Sequence[tuple[float, float, float]],
    keep_rects: Sequence[tuple[float, float, float, float]],
    lines: Sequence[tuple[Poly, float]],
    marshes: Sequence[Poly],
    window: tuple[float, float, float, float],
) -> Any:
    """The ground a woodland square of half-side `half` may not CENTER on (feature 297, plan B4), as one `Region` built once per
    (half, set-backs) into `cache`: each crop grown by its set-back plus `half` (`_crop_refuses`'s `normal`), and by the sunny
    set-back over the band south of it (its `south_of` - the square's top below the crop's last 40 px, its center within the crop's
    x-span grown by `half`); the keep circles grown by `half`; the keep rectangles grown by `half`; the lanes and streams at their
    reach plus `half`; the marsh grown by `half` (a square with any of its nine points in a marsh is refused, `_wet`)."""
    key = (half, normal, sunny)
    got = cache.get(key)
    if got is None:
        import shapely
        from shapely.geometry import Polygon

        from l7r.diagram.settlement._geom.region import Region

        x0, y0, x1, y1 = window
        pad = max([normal, sunny]) + half + 40.0
        got = Region((x0 - pad, y0 - pad, x1 + pad, y1 + pad), 3.0)  # 3 px: the margin is two cells, 6 px; at 8 px its 16 px moved a parcel off the brook line its lot follows (test_hinterland_287)
        polys = [g if g.is_valid else g.buffer(0) for g in (Polygon(c) for c in crops if len(c) >= 3)]
        geoms: list[Any] = list(polys)
        pads: list[float] = [normal + half] * len(polys)
        if polys:  # ...the sunny set-back over the band south of each crop (`_crop_refuses`' `south_of`)
            b = shapely.bounds(polys)
            bands = shapely.box(b[:, 0] - half, b[:, 3] - 40.0 + half, b[:, 2] + half, b[:, 3] + sunny + half + 1.0)
            south = shapely.intersection(shapely.buffer(polys, sunny + half, quad_segs=4), bands)
            geoms += [g for g in south if not g.is_empty]
            pads += [0.0] * sum(1 for g in south if not g.is_empty)
        geoms += [shapely.Point(float(kx), float(ky)) for kx, ky, _kr in keep]
        pads += [float(kr) + half for _kx, _ky, kr in keep]
        geoms += [shapely.box(rx0, ry0, rx1, ry1) for rx0, ry0, rx1, ry1 in keep_rects]
        pads += [half] * len(keep_rects)
        for pl, reach in lines:
            if len(pl) >= 2:
                geoms.append(shapely.LineString([(float(q[0]), float(q[1])) for q in pl]))
                pads.append(float(reach) + half)
        for mp in marshes:
            if len(mp) >= 3:
                g = Polygon(mp)
                geoms.append(g if g.is_valid else g.buffer(0))
                pads.append(half)
        got.fill_many(geoms, pads)
        cache[key] = got
    return got


def _crop_refuses(center: Pt, half: float, crop: RingIndex, normal: float = 80.0, sunny: float = 180.0) -> bool:
    """Does this crop refuse a candidate square here - standing in it, or nearer than its set-back?

    The set-back is 80 px normally and 180 px when the square sits on the crop's SUNNY side (south,
    in screen terms) - the shading case. `woodland_clear_of_crops` uses 1 : 2.5-ish set-backs for the
    same reason; this is deliberately a little more generous than the check, so a patch that passes
    here passes there with room to spare rather than sitting on the line.

    One crop at a time, from its ring index (feature 218): the scan used to measure every candidate
    against every edge of every crop to return the nearest distance, and its only caller asked
    whether that was None. The distance is asked of the index only under the widest set-back this
    crop could apply (+1 px of slack), and the refusal is the expression the scan ran - `d - half <
    set-back` on the true distance - so the verdict is the same to the bit.

    Research: crop set-back - UNRESEARCHED: 80 px, 180 px on the crop's sunny side
    """
    cx, cy = center
    if crop.inside(cx, cy):
        return True
    south_of = cy - half > crop.y1 - 40 and crop.x0 - half < cx < crop.x1 + half
    limit = sunny if south_of else normal
    dist = crop.edge_within(cx, cy, limit + half + 1.0)
    return dist is not None and dist - half < limit


def _lines_at(cache: dict[float, PointGrid], lines: Any, half: float) -> PointGrid:
    """`seg_reach_index(lines, half)`, built once per `half` into `cache` (feature 278)."""
    grid = cache.get(half)
    if grid is None:
        grid = cache[half] = seg_reach_index(lines, half)
    return grid


def _near_line(center: Pt, half: float, pts: Sequence[Pt], pad: float) -> bool:
    cx, cy = center
    return any(seg_dist(cx, cy, pts[i], pts[i + 1]) < half + pad for i in range(len(pts) - 1))
