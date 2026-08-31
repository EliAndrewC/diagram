"""Split from waterfields/seams.py by feature 173 - see this package's CLAUDE.md for the index."""

import math
import random
from collections.abc import Callable
from typing import Any

from shapely.geometry import Polygon
from shapely.ops import unary_union

from ..banks import (
    _GATE_MIN_APEX,
    _GATE_MIN_AREA,
    _TINT_END_FT,
    _TINT_MAX_AREA_RATIO,
    _TINT_MAX_ASPECT,
    _TINT_MIN_APEX,
    _TINT_MIN_SOLIDITY,
    _TOE_MIN_APEX,
    _TOE_MIN_AREA,
    cell_area,
    dedup_ring,
    is_chevron,
    pointed_ring,
    tapers_to_a_point,
)
from ..frame import Poly, _Frame
from ..palette import FLOODED, RICE_GREENS
from .plots import _plant, _unjog
from .pockets import MIN_PLOT_SIDE, _absorb, _despike, _outside_command, _parts, _ring, _water

# past that the 'repair' is moving more ground than the step it retires, which is a land grab wearing a
# repair's clothes. Feature 152 T18; the lever itself was recorded untried in future-work/farming-communities.md.


def close_seams(
    R: random.Random,
    F: _Frame,
    plots: list[dict[str, Any]],
    envelope: Poly,
    g: float,
    channels: list[dict[str, Any]],
    plot_across: float,
    row_step: tuple[float, float],
    a_pts: Poly,
    dpts: Poly,
    bank: Callable[[float], float],
) -> None:
    """Plant or absorb every scrap of bare ground the carve left inside the command area, so that
    each basin's bund is shared with whatever lies on the other side of it. Mutates `plots` in
    place: absorbed neighbors get a new `poly`, planted pockets are appended."""
    if not plots or len(envelope) < 3:
        return
    half = MIN_PLOT_SIDE * g / 2
    # A RING THAT CROSSES ITSELF IS NOT A BASIN, and it is drawn as ink whatever the manifest thinks.
    # Sawada shipped one: ring 688 at (167, 2558), four vertices whose edges 1-2 and 3-0 cross, and
    # the SVG carries it verbatim as a `<polygon>` (settlement-review 2026-08-18). It is INVISIBLE -
    # the neighbor painted after it covers the stray edge and the nonzero fill hides the bow - so no
    # amount of looking would have found it; what makes it worth removing is that it is not a simple
    # polygon, so every shape metric computed on it is meaningless. It scores solidity 0.43, the
    # worst on the sheet, and the area floor cannot reach it because its shoelace area is 2.9x the
    # floor. This pass already drops a WELD whose rounded ring will not survive validation, on
    # exactly the argument that "bare ground is an honest thing to record, a crossing ring is not";
    # a CARVED plot had no equivalent. One ring in 818 fails it, so the cost is a scrap of floor the
    # fan's base fill already covers.
    #
    # REPAIR, DO NOT DROP - measured. `buffer(0)` nodes a bow-tie into valid parts and the largest
    # is the basin the carve meant; keeping it holds the plot COUNT, so the shared placement RNG
    # does not re-roll and the map barely moves. Dropping instead cost two cohort seeds
    # (`features_do_not_overlap`, `lanes_reach_something`) purely through that rotation, on top of
    # the bare-ground problem below. A ring `buffer(0)` cannot rescue is still dropped.
    #
    # IT RUNS FIRST, not last, and that ordering is the whole fix. Dropped AFTER the plant/absorb
    # passes the ring's ground is simply gone, and the neighbor's wall is left standing alone -
    # 12 of 48 cohort seeds failed `paddy_plot_seams_shared` that way. Dropped HERE the ground is
    # just more bare pocket, and this pass reclaims it like any other.
    for _p in plots:
        if len(_p["poly"]) < 3 or Polygon(_p["poly"]).is_valid:
            continue
        _fixed = _parts(Polygon(_p["poly"]).buffer(0))
        if not _fixed:
            continue
        # ...and the repaired ring faces the same bar every other basin does. Noding a bow-tie can
        # leave the surviving lobe pointed - cohort seed 20 came out as a needle and tripped
        # `paddy_plots_are_workable_basins` - so a repair that is not a workable basin is refused and
        # the ground returns to the bare pocket below, which is this pass's standing answer for a
        # scrap. Judged at the GATE's own threshold, since a repair is not a placement choice.
        _cand = _ring(max(_fixed, key=lambda q: q.area))
        if len(_cand) >= 3 and not pointed_ring(dedup_ring(_cand, 1.0), _GATE_MIN_APEX):
            _p["poly"] = _cand
    plots[:] = [_p for _p in plots if len(_p["poly"]) >= 3 and Polygon(_p["poly"]).is_valid]
    keep = [Polygon(p["poly"]).buffer(0) for p in plots]
    field = Polygon(envelope).buffer(0)
    outside = _outside_command(F, a_pts, dpts, field, g, bank)
    water = _water(channels, g)
    carved = len(keep)
    grown: set[int] = set()
    # TWICE ROUND. Welding a scrap into a basin changes which basin borders the NEXT scrap, and
    # planting a pocket gives its neighbors a new edge to weld against - so a second look at the
    # bare ground reaches scraps the first pass could not place (three of Inashiro's toe wedges,
    # where a strip's only candidate refused the union until the basin beside it had grown). A
    # third round finds nothing on any pool map: the set converges because every round can only
    # shrink the bare ground.
    for _round in range(2):
        bare = field.difference(unary_union(keep)).difference(water).difference(outside)
        basins: list[Polygon] = []
        scraps: list[Polygon] = []
        for pocket in _parts(bare):
            for piece in _parts(_despike(pocket.simplify(0.05))):
                if piece.buffer(-half).is_empty:
                    scraps.append(piece)
                else:
                    got, offcuts = _plant(F, piece, plot_across, row_step, half)
                    # A NEEDLE IS A SCRAP, NOT A BASIN - it just does not look like one to the
                    # thinness test above. `buffer(-half).is_empty` asks "is this too thin
                    # ANYWHERE to be a plot", which a LONG wedge passes on the strength of its
                    # middle while its point is still unworkable; that is how the fan-toe sunburst
                    # survived both this pass and `_comb_toe_and_hem`'s inradius drop (GM realism
                    # ruling 2026-08-17 - see `_TOE_MIN_APEX`). So re-judge what `_plant` hands
                    # back by APEX as well, and send the needles down the scrap path, where
                    # `_absorb` welds each into the basin it shares the most bund with. That is
                    # this module's own research answer for an unplantable scrap ("taken into the
                    # basin beside it rather than walled off on its own"), so the ground stays
                    # planted, the bund stays shared, and no bare floor is opened. BOTH rings, at
                    # the carve's generous 25 deg, for the reason the tint rule below gives: the
                    # merge retires some apexes and creates others, and the placer must stay
                    # strictly stricter than the gate's 15.
                    # A FRAGMENT IS A SCRAP TOO, on exactly the same argument and for the same
                    # destination. `_plant` tiles at ~plot_across x row_step, so its whole tiles are
                    # fine; what it also hands back are the part-tiles where the pocket ran out, and
                    # a part-tile under `_TOE_MIN_AREA` of the design cell is not a basin worth its
                    # own perimeter of azenuri when the neighbor can simply take the ground in (see
                    # `_TOE_MIN_AREA` in banks.py for why the floor is a RATIO and not an acreage).
                    # This is the seam-pass half of the rule `_comb_toe_and_hem` applies to the
                    # carve: without it the toe pass drops a fragment, the ground returns here as
                    # bare pocket, and this pass plants the same fragment straight back.
                    _floor = _TOE_MIN_AREA * cell_area(plot_across, row_step)
                    for _q in got:
                        _qr = _ring(_q)
                        if len(_qr) >= 3 and (pointed_ring(_qr, _TOE_MIN_APEX) or pointed_ring(dedup_ring(_qr, 1.0), _TOE_MIN_APEX) or _q.area < _floor or is_chevron(_qr)):
                            scraps.append(_q)
                        else:
                            basins.append(_q)
                    scraps += offcuts
        # PLANT FIRST, WELD SECOND, and weld against the whole field including what was just
        # planted: a scrap's best neighbor is often the new basin beside it, and a scrap offered
        # only its own siblings has nowhere to go when they refuse the union.
        keep += sorted(basins, key=lambda q: (round(q.bounds[0], 1), round(q.bounds[1], 1)))
        for scrap in sorted(scraps, key=lambda q: (round(q.bounds[0], 1), round(q.bounds[1], 1))):
            # The 3 ft `paddy_plot_seams_shared` itself ignores, in px at this map's scale. MIND THE
            # UNIT: `grain` is `2 / ftpx` (the scripted tier's principled value), so px-per-foot is
            # `g / 2` and 3 ft is `1.5 * g` - NOT `3.0 * g`, which is what this said first and is
            # double. At a hamlet's ftpx 1.0 that fed 6.0 px to an opening meant to shed a tail from
            # a strip whose whole mean width was 5.6 px, so it annihilated every scrap it was handed
            # and the escape hatch silently did nothing (cohort seeds 9 and 11). Measured at the
            # corrected width the same weld comes out at a 77.1 deg apex.
            _absorb(scrap, keep, grown, 1.5 * g, g)
    for j in sorted(j for j in grown if j < carved):
        plots[j]["poly"] = _ring(keep[j])
    for basin in keep[carved:]:
        # ROUND-TRIP THE RECORDED RING here too, for the reason `_absorb` gives: a valid polygon can
        # still cross itself once `_ring` rounds it to 0.1 px, and a planted basin gets the same
        # rounding a welded one does. A basin that will not survive it is dropped and its ground
        # left to the fan floor - bare ground is an honest thing to record, a crossing ring is not.
        ring = _ring(basin)
        # A PLANTED BASIN THAT WILL NOT SURVIVE ITS OWN ROUNDING. Defensive, and not reachable from this
        # engine's own geometry: a valid polygon can still cross itself once `_ring` rounds it to 0.1 px,
        # so a planted basin gets the same test a welded one does - but the basins this pass plants come
        # from the fan's own tessellation and are far larger than the rounding. Tried and refused
        # (feature 146): collinear plot rings, 0.02-0.06 px slivers, and bow-tie rings, all dropped by an
        # earlier guard. Bare ground is an honest thing to record; a crossing ring is not.
        if len(ring) < 3 or not Polygon(ring).is_valid:  # pragma: no cover - see above
            continue
        # `filler` is read by the water-topology anchors (channel_field_anchored), which want a
        # plot the CARVE sited rather than one this pass reclaimed
        plots.append({"poly": ring, "fill": R.choice(RICE_GREENS), "filler": True})
    _unjog(plots, g, _GATE_MIN_AREA * cell_area(plot_across, row_step), water, outside)
    # A POINTED SLIVER MUST NOT WEAR THE WATER TINT - the same rule `_sector_closing_rank` applies
    # when it carves one, and for the same reason: a blue plot tapering to a needle reads as a tiny
    # triangular pond at fit zoom, not as a leveled basin. The carve's own demotion judges the quad
    # it cuts, and TWO later stages reshape it - `_comb_toe_and_hem`'s re-hem onto the drain bank,
    # and this pass's welds - so the tint is re-judged here, at the end, against every plot's final
    # ring rather than only the ones this pass touched. The replacement green is indexed by POSITION
    # rather than drawn from R - the point is the ABSENT DRAW (the stream stays put, so demoting one
    # plot cannot re-roll the rest), not variety: `RICE_GREENS` holds one color three times today.
    # Wording kept honest after a settlement-review read the old comment as promising shades.
    # so it takes no draw from R and no other plot's color moves; `low` is untouched, because it is
    # the topography and the tint is only the picture (feature 010).
    # BOTH the raw ring and the deduped one, because the two carry different apexes and the gate
    # judges the RAW one. `_sector_closing_rank` dedupes before testing for the reason its own
    # comment gives - a quad with a sub-pixel collapsed edge shows near-90 deg corners while its
    # merged triangle shows the needle - but the merge can also retire an apex the raw ring still
    # has, and `flooded_plots_read_as_basins` reads the ring as recorded (cohort seed 8). Testing
    # both at the carve's generous 25 deg keeps the placer strictly stricter than the gate's 15.
    # THE FOURTH BLIND SPOT: EVERY PREDICATE MEASURES SHAPE, NONE MEASURES SIZE (feature 152 T10,
    # settlement-review 2026-08-29). Sawada's surviving flooded plot is 6,706 sq ft - 4.9x the median
    # basin and the largest of 776 - on the one map whose whole brief is that it has no pond, so the
    # object a reader's eye lands on in the field is a 170 ft blue sheet. Every shape test passed it
    # honestly: min apex 29.4 deg, no short end, good solidity. What it is, is BIG - `close_seams`
    # absorbed it up to several design cells and it kept the tint it was given as one. A basin far
    # larger than its neighbors does not read as a basin whatever its outline, so size joins the other
    # four. Measured on the FINAL ring, after absorption, which is the only place the size exists.
    _areas = sorted(Polygon(_q["poly"]).buffer(0).area for _q in plots if len(_q.get("poly") or []) >= 3)
    _median_plot = _areas[len(_areas) // 2] if _areas else 0.0
    for p in plots:
        # TWO RINGS, AND BOTH CLAUSES EARN THEIR KEEP - this is the one place a second measurement is
        # right, and the reason is that they answer to different masters. `flooded_plots_read_as_basins`
        # is the GATE for a tinted plot and it reads `dedup_ring(r, 1.0)` at 15 deg, so the first
        # clause is the placer being strictly stricter on the GATE'S OWN measurement (25 vs 15) - drop
        # it and a plot pointed at 1.0 but blunt at the end width keeps its tint and trips the gate,
        # which is exactly what cohort seed 8 did when this briefly tested the end-collapsed ring
        # alone. The second clause catches the defect the gate CANNOT see: a needle truncated a few
        # feet short of its point, which no interior angle on the 1.0 ring will ever report.
        # AND A THIRD CLAUSE, WHICH MEASURES SHAPE RATHER THAN TAPER. Both clauses above ask "does
        # this come to a point"; neither can see a blunt-cornered LOBE, and welding a scrap into
        # the fan's one blue plot is exactly how a lobe gets there. Sawada shipped a 0.731-solidity
        # flooded plot reading as an arrowhead pond with a 41.8 deg minimum apex and both ends
        # wider than 5 ft - clear of both guards (see `_TINT_MIN_SOLIDITY`). Blue has to mean "a
        # leveled basin pooling on the collector", so a blue plot that does not read as a basin
        # goes back to rice green whatever its corners measure.
        # AND A FOURTH CLAUSE, WHICH MEASURES SITING RATHER THAN SHAPE - the first blind spot the
        # three above share. Sawada, whose gen docstring and notes both define it as the hamlet with
        # NO pond, shipped a 78 x 72 ft blue basin 4 ft from the collector's tail and 15 ft from the
        # head of the off-map brook: a compact blue blob fused to the exact point where the ditch
        # becomes a stream and leaves the frame, which is where a tameike sits. Every shape predicate
        # passed it and correctly so - min apex 81.4 deg, no end under `_TINT_END_FT`, solidity 0.910.
        # It is a perfectly good basin standing in the one place a reader cannot read as a basin
        # (settlement-review 2026-08-18).
        #
        # THE OUTFALL, NOT THE WHOLE DRAIN. Blue MEANS "the closing rank pooling before the outfall",
        # so a blue plot lying ALONG the collector is the rule working; only the terminus is
        # ambiguous, and the keep-out is one and a half plot widths of it - far enough to break the
        # fusion with the stream head, near enough to leave the rest of the closing rank tinted.
        _t_end = _TINT_END_FT * g / 2
        _pg = Polygon(p["poly"]).buffer(0)
        _psol = (_pg.area / (_pg.convex_hull.area or 1.0)) if isinstance(_pg, Polygon) and not _pg.is_empty else 1.0
        _pcx = sum(_q[0] for _q in p["poly"]) / len(p["poly"])
        _pcy = sum(_q[1] for _q in p["poly"]) / len(p["poly"])
        # TO THE PLOT'S NEAREST CORNER, NOT ITS CENTROID (settlement-review, Sawada, feature 145). The
        # centroid put Sawada's brook-mouth plot 88.1 px from the terminus - outside the radius - while its
        # nearest corner was 43.6 px, well inside it, and at fit zoom the 72 x 68 ft blue square fused with
        # the stream head exactly as this rule exists to prevent. The engine's own doctrine is that a gap
        # verdict reads footprints and never centers; this one read a center. The radius is unchanged.
        _at_outfall = bool(dpts) and min(math.hypot(_q[0] - dpts[-1][0], _q[1] - dpts[-1][1]) for _q in [*p["poly"], (_pcx, _pcy)]) < 1.5 * plot_across
        # AND A FIFTH CLAUSE, WHICH MEASURES PROPORTION - the blind spot the four above share. Apex,
        # end width, solidity and siting all pass a long parallel-sided WEDGE, and a wedge in blue
        # reads as a channel of water rather than as a basin holding it (see `_TINT_MAX_ASPECT`).
        _mrr = _pg.minimum_rotated_rectangle if isinstance(_pg, Polygon) and not _pg.is_empty else None
        _asp = 1.0
        if isinstance(_mrr, Polygon):
            _sides = [math.dist(_q, _r) for _q, _r in zip(list(_mrr.exterior.coords)[:-1], list(_mrr.exterior.coords)[1:], strict=True)]
            if len(_sides) >= 2 and min(_sides[0], _sides[1]) > 0.0:
                _asp = max(_sides[0], _sides[1]) / min(_sides[0], _sides[1])
        if p.get("fill") == FLOODED and (
            pointed_ring(dedup_ring(p["poly"], 1.0), _TINT_MIN_APEX)
            or tapers_to_a_point(p["poly"], _t_end, _TINT_MIN_APEX, 4 * _t_end)
            or _psol < _TINT_MIN_SOLIDITY
            or _at_outfall
            or _asp > _TINT_MAX_ASPECT
            or (_median_plot > 0.0 and _pg.area > _TINT_MAX_AREA_RATIO * _median_plot)
        ):
            p["fill"] = RICE_GREENS[(int(abs(p["poly"][0][0]) * 7) + int(abs(p["poly"][0][1]) * 3)) % len(RICE_GREENS)]
