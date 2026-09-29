"""Split from waterfields/seams.py by feature 173 - see this package's CLAUDE.md for the index."""

from __future__ import annotations

import math
import random
from collections.abc import Callable, Collection
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:  # shapely's names for the type checker; `_load_shapely` binds the runtime ones
    from shapely.geometry import LineString, Polygon
    from shapely.ops import unary_union
    from shapely.strtree import STRtree

from ..banks import (
    _GATE_MIN_APEX,
    _GATE_MIN_AREA,
    _TINT_END_FT,
    _TINT_MAX_AREA_RATIO,
    _TINT_MAX_ASPECT,
    _TINT_MIN_APEX,
    _TINT_MIN_RECTANGULARITY,
    _TINT_MIN_SOLIDITY,
    _TOE_MIN_APEX,
    _TOE_MIN_AREA,
    cell_area,
    dedup_ring,
    is_chevron,
    jog_vertices,
    pointed_ring,
    tapers_to_a_point,
)
from ..frame import Poly, Pt, _Frame
from ..palette import FLOODED, RICE_GREENS
from ..ring_rules import MAX_STEPS, RingContext, as_recorded, fan_context, needle, ring_violations
from .geoms import GeomTree, ring_polygons
from .plots import _plant, _unjog
from .pockets import MIN_PLOT_SIDE, _absorb, _despike_many, _outside_command, _parts, _ring, _water

_SHAPELY_LOADED = False


def _load_shapely() -> None:
    """Bind shapely's names into this module, on first use rather than at import (feature 237, FR-010).

    WHY. `import shapely` costs 16.3 MiB of resident memory - it pulls numpy in with it - and a module-level
    import here made all ten gate workers pay that merely to COLLECT this package, whichever one of them ran
    the geometry (`specs/237-lean-test-collection/research.md` R9). Only a worker that builds a map needs it.

    WHY NOT AN `import` INSIDE THE FUNCTIONS THEMSELVES. Several of them run per plot, per seam or per
    candidate, and an `import` statement re-enters `__import__` on every call. Binding the names into this
    module's own globals ONCE leaves every call site the plain global lookup it already was, so the deferral
    costs nothing in steady state (spec D6); the sentinel makes a repeat call two bytecodes. An increase on
    any seed is not waiverable for this item - the bookends are `make perf LABEL=237-start|-end`.
    """
    global _SHAPELY_LOADED, LineString, Polygon, STRtree, unary_union  # binding this module's own names is the point
    if _SHAPELY_LOADED:
        return
    from shapely.geometry import LineString, Polygon
    from shapely.ops import unary_union
    from shapely.strtree import STRtree

    _SHAPELY_LOADED = True


def _needle(poly: Poly) -> bool:
    """The flooded tint's needle rule on the ring AS RECORDED - `ring_rules.needle`, the test's own call, asked of the
    plot rounded to the manifest's 0.1 px (feature 287, T04), so the tint pass and the test judge one ring."""
    return needle([(round(float(q[0]), 1), round(float(q[1]), 1)) for q in poly])


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
    supply_banks: bool = True,
) -> None:
    """Plant or absorb every scrap of bare ground the carve left inside the command area, so that
    each basin's bund is shared with whatever lies on the other side of it. Mutates `plots` in
    place: absorbed neighbors get a new `poly`, planted pockets are appended.

    `supply_banks`: the carve hemmed its bunds onto the supply strokes (`build_comb(supply_banks=True)`, which every
    scripted hamlet passes), so the ring rules hold them to the stroke rule (W16). A comb carved without it - the legacy
    gens' opt-out, which the gate also exempts (`carve_comb`) - is held to every other ring rule."""
    _load_shapely()
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
    _visible_parts(plots, cell_area(plot_across, row_step), 1.25 * g)
    _repair_crossing_rings(plots)
    keep = ring_polygons([p["poly"] for p in plots])
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
    # THE SECOND ROUND'S COVER IS THE FIRST'S PLUS WHAT CHANGED (feature 276, FR-004, plan D14): the union of every plot -
    # ~700 on a pool field - was rebuilt from scratch each round, while between the two only the basins planted and the
    # basins that took a scrap in are new. Their union with the first round's cover is the same ground up to the
    # 0.05 px a weld's simplify can trim, far under the half-pixel `_despike` removes from what bare ground is left.
    import shapely

    covered: Any = None
    _round_start, _grown_before = len(keep), set(grown)
    for _round in range(2):
        covered = unary_union(keep) if covered is None else unary_union([covered, *[keep[j] for j in sorted(grown - _grown_before)], *keep[_round_start:]])
        _round_start, _grown_before = len(keep), set(grown)
        bare = field.difference(covered).difference(water).difference(outside)
        basins: list[Polygon] = []
        scraps: list[Polygon] = []
        # EVERY POCKET SIMPLIFIED AND DESPIKED IN ONE BATCH (feature 276, FR-004): the same `_despike`, as array calls.
        _pockets = _parts(bare)
        for _despiked in _despike_many(list(shapely.simplify(_pockets, 0.05))) if _pockets else []:
            for piece in _parts(_despiked):
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
        _tree = GeomTree(keep)  # the basins' envelopes, indexed once per round (feature 220); `_absorb` tells it when it merges
        for scrap in sorted(scraps, key=lambda q: (round(q.bounds[0], 1), round(q.bounds[1], 1))):
            # The 3 ft `paddy_plot_seams_shared` itself ignores, in px at this map's scale. MIND THE
            # UNIT: `grain` is `2 / ftpx` (the scripted tier's principled value), so px-per-foot is
            # `g / 2` and 3 ft is `1.5 * g` - NOT `3.0 * g`, which is what this said first and is
            # double. At a hamlet's ftpx 1.0 that fed 6.0 px to an opening meant to shed a tail from
            # a strip whose whole mean width was 5.6 px, so it annihilated every scrap it was handed
            # and the escape hatch silently did nothing (cohort seeds 9 and 11). Measured at the
            # corrected width the same weld comes out at a 77.1 deg apex.
            _absorb(scrap, keep, grown, 1.5 * g, g, _tree)
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
    # ...AND ONCE MORE AT THE END, ON THE RINGS AS THE MANIFEST WILL ROUND THEM (feature 220,
    # settlement-review of Inashiro, 2026-09-09). The repair above runs first so a bow-tie's ground
    # returns to the pocket pool; but the trades and welds after it judge a `buffer(0)` COPY of the ring
    # they record, and the manifest rounds every vertex to 0.1 px - so a ring that is valid unrounded
    # can revisit a vertex exactly once rounded. Two shipped that way on the reference hamlet (#29 and
    # #303, a 2 px needle each, ink-invisible under the bund stroke, and not a simple polygon for any
    # shape metric). This pass consumes no randomness, so the plot count and the RNG are untouched.
    # EVERY RING RULE, JUDGED WHERE THE RINGS ARE DECIDED (feature 287, water W16-W27). The context is the one the gate
    # builds from the manifest - the supply and collector strokes as `_comb_record_ditches` records them, the design cell
    # as `_comb_record_field` records it, this map's grain - so the trades below and the sweep after them ask the rules
    # the finished-map tests ask, at the tests' own thresholds (`waterfields/ring_rules.py`).
    ctx = fan_context(channels if supply_banks else [c for c in channels if c.get("role") == "drain"], g, cell_area(plot_across, row_step))
    _shed_necks(plots, 1.25 * g, 15.0 * g, ctx)
    _repair_crossing_rings(plots, rounded=True)
    # ...AND THE LAST WORD (water W16-W24): every ring that still breaks a rule - a carved ring no step touched, a weld
    # the ladder had no clean host for, a staircase - is welded into a neighbor, split, or left bare under the fan floor.
    # Nothing after this line reshapes a ring, so what leaves this pass is what the rules were asked of.
    hold_ring_rules(plots, ctx)
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
    # EACH PLOT'S SHAPE ONCE, AND ITS HULL AND MINIMUM RECTANGLE IN ONE ARRAY CALL EACH (feature 276, FR-004, plan D11/D12):
    # the median below and the tint rules each rebuilt `Polygon(poly).buffer(0)` for every plot, and each plot asked its
    # hull and its rectangle one call at a time. The rules read the same numbers.
    _pgs = ring_polygons([_q["poly"] for _q in plots])
    _hull_areas = shapely.area(shapely.convex_hull(_pgs)).tolist() if _pgs else []
    _mrrs = list(shapely.minimum_rotated_rectangle(_pgs)) if _pgs else []
    _areas = sorted(_pg.area for _q, _pg in zip(plots, _pgs, strict=True) if len(_q.get("poly") or []) >= 3)
    _median_plot = _areas[len(_areas) // 2] if _areas else 0.0
    _keeps: list[tuple[tuple[bool, float, float], dict[str, Any]]] = []
    _collector = LineString(dpts) if len(dpts) >= 2 else None
    _to_collector = shapely.distance(_pgs, _collector).tolist() if _collector is not None and _pgs else []  # every plot's, in one call
    for _k, p in enumerate(plots):
        # THE RULE ITSELF FIRST, AS THE TEST READS IT (feature 287, FR-003, water W20). `flooded_plots_read_as_basins`
        # (`test_a_flooded_plot_reads_as_a_basin_and_not_as_a_pond`) calls `ring_rules.needle` on the RAW ring as the
        # manifest records it (rounded to 0.1 px), and so does `_needle` here, on the same rounded ring - one predicate.
        # This pass used to read only the deduplicated ring and its comment said the gate did too; the two had drifted,
        # and a tip that the 1.0 px dedup collapses into a blunt corner still reads raw as a needle under 15 deg. The raw
        # reading is the right one: the rule is about the ring AS DRAWN, and the drawn ring is the raw one.
        # THEN TWO MORE RINGS, AND BOTH CLAUSES EARN THEIR KEEP. The deduplicated ring at 25 deg is the placer's margin
        # over the rule - drop it and a plot pointed at 1.0 but blunt at the end width keeps its tint, which is exactly
        # what cohort seed 8 did when this briefly tested the end-collapsed ring alone. The end-collapsed clause
        # catches a needle truncated a few feet short of its point, which no interior angle on the 1.0 ring reports.
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
        _pg = _pgs[_k]
        _psol = (_pg.area / (_hull_areas[_k] or 1.0)) if isinstance(_pg, Polygon) and not _pg.is_empty else 1.0
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
        _mrr = _mrrs[_k] if isinstance(_pg, Polygon) and not _pg.is_empty else None
        _asp = 1.0
        _fill = (_pg.area / _mrr.area) if isinstance(_mrr, Polygon) and _mrr.area > 0.0 else 1.0
        if isinstance(_mrr, Polygon):
            _sides = [math.dist(_q, _r) for _q, _r in zip(list(_mrr.exterior.coords)[:-1], list(_mrr.exterior.coords)[1:], strict=True)]
            if len(_sides) >= 2 and min(_sides[0], _sides[1]) > 0.0:
                _asp = max(_sides[0], _sides[1]) / min(_sides[0], _sides[1])
        _wrong = (
            _needle(p["poly"])
            or pointed_ring(dedup_ring(p["poly"], 1.0), _TINT_MIN_APEX)
            or tapers_to_a_point(p["poly"], _t_end, _TINT_MIN_APEX, 4 * _t_end)
            or _psol < _TINT_MIN_SOLIDITY
            or _at_outfall
            or _asp > _TINT_MAX_ASPECT
            or _fill < _TINT_MIN_RECTANGULARITY
            or (_median_plot > 0.0 and _pg.area > _TINT_MAX_AREA_RATIO * _median_plot)
        )
        if p.get("fill") == FLOODED and _wrong:
            p["fill"] = RICE_GREENS[(int(abs(p["poly"][0][0]) * 7) + int(abs(p["poly"][0][1]) * 3)) % len(RICE_GREENS)]
        elif not _wrong and _pg.area > 0.0 and (p.get("low") or (_collector is not None and _to_collector[_k] <= 0.25 * plot_across)):
            # ...and a plot ON the collector is low ground whatever it records: `low` is set only on the plots the carve
            # cut, so the basins this pass plants or `_comb_toe_and_hem` re-hems onto the drain's bank never carry it -
            # measured on Mizuguchi, 49 of the 64 plots on the collector, while the 15 that did were the seam wedges
            _keeps.append((_basin_rank(_pg, _fill, _median_plot, _collector, plot_across), p))
    # THE MAP MUST STILL EXHIBIT THE CLASS IT DECLARES (feature 230). The tint is a SAMPLE - a random
    # 45% of the closing rank, for texture - and every one of those draws can be taken back by the six
    # clauses above, which is how the reference hamlet came to paint no blue plot at all: of 90-odd
    # blue draws across the size search, 71% were demoted as slivers at the size shipped BEFORE this
    # feature and 72% at the size after it, so the map's whole wet-paddy exhibit was resting on one
    # survivor and any re-roll could take it. `flooded_plots` is the picture record the interactive
    # page's wet-paddy class reads, and a sheet that paints none has silently stopped exhibiting the
    # class feature 159 created. So when the sample comes back empty, the most BASIN-LIKE compliant plot on
    # the low ground is tinted - it passed every clause the random ones are judged by, so nothing is
    # painted blue that could not have been painted blue by the draw. (The first cut took the LARGEST, and
    # settlement-review pass 10 measured what that key selects: whatever is pressed hardest against the size
    # ceiling, which at a fan seam is the long irregular wedge - Mizuguchi's was 3.71 long and 23 ft back from
    # the collector, where the carve's own rule is that a blue plot abuts the drain. See `_basin_rank`.) It takes NO draw from R (the
    # stream stays put, exactly as the demotion's indexed green does), so promoting one plot cannot
    # re-roll another, and on a roll whose sample survived this does nothing at all.
    if _keeps and not any(_p.get("fill") == FLOODED for _p in plots):
        _keeps.sort(key=lambda _a: (_a[0], round(_a[1]["poly"][0][0], 1), round(_a[1]["poly"][0][1], 1)))
        _keeps[0][1]["fill"] = FLOODED


def _basin_rank(basin: Polygon, fill: float, median: float, collector: LineString | None, plot_across: float) -> tuple[bool, float, float]:
    """How a compliant low plot ranks as THE flooded basin a map must exhibit - lower is better.

    First, whether it lies ON the collector (within a quarter of a plot's width): the carve tints only the level whose bottom
    edge is snapped to the drain's bank, because blue means the closing rank pooling before the outfall, and a promoted plot
    owes the same reading. Then how far it falls short of filling its own rectangle, which is what a leveled basin looks
    like. Then how far its size is from the median basin's, so the one blue plot on the sheet is not also its biggest.
    """
    _load_shapely()
    # ON the collector means FRONTING it, not touching it at a corner (settlement-review, feature 230 pass 11): Kashikawa's
    # promoted basin met the drain at one corner with a sliver and a wedge between it and the drain-side edge. A basin fronts
    # the drain when a real length of its boundary runs along it - a quarter of a plot's width.
    on = collector is not None and basin.buffer(0.25 * plot_across).intersection(collector).length >= 0.25 * plot_across
    size = abs(math.log(basin.area / median)) if median > 0.0 and basin.area > 0.0 else 0.0
    return (not on, round(1.0 - fill, 4), round(size, 4))


def _visible_parts(plots: list[dict[str, Any]], cell: float, neck: float = 0.0) -> None:
    """Make the plots a PARTITION: cut each one back to the part of it no later plot covers.

    THE CARVE HANDS THIS PASS OVERLAPPING BASINS, and the page hides it. Measured on Sawada, `_carve` returns 49 pairs of
    plots that claim the same ground (up to 1,290 sq px) and `_comb_toe_and_hem` leaves 29 (up to 409); main's pool maps
    carry the same 20-49 pairs. The renderer paints the plots in order, so what a reader sees is always the LATER plot,
    and the earlier one's bund shows only where it pokes out - the stray notches and dangling bund stubs two reviews
    flagged (settlement-review, feature 230 pass 10). The record meanwhile claims both, so every rule judging a basin's
    size, shape or neighbors judged ground the map does not show.

    So, walking back from the last plot, each is cut to its visible part - the record becomes the picture, which does
    not change. A detached remainder smaller than the rest, and a whole plot left too small to be a basin or pointed to
    a needle, return their ground to the bare pocket this pass exists to plant or weld, exactly as a carved scrap does.
    Earlier plots are the ones cut because later ones are the ones painted on top."""
    _load_shapely()
    # INDEXED, per constitution X clause 15: a running union of every later plot grows to the whole field and each plot
    # would be tested against all of it. The rings are indexed ONCE and each plot unions only the later rings its box meets.
    shapes: list[tuple[int, Polygon]] = []
    for k, gk in enumerate(ring_polygons([q.get("poly") or [] for q in plots])):
        if isinstance(gk, Polygon) and not gk.is_empty:
            shapes.append((k, gk))
    if not shapes:
        return
    import shapely

    # EVERY PLOT AT ONCE (feature 276, FR-004, plan D14). Each plot's visible part is cut against the ORIGINAL shapes of the
    # later plots it meets - never against one already cut here - so no plot's answer depends on another's, and the pass
    # runs as array calls: one tree query for every intersecting pair (the `intersects` the loop asked), one difference,
    # one opening at the neck. The per-plot bookkeeping below is the loop's, plot by plot, walking back from the last.
    geoms = [gk for _k, gk in shapes]
    tree = STRtree(geoms)
    src, dst = tree.query(geoms, predicate="intersects")
    pairs = [(a, b) for a, b in zip(src.tolist(), dst.tolist(), strict=True) if shapes[b][0] > shapes[a][0]]
    # A NEIGHBOR THAT ONLY TOUCHES TAKES NOTHING (feature 276): plots share their bunds, so almost every later neighbor
    # meets a plot along an edge and no more, and cutting a plot by a union of neighbors that only touch it returns the
    # plot. So only the neighbors whose INTERIORS meet it are unioned and cut away; a plot met only along edges goes to
    # the neck opening below as it stands, as it always did.
    inner = shapely.relate_pattern([geoms[a] for a, _b in pairs], [geoms[b] for _a, b in pairs], "T********").tolist() if pairs else []
    later_of: dict[int, list[int]] = {}
    for (a, b), overlaps in zip(pairs, inner, strict=True):
        later_of.setdefault(a, [])
        if overlaps:
            later_of[a].append(b)
    order = sorted(later_of, reverse=True)
    viss: Any = []
    if order:
        cut = [a for a in order if later_of[a]]
        cut_vis = dict(zip(cut, list(shapely.difference([geoms[a] for a in cut], [shapely.union_all([geoms[b] for b in later_of[a]]) for a in cut])), strict=True)) if cut else {}
        viss = [cut_vis.get(a, geoms[a]) for a in order]
        if neck > 0.0:
            # ...AND OPENED AT THE WIDTH FLOOR (settlement-review, feature 230 pass 11). Where two rings only partly
            # overlapped, the cut leaves the earlier plot a thin tail along its neighbor - six on Kashikawa, 46 to 81 ft
            # long and under 5 ft wide, none on main - which draws as a doubled bund. Opening at half the floor (`neck`,
            # 2.5 ft) sheds the tail, and its ground goes back to the bare pocket like any other scrap.
            viss = shapely.intersection(shapely.buffer(shapely.buffer(viss, -neck, join_style="mitre"), neck, join_style="mitre"), viss)
    drop: list[int] = []
    for a, vis in zip(order, list(viss), strict=True):
        i, g = shapes[a]
        if vis.area < g.area - 1.0:
            parts = sorted(_parts(vis), key=lambda q: -q.area)
            best = _ring(parts[0]) if parts else []
            if not parts or parts[0].area < _TOE_MIN_AREA * cell or len(best) < 3 or pointed_ring(best, _TOE_MIN_APEX) or pointed_ring(dedup_ring(best, 1.0), _TOE_MIN_APEX):
                drop.append(i)
            else:
                plots[i]["poly"] = best
    for i in sorted(drop, reverse=True):
        del plots[i]


def _span(shape: Any) -> float:
    """The long side of a piece's minimum rectangle - how far a tail runs."""
    _load_shapely()
    mrr = shape.minimum_rotated_rectangle if not shape.is_empty else None
    if not isinstance(mrr, Polygon) or shape.area <= 20.0:
        return 0.0
    c = list(mrr.exterior.coords)
    return max(math.dist(c[0], c[1]), math.dist(c[1], c[2])) if len(c) >= 4 else 0.0


def _shed_necks(plots: list[dict[str, Any]], neck: float, min_len: float, ctx: RingContext | None = None) -> None:
    """Hand a basin's thin tail to the neighbor it runs along, so two bunds a few feet apart become one.

    A NECK IS A DOUBLED BUND (settlement-review, feature 230 pass 11). Fitting the fan at its true size carves some basins
    with a long tail under the width floor running beside the next basin - five on Kashikawa, 46 to 81 ft long, none on
    main at the old size - and on the page that is two bunds side by side with a sliver of paddy between. The tail is
    what a morphological opening at half the floor (`neck`) removes; each tail at least `min_len` long is given to the
    plot it shares the most edge with, and the trade is kept only when both plots stay valid, simple, unpointed rings.
    Ground is conserved: what one plot loses the other gains.

    AND ONLY WHEN BOTH RINGS KEEP EVERY RING RULE (feature 287, water W16/W21/W23): given `ctx`, a trade whose giver or
    taker would break any rule in `ring_rules.ring_violations` is not taken - the giver shrunk under the area floor, a
    taker grown into a supply stroke or up a flight of steps. The step is refused and both plots stand as they were."""
    _load_shapely()

    def _may_have_a_tail(shape: Polygon) -> bool:
        """Cheap prefilter for the opening below (constitution X clause 15): a basin whose mean width - four times its
        area over its perimeter - is comfortably past the floor has nothing thin to shed, and most basins are that."""
        per = shape.length or 1.0
        return (4.0 * shape.area / per) < 14.0 * neck

    def _long_tail(shape: Polygon) -> bool:
        if not _may_have_a_tail(shape):
            return False
        return any(_span(q) >= min_len for q in _parts(shape.difference(shape.buffer(-neck, join_style="mitre").buffer(neck, join_style="mitre"))))

    shapes = [q if q is not None else Polygon() for q in ring_polygons([q.get("poly") or [] for q in plots])]
    tree = STRtree(shapes)
    import numpy
    import shapely

    for _round in range(2):  # a trade can leave the taker a tail of its own; a second look sheds it
        traded = False
        # THE PREFILTER FOR EVERY BASIN IN TWO ARRAY CALLS (feature 276, FR-004): `_may_have_a_tail` on each shape as the
        # round opens. A shape a trade replaces during the round is asked again, live, when the walk reaches it.
        _open = (4.0 * shapely.area(shapes) / numpy.where(shapely.length(shapes) == 0.0, 1.0, shapely.length(shapes)) >= 14.0 * neck) & ~shapely.is_empty(shapes)
        _open_at = set(numpy.flatnonzero(_open).tolist())
        _swapped: set[int] = set()
        for i, g in enumerate(shapes):
            if g.is_empty:
                continue
            if i in _open_at and i not in _swapped:
                continue
            if not _may_have_a_tail(g):
                continue
            tails = g.difference(g.buffer(-neck, join_style="mitre").buffer(neck, join_style="mitre"))
            for tail in _parts(tails):
                if _span(tail) < min_len:
                    continue
                best, shared = -1, 0.0
                for n in tree.query(tail.buffer(1.0)):
                    j = int(n)
                    if j == i or shapes[j].is_empty:
                        continue
                    s = shapes[j].buffer(1.0).intersection(tail.boundary).length
                    if s > shared:
                        best, shared = j, s
                if best < 0:
                    continue
                kept = [q for q in _parts(g.difference(tail)) if q.area > 0.0]
                grown = shapes[best].union(tail.buffer(0.05)).buffer(0)
                if not kept or not isinstance(grown, Polygon) or grown.interiors:
                    continue
                body = max(kept, key=lambda q: q.area)
                gi, gj = _ring(body), _ring(grown)
                if len(gi) < 3 or len(gj) < 3 or not Polygon(gi).is_valid or not Polygon(gj).is_valid:
                    continue
                if _long_tail(Polygon(gj).buffer(0)) or pointed_ring(gi, _GATE_MIN_APEX) or pointed_ring(gj, _GATE_MIN_APEX):
                    continue
                if ctx is not None and (ring_violations(gi, ctx) or ring_violations(gj, ctx)):
                    continue
                plots[i]["poly"], plots[best]["poly"] = gi, gj
                traded = True
                shapes[i], shapes[best] = Polygon(gi).buffer(0), Polygon(gj).buffer(0)
                _swapped.update((i, best))
                g = shapes[i]
                # ...AND THE INDEX IS REBUILT WITH THEM (perf-audit, feature 230 pass 14, reading this code for a
                # different reason). `shapes` is mutated here and `tree` was built from it once, so for the rest of
                # the round the query returned boxes for plots that had already given a tail away or taken one -
                # while the exact test read `shapes[j]` live. The index is a PREFILTER, so a stale box can only
                # return the wrong CANDIDATES: a neighbor that has since shrunk away from this tail is still
                # offered, and one that has grown into it may be missed, which is the direction that loses a trade
                # the pass exists to make. A fan carves 200-700 plots and a round trades a handful, so rebuilding
                # on a trade costs a tree per trade and not per plot.
                tree = STRtree(shapes)
        if not traded:
            break


def _repair_crossing_rings(plots: list[dict[str, Any]], rounded: bool = False) -> None:
    """Node every self-crossing ring into its largest valid part, and drop what cannot be rescued.
    `rounded`: judge and repair the ring as the manifest will record it (0.1 px), which is where a
    needle that is open unrounded closes on itself."""
    _load_shapely()
    import shapely

    def as_judged(poly: Any) -> Any:
        return [(round(float(a), 1), round(float(b), 1)) for a, b in poly] if rounded else poly

    # EVERY RING'S VALIDITY IN ONE ARRAY CALL, and each ring judged once (feature 276, FR-004, plan D11/D12): the loop built
    # a Polygon per plot to test it and the filter below built it again. A ring this pass rewrites is judged afresh.
    rings = [as_judged(_p["poly"]) for _p in plots]
    ok = shapely.is_valid([q if q is not None else Polygon() for q in ring_polygons(rings, clean=False)]).tolist() if rings else []
    for k, _p in enumerate(plots):
        ring = rings[k]
        if len(ring) < 3 or ok[k]:
            continue
        _fixed = _parts(Polygon(ring).buffer(0))
        if not _fixed:
            continue
        _cand = _ring(max(_fixed, key=lambda q: q.area))
        if len(_cand) >= 3 and not pointed_ring(_cand, _GATE_MIN_APEX) and not pointed_ring(dedup_ring(_cand, 1.0), _GATE_MIN_APEX):
            _p["poly"] = _cand
            judged = as_judged(_cand)
            ok[k] = len(judged) >= 3 and Polygon(judged).is_valid
    plots[:] = [_p for k, _p in enumerate(plots) if len(_p["poly"]) >= 3 and ok[k]]


# A STAIRCASE IS CUT AT MOST THIS MANY TIMES. Each cut takes one step off a ring and hands back two rings with fewer
# steps between them, so a ring with n steps needs n - 1 cuts; 32 is far past any ring the pool carries (the worst the
# record names is cohort seed 12's four) and exists only so a degenerate ring cannot loop.
_SPLIT_LIMIT = 32


def hold_ring_rules(plots: list[dict[str, Any]], ctx: RingContext, only: Collection[int] | None = None) -> None:
    """The seam pass's last word on the rings (feature 287, water W16-W27): after it, every plot ring - judged AS THE
    MANIFEST RECORDS IT, rounded to 0.1 px - keeps every rule `ring_rules.ring_violations` asks in `ctx`.

    A ring that breaks one is not kept as it stands, whatever made it (a carved ring no seam step touched, a weld the
    ladder had no clean host for, a repair). Its ground goes one of three ways, in this order:

    1. SPLIT, where the ring is a staircase (W23, one of the GM's five): cut along the line that continues the step's
       hop across the basin - the GM's own description of the right form, the wall "continuing on and meeting at the
       four way intersection" instead of going "sharply to the left before going down" (Inashiro, 2026-08-18). Each part
       that keeps every rule is a basin of its own.
    2. WELDED into the neighbor it shares the most bund with, when the union keeps every rule - research/fields 'Bunds
       are shared': the odd scrap is "taken into the basin beside it rather than walled off on its own".
    3. BARE, under the fan floor `comb_base_fill` draws - "the odd corner left unpaddied" the same research describes,
       which the Sawada review confirmed invisible in ink (`pockets._absorb`'s last branch).

    Never a violating ring kept because nothing better was found (FR-005). No draw from any random stream: split parts
    keep their parent's fill, so the count of plots may change but no color re-rolls. `only` confines the judgment to the plots
    it names (a later stage that reshaped a few rings - the grave island's carve - asks of those alone); welds still reach
    any neighbor."""
    _load_shapely()
    bad = [k for k in (range(len(plots)) if only is None else sorted(only)) if ring_violations(as_recorded(plots[k]["poly"]), ctx)]
    if not bad:
        return
    scraps: list[Polygon] = []
    added: list[dict[str, Any]] = []
    gone: set[int] = set()
    for k in bad:
        p = plots[k]
        ring = as_recorded(p["poly"])
        pieces = [q for part in (_parts(Polygon(ring).buffer(0)) if len(ring) >= 3 else []) for q in (_split_steps(part, ctx) if ctx.g else [part])]
        kept = [q for q in pieces if not ring_violations(_ring(q), ctx)]
        scraps += [q for q in pieces if q not in kept]
        if kept:
            p["poly"] = _ring(kept[0])
            added += [{**p, "poly": _ring(q)} for q in kept[1:]]
        else:
            gone.add(k)
    plots[:] = [p for k, p in enumerate(plots) if k not in gone] + added
    geoms: list[Any] = ring_polygons([p["poly"] for p in plots])
    tree = GeomTree(geoms)
    for scrap in sorted(scraps, key=lambda q: (round(q.bounds[0], 1), round(q.bounds[1], 1))):
        _weld_within_rules(scrap, plots, geoms, tree, ctx)


def _weld_within_rules(scrap: Polygon, plots: list[dict[str, Any]], geoms: list[Any], tree: GeomTree, ctx: RingContext) -> bool:
    """Weld `scrap` into the plot it shares the most bund with, among those whose union keeps every ring rule; False,
    and the scrap left bare, when none does. The union is taken as `_absorb` takes it - the scrap grown by 0.02 px so
    two polygons that only touch merge, and simplified at 0.05 px only when that stays a simple polygon."""
    reach = scrap.buffer(0.4)
    grown = scrap.buffer(0.02)
    ranked = sorted((-geoms[j].boundary.intersection(reach).length, j) for j in tree.near(scrap.bounds, pad=1.0))
    for neg, j in ranked:
        if neg >= 0.0:
            break  # sorted: every host after this one shares no bund with the scrap either
        merged = geoms[j].union(grown).buffer(0)
        if not isinstance(merged, Polygon) or merged.interiors:
            continue
        simplified = merged.simplify(0.05)
        candidate = simplified if isinstance(simplified, Polygon) and simplified.is_valid and not simplified.interiors else merged
        ring = _ring(candidate)
        if ring_violations(ring, ctx):
            continue
        plots[j]["poly"] = ring
        geoms[j] = Polygon(ring).buffer(0)
        tree.replaced(j)
        return True
    return False


def _split_steps(poly: Polygon, ctx: RingContext) -> list[Polygon]:
    """`poly` cut, one step at a time, until no part carries more than `ring_rules.MAX_STEPS` sideways steps (W23).

    Each cut continues a step's hop across the basin (`_cut_on_hop`). WHICH HOP: a staircase of even treads and risers
    reads both ways - each tread is also the hop between two risers - so every hop is tried and the cut kept is the one
    leaving the fewest parts that break a rule other than the steps still to be cut, then the one whose smallest part is
    largest (first on a tie, in ring order): the cut that makes basins, not scraps - a riser carried across the whole
    basin, not a tread shaved off it. A ring none of whose hops can be cut is handed back whole, and the caller judges it
    as it stands - a staircase goes to the scrap path, never onto the map."""
    g = float(ctx.g or 0.0)
    done: list[Polygon] = []
    todo = [poly]
    for _ in range(_SPLIT_LIMIT):
        if not todo:
            break
        q = todo.pop()
        hops = jog_vertices(_ring(q), g)
        cuts = [cut for b, c in hops for cut in [_cut_on_hop(q, b, c)] if cut] if len(hops) > MAX_STEPS else []
        if cuts:
            todo += min(cuts, key=lambda cut: (sum(1 for part in cut if ring_violations(_ring(part), ctx) - {"steps"}), -min(part.area for part in cut)))
        else:
            done.append(q)
    return done + todo


def _cut_on_hop(poly: Polygon, b: Pt, c: Pt) -> list[Polygon]:
    """`poly` split along its hop `b`-`c` continued into the basin until it meets the far bund - or [] where it cannot be.

    The hop runs between a wall and the same wall resumed a few feet over, so exactly one of its two ends is the reflex
    corner the basin's floor lies beyond: the knife starts there and runs on, in the hop's own direction, to where it
    first leaves the basin. That is the wall the step should have been - carried straight on to the junction."""
    from shapely.geometry import LineString as _Line
    from shapely.geometry import Point as _Point
    from shapely.ops import split

    x0, y0, x1, y1 = poly.bounds
    far = 2.0 * math.hypot(x1 - x0, y1 - y0) + 10.0
    for s, r in ((b, c), (c, b)):
        length = math.dist(s, r)  # never zero: `jog_vertices` names a hop only when it has length
        ux, uy = (r[0] - s[0]) / length, (r[1] - s[1]) / length
        if not poly.contains(_Point(r[0] + 0.5 * ux, r[1] + 0.5 * uy)):
            continue  # this end's continuation runs outside the basin: the other end is the reflex corner
        inside = _Line([r, (r[0] + far * ux, r[1] + far * uy)]).intersection(poly)
        runs = sorted((q for q in getattr(inside, "geoms", [inside]) if isinstance(q, _Line) and not q.is_empty), key=lambda q: q.distance(_Point(r)))
        for first in runs[:1]:  # the stretch that starts at the corner - a concave basin can be re-entered further on
            reach = max(math.dist(r, q) for q in first.coords)
            knife = _Line([r, (r[0] + (reach + 1.0) * ux, r[1] + (reach + 1.0) * uy)])
            parts = _parts(split(poly, knife))
            if len(parts) >= 2:
                return parts
    return []
