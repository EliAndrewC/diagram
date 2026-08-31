"""Split from waterfields/seams.py by feature 173 - see this package's CLAUDE.md for the index."""

import math
from typing import Any

from shapely.errors import GEOSException
from shapely.geometry import LineString, MultiPolygon, Polygon
from shapely.geometry.base import BaseGeometry
from shapely.ops import unary_union

from ..banks import (
    _GATE_MIN_APEX,
    dedup_ring,
    jog_steps,
    jog_vertices,
    pointed_ring,
)
from ..frame import Poly, Pt, _Frame
from .pockets import _despike, _parts, _ring


def _seam_cuts(lo: float, hi: float, want: float, marks: list[float]) -> list[float]:
    """Where to cut a pocket between `lo` and `hi`, aiming for cells about `want` across.

    CUT WHERE THE FABRIC ALREADY BREAKS. A pocket's own outline IS the surrounding basins' outline,
    so the coordinates of its corners are the positions at which the rows either side of it end -
    and cutting there means a piece this pass hands back lines up with the basin it will be welded
    into. Cutting on a fresh grid instead, which is what this did first, puts every seam where
    NEITHER row breaks: on a hamlet that is `plot_across`, 48 ft, and it is the mechanism behind the
    staircase the GM reported (2026-08-18) - the offcuts land mid-basin on both sides and get welded
    alternately up and down.

    The ideal spacing still governs; a mark only wins when it is within 0.35 of a cell of where the
    next cut wanted to be, and never when it would leave a sliver under a third of a cell on either
    side. THAT NUMBER IS A MEASURED CEILING, not a taste: at 0.40 and above the cut follows the
    neighbors far enough to move the fan's envelope, and Kashikawa's dry hem - which tiles against
    that envelope - shifts onto a footbridge and trips `features_do_not_overlap`. Steps across the
    four scripted hamlets go 2/2/9/3 at 0.35 and 1/2/8/1 at 0.40, so the last four cost a regression
    in another subsystem and are not taken (see `future-work/`). Where the neighbors break nowhere near the right place the grid falls back to the even
    spacing it always used, which is the honest answer: there is no seam there to line up with."""
    span = hi - lo
    if span <= 1.5 * want or want <= 0.0:
        return [lo, hi]
    keep = want / 3.0
    cuts = [lo]
    while hi - cuts[-1] > 1.5 * want:
        target = cuts[-1] + want
        near = [m for m in marks if cuts[-1] + keep <= m <= hi - keep and abs(m - target) <= 0.35 * want]
        cuts.append(min(near, key=lambda m: abs(m - target)) if near else target)
    cuts.append(hi)
    return cuts


def _plant(F: _Frame, pocket: Polygon, plot_across: float, row_step: tuple[float, float], half: float) -> tuple[list[Polygon], list[Polygon]]:
    """Subdivide a plantable pocket at the FAN'S OWN GRAIN and hand back the basins.

    One giant slab would dwarf the ~0.08-acre plots around it (the relative-size doctrine), so the
    pocket's (u, f) box is cut into ~plot_across x row_step cells and the pocket clipped to each.
    Cells are cut from ONE box, so neighboring pieces share their seam exactly; the pocket's own
    outline is the surrounding plots' outline, so the outer bunds are shared too.

    Returns `(basins, offcuts)`. Offcuts - cells the grid cut too thin to bund - are handed BACK
    rather than welded here, so the caller can offer them the whole field to weld into. Welding
    them among their own siblings was tried first and left five toe wedges bare on Inashiro: a
    scrap whose only sibling refuses the union (the two meet at a point) had nowhere else to go,
    and stayed a doubled bund."""
    x0, y0, x1, y1 = pocket.bounds
    corners = [F.to_uf(x0, y0), F.to_uf(x1, y0), F.to_uf(x1, y1), F.to_uf(x0, y1)]
    ulo, uhi = min(u for u, _ in corners), max(u for u, _ in corners)
    flo, fhi = min(f for _, f in corners), max(f for _, f in corners)
    # THE POCKET'S OWN CORNERS ARE THE SURROUNDING BASINS' CORNERS, so they are where the fabric
    # actually breaks - see `_seam_cuts`.
    marks = [F.to_uf(float(q[0]), float(q[1])) for q in pocket.exterior.coords]
    us = _seam_cuts(ulo, uhi, plot_across, sorted(m[0] for m in marks))
    fs = _seam_cuts(flo, fhi, (row_step[0] + row_step[1]) / 2, sorted(m[1] for m in marks))
    cells: list[Polygon] = []
    for ua, ub in zip(us[:-1], us[1:], strict=True):
        for fa, fb in zip(fs[:-1], fs[1:], strict=True):
            cell = Polygon([F.to_xy(ua, fa), F.to_xy(ub, fa), F.to_xy(ub, fb), F.to_xy(ua, fb)])
            cells += _parts(_despike(pocket.intersection(cell)))
    good = [c for c in cells if not c.buffer(-half).is_empty]
    if not good:
        return [pocket], []  # the grid cut the one thick part up; the pocket is a basin as it stands
    return good, [c for c in cells if c.buffer(-half).is_empty]


def _tab_cut(poly: Poly, g: float, rb: Pt, rc: Pt) -> set[Pt] | None:
    """The four vertices of the TAB this step is one end of, or None if the step stands alone.

    A tab is the shape a weld leaves: the wall steps off its line, runs along a second line for a
    stretch, and steps back. Cutting one of its risers turns the tab into a TRIANGLE, so a row of
    tabs becomes a rank of long diagonal slashes - which is a different artifact, not a fix, and was
    exactly what Inashiro's east flank turned into when this cut did not exist. Dropping all four
    vertices hands the whole strip to the basin on the other side and the wall runs on unbroken.

    A TAB SHOWS UP AS ONE STEP, NOT TWO, which is the thing to know before editing this. `jog_steps`
    is directed - it wants the wall to resume in the SAME direction - and a tab's two risers face
    opposite ways, so only the second of them is ever reported. The first is found by walking BACK
    along the ring from the reported riser: one edge for the tab's own run, one more for the riser
    that opened it, and that riser must oppose the reported one to within a quarter of its length."""
    ring = dedup_ring([(float(q[0]), float(q[1])) for q in poly], 0.5)
    n = len(ring)
    if n < 6:
        return None
    at = {(round(v[0], 1), round(v[1], 1)): k for k, v in enumerate(ring)}
    if rb not in at or rc not in at:
        return None
    j = at[rb]
    if (j + 1) % n != at[rc]:
        return None
    riser = (ring[at[rc]][0] - ring[j][0], ring[at[rc]][1] - ring[j][1])
    for back in (True, False):
        if back:
            b, c = ring[(j - 2) % n], ring[(j - 1) % n]
        else:
            b, c = ring[(j + 2) % n], ring[(j + 3) % n]
        other = (c[0] - b[0], c[1] - b[1])
        if riser[0] * other[0] + riser[1] * other[1] >= 0.0:
            continue  # the two risers go the same way: a staircase, not a tab
        if abs(math.hypot(*other) - math.hypot(*riser)) > 0.25 * math.hypot(*riser):
            continue  # a riser of a different depth is a different feature, not this tab's other end
        return {rb, rc, (round(b[0], 1), round(b[1], 1)), (round(c[0], 1), round(c[1], 1))}
    return None


def _unjog(plots: list[dict[str, Any]], g: float, floor: float, water: BaseGeometry, outside: BaseGeometry) -> None:
    """Straighten a wall that still steps, by TRADING the corner between the two basins that share it.

    WHY A REPAIR AND NOT A BETTER CHOICE (GM 2026-08-18, on Inashiro: *"instead of just continuing on
    and meeting at the four way intersection ... it just goes sharply to the left before going down"*).
    `_absorb`'s jog guard picks the host whose wall does not end up stepping, and that is worth having,
    but it can only choose - and the steps that survive it are the ones where the ground had exactly
    one home, so no choice existed. Those need the wall MOVED, which is this pass.

    THE MOVE IS THE ONE A FIELD WOULD MAKE: run the wall from where it starts to where it resumes, so
    the hop becomes a bend. `research/fields.md` says a bend is period-correct and a parcel fitted to
    its neighbors is the honest look; what it never describes is a wall doubling back, which is
    exactly and only what this removes.

    IT TRADES GROUND RATHER THAN DROPPING VERTICES, and that distinction is the whole difference
    between this and the version that did not work. Dropping the step's two vertices from every ring
    that carries them looks partition-preserving and is not: the two rings either side of a wall have
    DIFFERENT neighboring vertices, so the chords they close over differ, and on Inashiro rings 460
    and 592 lost 400 px2 and gained 259 - the difference being bare floor with a bund each side of it.
    Taking the corner as a polygon (`was.difference(now)`) and handing that same polygon to the
    neighbor conserves the ground by construction, whatever the two rings look like.

    EVERY REFUSAL BELOW IS A RULE THIS PASS WOULD OTHERWISE BREAK, and each was measured breaking it:

    - a **T-junction** (three rings on the corner): each cuts its corner a different way and the patch
      between them is bare floor - `paddy_plot_seams_shared`, 4 plots.
    - a corner whose two vertices are **not held by the same basins**: the wall then moves on one side
      only - `paddy_plot_seams_shared`, 2 plots.
    - a trade that would **shrink both** rings, or shrink the only ring on the wall: the ground given
      up lies bare rather than moving.
    - a repair that takes a basin under the fan's **size floor** - `paddy_basins_are_worth_their_bund`,
      1 basin at 16% of the cell. Judged at the GATE's line (`_GATE_MIN_AREA`, 0.20 of the design
      cell) rather than the placer's margin above it (`_TOE_MIN_AREA`, 0.25), for the same reason the
      apex is judged at the gate's 15 deg: a repair is not a placement choice, so it is allowed
      exactly where the map would have been allowed to draw it. Measured, the difference is not
      cosmetic - the basin that has to GIVE UP the corner is usually the one near the floor, and the
      placer's margin refused the repair on rings the gate would have accepted.
    - a repair that draws a basin out to a **needle** - `paddy_plots_are_workable_basins`, judged on the
      ring the gate reads at the gate's own 15 deg, because a repair is not a placement choice: it is
      allowed exactly where the map would have been allowed to draw it.
    - a repair whose new wall lands **in the water or off the command area** - the chord cuts the corner,
      and a corner the carve put there was often hugging a delivery ditch's bank
      (`paddy_bunds_clear_the_supply_channels`, Mizuguchi). Tested against the same `water` and
      `outside` geometries the pass itself uses to decide what may be planted, which are strictly
      stricter than the gate's own sampled clearance.

    IT RUNS UNTIL NOTHING MOVES, capped, because straightening one step can retire or expose
    another and the cheapest cut for a ring often only becomes available once its neighbor has been
    repaired. The cap is a backstop against a repair that undoes itself, not a tuning knob - on every
    pool map the set converges in three rounds or fewer."""
    for _ in range(6):
        moved = False
        seen: set[frozenset[Pt]] = set()
        for i in range(len(plots)):
            for b, c in jog_vertices([(float(q[0]), float(q[1])) for q in plots[i]["poly"]], g):
                rb = (round(b[0], 1), round(b[1], 1))
                rc = (round(c[0], 1), round(c[1], 1))
                if frozenset((rb, rc)) in seen:
                    continue
                seen.add(frozenset((rb, rc)))
                # THE WHOLE TAB FIRST, WHERE THERE IS ONE - and this is the cut that matters most,
                # because it is the only one that leaves a STRAIGHT wall. A welded tab is TWO steps a
                # few feet apart on the same ring: the wall drops to the tab's line, runs along it,
                # and climbs back. Cutting either corner on its own turns the tab into a triangle, so
                # a row of tabs becomes a row of long diagonal slashes - measured by eye on Inashiro's
                # east flank, where the staircase was gone and a rank of parallel diagonals had taken
                # its place, which is a different artifact rather than a fix. Dropping all four of the
                # tab's vertices hands the whole strip to the basin on the other side and the wall
                # runs on unbroken, which is what the fabric should have had.
                _tab = _tab_cut(plots[i]["poly"], g, rb, rc)
                _cuts = ([_tab] if _tab else []) + [{rb}, {rc}, {rb, rc}]
                # GENTLEST CUT NEXT. Dropping the end of the hop that sits on the LONGER run
                # absorbs the offset over the longer distance, so the wall slants where it used to
                # step and the two basins trade a sliver rather than a corner; dropping the other end
                # is the same repair over a shorter run; dropping both cuts the corner off square and
                # is the crudest, because it hands over the whole triangle and is what drove the
                # needle refusals (230 of 580 trades, 2026-08-18) when it was the only cut on offer.
                # A DEAD LEVER, MEASURED, so the next reader does not pull it: a wall belongs to TWO
                # basins, and letting the one on the other side attempt the repair when this one is
                # refused looks like it should help - the two cuts are genuinely different. It buys
                # one step in four maps (5/5/7/5 -> 5/5/6/5) and costs 70% of the regeneration, because
                # finding the other side means scanning every plot's vertices for the corner.
                for _drop in _cuts:
                    if _trade(plots, i, _drop, g, floor, water, outside):
                        moved = True
                        break
        if not moved:
            return


def _trade(
    plots: list[dict[str, Any]],
    i: int,
    drop: set[Pt],
    g: float,
    floor: float,
    water: BaseGeometry,
    outside: BaseGeometry,
) -> bool:
    """Move the wall of plot `i` past the step at (`rb`, `rc`), giving the corner it cuts off to
    whatever lies on the other side. Returns whether the trade happened.

    THE NEIGHBOUR IS FOUND BY GEOMETRY, NOT BY SHARED VERTICES, and that is what makes the pass
    actually reach the steps. The first version required both ends of the hop to be held by the same
    basins, on the reasoning that a shared wall is shared vertex for vertex - true of the carve, and
    false of exactly the fabric this pass exists to repair: a welded tab's two base vertices belong to
    the host, while the basin under it may touch only one of them. Measured, that rule refused **399
    of 580 steps**, more than every other refusal combined. The corner is a POLYGON; who it belongs to
    is a question about that polygon's boundary, and `_absorb` has answered the same question by
    shared boundary length since it was written."""
    cut = [q for q in plots[i]["poly"] if (round(q[0], 1), round(q[1], 1)) not in drop]
    if len(cut) < 3:
        return False
    # AND THE REPAIR MUST ACTUALLY RETIRE THE STEP. Dropping ONE end of the hop absorbs the offset as
    # a slant over the run beside it - a bend, which is what the fabric should have had - and dropping
    # BOTH cuts the corner off square. Either can fail to help on an awkward ring, and a repair that
    # merely moves a step somewhere else is worse than none, so the ring is re-measured rather than
    # assumed.
    if jog_steps([(float(q[0]), float(q[1])) for q in cut], g) >= jog_steps([(float(q[0]), float(q[1])) for q in plots[i]["poly"]], g):
        return False
    try:
        was = Polygon(plots[i]["poly"]).buffer(0)
        now = Polygon(cut).buffer(0)
        if not isinstance(now, Polygon) or not now.is_valid or now.is_empty or now.area < floor:
            return False
        gives = now.area < was.area
        traded = was.difference(now) if gives else now.difference(was)
        # A CUT THAT TRADES NOTHING. Defensive, and not reachable from this engine's own geometry: the
        # guard above has already refused a cut that does not LOWER the ring's step count, and a cut that
        # lowers it has moved a wall, so the symmetric difference has area. Tried and refused by the
        # earlier guards (feature 146): a collinear extra vertex, a zero-area spike back up a wall, a
        # self-touching slit that `buffer(0)` repairs away, and rings carrying NaN and 1e400 coordinates.
        # It stays because shapely, not this module, decides what `difference` returns.
        if traded.is_empty or traded.area <= 0.0:  # pragma: no cover - see above
            return False
        near = traded.buffer(0.4)
        # THE NEW WALL, WHICH IS THE ONLY GEOMETRY THIS REPAIR INVENTS. A basin's bund is SUPPOSED to
        # lie against a delivery ditch's bank - the carve hems it there on purpose - so testing the
        # whole ring against the water refuses repairs that never went near a channel (measured: 926
        # of 1,368 trades). What can actually put a bund in the water is the edge the cut creates,
        # where the chord crosses a corner the carve had wrapped around a bank
        # (`paddy_bunds_clear_the_supply_channels`, Mizuguchi). Tested against the same `water` and
        # `outside` the pass uses to decide what may be planted at all - strictly stricter than the
        # gate's own sampled clearance.
        _had = {(min(_va, _vb), max(_va, _vb)) for _va, _vb in zip(plots[i]["poly"], plots[i]["poly"][1:] + plots[i]["poly"][:1], strict=True)}
        _new = _ring(now)
        for _va, _vb in zip(_new, _new[1:] + _new[:1], strict=True):
            if (min(_va, _vb), max(_va, _vb)) in _had:
                continue
            _seg = LineString([_va, _vb])
            if (not water.is_empty and _seg.intersects(water)) or (not outside.is_empty and _seg.intersects(outside)):
                return False
        if len(_new) < 3 or pointed_ring(dedup_ring(_new, 1.0), _GATE_MIN_APEX):
            return False
        if gives:
            # EVERY BASIN ALONG THE CORNER IN TURN, best first - the same ladder `_absorb` runs, and
            # for the same reason. The corner has to go somewhere, and the basin whose bund forms most
            # of its edge is the right first preference; but a corner welded into one basin can draw it
            # out to a needle while the runner-up takes it cleanly, and refusing outright leaves the
            # step standing. Measured before this loop existed: 366 of 1,468 trades refused on a
            # needle and 248 more on a malformed union, against 260 that went through.
            ranked: list[tuple[float, int]] = []
            nx0, ny0, nx1, ny1 = near.bounds
            for k, q in enumerate(plots):
                if k == i or len(q["poly"]) < 3:
                    continue
                if max(v[0] for v in q["poly"]) < nx0 or min(v[0] for v in q["poly"]) > nx1 or max(v[1] for v in q["poly"]) < ny0 or min(v[1] for v in q["poly"]) > ny1:
                    continue
                qp = Polygon(q["poly"]).buffer(0)
                if not isinstance(qp, Polygon) or not qp.is_valid or qp.is_empty or not qp.intersects(near):
                    continue
                shared = qp.boundary.intersection(near).length
                if shared > 0.0:
                    ranked.append((-shared, k))
            for _neg, k in sorted(ranked):
                grew = (Polygon(plots[k]["poly"]).buffer(0).union(traded.buffer(0.02))).buffer(0)
                if not isinstance(grew, Polygon) or grew.interiors or grew.is_empty or grew.area < floor:
                    continue
                gr = _ring(grew)
                if len(gr) < 3 or not Polygon(gr).buffer(0).is_valid or pointed_ring(dedup_ring(gr, 1.0), _GATE_MIN_APEX):
                    continue
                rings = [(i, _new), (k, gr)]
                break
            else:
                return False
        else:
            # THE GROUND HAS TO COME FROM SOMEWHERE. Whatever the corner overlaps gives it up - all of
            # them, not the best one, or two basins end up claiming the same square foot. What it
            # overlaps nothing of is bare floor, and taking that in is free and is the point.
            # THE BITE WIDENS RATHER THAN THE NEIGHBOUR SPLITTING (feature 152 T18). The dominant refusal
            # on Mizuguchi - and the largest surviving step in the pool, 30.0 ft - is a neighbor that
            # would come apart in two if it gave up the corner, so `qp.difference(traded)` returns a
            # MultiPolygon and the whole repair is declined. `future-work/farming-communities.md` recorded
            # the answer and left it UNTRIED: "keep the largest part for the neighbor and hand the
            # orphaned fragment to the basin that cut it, so the bite widens rather than the neighbor
            # splitting." That is what this does, once, before the neighbor loop - widening mid-loop would
            # change decisions already taken. The orphan is capped against the trade so this stays a repair
            # rather than a land grab, and every guard below still judges the widened result.
            _orphans = []
            for _k, _q in enumerate(plots):
                if _k == i or len(_q["poly"]) < 3:
                    continue
                _qp = Polygon(_q["poly"]).buffer(0)
                if not isinstance(_qp, Polygon) or not _qp.is_valid or _qp.is_empty or _qp.intersection(traded).area <= 0.01:
                    continue
                _lost = _qp.difference(traded).buffer(0)
                if isinstance(_lost, MultiPolygon):
                    _parts = sorted((_g for _g in _lost.geoms if isinstance(_g, Polygon) and not _g.is_empty), key=lambda _g: _g.area, reverse=True)
                    _orphans.extend(_parts[1:])
            if _orphans and sum(_g.area for _g in _orphans) <= _ORPHAN_MAX_SHARE * traded.area:
                _wide = unary_union([traded, *_orphans]).buffer(0)
                _grown = unary_union([now, *_orphans]).buffer(0)
                _gr = _ring(_grown) if isinstance(_grown, Polygon) and _grown.is_valid and not _grown.interiors else []
                # the widened taker must still be a basin, and the repair must still RETIRE the step
                if (
                    len(_gr) >= 3
                    and Polygon(_gr).buffer(0).is_valid
                    and not pointed_ring(dedup_ring(_gr, 1.0), _GATE_MIN_APEX)
                    and jog_steps([(float(_a), float(_b)) for _a, _b in _gr], g) < jog_steps([(float(_a), float(_b)) for _a, _b in plots[i]["poly"]], g)
                ):
                    traded, now, _new = _wide, _grown, _gr
            rings = [(i, _new)]
            tx0, ty0, tx1, ty1 = traded.bounds
            for k, q in enumerate(plots):
                if k == i or len(q["poly"]) < 3:
                    continue
                if max(v[0] for v in q["poly"]) < tx0 or min(v[0] for v in q["poly"]) > tx1 or max(v[1] for v in q["poly"]) < ty0 or min(v[1] for v in q["poly"]) > ty1:
                    continue
                qp = Polygon(q["poly"]).buffer(0)
                if not isinstance(qp, Polygon) or not qp.is_valid or qp.is_empty or qp.intersection(traded).area <= 0.01:
                    continue
                lost = qp.difference(traded).buffer(0)
                if not isinstance(lost, Polygon) or lost.interiors or lost.is_empty or lost.area < floor:
                    return False
                lr = _ring(lost)
                if len(lr) < 3 or not Polygon(lr).buffer(0).is_valid or pointed_ring(dedup_ring(lr, 1.0), _GATE_MIN_APEX):
                    return False
                rings.append((k, lr))
    # SHAPELY DECIDING IT CANNOT ANSWER. Defensive, and not reachable from this engine's own geometry:
    # every ring entering the block is `buffer(0)`-repaired first, which is what makes the predicate
    # operations safe. Tried and refused (feature 146): NaN and 1e400 coordinates in the plot ring, and
    # in the `water` and `outside` geometries the block intersects against - each was caught by an
    # earlier guard or sanitized by `buffer(0)`. Removing it would turn a library edge case into a
    # crash mid-carve, which is the one outcome worse than a refused trade.
    except GEOSException:  # pragma: no cover - see above
        return False
    for k, r in rings:
        plots[k]["poly"] = r
    return True


_ORPHAN_MAX_SHARE = 0.5  # an orphaned fragment handed to the taker may not exceed half the traded corner:
