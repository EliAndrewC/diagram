"""Split from hamletgen/hinterland.py by feature 173 - see this package's CLAUDE.md for the index.

Research: belt geometry - NONE: wind coordinates, sampling and curve plumbing
"""

from __future__ import annotations

import math
import random
from collections.abc import Sequence
from typing import Any

from l7r.diagram.settlement import Settlement, point_in_poly
from l7r.diagram.settlement._geom import RingIndex
from l7r.diagram.settlement.land.wet import marsh_ground
from l7r.diagram.sitegen.geom import crop_polys

from ..consts import Poly, Pt
from ..plan import SitePlan


def fringe_profile(uv: Sequence[tuple[float, float]], cols: int, half: float, v_mid: float, u_floor: float, span_f: float) -> list[tuple[float, float]]:
    """(v, u) of the cluster's windward fringe, sampled in columns ACROSS the wind.

    `uv` is every house in wind coordinates - u along the wind, v across it - so a column is a slice of
    the settlement at one v, and its u is how far windward the belt must stand to be in front of the
    houses THERE. That is the whole of the belt's shape: the band follows this profile.

    A COLUMN WITH NO HOUSE OF ITS OWN LEANS ON ITS NEAREST NEIGHBOR THAT HAS ONE (settlement-review,
    feature 230 pass 12). It used to lean on the whole cluster's windward-most house, and on a cluster
    lying square to the wind that is harmless - the fringe is level, so the global answer and the local
    one agree. On a cluster lying DIAGONALLY to the wind they disagree by the length of the settlement:
    measured on the reference hamlet after this feature re-seated its cluster (aspect 3.25 -> 5.01, the
    wind N), column 8 held no house, took the global fringe 800 ft away across the wind, and threw the
    belt's last column 437 ft north over 99 ft of x. Thirty-two clumps drew a 430 ft file of trees along
    the frame's edge, 246-522 ft from the nearest farmhouse, sheltering nothing, and the belt read as a
    check-mark rather than a wall. `village_windbreak_embraces_cluster` cannot see it: the belt's other
    222 clumps are adjacent to the houses, so the limb that has left the settlement passes on their
    adjacency.

    Lifted out of `belt_polygon` under the feature-146 doctrine: the empty-column case is a question
    about a list of points, and inside the closure it could only be reached by rolling a hamlet whose
    cluster happens to lie diagonally to its wind.

    Research: belt follows the windward fringe - research/questions/0072-shelter-belts-on-a-villages-windward-side-bofurin.drawing.html: each column stands behind the windward-most house near it
    """
    raw: list[tuple[float, float | None]] = []
    for k in range(cols + 1):
        v = v_mid + half * span_f * (-1.0 + 2.0 * k / cols)
        width = half * span_f / cols + 40.0
        near = [u for u, vv in uv if abs(vv - v) <= width]
        # THE COLUMN CLEARS THE WINDWARD-MOST HOUSE IN ITS OWN NEIGHBORHOOD, not merely the ones directly
        # in front of it. `near` is the houses within half a column of this v, so a steading sitting just
        # outside that window - which a SPREAD cluster produces constantly - is not counted, the band is
        # laid across it, and `village_grove` then correctly skips every clump that would fall on its
        # house, yard, garden and shed. The belt ends up with a hole exactly one homestead wide.
        #
        # Measured on cohort seeds 33 and 37: the biggest hole in each belt has a whole steading inside it
        # (house 57 ft from the hole center, threshing yard 38-41, gardens 10-46), and the holes are 78 and
        # 84 ft - about one homestead across. Widening the window to a full column each side is what makes
        # the band clear the fabric it is meant to shelter rather than straddle it.
        wide = [u for u, vv in uv if abs(vv - v) <= width * 2.0]
        raw.append((v, max(max(near or wide), u_floor) if (near or wide) else None))
    known = {k: u for k, (_v, u) in enumerate(raw) if u is not None}
    if not known:  # no column sees a house at all: the whole profile is the floor, which is the median house
        return [(v, u_floor) for v, _u in raw]
    return [(v, u if u is not None else known[min(known, key=lambda j: abs(j - k))]) for k, (v, u) in enumerate(raw)]


def trim_receding_ends(cols: Sequence[tuple[float, float]], drop: float) -> list[tuple[float, float]]:
    """The fringe profile `cols` ((v, u), in order across the wind) without its END columns that fall back more than `drop`
    downwind of their inner neighbor, from each end inward while that holds.

    THE BELT STANDS ACROSS THE WIND (settlement-review of Sawada at the 269 landing). Where a cluster lies along the wind,
    the column at the belt's end leans on a house far downwind of the rest - Sawada's end column stood 766 ft behind its
    neighbor - and the band followed it into an arm lying along the wind: 500 ft of one row of trees, 35-60 ft across,
    sheltering nothing, where research/contents.json#vegetation asks a belt never thinner than 80 ft. A column that recedes more than a
    belt's own depth is not the windward fringe any more; the belt ends at the column before it.

    Research: no arm along the wind - research/questions/0071-groves-around-a-southern-chinese-village-the-fengshui-woods-fengshuilin-and-the-dooryard-copse.drawing.html: an end column falling back more than the belt's depth is dropped, a belt never thinner than 80 ft
    """
    out = list(cols)
    while len(out) > 2 and out[1][1] - out[0][1] > drop:
        out.pop(0)
    while len(out) > 2 and out[-2][1] - out[-1][1] > drop:
        out.pop()
    return out


BELT_LANE_CLEAR_FT = 12.0  # ft: a belt whose band a lane runs along stands this far beyond the lane's tread
"""Research: belt clear of a back lane - UNRESEARCHED: 12 ft beyond the tread"""


def past_the_lanes(cols: Sequence[tuple[float, float]], lanes: Sequence[tuple[float, float]], width: float, near: float = 36.0, depth: float = 146.0, wet: Any = None) -> list[tuple[float, float]]:
    """The fringe profile `cols` ((v, u) in wind coordinates) moved upwind past any lane running inside the belt's band
    (settlement-review of Kuwabata, feature 261). `lanes` are samples of the web's lanes in the same coordinates. A back
    lane along the windward row of houses ran lengthwise down the middle of the band, 40 ft from its near face; the lane
    keep-out took the clumps there and the belt drew a 63 ft wall where the record asks 80-120 (main's back lane ran
    outside the near face). So a column whose band holds a lane stands its near face `BELT_LANE_CLEAR_FT` beyond the
    lane, and keeps its whole depth - unless `wet(v, u)` says the moved band would stand in the marsh, where no woody cover
    stands (Sawada's belt, pushed past its back lane, walked into the toe marsh's reeds).

    Research:
        belt keeps its depth past a back lane - research/questions/0071-groves-around-a-southern-chinese-village-the-fengshui-woods-fengshuilin-and-the-dooryard-copse.drawing.html: moved upwind past a lane inside the band
        no belt in the marsh - research/questions/0074-reed-beds-and-the-marshs-edge-yoshihara.drawing.html: a band the move would stand in the marsh stays put
        lane clearance - UNRESEARCHED: BELT_LANE_CLEAR_FT
    """
    out: list[tuple[float, float]] = []
    for v, u in cols:
        inside = [lu for lu, lv in lanes if abs(lv - v) <= width and u + near - BELT_LANE_CLEAR_FT <= lu <= u + depth]
        moved = max(u, max(inside) + BELT_LANE_CLEAR_FT - near) if inside else u
        out.append((v, u if moved != u and wet is not None and wet(v, moved) else moved))
    return out


BELT_NEAR_FT = 36.0  # ft behind the fringe the band's near face stands
"""Research: near stand-off - UNRESEARCHED: the near face 36 ft behind the fringe"""
# THE BAND'S DEPTH BEFORE THE RAG, near face to far, and the rag on each face. The near face is roughened along its length
# and pushed only OUT of the band, 0-`BELT_NEAR_RAG_FT`; the far face moves up to `BELT_FAR_RAG_FT` either way. A band
# laid 100 ft deep so draws 90-115 ft where the fringe lies square to the wind - inside the record's 80-120 ft
# (research/questions/0071-groves-around-a-southern-chinese-village-the-fengshui-woods-fengshuilin-and-the-dooryard-copse.drawing.html). The old rag moved both faces up to 13 ft either way
# about a 110 ft band (84-136): the near face moving in with the far took the band to 72.7 ft at Sawada's bend. Moving
# both faces only outward about 110 drew a median band of 118-122 ft, over half of two maps' faces past 120. A 100 ft band
# once left Kashikawa's belt in two pieces where its westernmost garden's afternoon-sun lane crossed the band, and 105
# was laid to cover it; the cause was the near face's chord cutting that garden, fixed at its source by
# `round_the_houses`, and 105 then drew 17-24% of two faces past 120 where 100 draws 1-16%, at the ends and bends
# (spec-fidelity rounds of 2026-09-28; measured every 5 ft along the near face, `m:belt-r22-depth`).
BELT_DEPTH_FT = 100.0
"""Research: belt depth - research/questions/0071-groves-around-a-southern-chinese-village-the-fengshui-woods-fengshuilin-and-the-dooryard-copse.drawing.html: laid 100 ft, drawn 90-115 ft with the rag"""
BELT_NEAR_RAG_FT = 5.0
"""Research: near face rag - research/questions/0071-groves-around-a-southern-chinese-village-the-fengshui-woods-fengshuilin-and-the-dooryard-copse.drawing.html: up to 5 ft outward, an irregular grove edge"""
BELT_FAR_RAG_FT = 10.0
"""Research: far face rag - research/questions/0071-groves-around-a-southern-chinese-village-the-fengshui-woods-fengshuilin-and-the-dooryard-copse.drawing.html: up to 10 ft either way, an irregular grove edge"""


BELT_PROFILE_STEP_FT = 30.0  # ft along the fringe profile between the band's samples


def along_the_profile(cols: Sequence[tuple[float, float]], step: float = BELT_PROFILE_STEP_FT) -> list[tuple[float, float]]:
    """The fringe profile (v, u) with a sample every `step` ALONG it between the columns (spec-fidelity of round 31ef113b:
    Sawada's belt 72.7 ft across itself where it turns). The columns stand about 90 ft apart ACROSS the wind, and where
    the fringe falls back steeply between two of them - Sawada's belt turns a right angle there, its near face one 480 ft
    chord - a disc round the columns alone sees only the two ends, so the far face runs parallel to that chord at whatever the two
    ends allow: 72 ft. Sampled along its length, the disc sees every stretch of the face and the band keeps its depth."""
    out: list[tuple[float, float]] = []
    for (v0, u0), (v1, u1) in zip(cols, cols[1:], strict=False):
        n = max(1, int(math.hypot(v1 - v0, u1 - u0) // step))
        out += [(v0 + (v1 - v0) * k / n, u0 + (u1 - u0) * k / n) for k in range(n)]
    return [*out, *cols[-1:]]


def far_envelope(cols: Sequence[tuple[float, float]], depth: float = BELT_DEPTH_FT, step: float = BELT_PROFILE_STEP_FT) -> list[tuple[float, float]]:
    """The fringe the band's far face is laid `depth` behind: a disc of `depth` grown round every point ALONG the
    profile (`along_the_profile`), and sampled every `step` ACROSS the wind in order, so the face is one curve that never
    folds back (spec-fidelity of round 31ef113b: Sawada's belt 72.7 ft across itself where it turns a right angle between
    two columns). Sampling the far face along the profile instead was tried first and folded it: across a steep chord the
    samples share nearly one position across the wind, and the face ran back and forth over itself - Sawada's belt fell
    into six pieces."""
    pts = along_the_profile(cols, step)
    lo, hi = cols[0][0], cols[-1][0]
    n = max(1, int(abs(hi - lo) // step))
    vs = sorted({*(lo + (hi - lo) * k / n for k in range(n + 1)), *(v for v, _u in cols)}, reverse=hi < lo)
    return [(v, max(u2 + depth * (1.0 - ((v2 - v) / depth) ** 2) ** 0.5 for v2, u2 in pts if abs(v2 - v) <= depth) - depth) for v in vs]


def round_the_houses(cols: Sequence[tuple[float, float]], uv: Sequence[tuple[float, float]], reach: float, step: float = BELT_PROFILE_STEP_FT) -> list[tuple[float, float]]:
    """The fringe profile `cols` ((v, u), in order across the wind) with the near face kept `reach` from every house
    (`uv`, (u, v) per house) all along it, not only at the columns (feature 261, once main's placer re-laid the pool).
    A column stands its face `reach` windward of the house it leads with; between two columns the face is one chord, and
    where the fringe falls back steeply the chord cuts the corner at the leading house - Kashikawa's ran 37 ft from its
    westernmost farmhouse, through that house's garden, and the garden's afternoon-sun lane then took the band's trees
    there and left the belt in two pieces. So every `step` across the wind, and every 15 degrees round each house's disc of
    `reach`, a point is added where the disc stands windward of the chord; the columns are kept as they are. The face
    goes round the house at the distance the column rule already gives it.

    Research: near face clear of every house - UNRESEARCHED: the stand-off kept from each house all along the face
    """
    if len(cols) < 2:
        return list(cols)
    rev = cols[-1][0] < cols[0][0]
    lo, hi = min(cols[0][0], cols[-1][0]), max(cols[0][0], cols[-1][0])

    def chord(v: float) -> float:
        for (v0, u0), (v1, u1) in zip(cols, cols[1:], strict=False):
            if min(v0, v1) <= v <= max(v0, v1):
                return u0 if v1 == v0 else u0 + (u1 - u0) * (v - v0) / (v1 - v0)
        return cols[0][1] if abs(v - cols[0][0]) < abs(v - cols[-1][0]) else cols[-1][1]  # pragma: no cover - every v asked lies in [lo, hi]

    def disc(v: float) -> float:
        return max((hu + (reach * reach - (v - hv) ** 2) ** 0.5 - reach for hu, hv in uv if abs(v - hv) <= reach), default=-math.inf)

    n = max(1, int((hi - lo) // step))
    # round each disc every 15 degrees of arc, so no chord between two points sags more than 0.7 ft into it at 79 ft
    ends = {hv + sy * reach * math.sin(math.radians(15.0 * k)) for _hu, hv in uv for k in range(1, 7) for sy in (-1.0, 1.0)}
    ends = {v for v in ends if lo < v < hi}
    vs = sorted({*(lo + (hi - lo) * k / n for k in range(1, n)), *ends} - {v for v, _u in cols}, reverse=rev)
    extra = [(v, disc(v)) for v in vs if disc(v) > chord(v) + 1.0]
    return sorted([*cols, *extra], key=lambda q: -q[0] if rev else q[0])


def belt_polygon(s: Settlement, plan: SitePlan) -> Poly:
    """The windbreak belt's footprint - a band FOLLOWING the cluster's windward fringe.

    The belt used to be a straight band standing off the single windward-most house, its length set
    by the widest cross-wind pair. That is right for a round cluster and wrong for every other
    shape: on a tall narrow settlement under a diagonal wind it put the belt 350 px clear of the
    nearest farmhouse and nearly square, and `village_grove`'s own filters then threw most of its
    clumps away - nine survived. A belt that shelters nothing fails
    `village_windbreak_embraces_cluster` and `village_windbreak_scales_with_cluster` together, and
    both are right to fail it.

    So the near face is sampled ACROSS the wind and, in each column, sits just behind whichever
    house is furthest upwind THERE. The result hugs the settlement's windward profile whatever its
    shape - which is what a back-village grove does, being planted where the houses are - and stays
    a band of constant depth, so `village_grove` still fills it as a belt rather than a blob.

    Research:
        one village belt for the clustered form only - research/questions/0071-groves-around-a-southern-chinese-village-the-fengshui-woods-fengshuilin-and-the-dooryard-copse.html, research/questions/0031-clustered-and-scattered-villages-shuson-sanson.drawing.html: none where every farm carries its own grove
        belt on the windward fringe - research/questions/0072-shelter-belts-on-a-villages-windward-side-bofurin.drawing.html: a band hugging the cluster's windward profile, never behind its center
        shoulder past the end houses - UNRESEARCHED: the band runs 90 ft past the outermost house across the wind
        off the afternoon sun-lane - research/questions/0038-sunlight-and-shade-on-the-farm.drawing.html: the near face moved back by the west sun lane, scaled by the wind's westward share
        off the crop - UNRESEARCHED: stands back 22-60 px, then shortens to 0.6 of its span
        no belt under three houses - UNRESEARCHED
    """
    houses = s.M.get("houses", [])
    if len(houses) < 3:
        return []
    # NO VILLAGE BELT WHERE EVERY FARM CARRIES ITS OWN GROVE (feature 291; research/questions/0071-groves-around-a-southern-chinese-village-the-fengshui-woods-fengshuilin-and-the-dooryard-copse.html, "Why one communal grove
    # and not a grove per house": "The per-farmstead belt is the DISPERSED settlement's answer; a nucleated cluster shelters
    # itself ... so its windbreak is a single village-scale wood"). The two are one answer or the other, never both; once
    # the dispersed and linear forms rolled again, Kashikawa drew 60 farm grove bands AND a 369-clump village belt behind
    # them (settlement-review, 2026-09-29).
    if not getattr(s, "_nucleated", True):
        return []
    wx, wy = plan.wind
    px, py = -wy, wx  # across the wind
    ccx, ccy = sum(h["x"] for h in houses) / len(houses), sum(h["y"] for h in houses) / len(houses)
    uv = [(((h["x"] - ccx) * wx + (h["y"] - ccy) * wy), ((h["x"] - ccx) * px + (h["y"] - ccy) * py)) for h in houses]
    # A PLOT-EXTENT FACE WAS TRIED AND ROTATED THE FAILURE (T99 unlock, 2026-08-27): tripwire seed 33's
    # 40-50 ft hole (broken since T10) sits where two garden beds stand 40-55 ft toward the wind from
    # their house, inside the band; reading every footprint's far edge into the column profile closed
    # it - and opened the same hole on seed 41, and pushed Inashiro's belt 75 px out until the reach was
    # cut by the stand-off. Principle XIII names that signature (three closed, one opened) as a knob
    # that moves the defect, so it is not kept; the hole is a real belt-vs-plot conflict that wants
    # `village_grove` to thin around a plot rather than the face to dodge it. Open, ledgered below.
    v_lo, v_hi = min(v for _u, v in uv), max(v for _u, v in uv)
    half = (v_hi - v_lo) / 2 + 90.0  # a shoulder past the outermost house at each end
    # SAMPLE THE FRINGE BY LENGTH, NOT BY A FIXED COUNT. `COLS` was 7 whatever the belt measured, so
    # the profile's resolution fell as the cluster spread: the columns move apart, the polygon
    # pinches between them, and the drawn canopy carries bare runs that
    # `village_windbreak_is_continuous` reports as gaps. Feature 126 spread the cluster (houses are
    # no longer seated against pre-laid lanes) and the check fired on four cohort seeds whose belts
    # were otherwise blameless - measured on seed 33: 113 clumps, not one polygon vertex in crop and
    # not one house inside the band, so nothing was blocking the trees; the band shape itself was
    # coarse.
    #
    # One column per ~90 px of belt keeps the profile as fine as it was on the clusters this was
    # tuned against, and the floor of 7 keeps every previously-passing short belt sampled exactly as
    # before. This is the same rule `front_row` already records for its own seats: resolution
    # follows the thing being sampled, never the count of what is being placed.
    # ONE COLUMN PER ~90 px. The profile is what the drawn band follows, so its resolution is the
    # belt's minimum feature size: too coarse and the band pinches between columns, and the check
    # reports the pinch as a bare run across the wind even though clumps sit feet away in plane
    # distance. The floor of 7 is the value every belt used before feature 126, so a short belt is
    # sampled exactly as it always was.
    #
    # 45 px WAS TRIED AND ROTATED THE FAILURES RATHER THAN FIXING THEM - do not reach for it again
    # as an obvious next step. Measured across the 48-seed cohort: at 90 px the windbreak failures
    # were seeds 23/27/33/37; at 45 px they were 22/23/28/39/46. Three closed, four opened, one
    # persisted, and the total went UP. That is the signature of a knob that moves WHICH map has the
    # defect instead of removing it, and Principle XIII names rotation explicitly as not an excuse.
    # Whatever leaves a 141 ft hole in an 833 ft belt (seed 23) is not sampling resolution.
    COLS = max(7, min(24, int(2 * half / 90.0)))
    v_mid = (v_lo + v_hi) / 2
    rng = random.Random((plan.spec.seed * 7919) & 0xFFFFFFFF)

    def rag(q: Pt, out: float) -> Pt:
        """A face vertex roughened ALONG the face, and moved across it - the near face (`out` -1, leeward) only OUT of the
        band, up to `BELT_NEAR_RAG_FT`; the far face (`out` +1) up to `BELT_FAR_RAG_FT` either way. The two draws are the two
        the old rag made, so the sequence is the same (see `BELT_DEPTH_FT` for the range this draws)."""
        amp = BELT_FAR_RAG_FT if out > 0 else BELT_NEAR_RAG_FT
        a, b = rng.uniform(-amp, amp), rng.uniform(-amp, amp)
        d = b if out > 0 else -abs(b)
        return (q[0] + px * a + wx * d, q[1] + py * a + wy * d)

    # NO COLUMN FALLS BEHIND THE MEDIAN HOUSE. Following the profile is right, but on a cluster
    # that is long ACROSS the wind the flank columns' own frontrunner sits well downwind of the
    # middle ones, so the band bows back around the settlement and its centroid can land level with
    # (or behind) the house cloud - which is exactly what `village_windbreak_on_windward_side`
    # measures, and it fired on two cohort maps with a belt that looked fine in every other check.
    # Flooring each column at the cluster's MEDIAN u keeps the belt following the fringe where the
    # fringe leads it, and keeps the whole band on the windward half where a back-village grove
    # belongs. The median, not the mean: one house pushed far upwind should not drag the wall out.
    u_sorted = sorted(u for u, _v in uv)
    # ...AND NEVER BEHIND THE CLUSTER'S CENTER (feature 287, woods W18): where the median house stands downwind of the
    # houses' centroid (a cluster lying diagonally to the wind), a column floored at the median could still lay its band
    # level with the centroid. At 0 the band's near face stands `BELT_NEAR_FT` windward of the centroid in every column, so
    # the planted belt starts on the wind's quarter and `trim_to_the_wind` only shortens its hook.
    u_floor = max(u_sorted[len(u_sorted) // 2], 0.0)

    def profile(span_f: float) -> list[tuple[float, float]]:
        """(v, u) of the windward fringe, sampled in columns across the wind."""
        return fringe_profile(uv, COLS, half, v_mid, u_floor, span_f)

    # ~110 px deep - a real wind wall, not a hedge. The 24 px stand-off is set by
    # `village_windbreak_embraces_cluster`, which wants a clump within 150 px of a farmhouse: the
    # clump grid starts some way inside the polygon, so a 42 px face measured 160 px to the nearest
    # tree.
    crops: list[Poly] = [list(plan.envelope), *crop_polys(s)]

    # THE NEAR FACE STANDS OFF THE AFTERNOON SUN-LANE when the belt lies to the WEST (feature 133
    # T10). `village_grove` refuses every clump inside `west_sun_lane` of a yard's or garden's west
    # edge, and a belt whose polygon starts 36 px behind the fringe HOUSE center would have its whole
    # front filtered away where a garden hangs off a west wall - a thinned, ragged belt rather than a
    # belt moved back. So the face itself moves: by the lane, scaled by how much of the wind points
    # west (`-wx`: 1 for a W wind, ~0.7 for NW/SW, 0 for N/E/S), plus 12 px - the west-most plot's
    # edge sits ~48 px past its house center (half-house 23 + gap 3 + bed ~22) and the 36 px face
    # already covers 36 of it. The filter is still the guarantee; this keeps the belt whole.
    _sun_off = max(0.0, -wx) * (float(getattr(s, "_west_sun_ft", 0.0)) + 12.0)

    # the web's lanes in wind coordinates, sampled every 10 ft; the connector and the field spur cross the belt face to
    # face, which is a way through a wind wall, so only the lanes that can run ALONG it are asked
    _lanes = [
        ((q[0] - ccx) * wx + (q[1] - ccy) * wy, (q[0] - ccx) * px + (q[1] - ccy) * py)
        for ln in s.M.get("lanes") or []
        if not ln.get("connector") and not ln.get("spur")
        for a, b in zip(ln.get("pts") or [], (ln.get("pts") or [])[1:], strict=False)
        for q in [(a[0] + (b[0] - a[0]) * t / 10, a[1] + (b[1] - a[1]) * t / 10) for t in range(11)]
    ]

    _marsh = marsh_ground(s.M)

    def _in_marsh(v: float, u: float) -> bool:
        """Would the band moved to fringe `u` in column `v` stand in the marsh - its middle, half its depth behind its near face?"""
        _mid = BELT_NEAR_FT + BELT_DEPTH_FT / 2.0
        x, y = ccx + wx * (u + _mid + _sun_off) + px * v, ccy + wy * (u + _mid + _sun_off) + py * v
        return any(point_in_poly(x, y, ring) for ring in _marsh)

    _near_n = [0]  # how many of the band's vertices are its near face, recorded for the depth measure (the far face has more)

    def band(span_f: float, back: float) -> Poly:
        cols = past_the_lanes(
            round_the_houses(trim_receding_ends(profile(span_f), BELT_DEPTH_FT), uv, BELT_NEAR_FT + _sun_off),
            _lanes,
            half * span_f / COLS,
            near=BELT_NEAR_FT,
            depth=BELT_NEAR_FT + BELT_DEPTH_FT,
            wet=_in_marsh,
        )
        # 36 px, not 24. `village_grove` filters clumps against every structure and crop, and it
        # filters the near face hardest - so a belt whose POLYGON sits clearly windward can still
        # have its DRAWN clumps average back onto the cluster's own line, which is what
        # `village_windbreak_on_windward_side` measures (Kashikawa: polygon centroid +137, drawn
        # centroid -5). The extra 12 px comes out of the 150 px embrace budget and leaves plenty.
        # The band is the belt's 80-120 ft depth (`BELT_DEPTH_FT` with the rag's outward push; research/contents.json#vegetation
        # "How our maps draw a village's groves" - a belt reads as a wall of trees only at that depth).
        _near_n[0] = len(cols)
        near = [rag((ccx + wx * (u + BELT_NEAR_FT + _sun_off + back) + px * v, ccy + wy * (u + BELT_NEAR_FT + _sun_off + back) + py * v), -1.0) for v, u in cols]
        _far = BELT_NEAR_FT + BELT_DEPTH_FT
        far = [rag((ccx + wx * (u + _far + _sun_off + back) + px * v, ccy + wy * (u + _far + _sun_off + back) + py * v), 1.0) for v, u in reversed(far_envelope(cols))]
        return near + far

    # EACH CROP AS A RING INDEX, BUILT ONCE (feature 278): `fouled` walked every edge of every crop for every vertex of each
    # candidate belt. `inside` counts the crossings `point_in_poly` counted, and `edge_within(.., 20)` is the nearest edge
    # under 20 px - and a vertex that close to an edge is fouled either way, so a rounding difference on the edge itself
    # cannot change the answer.
    crop_idx = [RingIndex(c) for c in crops if len(c) >= 3]

    def fouled(poly: Poly) -> bool:
        return any(ci.inside(q[0], q[1]) or ci.edge_within(q[0], q[1], 20.0) is not None for q in poly for ci in crop_idx)

    # THE LADDER STANDS BACK BEFORE IT SHRINKS. Both moves get the belt off the crop, but they cost
    # different things: standing back spends the embrace budget (a clump within 150 px of a
    # farmhouse, and the belt starts 24 px behind the fringe, so there is room), while shrinking
    # spends the SIZE budget (canopy worth 40% of the roof area it shelters, which a belt trimmed to
    # half its length cannot meet). Shrinking first cost both checks on two cohort maps.
    belt = band(1.0, 0.0)
    span_f, back = 1.0, 0.0
    for span_f, back in ((1.0, 0.0), (1.0, 22.0), (1.0, 44.0), (0.88, 44.0), (0.74, 60.0), (0.6, 60.0)):
        belt = band(span_f, back)
        if not fouled(belt):
            break
    s.M.setdefault("meta", {})["belt_near_vertices"] = _near_n[0]
    # THE BAND'S REACH (feature 287, woods W19): how far its designed far face stands from the house it is laid behind - the
    # near stand-off, the depth, the far face's rag, the afternoon-sun offset and the step back the ladder took, ALONG the
    # wind; and a column is laid behind the windward-most house within its own window ACROSS the wind (`fringe_profile`'s
    # `near`, half a column and 40 ft), so the far face stands that much farther from that house on the diagonal. A crown
    # farther than this from every farmhouse shelters none of them (Inashiro: 63 of 308 crowns over 200 ft from any house,
    # the furthest 518, on a limb joining a cluster's two groups), so the belt is planted within it (`plant_the_belt`) and
    # the stretch it leaves between two groups is a run break, not a hole (`belt_law`). The designed reach ALONG the wind
    # alone was tried first and cut into the band the design lays: a column's far face stood beyond it wherever its house
    # stood across the wind from it, the depth could not be kept there, and cohort seed 37's belt lost 120 of 332 crowns.
    s.M["meta"]["belt_reach"] = round(math.hypot(BELT_NEAR_FT + BELT_DEPTH_FT + BELT_FAR_RAG_FT + _sun_off + back, half * span_f / COLS + 40.0), 1)
    return [(max(6.0, min(plan.W - 6.0, bx)), max(6.0, min(plan.H - 6.0, by))) for bx, by in belt]
