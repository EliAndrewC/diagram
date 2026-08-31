"""Split from hamletgen/hinterland.py by feature 173 - see this package's CLAUDE.md for the index."""

from __future__ import annotations

import random

from l7r.diagram.settlement import Settlement, point_in_poly, seg_dist
from l7r.diagram.sitegen.geom import crop_polys

from ..consts import Poly, Pt
from ..plan import SitePlan


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
    a band of constant depth, so `village_grove` still fills it as a belt rather than a blob."""
    houses = s.M.get("houses", [])
    if len(houses) < 3:  # pragma: no cover - fewer houses than this fails the gate first
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

    def rag(q: Pt, amp: float = 13.0) -> Pt:
        return (q[0] + rng.uniform(-amp, amp), q[1] + rng.uniform(-amp, amp))

    # NO COLUMN FALLS BEHIND THE MEDIAN HOUSE. Following the profile is right, but on a cluster
    # that is long ACROSS the wind the flank columns' own frontrunner sits well downwind of the
    # middle ones, so the band bows back around the settlement and its centroid can land level with
    # (or behind) the house cloud - which is exactly what `village_windbreak_on_windward_side`
    # measures, and it fired on two cohort maps with a belt that looked fine in every other check.
    # Flooring each column at the cluster's MEDIAN u keeps the belt following the fringe where the
    # fringe leads it, and keeps the whole band on the windward half where a back-village grove
    # belongs. The median, not the mean: one house pushed far upwind should not drag the wall out.
    u_sorted = sorted(u for u, _v in uv)
    u_floor = u_sorted[len(u_sorted) // 2]

    def profile(span_f: float) -> list[tuple[float, float]]:
        """(v, u) of the windward fringe, sampled in columns across the wind."""
        cols: list[tuple[float, float]] = []
        for k in range(COLS + 1):
            v = v_mid + half * span_f * (-1.0 + 2.0 * k / COLS)
            width = half * span_f / COLS + 40.0
            near = [u for u, vv in uv if abs(vv - v) <= width]
            if not near:  # a column with no house of its own leans on the whole cluster's fringe
                near = [max(u for u, _v in uv) - 40.0]
            # THE COLUMN CLEARS THE WINDWARD-MOST HOUSE IN ITS OWN NEIGHBORHOOD, not merely the
            # ones directly in front of it. `near` is the houses within half a column of this v, so
            # a steading sitting just outside that window - which a SPREAD cluster produces
            # constantly - is not counted, the band is laid across it, and `village_grove` then
            # correctly skips every clump that would fall on its house, yard, garden and shed. The
            # belt ends up with a hole exactly one homestead wide.
            #
            # Measured on cohort seeds 33 and 37: the biggest hole in each belt has a whole
            # steading inside it (house 57 ft from the hole center, threshing yard 38-41, gardens
            # 10-46), and the holes are 78 and 84 ft - about one homestead across. Widening the
            # window to a full column each side is what makes the band clear the fabric it is
            # meant to shelter rather than straddle it.
            _wide = [u for u, vv in uv if abs(vv - v) <= width * 2.0]
            cols.append((v, max(max(near), max(_wide) if _wide else max(near), u_floor)))
        return cols

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

    def band(span_f: float, back: float) -> Poly:
        cols = profile(span_f)
        # 36 px, not 24. `village_grove` filters clumps against every structure and crop, and it
        # filters the near face hardest - so a belt whose POLYGON sits clearly windward can still
        # have its DRAWN clumps average back onto the cluster's own line, which is what
        # `village_windbreak_on_windward_side` measures (Kashikawa: polygon centroid +137, drawn
        # centroid -5). The extra 12 px comes out of the 150 px embrace budget and leaves plenty.
        near = [rag((ccx + wx * (u + 36.0 + _sun_off + back) + px * v, ccy + wy * (u + 36.0 + _sun_off + back) + py * v)) for v, u in cols]
        far = [rag((ccx + wx * (u + 146.0 + _sun_off + back) + px * v, ccy + wy * (u + 146.0 + _sun_off + back) + py * v)) for v, u in reversed(cols)]
        return near + far

    def fouled(poly: Poly) -> bool:
        return any(point_in_poly(q[0], q[1], list(c)) or min(seg_dist(q[0], q[1], c[i2], c[(i2 + 1) % len(c)]) for i2 in range(len(c))) < 20.0 for q in poly for c in crops)

    # THE LADDER STANDS BACK BEFORE IT SHRINKS. Both moves get the belt off the crop, but they cost
    # different things: standing back spends the embrace budget (a clump within 150 px of a
    # farmhouse, and the belt starts 24 px behind the fringe, so there is room), while shrinking
    # spends the SIZE budget (canopy worth 40% of the roof area it shelters, which a belt trimmed to
    # half its length cannot meet). Shrinking first cost both checks on two cohort maps.
    belt = band(1.0, 0.0)
    for span_f, back in ((1.0, 0.0), (1.0, 22.0), (1.0, 44.0), (0.88, 44.0), (0.74, 60.0), (0.6, 60.0)):
        belt = band(span_f, back)
        if not fouled(belt):
            break
    return [(max(6.0, min(plan.W - 6.0, bx)), max(6.0, min(plan.H - 6.0, by))) for bx, by in belt]
