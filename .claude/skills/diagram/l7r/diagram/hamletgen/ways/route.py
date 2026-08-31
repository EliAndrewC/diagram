"""Split from hamletgen/ways.py by feature 173 - see this package's CLAUDE.md for the index."""

from __future__ import annotations

import heapq
import math
from collections.abc import Sequence

from ..clearance import fabric_index
from ..consts import (
    WEB_FABRIC_GAP,
    WEB_HARD_GAP,
    Poly,
    Pt,
)
from .clearance import _clear_link, _clear_touch
from .geom import _TOUCH_GAP, _turn_deg


def _route(start: Pt, goal: Pt, hard: list[Poly], walls: Sequence[Poly], water: list[tuple[Pt, Pt]], cell: float = 10.0, gap: float = WEB_FABRIC_GAP, pad_mult: float = 0.75) -> Poly:
    """A walkable route from a door to a way, THREADING the steadings rather than assuming a line.

    A straight run plus a few dog-legs was the first two attempts and it is not enough. Measured on
    the in-gate cohort once everything else was fixed, EVERY remaining unreachable farmhouse was
    `hard-clear` and `fabric-blocked` - the paddy, the marsh and the toe were all out of the way, and
    the only thing between the house and the lane was other people's yards and gardens. That is a
    routing problem, and routing problems want a router: a fixed set of offsets either overshoots on
    a short run (a switchback, which a review caught) or misses the gap on a long one.

    Dijkstra on a coarse lattice, then string-pulled. The lattice is the INDEX - it decides nothing,
    because every shortcut is re-tested against the real geometry by `_clear_link` before it is
    taken, so the drawn path is exactly as legal as one drawn by hand. 12 ft cells because the gaps
    these paths thread are `MIN_WEB_GAP` (16 ft) at their narrowest, and a lattice coarser than the
    gap cannot see the gap.

    Returns [] when there is genuinely no way through - which is a real answer, and better than the
    caret a review found on Mizuguchi: a 38 ft mark drawn 71 ft from the house it served, touching
    nothing, to cure a one-foot violation."""
    span = math.dist(start, goal)
    if span < 1.0:
        return [start, goal]
    # THE SEARCH BOX HAS TO BE BIG ENOUGH FOR THE DETOUR, not just for the gap. A path between two
    # steadings needs a little room either side; a link that has to get AROUND a paddy needs as much
    # room as the paddy is wide, and at 0.75 the box simply did not contain the way round - the
    # router reported NO ROUTE for a journey that plainly exists. `pad_mult` is how far the caller
    # thinks the detour might reach.
    pad = max(80.0, span * pad_mult)
    x0, x1 = min(start[0], goal[0]) - pad, max(start[0], goal[0]) + pad
    y0, y1 = min(start[1], goal[1]) - pad, max(start[1], goal[1]) + pad
    nx, ny = int((x1 - x0) / cell) + 1, int((y1 - y0) / cell) + 1
    # AND IT DOES FIRE, on every connector - the older note here said the pad was bounded so the
    # grid was too, which is true only of the short links this router was written for. A connector
    # reaches the map frame, so its span is the canvas width; at `pad_mult` 0.75 the search box is
    # 2.5 canvases across and the lattice is hundreds of thousands of cells. The router therefore
    # declines EVERY connector, which is precisely why `_thread_the_fabric` cannot rescue a track
    # aimed through the cluster and why the bearing has to be chosen clear of the steadings up in
    # `connector_track`. Knowing that this returns [] rather than a detour is load-bearing.
    if nx * ny > 90000:
        return []

    def to_pt(ix: int, iy: int) -> Pt:
        return (x0 + ix * cell, y0 + iy * cell)

    # THE LATTICE TESTS CELL CENTERS, SO IT MUST CLEAR HALF A CELL MORE THAN THE PATH NEEDS.
    #
    # A cell whose CENTER is `gap` from a wall is marked free, and the drawn line through that cell
    # can pass half a cell nearer than its center does - at a 14 ft cell, seven feet nearer. Measured:
    # three web lanes on cohort seed 11 came within 4.0 ft of a farmhouse corner having been planned
    # at 7, and a farmhouse ended up standing on the lane. Inflating the planning clearance by half
    # the cell's diagonal makes "this cell is free" mean "every point in this cell is clear", which is
    # what the rest of the router assumes it means.
    _plan_gap = gap + cell * 0.71
    # ONE INDEX FOR THE WHOLE BOX (feature 138): this was a `clear_runs` call per cell - a degenerate
    # two-point polyline whose truth value is exactly "the cell center is not fouled" - so every cell
    # re-derived every polygon's bounds and measured every edge; 57 of a polder's 110 s.
    _index = fabric_index(hard, WEB_HARD_GAP, walls, _plan_gap, water, 14.0)
    free = [[not _index.fouled(to_pt(ix, iy)) for ix in range(nx)] for iy in range(ny)]
    sx, sy = min(nx - 1, max(0, round((start[0] - x0) / cell))), min(ny - 1, max(0, round((start[1] - y0) / cell)))
    gx, gy = min(nx - 1, max(0, round((goal[0] - x0) / cell))), min(ny - 1, max(0, round((goal[1] - y0) / cell)))
    free[sy][sx] = free[gy][gx] = True  # the two given endpoints are the caller's, not the lattice's to refuse
    dist = {(sx, sy): 0.0}
    prev: dict[tuple[int, int], tuple[int, int]] = {}
    heap = [(0.0, sx, sy)]
    while heap:
        d, ix, iy = heapq.heappop(heap)
        if (ix, iy) == (gx, gy):
            break
        if d > dist.get((ix, iy), 1e18):
            continue
        for dx2 in (-1, 0, 1):
            for dy2 in (-1, 0, 1):
                jx, jy = ix + dx2, iy + dy2
                # A DIAGONAL MAY NOT CUT A BLOCKED CORNER. Cell centers can both be clear while the
                # step between them clips the corner of a steading standing between them - so the
                # planned route was not actually walkable and failed its own acceptance test a moment
                # later, having been "found". Requiring both orthogonal neighbors makes the lattice
                # tell the truth about what it can walk.
                if (dx2 or dy2) and 0 <= jx < nx and 0 <= jy < ny and free[jy][jx] and (not (dx2 and dy2) or (free[iy][jx] and free[jy][ix])):
                    nd = d + math.hypot(dx2, dy2) * cell
                    if nd < dist.get((jx, jy), 1e18):
                        dist[(jx, jy)] = nd
                        prev[(jx, jy)] = (ix, iy)
                        heapq.heappush(heap, (nd, jx, jy))
    if (gx, gy) not in dist:
        return []
    path: Poly = []
    cur = (gx, gy)
    while cur != (sx, sy):
        path.append(to_pt(*cur))
        cur = prev[cur]
    path.append(start)
    path.reverse()
    path[-1] = goal
    # STRING-PULL against the real geometry, so the lattice never shows in the drawing.
    out: Poly = [path[0]]
    i = 0
    while i < len(path) - 1:
        j = len(path) - 1
        # STRING-PULL AT THE CLEARANCE THE LATTICE PLANNED WITH, not at the default. Validating
        # shortcuts more strictly than the route was planned produced paths that failed their own
        # acceptance test a moment later - the router found a way through at 5 ft and the pull then
        # refused every shortcut along it at 7, leaving a chain of lattice steps whose diagonals
        # clipped the corners the cell centers had cleared. One number, used by both.
        while j > i + 1 and not _clear_link(path[i], path[j], hard, walls, water, gap=gap):
            j -= 1
        out.append(path[j])
        i = j
    return _unjog(out, hard, walls, water)


def _unjog(path: Poly, hard: list[Poly], walls: Sequence[Poly], water: list[tuple[Pt, Pt]], gap: float | None = None) -> Poly:
    """Take the lattice's jogs out of a routed path where the chord clears at the JUNCTION margin.

    The string-pull above tests every shortcut at the margin the route was planned with, so a route
    that hugs a garden's corner at the fabric margin keeps a 7 ft step and a 13 ft step back where
    the lattice turned the corner - `lanes_bend_like_paths` reads two turns past 50 degrees within
    40 ft as a zigzag (cohort seed 14, feature 137 T03), and a turn past 140 as a hairpin. Both are
    the lattice showing through, not the ground; a path that may brush a fence at a junction may
    brush it at a corner, so each such jog is replaced by its chord when `_clear_touch` allows it.
    The thresholds are the check's own, so this undoes exactly what the check would refuse."""
    gap = _TOUCH_GAP if gap is None else gap  # the module constant is defined below this function
    out = list(path)
    k = 1
    while k < len(out) - 1:
        if _turn_deg(out[k - 1], out[k], out[k + 1]) >= 140.0:
            if _clear_touch(out[k - 1], out[k + 1], hard, walls, water, gap):
                del out[k]
                k = max(1, k - 1)
                continue
            eased = _ease_corner(out[k - 1], out[k], out[k + 1], hard, walls, water)
            if eased is not None:
                out[k : k + 1] = eased
                k = max(1, k - 1)
                continue
        if k < len(out) - 2 and _turn_deg(out[k - 1], out[k], out[k + 1]) >= 50.0 and _turn_deg(out[k], out[k + 1], out[k + 2]) >= 50.0 and math.dist(out[k], out[k + 1]) <= 40.0:
            if _clear_touch(out[k - 1], out[k + 2], hard, walls, water, gap):
                del out[k : k + 2]
                k = max(1, k - 1)
                continue
            # THE CHORD IS BLOCKED BUT THE KNEE MAY NOT BE (feature 145, Kashikawa after the field moved): a
            # 7 px lattice step round a garden corner survived because the straight chord over both turns
            # brushed the garden; one vertex at the step's midpoint keeps the corner and takes the zigzag out.
            knee = ((out[k][0] + out[k + 1][0]) / 2.0, (out[k][1] + out[k + 1][1]) / 2.0)
            if _clear_touch(out[k - 1], knee, hard, walls, water, gap) and _clear_touch(knee, out[k + 2], hard, walls, water, gap):
                out[k : k + 2] = [knee]
                k = max(1, k - 1)
                continue
            # ...AND WHEN EVEN THE KNEE IS BLOCKED, WALK THE CORNER OFF ITS APEX (feature 134 T50). The knee
            # is one candidate on the step's own midline; `_ease_corner` searches perpendicular to the chord,
            # so it clears an obstacle the midpoint still sits inside. Ordered second because it is the
            # broader, costlier search and the knee answers the common case.
            eased = _ease_corner(out[k - 1], out[k], out[k + 2], hard, walls, water)
            if eased is not None:
                out[k : k + 2] = eased
                k = max(1, k - 1)
                continue
        k += 1
    return out


# HOW FAR A CORNER MAY BE PUSHED OFF ITS APEX to ease a hairpin or a zigzag the straight chord cannot
# cut. 24 ft is three paces past the widest homestead gap the fabric leaves; beyond that the detour
# stops being the same way and the router should have found another line.
_EASE_FT = 24.0
_EASE_STEPS = 6


def _ease_corner(a: Pt, apex: Pt, b: Pt, hard: list[Poly], walls: Sequence[Poly], water: list[tuple[Pt, Pt]]) -> Poly | None:
    """A hairpin or zigzag whose straight chord is BLOCKED, walked around instead of left in place.

    `_unjog` above replaces a jog with its chord when the chord is walkable. When it is not - the
    ground the lattice went around is genuinely occupied - the jog used to survive and
    `lanes_bend_like_paths` refused the map. That was rare while the threshing yard was a fixed
    fraction of its house; once the yard is ROLLED per household (feature 134 T49) the wider yards
    block more chords, and cohort seeds 27 and 47 regressed on exactly this.

    So: slide the corner off its apex, perpendicular to the chord, in both directions, and take the
    nearest position whose two legs are both walkable and whose turns are inside the check's own
    thresholds. That keeps the way going round what is actually there - which is what a trodden path
    does - instead of doubling back on itself. Returns the replacement point as a one-item path, or
    None when no offset within `_EASE_FT` works, in which case the jog stays and the caller's other
    passes (or the router) must deal with it."""
    mx, my = (a[0] + b[0]) / 2.0, (a[1] + b[1]) / 2.0
    dx, dy = b[0] - a[0], b[1] - a[1]
    span = math.hypot(dx, dy)
    if span < 1.0:
        return None
    px, py = -dy / span, dx / span  # the chord's unit normal
    # THE APEX'S OWN SIDE FIRST. Trying a fixed sign order flips the lane to the far side of the
    # obstacle whenever both sides are equally clear, which moves the way somewhere the router never
    # considered; the eased corner should stay on the side the route already chose.
    apex_side = 1.0 if ((apex[0] - mx) * px + (apex[1] - my) * py) >= 0 else -1.0
    # nearest offsets first, both sides, so the eased corner stays as close to the original as it can
    for i in range(1, _EASE_STEPS + 1):
        off = _EASE_FT * i / _EASE_STEPS
        for sign in (apex_side, -apex_side):
            cand = (mx + px * off * sign, my + py * off * sign)
            if _turn_deg(a, cand, b) >= 140.0:
                continue  # the eased corner must not itself be a hairpin
            if _clear_touch(a, cand, hard, walls, water) and _clear_touch(cand, b, hard, walls, water):
                return [cand]
    return None
