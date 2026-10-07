"""Split from hamletgen/homesteads.py by feature 173 - see this package's CLAUDE.md for the index.

Research: seat geometry - NONE: offsets, sampling and measures; the units that decide carry their own claims
"""

from __future__ import annotations

import math
from collections.abc import Mapping
from typing import Any

from l7r.diagram.settlement import Settlement
from l7r.diagram.settlement.houses import HOUSE_PADDY_GAP_FT
from l7r.diagram.sitegen.geom import unit

from ..consts import BUNDLE_PITCH, CLUSTER_ROW_SPAN, CLUSTER_SPAN_FACTOR, LANE_FRONTAGE_STANDOFF, Pt
from ..plan import SitePlan

# A pixel of margin and the rounding of a turn keyed on a 4 px cell (`bearing.KEY_CELL_PX`). It was the +/-5 degree rake's
# reach past the axis-aligned box; since 269 B18 a house may turn 30 degrees or a quarter turn, and the stage measures that
# reach per seat (`turn_the_seat`) instead of carrying it here as slack.
STANDOFF_SLACK_PX = 3.0
DEFAULT_HOUSE = (46.0 * 1.35, 28.0 * 1.10)  # the LARGEST nucleated house `_try_place_bundle` rolls, in px at 1 px = 1 ft; the stage passes the map's own
"""Research: largest house - research/questions/0029-farmhouses-minka.drawing.html: 46 x 28 ft scaled by 1.35 and 1.10"""

# ---- STAGE 5: the homesteads --------------------------------------------------------------------


def front_row(
    plan: SitePlan,
    count: int,
    standoff: float | None = 46.0,
    chains: Any = (),
    house: tuple[float, float] | None = None,
    envelope: tuple[float, float, float, float] | None = None,
    with_normals: bool = False,
    pitch: float = BUNDLE_PITCH,
    reach: float | None = None,
) -> list[Any]:
    """Seats for the row of homesteads that FRONTS the field, offset from the field OUTLINE itself. `pitch` is the step
    along the chains (a farm with its own grove is far wider than the nucleated pitch) and `reach` how far along the seat
    the row may run (default: the rolled cluster's stretch; a row village takes the whole field edge - feature 291).

    Offsetting from the cluster band's straight near face is not the same thing and is not good
    enough: the outline curves away from the band, so a row laid along the face can sit 32 px from
    the field at its middle and 300 px from it at its ends - a front row that is 300 px off its own crop
    at the ends on a map whose cluster is plainly beside its paddy. (This paragraph used to rest that on
    `field_ringed` (retired, feature 141), a check feature 141 retired; the geometry is the reason, and it did not need one.)
    Following the outline also draws better - a farming hamlet's front row bends with the field edge
    the way a real one does, rather than ruling a straight line across a curved margin.

    Research: a row fronting the field - UNRESEARCHED: the first seats offered one pitch apart along the field's outline, center-out
    """
    # THE ENVELOPE WALK IS RETIRED (feature 226, at the gate's coverage floor): every hamlet builds a site boundary
    # before this runs, so the row is always offset from its chains; the walk along the paddy's own outline (one seat
    # in two on the hem, which the pre-test now refuses before the placer is asked) was unreachable and, under feature 174, deleted
    # rather than kept for a caller that no longer exists. `count` is kept in the signature for the callers' sake; the
    # chain walk samples at the pitch and caps at 64, as the walk did.
    return _front_row_from_chains(plan, standoff, chains, house, envelope, with_normals, pitch, reach)


def _front_row_from_chains(
    plan: SitePlan,
    standoff: float | None,
    chains: Any,
    house: tuple[float, float] | None = None,
    envelope: tuple[float, float, float, float] | None = None,
    with_normals: bool = False,
    pitch: float = BUNDLE_PITCH,
    reach: float | None = None,
) -> list[Any]:
    """The front row offset from the SITE BOUNDARY's chains (feature 226 FR-003): the paddy's facing chains, each
    chord pushed out by its keep-out, so a seat offset from them by `standoff` along the chord's outward normal is
    the right distance from the paddy by construction; the hem, the marsh and the pond are refused at the PRE-TEST
    (`_site_blocks_rect` against the containment outline), where the paddy-envelope walk this replaces landed a
    seat on the hem one time in two and left the placer to discover it.
    Sampled at one bundle pitch along the chains (the honest spacing, as `front_row` argues), confined to the
    stretch the cluster fronts (the rolled shape's wrap, as there), ordered center-out (as there), at most 64.

    Research:
        house off the paddy - research/questions/0029-farmhouses-minka.drawing.html: the wall rule's gap plus a foot, past the homestead's reach toward the chord
        a row fronting the field - UNRESEARCHED: seats one pitch apart along the chains within the cluster's stretch, center-out
    """
    seat = plan.seat
    ax, ay = seat["along"]
    if reach is None:
        reach = seat["lat"] * CLUSTER_ROW_SPAN.get(plan.cluster_shape or "crescent", CLUSTER_SPAN_FACTOR)
    out: list[tuple[Pt, Pt]] = []
    for chain in chains:
        carry = 0.0
        for a, b, n in chain:
            seg = math.hypot(b[0] - a[0], b[1] - a[1])
            if seg <= 1e-9:
                continue
            # THE STANDOFF IS COMPUTED, NOT STEPPED TO (feature 227 FR-002): `standoff=None` puts the seat where the house
            # will stand - the wall rule's distance from the chord (`HOUSE_PADDY_GAP_FT` + 1), the tilt's slack, and the
            # HOMESTEAD's reach toward the chord along this chord's normal: the house's own half-extent, or, when the
            # envelope is given, the whole homestead's (`(left, top, right, bottom)` about the house center at the largest
            # size the roll can take) - so a paddy the YARD faces (the dike heads of Kuwabata: the threshing yard south of
            # the house, the paddy south of the yard) gets the yard's depth too, not a rung of a ladder. A numeric standoff
            # is a caller's own figure.
            if standoff is not None:
                off = standoff
            else:
                dx, dy = -n[0], -n[1]  # toward the chord
                hw_, hh_ = house or DEFAULT_HOUSE
                if envelope is not None:
                    left, top, right, bottom = envelope
                    reach_ = abs(dx) * (right if dx > 0 else -left) + abs(dy) * (bottom if dy > 0 else -top)
                else:
                    reach_ = abs(dx) * hw_ / 2 + abs(dy) * hh_ / 2
                off = HOUSE_PADDY_GAP_FT + 1.0 + STANDOFF_SLACK_PX + reach_
            t = carry
            while t <= seg:
                px, py = a[0] + (b[0] - a[0]) * t / seg, a[1] + (b[1] - a[1]) * t / seg
                if abs((px - seat["anchor"][0]) * ax + (py - seat["anchor"][1]) * ay) <= reach:
                    out.append(((px + n[0] * off, py + n[1] * off), (float(n[0]), float(n[1]))))
                t += pitch
            carry = t - seg
    if len(out) > 64:
        step = len(out) / 64.0
        out = [out[int(i * step)] for i in range(64)]
    out.sort(key=lambda q: math.hypot(q[0][0] - seat["cx"], q[0][1] - seat["cy"]))
    return out if with_normals else [q for q, _n in out]


# `_FIELD_RING_FLOOR` and `_FRONT_ROW_LANE_CAP` lived here and are GONE (feature 126). They were the
# two halves of a rule that judged a front-row seat by its distance to a drawn lane, and they existed
# only because the lanes were drawn BEFORE the houses. Now that the internal lanes are worn
# afterwards, a seat has no lane to be near and the rule had nothing left to mean.
#
# DO NOT REINTRODUCE A DISTANCE-TO-LANE TEST IN THIS STAGE. That is the inversion the whole feature
# removes: a farmhouse is sited by the field it works and the ground it can stand on. Two earlier
# attempts to TUNE this cap are recorded in the git history as dead ends; a third would be worse than
# either, because the thing it measures is no longer on the map when it runs.


def lane_frontage(s: Settlement, seat: Mapping[str, Any], step: float = 86.0, connector: bool = False) -> list[Pt]:
    """Candidate seats along BOTH verges of every internal lane, just outside its no-build corridor.

    Ordered from the cluster's center outward, so the lanes fill from their busy end. The connector
    is skipped: it is the track OUT of the settlement, and lining it with farmhouses would string the
    hamlet along the road instead of nucleating it (that is the `linear` settlement form, a
    different archetype).

    Research:
        houses front their lanes - UNRESEARCHED: seats every 86 ft on both verges of each internal lane
        frontage seat off the lane - UNRESEARCHED: `LANE_FRONTAGE_STANDOFF` (70 ft) off the lane's centerline
    """
    out: list[Pt] = []
    off = LANE_FRONTAGE_STANDOFF
    for lane in s.M.get("lanes", []):
        # `connector=True` INVERTS the skip: the caller wants the road itself, because it is siting a
        # linear hamlet along it. Everything else is unchanged.
        if lane.get("web") or (bool(lane.get("connector")) is not connector):
            continue
        pts = lane["pts"]
        for i in range(len(pts) - 1):
            (x0, y0), (x1, y1) = pts[i], pts[i + 1]
            run = math.hypot(x1 - x0, y1 - y0)
            nx, ny = unit(-(y1 - y0), x1 - x0)
            k = 1
            while k * step < run:
                px, py = x0 + (x1 - x0) * (k * step / run), y0 + (y1 - y0) * (k * step / run)
                out += [(px + nx * off, py + ny * off), (px - nx * off, py - ny * off)]
                k += 1
    return sorted(out, key=lambda q: math.hypot(q[0] - seat["cx"], q[1] - seat["cy"]))


def cluster_aspect(xs: list[float], ys: list[float]) -> float:
    """The house cloud's long:short ratio measured on ITS OWN principal axis - rotation-invariant.

    The observable `CLUSTER_DRAWN_ASPECT` is stated in, and the quantity a reader gets by laying a
    ruler along the cluster rather than along the page. A page-axis bbox ratio is not that quantity:
    it tends to 1.0 for any band on a diagonal, and is maximally blind at 45 degrees.

    Principal axis by second moments (a 2x2 covariance eigenvector, closed form via atan2), then the
    EXTENT along and across it. Extent rather than the eigenvalue ratio on purpose - a ruler measures
    the cloud's span, not its variance, and the two differ for an uneven rank (Sawada 3.02 by extent,
    2.72 by PCA sd). Mirrored in the gate; `tests/hamletgen/test_cluster_shape.py` pins the two equal
    by evaluating both on the same point sets, not by comparing source."""
    _n = len(xs)
    if _n < 2:
        return 1.0
    _mx, _my = sum(xs) / _n, sum(ys) / _n
    _sxx = sum((x - _mx) ** 2 for x in xs) / _n
    _syy = sum((y - _my) ** 2 for y in ys) / _n
    _sxy = sum((x - _mx) * (y - _my) for x, y in zip(xs, ys, strict=True)) / _n
    _th = 0.5 * math.atan2(2.0 * _sxy, _sxx - _syy)
    _c, _s = math.cos(_th), math.sin(_th)
    _along = [x * _c + y * _s for x, y in zip(xs, ys, strict=True)]
    _across = [-x * _s + y * _c for x, y in zip(xs, ys, strict=True)]
    _du = max(_along) - min(_along)
    _dv = max(_across) - min(_across)
    # A ROW IS ONE HOMESTEAD DEEP, NOT ZERO DEEP (the GM, 2026-10-01: tripwire seed 33 fixed). The extents are of the
    # houses' CENTERS, so a perfectly straight single row - ten houses fronting one straight field margin - measured
    # about 0.2 ft across and drew 2,345:1, past every shape's band, and `seat_every_household` refused every margin of
    # the site. A reader's ruler laid across that row reads the homesteads' own depth, so the short side is floored
    # at the ground one homestead takes (`BUNDLE_PITCH`, 92 ft): the row reads about n:1, a string. The floor reaches
    # only a near-straight row - every exhibit the bands were calibrated on (`CLUSTER_DRAWN_ASPECT`) is far deeper. The
    # long side takes the same floor, so a cloud smaller than one homestead each way reads 1:1, never under it.
    return max(BUNDLE_PITCH, _du, _dv) / max(BUNDLE_PITCH, min(_du, _dv))
