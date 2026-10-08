"""STAGE 4a: seating the settlement on the margin the water leaves.

Split from hamletgen.py by feature 111; bodies verbatim. See hamletgen/CLAUDE.md.

Research: seat geometry - NONE: segment indexes, ray tests, polyline crossings and the refusal type
"""

from __future__ import annotations

import math
from collections.abc import Sequence
from typing import Any

from l7r.diagram.settlement import point_in_poly, seg_dist, seg_intersect
from l7r.diagram.settlement._geom import seg_reach_index
from l7r.diagram.sitegen.geom import centroid, unit

from .consts import WIND_BACK_MIN_DOT, Poly, Pt
from .plan import SitePlan, band_extent

# ---- STAGE 4: seating the settlement, and its ways ----------------------------------------------


def below_drain(pt: Pt, drain: Poly, dx: float, dy: float, band: float = 150.0) -> bool:
    """Is `pt` on the WET side of the drain collector, within a toe band of it?

    The question the retired `dwellings_above_field_drain` check asked of every dwelling, asked before the
    dwellings exist. Reading the drain itself rather than approximating it with "downhill of the field
    centroid" is the point: an aggregate cannot stand in for a distributed thing, and
    the drain is a LINE across the low side, not a point.

    The ground judged lies downslope of the drain along the map's set downhill direction (`dx`, `dy`) and within the drain's
    own span ACROSS the slope: a point is measured against the drain where the drain crosses the point's line down the
    slope, so ground past either end of the drain - a dry flank - is never below it (feature 328: the nearest segment's
    clamped end used to stand in, and refused that flank).

    Research:
        wet side of the drain - research/questions/0058-ground-too-wet-to-build-on.drawing.html: downslope of the drain, within its span across the slope
        toe band - UNRESEARCHED: 18 ft past the drain line, within 150 ft of it"""
    ax, ay = -dy, dx  # across the slope
    across = pt[0] * ax + pt[1] * ay
    down = pt[0] * dx + pt[1] * dy
    for a, b in zip(drain, drain[1:], strict=False):
        a_across, b_across = a[0] * ax + a[1] * ay, b[0] * ax + b[1] * ay
        if a_across == b_across or not min(a_across, b_across) <= across <= max(a_across, b_across):
            continue  # this stretch of the drain does not cross the point's line down the slope
        t = (across - a_across) / (b_across - a_across)
        drain_down = (a[0] + t * (b[0] - a[0])) * dx + (a[1] + t * (b[1] - a[1])) * dy
        if 18.0 < down - drain_down <= band:
            return True
    return False


def nearest_within(index: Any, px: float, py: float, reach: float) -> float:
    """The distance from (px, py) to the nearest segment of a `seg_reach_index` built at `reach`, exactly as a scan of
    every segment finds it, when that is under `reach`; otherwise `reach` (feature 306). A segment whose grown box does not
    hold the point stands at least `reach` off, so the minimum under `reach` is always among those `near` returns."""
    return min((seg_dist(px, py, a, b) for a, b, _r, bx0, by0, bx1, by1 in index.near(px, py) if bx0 <= px <= bx1 and by0 <= py <= by1), default=reach)


def back_fouled(anchor: Pt, out: Pt, dep: float, dry_plots: Sequence[Poly], reach: float = 2.6, samples: int = 7) -> float:
    """What fraction of the ground BEHIND a candidate margin is already cropland.

    Samples a fan of points running out from the anchor along its outward normal, over the depth the
    cluster plus its windbreak will occupy. Returns 0.0 for a clear back and 1.0 for one entirely
    under the hem.

    Research: depth sampled behind the margin - UNRESEARCHED: 2.6 band depths, the cluster and its belt"""
    if not dry_plots:
        return 0.0
    ax, ay = -out[1], out[0]
    hit = 0
    total = 0
    # EACH PLOT COPIED AND SPANNED ONCE, NOT PER SAMPLE (feature 287 perf: 110,000 ray tests on the reference seed 4's seat,
    # each copying its ring). A ray test counts an edge only where `(yi > py) != (yj > py)`, so a point outside a ring's
    # [lowest, highest) y can count none and is outside it - the same verdict, without the walk.
    rings = [(min(q[1] for q in r), max(q[1] for q in r), r) for r in (list(poly) for poly in dry_plots) if r]
    for i in range(samples):
        t = (i + 0.5) / samples
        for lat in (-0.5, 0.0, 0.5):
            px = anchor[0] + out[0] * dep * reach * t + ax * dep * lat
            py = anchor[1] + out[1] * dep * reach * t + ay * dep * lat
            total += 1
            hit += any(y0 <= py < y1 and point_in_poly(px, py, r) for y0, y1, r in rings)
    return hit / total


BELT_ROOM_MAX_OFF = 0.2  # share of the belt band that may fall off the canvas before a seat is only a fallback - three of
# its fifteen sample points, the near corners a band square to a diagonal wind clips on a seat with room (a drawing
# judgment: the seat's belt room is geometry, not a researched figure)
"""Research: belt room off the canvas - CONVENTION: at most 0.2 of the band's samples"""


def belt_off_canvas(center: Pt, along: Pt, out: Pt, lat: float, dep: float, wind: Pt, W: float, H: float) -> float:
    """The share of the windbreak's band that would fall off the canvas behind a cluster seated at `center` (feature 261).
    The band is sampled where `belt_polygon` draws it: 36, 90 and 146 ft upwind of the cluster's windward fringe, across
    the cluster's width square to the wind.

    Research: belt distance upwind - research/questions/0072-shelter-belts-on-a-villages-windward-side-bofurin.drawing.html: sampled at 36, 90 and 146 ft"""
    wx, wy = unit(*wind)
    px, py = -wy, wx
    reach = abs(wx * along[0] + wy * along[1]) * lat + abs(wx * out[0] + wy * out[1]) * dep  # the fringe, upwind of the middle
    span = abs(px * along[0] + py * along[1]) * lat + abs(px * out[0] + py * out[1]) * dep  # half the width across the wind
    pts = [(center[0] + wx * (reach + d) + px * span * t, center[1] + wy * (reach + d) + py * span * t) for d in (36.0, 90.0, 146.0) for t in (-0.9, -0.45, 0.0, 0.45, 0.9)]
    return sum(1 for x, y in pts if not (0.0 <= x <= W and 0.0 <= y <= H)) / len(pts)


def seat_has_dry_exit(plan: SitePlan, start: Pt, toe: Poly | None = None, wet: Sequence[Poly] = ()) -> bool:
    """Has a seat at `start` a dry way out of the frame (feature 287, homes; ways W23)? The connector leaves the cluster by
    the flood fill `dry_exit` when no bearing is clean, and raises `NoDryExit` where the gateway is walled in - a property of
    the SEAT, so the seat is refused here instead. Asked with what stands at seat time, as `connector_dry_exit` walls it:
    the wet toe and the reed fringe grown by the lane's width, the field, the tameike at its 80 ft berth; the drain brook and
    every watercourse (the brook gapped at its fords) are lines it may not cross. The ONE flood fill, WAYS' own.

    Research:
        dry way out of the seat - research/questions/0081-village-lanes.drawing.html: lanes keep to dry ground
        tameike berth - UNRESEARCHED: 80 ft"""
    from .ways.dry_exit import EXIT_CELL_FT, dry_exit
    from .ways.track import wet_grown_by_the_lane

    walls: list[tuple[Poly, float]] = [(wet_grown_by_the_lane(w), 0.0) for w in [*([toe] if toe else []), *wet] if len(w) >= 3]
    walls.append((list(plan.envelope), 0.0))
    if plan.sink_pond:
        px, py, rx, ry = plan.sink_pond
        r = max(rx, ry)
        walls.append(([(px + r * math.cos(k * math.pi / 8), py + r * math.sin(k * math.pi / 8)) for k in range(16)], 80.0))
    lines = [(plan.sink_brook[i], plan.sink_brook[i + 1]) for i in range(len(plan.sink_brook) - 1)] + list(plan.watercourses)
    if straight_exit(start, walls, lines, float(plan.W), float(plan.H), EXIT_CELL_FT):
        return True
    return dry_exit(start, walls, lines, float(plan.W), float(plan.H)) is not None


#: The straight exits the fast path tries: every 22.5 degrees.
EXIT_BEARINGS = 16


def straight_exit(start: Pt, walls: Sequence[tuple[Poly, float]], lines: Sequence[tuple[Pt, Pt]], W: float, H: float, cell: float) -> bool:
    """A SUFFICIENT test for `dry_exit`, asked first because the flood fill costs a canvas (feature 287): a straight run
    from `start` off the canvas that keeps every wall at its margin plus one and a half cells, and every water line at
    one and three quarter cells. Every cell such a run passes through then has its center clear of the fill's own
    blocking distances (a wall's margin plus half a cell's diagonal, a line's one cell), and the cells a straight run
    passes through are joined, so the fill would find its way out along it. False says nothing: the fill decides."""
    from shapely import LineString, Polygon

    polys = [(Polygon(p), m) for p, m in walls if len(p) >= 3]
    segs = [LineString([a, b]) for a, b in lines]
    for k in range(EXIT_BEARINGS):
        dx, dy = math.cos(math.tau * k / EXIT_BEARINGS), math.sin(math.tau * k / EXIT_BEARINGS)
        run = min(((W if dx > 0 else 0.0) - start[0]) / dx if abs(dx) > 1e-9 else math.inf, ((H if dy > 0 else 0.0) - start[1]) / dy if abs(dy) > 1e-9 else math.inf) + 2.0 * cell
        ray = LineString([start, (start[0] + dx * run, start[1] + dy * run)])
        if all(p.distance(ray) >= m + 1.5 * cell for p, m in polys) and all(s.distance(ray) >= 1.75 * cell for s in segs):
            return True
    return False


class SeatRefused(ValueError):
    """No field margin turns the settlement's back to the wind on legal ground (feature 287, homes H30, plan D3): the site
    is refused at `stage_seat`, naming it, before any house exists - never seated off the wind."""


def seat_cluster(plan: SitePlan, dry_plots: Sequence[Poly] = (), toe: Poly | None = None, wet: Sequence[Poly] = (), brook: Sequence[Pt] = ()) -> dict[str, Any]:
    """WHERE THE HOUSES GO - the one derivation that decides how the whole map reads.

    背山面水, "back to the hill, face the water": a farming settlement stands with its back to the
    high, cold, windward side and its face to the field and its water. That is not decoration, it is
    the reason the windbreak grove has a side to be on, and it is what Ikegami's own docstring cites.
    So the cluster is seated on the field-envelope margin whose OUTWARD NORMAL best points into the
    wind, scored by the wind (1.0) and by the UPSLOPE end (0.8), with penalties for wet ground, the dry
    hem, the brook and the belt's room - the wet toe below the fields is not building ground; the drain's own rule is a
    dispersed farmstead's, not the cluster's (research 0058). A margin whose normal is within 45 degrees of the wind faces it (tier 0);
    one whose belt would fall off the canvas is not a candidate (`BELT_ROOM_MAX_OFF`): the wind is the
    regional northwest unless declared, and the seat bends to it.

    NO FALLBACK (feature 287, homes H30/H31, plan D3): the off-wind and cramped margins were kept as a
    last resort, recorded as `seat_offwind`; they are gone. A margin whose normal is 45 to 90 degrees off
    the wind offers its back turned to the wind instead (`margin_candidates`, tier 1, after every margin
    that faces it), so a fan falling into the wind seats on a flank above its toe; `plan_site` rolls only
    falls that leave a wind-facing margin, and the canvas holds the seat and its belt on every side
    (`plan.seat_room`). A site with no legal seat even so is refused here, naming it (`SeatRefused`).

    Scoring every margin point of the DRAWN envelope, rather than picking a compass corner, is what
    makes this survive a field that came out a different shape: the seat follows the fan.

    Returns the seat frame - a center, an ALONG-the-margin unit, an AWAY-from-the-field unit, and
    the band's half-extents - which the lanes, the house seeds, the connector and the windbreak all
    work in, so every one of them lands correctly at any fall direction; and its `ladder`, the ranked
    margins the seating falls back to (`seat_every_household`).

    Research:
        seat on the field's margin - research/questions/0031-clustered-and-scattered-villages-shuson-sanson.drawing.html: higher, drier ground beside the paddy
        back to the wind - research/questions/0072-shelter-belts-on-a-villages-windward-side-bofurin.drawing.html: the margin facing the northwest unless declared
        band area - research/questions/0037-threshing-and-drying-yards-at-farmhouses-niwa.drawing.html: households times the homestead's ground
        no drain rule at the seat - research/questions/0058-ground-too-wet-to-build-on.drawing.html: the ground below a drain kept only from dispersed farmsteads, not a nucleated cluster
        clear ground behind - UNRESEARCHED: refused past 0.30 of the back under dry crop
        not on the wet toe - research/questions/0058-ground-too-wet-to-build-on.drawing.html: seat and anchor off the marsh below the fields
        not in the reed fringe - CANON: the GM's ruling of 2026-08-28, refused centered in a pond's reed fringe, scored down at an end; it departs from research/questions/0058-ground-too-wet-to-build-on.drawing.html, which does not count the fringe as marsh
        seat standoff from the field - UNRESEARCHED: the seat center set `dep` + 12 ft out from the field margin
        reed-fringe share weight - UNRESEARCHED: 2.5 times the band's share in the reeds
        wind and upslope weights - UNRESEARCHED: 1.0 for facing the wind, 0.8 for upslope
        dry hem penalty - UNRESEARCHED: 1.6 within two band depths, plus 2.5 times the back's foul
        brook across the band - research/questions/0035-villages-beside-their-stream-one-bank-or-both.drawing.html: scored down, never refused
        brook penalty weight - GUESS: 3.0
        brook reach on the band - UNRESEARCHED: a band point within 30 ft of the brook counts as on the water
        belt room on the canvas - CONVENTION: scored, refused past BELT_ROOM_MAX_OFF
        band on the canvas - CONVENTION: the seat center at least half the band's length (`lat`, the band's semi-axis along the field) inside the frame
        dry way out - research/questions/0081-village-lanes.drawing.html: a walled-in head is refused"""
    env = plan.envelope
    cen = centroid(env)
    dx, dy = plan.fall
    wx, wy = plan.wind
    # A band sized from the household count x the ground a homestead ACTUALLY takes.
    #
    # THE PITCH IS THE WHOLE THING, and getting it wrong is silent. `roll_village` sizes its band at
    # a 56 px pitch per household, which is the FARMHOUSE - but the to-scale tiers do not place a
    # farmhouse, they place a BUNDLE: house (46 x 28 ft) plus its threshing yard below and its
    # dooryard garden beside, ~71 x 57 ft of reserved ground, and the placer keeps bundles apart by
    # circumscribed circles rather than real footprints, which costs up to another ~2x in spacing
    # (the engine's documented collision-circle debt). 56 px per household therefore asks a band to
    # hold about three times what fits in it.
    #
    # The symptom is NOT a shortfall, which is what makes it worth writing down: the retry loop
    # widens the band until the houses do fit, so the count comes out right and the cluster ends up
    # packed absolutely solid. Then the wells have nowhere to go - 702 candidate seats offered,
    # every one refused, `open_seat` finding nothing anywhere in the cluster - and the map fails
    # `settlement_has_wells` for a reason that looks nothing like its cause. Sizing the band from
    # the bundle leaves the courtyards a well can stand in.
    # THE ROLLED SHAPE BINDS HERE, and until 2026-08-19 it bound nowhere - see
    # `CLUSTER_BAND_ASPECT` for the census that showed the knob was dead. Area is held, so a
    # round hamlet is a compact blob and an elongated one a long string of the same ground.
    dep, lat = band_extent(plan.spec.households, plan.cluster_shape)
    # THE DRY PLOTS' EDGES AND THE BROOK, INDEXED ONCE (feature 306: every margin asked every edge of every dry plot for
    # its hem and every brook segment for each of fifteen band points - ~30,000 distance tests a seat). The hem only
    # scores while it is under two band depths, and the brook only while a point is within 30 ft of it, so each is filed
    # in a `seg_reach_index` grown by that reach and a margin asks only the segments whose grown box holds it. The nearest
    # one under the reach is the same number the full scan's minimum was; past it the penalty is 0 either way.
    hem_index = seg_reach_index([([*p, p[0]], 0.0) for p in dry_plots if len(p)], 2.0 * dep) if dry_plots else None
    brook_index = seg_reach_index([(list(brook), 0.0)], 30.0) if brook else None

    ranked: list[tuple[float, Pt, Pt]] = []  # the wind-facing margins with room for their belt, in the order met
    turned: list[tuple[float, Pt, Pt]] = []  # margins whose back is turned to the wind off a flank (`margin_candidates`)
    for mid, (nx, ny), tier in margin_candidates(env, cen, (wx, wy)):
        rel = ((mid[0] - cen[0]), (mid[1] - cen[1]))
        # ...and belt-and-braces: the BAND ITSELF must stand on open ground. An edge normal can
        # still graze a lobe of the fan a little further along, and a check is cheaper than a theory.
        if any(point_in_poly(mid[0] + nx * d - ny * lat * t, mid[1] + ny * d + nx * lat * t, env) for d in (dep * 0.5, dep + 34.0, dep * 2.0) for t in (-0.6, 0.0, 0.6)):
            continue
        # NO DRAIN RULE AT THE SEAT (feature 328): the ground below a field's drain is kept from farmsteads strewn one by
        # one, never from a nucleated cluster placed as one block (research 0058's drawing page - unscoped, the rule would
        # forbid the Ueda map's cluster beside a diagonal drain). The wet toe and the reed fringe below stay refused.
        # HARD 2: there must be clear ground BEHIND the margin. The settlement is a band and its
        # windbreak is a belt behind that - together most of a cluster's depth again - so a margin
        # is only usable if the ground it backs onto is free of crop. Testing the anchor POINT is
        # not enough (that was the first attempt): a point can stand clear of the hem while the belt
        # that goes 250 px behind it lands squarely in the plots.
        if back_fouled(mid, (nx, ny), dep, dry_plots) > 0.30:
            continue
        # HARD 3: the band has to FIT ON THE CANVAS. A margin near the canvas edge seats its band
        # center outside it - and `_fits` refuses every candidate beyond `s.bound`, so the cluster
        # simply does not get built: seed 106 seated 7 farmhouses of a declared 15, with the band's
        # center 56 px off the east edge. The map is not wrong, the seat is; another margin will do.
        seat_c = (mid[0] + nx * (dep + 12.0), mid[1] + ny * (dep + 12.0))
        # `lat` is already HALF the band's length (`band_extent`: dep and lat are the ellipse's semi-axes), so the seat
        # center stands a whole `lat` inside the frame - half the band's length, as the claim reads (feature 328)
        if not (lat <= seat_c[0] <= plan.W - lat and lat <= seat_c[1] <= plan.H - lat):
            continue
        # HARD 4: THE CLUSTER IS NOT BUILT ON THE WET TOE (GM 2026-08-12). `hinterland` lays reed
        # marsh across everything below the crop's low point, and on a crescent cluster hugging the
        # fan's toe the seat landed INSIDE that band - so the settlement's own lanes started in the
        # marsh and no amount of routing could save them (3 of 36 cohort maps). No reeds are drawn
        # on the houses, because the scatter skips the settlement halo, but the ground is still
        # marsh and the map says so. This is the same instinct as HARD 1 one step further out: you
        # do not build in the bog, and you do not build where the bog is either.
        if toe and (point_in_poly(seat_c[0], seat_c[1], toe) or point_in_poly(mid[0], mid[1], toe)):
            continue
        # THE REED FRINGE IS NOT BUILDING GROUND EITHER (feature 150 T50, GM 2026-08-28: "multiple farmhouses
        # ... overlap with marshland ... update our placement algorithms to make that impossible"). The fringe
        # round the reservoir is drawn before the seat is chosen but was never scored here, so a cluster could
        # be seated with one end in the reeds; the house placer then refuses those seats (the marsh is hard
        # ground since T50) and re-seats the displaced houses at the cluster's far ends, where the lane web
        # cannot serve them (Kuwabata seed 21: two houses, a web in three pieces). Scored like the dry-plot
        # foul above - the share of the seat band's sample points standing in wet ground - so a seat with
        # its end in the reeds loses to the next edge along; a seat CENTERED in them is refused outright.
        if wet:
            if any(point_in_poly(seat_c[0], seat_c[1], w) for w in wet):
                continue
            _wet_pts = [(mid[0] + nx * d - ny * lat * t, mid[1] + ny * d + nx * lat * t) for d in (dep * 0.5, dep + 34.0, dep * 2.0) for t in (-0.6, 0.0, 0.6)]
            wet_foul = sum(1 for q in _wet_pts if any(point_in_poly(q[0], q[1], w) for w in wet)) / len(_wet_pts)
        else:
            wet_foul = 0.0
        # 1.0 x facing the wind (the back), 0.8 x being upslope. Both express the same siting
        # instinct from two directions, and weighting the wind slightly higher keeps the windbreak
        # unambiguously behind the houses even on a map whose fall and wind nearly oppose.
        score = 1.0 * (nx * wx + ny * wy) - 0.8 * unit(*rel)[0] * dx - 0.8 * unit(*rel)[1] * dy - 2.5 * wet_foul
        # ...MINUS the dry hem. The upslope margin is contested ground: the comb's dry (hatake)
        # plots hem the high side along the supply canal, and they are cropland - a settlement
        # seated on top of them puts its windbreak's canopy in the crop (`groves_clear_of_dry_plots`)
        # and its farmsteads on the plots (`structures_clear_of_dry_plots`). So a margin that is
        # already hemmed scores down, in proportion to how close the hem is, and the seat slides
        # around the field to the free shoulder. Nothing here says WHICH shoulder - the geometry
        # does, which is why this works on a fan that came out a different shape.
        if dry_plots:
            hem = nearest_within(hem_index, mid[0], mid[1], 2.0 * dep)
            score -= 1.6 * max(0.0, 1.0 - hem / (2.0 * dep))
            score -= 2.5 * back_fouled(mid, (nx, ny), dep, dry_plots)
        # ...AND MINUS THE BROOK ON THE BAND. A band whose sample points stand on the water is ground the houses cannot
        # have, so it scores down - scored, never refused. Until feature 261 a band the brook ran THROUGH was struck out,
        # and the comment here called that "a GUESS ... NOT what the record shows; it is what this engine can draw":
        # against a settlement's OWN small channel the record has the water run through the middle of the place (Harie's
        # Okawa, specs/230 R6), and the strike-out existed only because no way could cross the brook. Ways cross it now
        # at a ford (`ways/checks.py` `brook_fords`) and `bridges()` decks the crossing, so the seat is free to stand on
        # either bank of its field, or astride the brook (the GM, 2026-09-27: "fix the placement algorithm instead").
        # THE RECORD NOW SUPPORTS BOTH FORMS (269 B23; research/questions/0035-villages-beside-their-stream-one-bank-or-both.html, "Villages beside their stream: one bank or
        # both"): against a river one bank only, around a settlement's own channel the reverse, and at a stream's
        # size both - Hongcun beside its stream, Xidi and Likeng along both banks. The record prefers neither, and "each
        # map takes the form its site gives it" (0035, "How our maps place a hamlet on its stream"), so
        # which form a hamlet draws follows from where this scorer seats it, not from a roll. The score below is the
        # rendering section's "a site the brook does not cross is still preferred when two are
        # otherwise level" - this project's decision (a crossing is one more thing to build and keep), and the 3.0 weight
        # a GUESS. A bank knob, rolling the form, stays deferred (fc:2342) until a roll could choose a site the site does
        # not give.
        if brook:
            _bp = [(mid[0] + nx * d - ny * lat * t, mid[1] + ny * d + nx * lat * t) for d in (dep * 0.5, dep + 34.0, dep * 2.0) for t in (-0.9, -0.45, 0.0, 0.45, 0.9)]
            crossed = sum(1 for q in _bp if nearest_within(brook_index, q[0], q[1], 30.0) < 30.0) / len(_bp)
            score -= 3.0 * crossed
        # ...AND A BELT WITH GROUND TO STAND ON (settlement-review of Mizuguchi, feature 261, two rounds). The windbreak
        # stands 36-146 ft upwind of the houses' windward fringe (`belt_polygon`); a seat whose band runs that belt off the
        # canvas left the belt a strip beside the westernmost farmsteads, holed where they stood in it. Scored alone (-2.5
        # x the share off the canvas) the seat still won, because every other wind-facing margin had the brook across its
        # band - so the share still scores, and past `BELT_ROOM_MAX_OFF` the margin is refused (feature 287, homes H31:
        # it was a fallback below every seat with room; the canvas is grown for the belt by `plan.seat_room`, so a cramped
        # margin is never the only wind-facing one).
        off = belt_off_canvas((mid[0] + nx * (dep + 12.0), mid[1] + ny * (dep + 12.0)), (-ny, nx), (nx, ny), lat, dep, (wx, wy), plan.W, plan.H)
        score -= 2.5 * off
        if off > BELT_ROOM_MAX_OFF:
            continue
        (ranked if tier == 0 else turned).append((score, mid, (nx, ny)))
    # ONE RANKING, BEST FIRST (feature 287, plan D2): the margins in the order this function prefers them - by score,
    # the first met winning a tie - so the chosen seat is the ranking's head and the rest are its LADDER, the margins
    # `stage_homesteads` takes in turn when the chosen one cannot seat every household (`homesteads/capacity.py`).
    order = sorted(ranked, key=lambda c: -c[0]) + sorted(turned, key=lambda c: -c[0])
    # ...AND THE HEAD HAS A DRY WAY OUT (feature 287, ways W23): a margin whose seat is walled in by the wet, the field and
    # the water is refused, so the connector never meets `NoDryExit`. Asked in ranking order until a margin has one - the
    # flood fill costs a canvas - and each rung of the ladder is asked the same before it is seated (`capacity`).
    while order and not seat_has_dry_exit(plan, _seat_center(order[0][1], order[0][2], dep), toe, wet):
        order.pop(0)
    if not order:
        raise SeatRefused(
            f"{plan.spec.name} (seed {plan.spec.seed}): no field margin turns its back to the {plan.windward} wind clear of the dry hem, the toe and the canvas edge - the site has no seat (plan D3)"
        )
    frames = [_seat_frame(anchor, out, lat, dep, (wx, wy)) for _score, anchor, out in order]
    return {**frames[0], "ladder": frames[1:]}


#: How far past the 45-degree bar a margin's back is turned, radians: a hair, so the turned back passes
#: `WIND_BACK_MIN_DOT`'s 0.7071 without resting on it.
TURN_SLACK = math.radians(0.5)


def margin_candidates(env: Poly, cen: Pt, wind: Pt) -> list[tuple[Pt, Pt, int]]:
    """The seats a field envelope offers, `(margin midpoint, the back's direction, tier)`, in the envelope's order.

    Tier 0, the margin's own outward normal where it lies within 45 degrees of the wind. THE EDGE'S OWN NORMAL, turned
    to face away from the field - not the ray from the field's middle: a comb fan is NOT CONVEX, it has concave shoulders
    where the carve stops short, and on those edges "away from the centroid" points straight back INTO the rice (seed 11
    put ten households on the paddy that way).

    Tier 1, THE BACK TURNED TO THE WIND OFF A FLANK (feature 287, homes H30, plan D3): a margin whose normal is 45 to 90
    degrees off the wind offers a seat whose back is turned toward the wind just past the 45-degree bar - at most 45
    degrees off its own normal, so the band still stands off the field (`seat_cluster`'s open-ground test asks it). A
    fan falling INTO the wind has its wind-facing edges on the wet toe and its flanks square to the wind, so until this
    tier its seat hung on an accident of the outline: Sawada's (down_deg 225, seed 24) was one short edge at the fan's
    upper west corner, facing west-northwest, and 287's brook repair (508bcd511) smoothed it away. A flank above the toe,
    the band beside it turned to the wind, is the same seat by construction. Offered after every tier-0 seat, so a site
    with an edge facing the wind seats as before.

    Research:
        back faces the wind - research/questions/0072-shelter-belts-on-a-villages-windward-side-bofurin.drawing.html
        45 degree bar - UNRESEARCHED: WIND_BACK_MIN_DOT, tier 0; 0072 gives no tolerance
        back turned off a flank - UNRESEARCHED: tier 1, at most 45 degrees off the margin's normal"""
    out: list[tuple[Pt, Pt, int]] = []
    n = len(env)
    for i in range(n):
        ax, ay = env[i]
        bx, by = env[(i + 1) % n]
        mid = ((ax + bx) / 2.0, (ay + by) / 2.0)
        nx, ny = unit(-(by - ay), bx - ax)
        if (nx * (mid[0] - cen[0]) + ny * (mid[1] - cen[1])) < 0:
            nx, ny = -nx, -ny  # flip to the outward side (winding-independent)
        dot = nx * wind[0] + ny * wind[1]
        if dot >= WIND_BACK_MIN_DOT:
            out.append((mid, (nx, ny), 0))
        elif dot > 0.0:
            off = math.atan2(nx * wind[1] - ny * wind[0], dot)  # the wind's bearing from the normal, signed
            turn = off - math.copysign(math.pi / 4 - TURN_SLACK, off)
            a = math.atan2(ny, nx) + turn
            out.append((mid, (math.cos(a), math.sin(a)), 1))
    return out


def _seat_center(anchor: Pt, out: Pt, dep: float) -> Pt:
    """The band's center on a margin: its half-depth and the standoff out from the margin's midpoint.

    Research: standoff from the field - UNRESEARCHED: 12 ft"""
    return (anchor[0] + out[0] * (dep + 12.0), anchor[1] + out[1] * (dep + 12.0))


def _seat_frame(anchor: Pt, out: Pt, lat: float, dep: float, wind: Pt) -> dict[str, Any]:
    """The seat frame on one margin: its center, the along and away units, the band's half-extents, the anchor, and
    whether its back is off the wind.

    Research: standoff from the field - UNRESEARCHED: 12 ft, the band's near edge hugging the field"""
    wx, wy = wind
    along = (-out[1], out[0])
    # THE BAND'S NEAR EDGE HUGS THE FIELD. The standoff is the front row's own depth and no more, and
    # the measurement below is why - not a check, which is the correction this comment needed
    # (2026-09-12): it used to cite `field_ringed` (retired, feature 141), five farmhouses within 165 px of the outline, which
    # feature 141 retired. Nothing enforces a MAXIMUM house-to-field distance today and the research
    # gives only a 6 ft minimum. What stands is the drawing: every pixel of standoff costs the front row
    # twice over, because the band is seeded across its whole depth rather than packed against its near
    # face, and a hamlet whose houses sit back off their own crop does not read as a farming hamlet. At 34 px of standoff three cohort maps rang
    # their field with four houses; at 12 the same maps ring it comfortably, and the front row still
    # fronts the paddy across its lane rather than standing in the rice.
    cx = anchor[0] + out[0] * (dep + 12.0)
    cy = anchor[1] + out[1] * (dep + 12.0)
    return {
        "cx": cx,
        "cy": cy,
        "along": along,
        "out": out,
        "lat": lat,
        "dep": dep,
        "anchor": anchor,
        "offwind": out[0] * wx + out[1] * wy < WIND_BACK_MIN_DOT,
    }


def _arm_hit(a: Poly, b: Poly) -> Pt | None:
    """The first PROPER mid-run crossing point of two polylines - a touch at a segment
    endpoint is a JUNCTION, not a crossing, and returns nothing. Returning the POINT rather
    than a bool matters: raw skeletons may cross by design (a stem poked through its bar, the
    'cross' layout's crossbar over its spine), so "the raw pair crosses somewhere" cannot
    license a clipped crossing ANYWHERE - Kashikawa's two clipped arms X-ed 87 px out in open
    ground while their raw junction sat at the hub, and the existence test waved it through
    (2026-08-16). A clipped crossing is designed only where the raw one is."""
    for i in range(len(a) - 1):
        for j in range(len(b) - 1):
            _h = seg_intersect(a[i], a[i + 1], b[j], b[j + 1])
            if _h is not None and all(math.dist(_h, q) > 2.0 for q in (a[i], a[i + 1], b[j], b[j + 1])):
                return _h
    return None


def _arm_crossing_accidental(arm: Poly, raw: Poly, kept: list[tuple[Poly, Poly]]) -> bool:
    """AN ARM MAY NOT CROSS A SIBLING ANYWHERE THE LAYOUT DOES NOT (settlement-review, Sawada
    2026-08-16): the clip pipeline bends each arm independently, and two of a Y's arms came back
    CROSSING mid-run in open ground, near-superimposed for ~250 ft. A clipped crossing is designed
    only where the RAW pair crosses within ~40 px of it - existence alone is not enough, since a
    raw stem poked through its bar "crosses" at the hub while the clipped X sat 87 px away.

    Research: arms cross only where the layout does - UNRESEARCHED: within 40 ft of the raw crossing"""
    for k_arm, k_raw in kept:
        _h = _arm_hit(arm, k_arm)
        if _h is None:
            continue
        _hr = _arm_hit(raw, k_raw)
        if _hr is None or math.dist(_h, _hr) > 40.0:
            return True
    return False


def _fork_spur(spur_pts: Poly, kept: list[tuple[Poly, Poly]]) -> Poly:
    """A FIELD SPUR BRANCHES OFF THE NETWORK - it does not cross it (settlement-review, Sawada
    2026-08-16: the spur left the cluster's middle on the far side of a Y arm and ran an X over
    it, where a real farm path FORKS from the lane it serves). If the run crosses a drawn arm,
    the spur starts AT the crossing: the shared point becomes the fork. BOUNDED pass count: with
    float hits a crossing can re-surface epsilon-shifted forever (the unbounded while hung a
    regen at 600s); a spur meets at most a handful of arms, so eight passes is generous and
    termination is structural, not numeric. The progress guard matters too: after a truncation
    the new start lies ON the arm, so the same intersection comes straight back on the next pass
    - a hit at the current start is the fork already made, not a crossing left to cure.

    Research: field spur forks from the lane - UNRESEARCHED: starts at its crossing with an arm"""
    for _pass in range(8):
        _cut = False
        if len(spur_pts) < 2:
            break
        for _ka, _kr in kept:
            for _si in range(len(spur_pts) - 1):
                for _sj in range(len(_ka) - 1):
                    _hit = seg_intersect(spur_pts[_si], spur_pts[_si + 1], _ka[_sj], _ka[_sj + 1])
                    if _hit is not None and math.dist(_hit, spur_pts[-1]) > 14.0 and math.dist(_hit, spur_pts[_si]) > 1.0:
                        spur_pts = [_hit, *spur_pts[_si + 1 :]]
                        _cut = True
                        break
                if _cut:
                    break
            if _cut:
                break
        if not _cut:
            break
    return spur_pts
