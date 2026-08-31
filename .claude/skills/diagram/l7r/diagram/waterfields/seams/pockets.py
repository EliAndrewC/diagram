"""Split from waterfields/seams.py by feature 173 - see this package's CLAUDE.md for the index."""

import math
from collections.abc import Callable
from typing import Any

from shapely.errors import GEOSException
from shapely.geometry import LineString, Point, Polygon
from shapely.geometry.base import BaseGeometry
from shapely.ops import unary_union

from ..banks import (
    _GATE_MIN_APEX,
    _WELD_MIN_APEX,
    _WELD_MIN_SOLIDITY,
    dedup_ring,
    is_chevron,
    jog_steps,
    polyline_cum,
)
from ..frame import BANK_MARGIN, Poly, _f_at_u, _Frame, taper_w

# The carve's own "too narrow to plant" side (`_sector_body_rows` / `_sector_canal_closers` both
# refuse an edge under 6 * grain), reused here so a pocket this pass plants is exactly a pocket the
# carve would have planted had its grid reached there. Below it the ground is a seam, not a basin.
MIN_PLOT_SIDE = 6.0

# Boolean geometry leaves hairline artifacts where two boundaries nearly graze; this is the width
# below which a feature is one of them rather than ground. A fifth of a drawn aze (AZE_FT 1.5, and
# never under 0.5 px), so the opening it drives cannot move anything the map can show.
_SPIKE = 0.25


def _parts(geom: BaseGeometry) -> list[Polygon]:
    """Simple polygons of `geom`, in a deterministic order (shapely does not promise one)."""
    out = [g for g in getattr(geom, "geoms", [geom]) if isinstance(g, Polygon) and not g.is_empty and g.is_valid]
    return sorted(out, key=lambda g: (round(g.bounds[0], 1), round(g.bounds[1], 1)))


def _despike(geom: BaseGeometry) -> BaseGeometry:
    """Open the geometry by a fraction of a pixel to shed hairline spurs.

    Subtracting one polygon from another that nearly grazes it leaves zero-width spikes: a vertex
    pair that runs out and straight back along the same line. On Inashiro one such spur reached
    5.5 px ACROSS a delivery ditch off a pocket that was correctly clipped to the ditch's bank, and
    the recorded ring failed `paddy_bunds_clear_the_supply_channels` - a bund vertex in the middle
    of the water that no bund was ever placed at. An opening (erode then dilate by the same amount)
    deletes anything narrower than 2 x SPIKE and restores every straight edge exactly, so a shared
    seam stays shared.

    MITRE JOINS, not the default round ones. A rounded opening is not idempotent on a real corner:
    it arcs every convex corner at SPIKE radius and samples the arc, which on the first run here
    turned 4-vertex basins into 130-vertex rings of near-duplicate points.

    AND THE RESULT IS INTERSECTED BACK WITH THE INPUT, so the opening can only ever REMOVE ground.
    A mitred offset extends an acute corner by up to `mitre_limit` times the offset in each of its
    two passes, and at the acute wedges where a pocket runs out between a ditch bank and a plot
    edge that was enough to push a corner ~5 px past the bank - putting a new basin's bund inside
    a delivery ditch, which is the very rule (`paddy_bunds_clear_the_supply_channels`) the pocket
    had been clipped to satisfy. Intersecting makes the pass monotone: whatever the offsets do,
    the output is a subset of the bare ground that was handed in.

    AND IT NEVER RAISES. Clipping a pocket to a grid cell can produce a ring carrying a zero-length
    edge, and GEOS refuses to offset one - `TopologyException: found non-noded intersection`, thrown
    from the middle of a map generation (`test_build_comb_supply_banks_hems_bunds_onto_the_channel_
    banks`, 2026-08-17). `buffer(0)` nodes the input first, which handles most of them; for the rest
    the honest answer is that this is a TIDYING step, so a geometry GEOS will not offset goes on
    un-tidied rather than taking the map down. Nothing downstream trusts it: every ring this pass
    records is round-tripped for validity before it is kept."""
    cleaned = geom.buffer(0)
    if cleaned.is_empty:
        return cleaned
    try:
        opened = cleaned.buffer(-_SPIKE, join_style="mitre", mitre_limit=2.0).buffer(_SPIKE, join_style="mitre", mitre_limit=2.0)
        return cleaned.intersection(opened)
    except GEOSException:
        return cleaned


def _ring(poly: Polygon) -> Poly:
    """A plot ring as the manifest records it: 1dp, no repeated closing vertex, and no vertex
    that rounding has collapsed onto its predecessor (a boolean result carries plenty)."""
    out: Poly = []
    for x, y in list(poly.exterior.coords)[:-1]:
        pt = (round(float(x), 1), round(float(y), 1))
        if not out or pt != out[-1]:
            out.append(pt)
    while len(out) > 3 and out[0] == out[-1]:
        out.pop()
    return out


def _water(channels: list[dict[str, Any]], g: float) -> BaseGeometry:
    """Every drawn course plus its BANK - the ground a bund may abut but never stand in.

    Buffered per SEGMENT at the local width, because the supply canals taper hard (14 px head to a
    couple at the tail): one buffer at the widest half-width would claim bank the fan really does
    plant, and re-open exactly the kind of strip this pass exists to close.

    AND A DISC AT EVERY INTERIOR VERTEX, which is not optional. Flat-capped segment buffers are
    rectangles, so two of them meeting at a bend leave a WEDGE of uncovered ground on the outside
    of the turn. Ten of Inashiro's new basins came out with a bund inside a delivery ditch through
    exactly those notches - the ground looked bare to this pass and was water to the gate. The
    discs close them without the over-claim a round CAP would add past the head and tail, where
    `supply_bank_clearance` reports `past` and the stroke governs nothing anyway."""
    strokes: list[BaseGeometry] = []
    for c in channels:
        pts = [(float(q[0]), float(q[1])) for q in c.get("pts") or []]
        if len(pts) < 2:
            continue
        w0 = float(c["w"])
        w1 = float(c.get("w_tail", w0))
        cum = polyline_cum(pts)
        tot = cum[-1] or 1.0

        def half(k: int, w0: float = w0, w1: float = w1, cum: list[float] = cum, tot: float = tot) -> float:
            return taper_w(w0, w1, cum[k] / tot) / 2 + BANK_MARGIN * g

        for i in range(len(pts) - 1):
            strokes.append(LineString([pts[i], pts[i + 1]]).buffer(half(i), cap_style="flat"))
        for i in range(1, len(pts) - 1):
            strokes.append(Point(pts[i]).buffer(half(i)))
    return unary_union(strokes) if strokes else Polygon()


def _band(F: _Frame, us: list[float], fs: list[float], f_far: float) -> Polygon:
    """The region between the sampled curve f(u) and a constant fall far outside the fan."""
    pts = [F.to_xy(u, f) for u, f in zip(us, fs, strict=True)]
    pts += [F.to_xy(us[-1], f_far), F.to_xy(us[0], f_far)]
    return Polygon(pts).buffer(0)


def _outside_command(F: _Frame, a_pts: Poly, dpts: Poly, field: Polygon, g: float, bank: Callable[[float], float]) -> BaseGeometry:
    """Ground the fan cannot command: below the collector, or upslope of the supply canal.

    The collector is extended LEVEL beyond both drawn ends (the same clamp `_fill_wedges` used and
    `floor_overhang` states): the command area's low boundary conceptually continues past the
    drawn water, so a low-u fork wedge still counts as commanded while the floating-diamond ground
    past the outfall does not. Where the canal does not reach a given u there is nothing upslope to
    exclude, so that sample falls back to a bound outside the fan entirely."""
    x0, y0, x1, y1 = field.bounds
    corners = [F.to_uf(x0, y0), F.to_uf(x1, y0), F.to_uf(x1, y1), F.to_uf(x0, y1)]
    ulo, uhi = min(u for u, _ in corners), max(u for u, _ in corners)
    flo, fhi = min(f for _, f in corners), max(f for _, f in corners)
    span = (uhi - ulo) + (fhi - flo) + 1.0
    # SAMPLE THE CURVES FINELY. The band is a polygon through sampled points, so between samples
    # its edge is a CHORD - and a chord across a bend in a wandering collector cuts inside the
    # curve, admitting ground the fan may not plant. A fixed 64 samples is ~23 px apart on a hamlet
    # fan, which was enough to put a new basin's bund in the collector on 4 of 24 cohort seeds. One
    # sample every 6 px is finer than the drain's own jitter, and the whole band costs one polyline
    # scan per sample.
    _n_u = max(64, int((uhi - ulo) / 6.0))
    us = [ulo + (uhi - ulo) * k / _n_u for k in range(_n_u + 1)]
    dus = [F.to_uf(*p)[0] for p in dpts]
    du_lo, du_hi = min(dus), max(dus)

    def drain_f(u: float) -> float:
        fd = _f_at_u(F, dpts, u)
        if fd is not None:
            return fd
        end = dpts[0] if abs(u - du_lo) < abs(u - du_hi) else dpts[-1]
        return F.to_uf(*end)[1]

    def canal_f(u: float) -> float:
        fc = _f_at_u(F, a_pts, u)
        return flo - span if fc is None else fc + 4 * g

    # The low bound is the collector's BANK IN FALL - `_drain_bank`, the very function `_carve`
    # hems its closing rank onto - not a flat margin. `_fill_wedges` used a flat 3 * grain, which
    # is neither: too much where the collector is narrow (it left the last residue of doubled bunds
    # along the fan's toe, wedges this pass was forbidden to reach) and too little downstream,
    # where the drain widens to DRAIN_FT[1] and `paddy_bunds_clear_the_collector` measures a
    # slope-leaned set-back that a flat margin does not cover. Same predicate as the placer, so
    # ground this pass plants is ground the carve would have been allowed to plant.
    below = _band(F, us, [drain_f(u) - bank(u) for u in us], fhi + span)
    above = _band(F, us, [canal_f(u) for u in us], flo - span)
    return unary_union([below, above])


def _open_to(pocket: Polygon, w: float) -> Polygon | None:
    """`pocket` with everything narrower than `w` removed, or None if nothing survives.

    THE TAPERING-SCRAP ESCAPE. A scrap that needles every basin it could join is almost always a
    TAPERING strip: wide enough to be real at one end, running out to nothing at the other. Welding
    all of it draws the host out to a point; welding none of it leaves a doubled bund. Neither is
    what a farmer does - they take the strip as far as it is worth walling and let the last sliver
    go, which is this function.

    The width to stop at is not a guess: `paddy_plot_seams_shared` ignores a gap under 3 ft on its
    own stated reasoning ("two bunds that close draw as one line"), so a tail left below that is
    invisible to the doubled-bund rule by the rule's OWN definition rather than by a tolerance
    tuned until the pool passed. So the weld gets the workable part and the sub-3-ft tail stays
    bare, which is also the "odd corner left unpaddied" the research describes.

    Mechanically this is `_despike`'s opening at a larger radius, with the same two safeguards and
    for the same reasons: MITRE joins (a rounded opening arcs every convex corner and explodes the
    vertex count) and INTERSECTING the result back with the input (a mitred offset can push an
    acute corner outward, and this pass must only ever REMOVE ground)."""
    try:
        opened = pocket.buffer(-w / 2, join_style="mitre", mitre_limit=2.0).buffer(w / 2, join_style="mitre", mitre_limit=2.0)
    except GEOSException:
        return None
    parts = _parts(pocket.intersection(opened.buffer(0)))
    if not parts:
        return None
    return max(parts, key=lambda p: p.area)


def _min_apex(ring: Poly) -> float:
    """The sharpest interior angle in `ring`, in degrees (180.0 for a ring too short to have one).

    `pointed_ring` answers the yes/no; this answers "how sharp", which is what lets `_absorb` RANK
    imperfect welds instead of only accepting or refusing them."""
    n = len(ring)
    if n < 3:
        return 180.0
    out = 180.0
    for i in range(n):
        a, v, c = ring[i - 1], ring[i], ring[(i + 1) % n]
        v1 = (a[0] - v[0], a[1] - v[1])
        v2 = (c[0] - v[0], c[1] - v[1])
        d1 = math.hypot(*v1) or 1.0
        d2 = math.hypot(*v2) or 1.0
        cs = max(-1.0, min(1.0, (v1[0] * v2[0] + v1[1] * v2[1]) / (d1 * d2)))
        out = min(out, math.degrees(math.acos(cs)))
    return out


def _absorb(pocket: Polygon, into: list[Polygon], grown: set[int], thin: float, g: float) -> bool:
    """Fold a too-thin pocket into the basin it shares the most bund with - the weld that turns two
    walls with a strip between them into the one wall a real aze is. The neighbor is chosen by
    SHARED BOUNDARY LENGTH rather than by distance or area: the basin whose wall actually forms
    most of this strip is the one whose farmer would have taken it in."""
    bx0, by0, bx1, by1 = pocket.bounds
    reach = pocket.buffer(0.4)
    ranked: list[tuple[float, int]] = []
    for j, q in enumerate(into):
        qx0, qy0, qx1, qy1 = q.bounds
        if qx1 < bx0 - 1 or qx0 > bx1 + 1 or qy1 < by0 - 1 or qy0 > by1 + 1:
            continue
        shared = q.boundary.intersection(reach).length
        if shared > 0.0:
            ranked.append((-shared, j))
    # EVERY candidate in turn, not just the best one. A union comes back as a MultiPolygon (the
    # strip meets that basin only at a point) or with a hole (it wraps the basin) often enough to
    # matter - 64 of 255 welds on Inashiro - and each failure leaves the doubled bund it was there
    # to close. The runner-up basin borders the same strip and usually takes it cleanly.
    _fallback: tuple[float, int, Polygon] | None = None
    _lumpy: tuple[float, int, Polygon] | None = None
    _chev: tuple[float, int, Polygon] | None = None
    _jogged: tuple[int, int, Polygon] | None = None
    for _neg, j in sorted(ranked):
        # dilate the scrap by a hair before the union. A scrap and the basin beside it only TOUCH
        # (they were cut from each other), and a union of two merely-touching polygons comes back
        # as a MultiPolygon or an invalid ring as often as not - which used to abandon the weld and
        # leave the doubled bund. 0.02 px is two orders below the 0.1 px the manifest records, so
        # it changes the geometry by nothing and the overlap by enough.
        merged = into[j].union(pocket.buffer(0.02)).buffer(0)
        if not isinstance(merged, Polygon) or merged.interiors:
            continue
        # SIMPLIFY CAN INVALIDATE. Douglas-Peucker moves vertices independently, and on the long
        # thin unions this pass makes that is enough to fold a ring back through itself: Inashiro
        # shipped a 10-vertex bow-tie basin whose outline crossed its neighbor's twice and read as
        # a doubled bund at the fan toe. Simplification here is only tidying, so a result that is
        # not a clean simple polygon is discarded in favor of the union it came from.
        simplified = merged.simplify(0.05)
        candidate = simplified if isinstance(simplified, Polygon) and simplified.is_valid and not simplified.interiors else merged
        # AND JUDGE THE RING THE MANIFEST WILL ACTUALLY CARRY. Validating the shapely polygon is
        # not enough: `_ring` rounds to 0.1 px afterwards, and on a near-degenerate weld that last
        # rounding is itself enough to cross two edges (settlement-review, Inashiro 2026-08-17,
        # basin #570 - a valid union recorded as a 13-vertex ring that folded back on itself into
        # an 875 sq ft lobe plus a 46 x 1.1 ft sliver). A crossing ring is invisible in ink under a
        # 1.5 px stroke, which is exactly why it has to be caught here rather than by eye: every
        # downstream consumer that measures basin geometry gets a MultiPolygon where it expects a
        # basin. So the recorded ring is round-tripped and the weld declined if it does not survive
        # - the runner-up basin takes the scrap instead.
        if not Polygon(_ring(candidate)).is_valid:
            continue
        # AND A WELD MUST NOT MAKE A NEEDLE OUT OF THE BASIN THAT TAKES THE SCRAP. Measured by
        # provenance on Inashiro (2026-08-17): with the carve and `_plant` both refusing needles,
        # EVERY surviving one was `carved_grown` - a perfectly good basin that welding a toe strip
        # into it drew out to a point. Absorbing is meant to turn two walls into one, not to trade
        # a doubled bund for an unworkable apex, so this is judged in the same ladder as the
        # MultiPolygon, hole and bow-tie rejections above and for the same reason: the runner-up
        # basin borders the same strip and usually takes it cleanly.
        #
        # AND IF NO NEIGHBOR CAN TAKE IT, THE SCRAP STAYS BARE, WHICH IS THE HONEST ANSWER. A
        # strip that needles every basin it touches is the "odd corner left unpaddied" that the
        # research describes at a real fan toe - the fan's base floor (`comb_base_fill`) draws
        # under it, so it reads as the toe's own ground rather than as a hole, exactly as it does
        # for the slivers `_comb_toe_and_hem` drops.
        # MEASURE THE RING THE GATE MEASURES - the DEDUPED one, and nothing else. This guard used to
        # take min(raw, deduped): stricter, but stricter on a DIFFERENT measurement than the rule it
        # is protecting, which is not a margin at all. `paddy_plots_are_workable_basins` reads the
        # deduped ring, so an apex only the raw ring carries is invisible to the rule and must not be
        # able to veto a weld here. Placer-stricter-than-gate means a stricter THRESHOLD on the SAME
        # measurement (18 vs 15), never a second measurement bolted alongside it.
        _cand = dedup_ring(_ring(candidate), 1.0)
        _apex = _min_apex(_cand)
        if _apex < _WELD_MIN_APEX:
            # NOT GOOD ENOUGH, BUT REMEMBER IT - refusing outright is its own defect. Measured on
            # the 24-seed cohort: declining every needling weld traded two needles for two doubled
            # bunds (seeds 9 and 11) and took the cohort 22 -> 20, because a scrap that needles the
            # basin it would join is often a TAPERING strip whose only alternative is to lie bare
            # between two walls. Neither outcome is realistic, so the choice is not decline-or-
            # accept: it is WHICH NEIGHBOR takes it. The ranking above is by shared bund length,
            # which is the right first preference (the farmer whose wall already forms most of the
            # strip); when none of those is clean, the honest fallback is the neighbor that takes
            # the strip BEST rather than the one that shares the most of it.
            # BEFORE GIVING UP ON THIS NEIGHBOR, TRY THE WORKABLE PART OF THE SCRAP. `_open_to`
            # drops the tapering tail that is narrower than the doubled-bund rule's own 3 ft floor,
            # so the host takes the part worth walling and what is left is a sliver that rule
            # already treats as one line rather than two. This is what resolves cohort seeds 9 and
            # 11, where welding the whole scrap needled the host and welding none of it doubled a
            # bund - the choice was never between those two.
            _part = _open_to(pocket, thin)
            if _part is not None:
                _m2 = into[j].union(_part.buffer(0.02)).buffer(0)
                if isinstance(_m2, Polygon) and not _m2.interiors:
                    _s2 = _m2.simplify(0.05)
                    _c2 = _s2 if isinstance(_s2, Polygon) and _s2.is_valid and not _s2.interiors else _m2
                    _r2 = _ring(_c2)
                    # ...and the partial weld faces the arrowhead test too. This path had only the
                    # apex guard, and a provenance probe found it was where the survivors came from:
                    # ZERO chevrons entered `close_seams` on Inashiro and Mizuguchi and three left,
                    # because welding the workable PART of a scrap is exactly how a basin acquires a
                    # point at one end and a bite in its side.
                    if Polygon(_r2).is_valid and _min_apex(dedup_ring(_r2, 1.0)) >= _WELD_MIN_APEX and not is_chevron(_r2):
                        into[j] = _c2
                        grown.add(j)
                        return True
            if _fallback is None or _apex > _fallback[0]:
                _fallback = (_apex, j, candidate)
            continue
        # AND A WELD MUST NOT MAKE A LUMP OUT OF THE HOST EITHER. The ranking above is by shared
        # bund length, which is blind to the SHAPE the union comes out as, and both guards it has
        # already passed measure an apex - so a union that grows a blunt-cornered lobe or an
        # out-and-back prong sails through them (settlement-review, Mizuguchi and Sawada
        # 2026-08-17; see `_WELD_MIN_SOLIDITY` for the measurements and for why solidity rather
        # than an angle). Treated exactly like a needling weld, and for the same reason: the
        # runner-up borders the same strip and usually takes it in a shape a farmer would
        # recognize, but refusing every host outright would trade the lump for a doubled bund.
        # A WELD MUST NOT MAKE AN ARROWHEAD EITHER, and this is a third measurement rather than a
        # tighter one: a chevron is pointed AND notched, and this ladder's apex guard (18 deg) and
        # solidity guard (0.85) each pass a ring at 39 deg / 0.878 that is plainly an arrowhead. See
        # `_CHEVRON_MIN_APEX` for the measured population. Same treatment as a lump - remembered, not
        # refused outright, so the scrap still finds a host when no clean one exists.
        _sol = candidate.area / (candidate.convex_hull.area or 1.0)
        if is_chevron(_ring(candidate)):
            if _chev is None or _sol > _chev[0]:
                _chev = (_sol, j, candidate)
            continue
        if _sol < _WELD_MIN_SOLIDITY:
            if _lumpy is None or _sol > _lumpy[0]:
                _lumpy = (_sol, j, candidate)
            continue
        # AND A WELD MUST NOT MAKE THE HOST'S WALL STEP SIDEWAYS. This is the third shape complaint
        # in the same ladder and it is blind to the two above it by construction: a scrap welded on
        # flush at both its own ends but a few feet PAST the host's leaves the host a rectangular
        # tab, which is a right-angled 90/270 corner pair (no apex to fail) at solidity ~0.8 (no lump
        # to fail) - and reads as an earthen wall randomly zigzagging, which is how the GM found it
        # (2026-08-18, `jog_steps`). It arises because `_plant` grids a pocket at ITS OWN pitch, so
        # the offcuts it hands back are cut where neither the row above nor the row below has a seam;
        # welding one alternately up and down builds the staircase. Judged as a DELTA against the
        # host's current ring rather than as an absolute, for the reason the apex guard gives about
        # measuring what the rule measures: a host that already carries a step must not be barred
        # from taking in the scrap beside it because of a step that was there first.
        _jog = jog_steps(_ring(candidate), g) - jog_steps(_ring(into[j]), g)
        if _jog > 0:
            if _jogged is None or _jog < _jogged[0]:
                _jogged = (_jog, j, candidate)
            continue
        into[j] = candidate
        grown.add(j)
        return True
    # THE LEAST-JOGGING WELD, ahead of both. When no host takes the scrap without complaint, a wall
    # standing a few feet off line is the mildest of the three: the basin is still a basin a farmer
    # would build, which is more than the lump or the needle can say. Ranked by how many steps the
    # weld ADDS, so a host that takes the scrap with one step beats one that takes it with three.
    if _jogged is not None:
        _, j, candidate = _jogged
        into[j] = candidate
        grown.add(j)
        return True
    # THE LEAST-LUMPY WELD, ahead of the needle fallback below. A lobe is a milder defect than an
    # unworkable apex - it is a basin a farmer would call awkward rather than one they could not
    # flood - so when no host takes the scrap cleanly, the shape complaint yields before the
    # workability one does.
    if _lumpy is not None:
        _, j, candidate = _lumpy
        into[j] = candidate
        grown.add(j)
        return True
    # ...then the least-bad ARROWHEAD, behind the lump. A chevron is the worse read of the two - a
    # lump is an awkward basin, an arrowhead does not read as a basin at all - so it is the last
    # shape the ladder will accept, and only when no other host will take the scrap. (Merged
    # 2026-08-18: this tier and the jog tier above were added independently by two sessions to the
    # same ladder. Order is by how badly the shape reads - jog, then lump, then arrowhead - so the
    # mildest complaint yields first, which is the ordering rule the two tiers above already state.)
    if _chev is not None:
        _, j, candidate = _chev
        into[j] = candidate
        grown.add(j)
        return True
    # THE LEAST-BAD WELD, and only if it still clears the GATE. `_WELD_MIN_APEX` is the placer's
    # margin, not the rule; a union between the gate line and that margin is a basin the gate
    # ACCEPTS, so welding it is strictly better than leaving a doubled bund. Below the gate line it
    # is a real needle and the scrap stays bare instead - the "odd corner left unpaddied" the
    # research describes, which the Sawada review confirmed is invisible in ink (the fan's base
    # floor is drawn in the same fill as a plot interior, measured at the pixel).
    if _fallback is not None and _fallback[0] >= _GATE_MIN_APEX + 1.0:
        _, j, candidate = _fallback
        into[j] = candidate
        grown.add(j)
        return True
    return False
