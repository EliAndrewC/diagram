"""The household's share of the wood floor, reserved at its seat (feature 287, woods W25 made absolute; plan D9).

THE FLOOR. Each homestead keeps no less than `HOMESTEAD_WOOD_FT2[0]` of trees - its windward grove and its share of the
copse together (research/rendering/homesteads/010; `homestead_wood_drawn` is the finished-map predicate). Until this module the floor
was met AFTER the fact: `stage_windbreak` topped a short copse up in the belt's lee, wherever the ground the houses, the
lanes and the belt had left still took a clump - which met it on cohort 1-60 (the lowest 6,012 sq ft, seed 14) but could
fall short on a site whose lee was already built over, and nothing then could make the room.

THE RESERVATION (plan D9: a rolled or required feature is laid as a part of the homestead, so a household is seated only
with room for it). A household is admitted only where it can reserve its share of the floor as copse SEATS: points
within `reach` of its own house, on its own bank, where the dooryard copse may stand a clump - clear of every copse
keep-out of its own parts and of every homestead already standing, of the crop, the water, the dike and the marsh, and
of every reserved access corridor - whose crowns, counted on the raster `wood_canopy` counts on, cover the floor on
ground no other household has reserved. Every later homestead is refused where one of its parts' keep-outs would cover a
reserved seat, and every later corridor where its strip would. So the reservations are disjoint and each holds its
share: planted, they draw `households x floor` of copse whatever the belt draws.

WHAT THE KEEP-OUTS ARE. A seat is refused where the copse's own planting (`village_grove`, `dense=False`) would refuse
its clump: the occupancy disc of a house, yard, garden bed, byre, kura or retirement house (half its diagonal, plus the
clump's radius and 2 px), a wellhead's (its drawn half-size, plus 1.05 clumps and 1 px), the sunny strip south of every
yard and bed and the morning lane east of every bed, and the crop (12 px plus the clump's radius), the dry plots (12),
the dike and the marsh, open water (its half-width plus the clump's radius). The figures are `village_grove`'s; the
placer holds them `BAR_MARGIN_PX` stricter, the placer-stricter-by-a-hair rule the sun corridor keeps (`_sun_corridor_ok`),
because the planting reads the drawn records and the seat reads the parts they are drawn from.

WHERE THE SEATS GO. Behind the house first - the homestead's own windward trees stand at its back (the yashikirin's
north and west, research/homesteads) and its front is the yard's and the garden's sun: the lattice is taken nearest a
point half the reach behind the house's back wall. A lattice of `SEAT_PITCH_BS` (a clump's radius times the square root
of two, so every point of a lattice cell lies under a crown) anchored on the house.

WHO HOLDS THE REST: the copse plants the reserved seats before any other clump (`stage_windbreak`) and the belt keeps off
them (`reserved_seat_keepouts`); every placer after the seating - the web's lanes by the copse's own lane buffer, the
title's pocket, the shared sheds, the wells, the parts laid after it - is kept off them by the registry of what stands
(`overlap/reserved.py`, plan M8), to which the seating hands them (`homesteads/stages.reserve_the_seating`).
"""

from __future__ import annotations

import math
from collections.abc import Iterable, Mapping, Sequence
from typing import TYPE_CHECKING, Any

from .._geom import PointGrid, Pt, seg_dist, segments_cross
from ..land.wet import marsh_ground
from ..shrines_wells.byres import BYRE_FT
from .grove_blocks import GroveBlocks
from .groves import crown_lift
from .stands import crown_reach

if TYPE_CHECKING:
    from ..core import Settlement

#: The dooryard copse's clump, in bscale units: `village_grove`'s sparse stand (`dense=False`) draws a 22 px clump.
COPSE_CLUMP_BS = 22.0

#: The seat lattice's pitch, in bscale units: the clump's radius times the square root of two, the widest square lattice
#: whose crowns leave no point of a cell bare - so the reserved crowns cover their ground without a gap.
SEAT_PITCH_BS = 11.0 * math.sqrt(2.0)

#: The placer's margin over the planting's own keep-outs, in px (see the module's note): the parts a seat is read against
#: are the rects the records are drawn from, and a record rounds to 0.1 px.
BAR_MARGIN_PX = 0.5

#: Where the reservation is centered, as a share of the reach behind the house's center, and how much dearer a foot to
#: the side is than a foot deeper: the wood is taken as a block BEHIND its own house before it spreads to the flanks,
#: where the row's neighbors stand their gardens (a front row at `BUNDLE_PITCH` lost a third of its seats to a round
#: reservation - `test_the_front_row_stops_at_its_share_and_the_ranks_seat_the_rest`). A MAP DRAWING CONVENTION on the
#: record's "the windward grove at the back" (research/homesteads, the yashikirin's north and west): the figures are
#: the placer's, not the record's.
FOCUS_DEPTH = 0.7
LATERAL_WEIGHT = 2.0

#: The strip the morning lane runs east of a garden bed, in px: `village_grove`'s `east` rectangle (24 px past the bed).
EAST_LANE_PX = 24.0


def copse_keepouts(parts: Mapping[str, Any], clump: float, sun_depth: float, well_vr: float) -> tuple[list[tuple[float, float, float]], list[tuple[float, float, float, float]]]:
    """The copse keep-outs of one homestead's parts, as `(circles, rects)`: the discs a clump's center may not enter and
    the open rectangles it may not stand in, each `village_grove`'s own figure (see the module's note) grown by
    `BAR_MARGIN_PX`. `parts` holds `(cx, cy, w, h)` rects - the unturned size at the drawn center, as a record is: `house`,
    `yard`, `gardens` (a list), `shed`, `byre`, `retirement` and `well` (the pocket; `well_vr` its drawn half-size)."""
    cr, m = clump / 2.0, BAR_MARGIN_PX
    circles: list[tuple[float, float, float]] = []
    rects: list[tuple[float, float, float, float]] = []
    solids = [parts.get(k) for k in ("house", "yard", "shed", "byre", "retirement")] + list(parts.get("gardens") or ())
    for r in solids:
        if r is not None:
            circles.append((r[0], r[1], 0.5 * math.hypot(r[2], r[3]) + cr + 2.0 + m))
    well = parts.get("well")
    if well is not None:
        circles.append((well[0], well[1], well_vr + clump * 1.05 + 1.0 + m))
    for r in [parts.get("yard"), *(parts.get("gardens") or ())]:
        if r is not None:  # the sunny strip south of a yard or a bed
            half, south = r[2] / 2.0 + cr + 2.0, r[1] + r[3] / 2.0
            rects.append((r[0] - half - m, south - cr - 2.0 - m, r[0] + half + m, south + sun_depth + 2.0 + cr + m))
    for g in parts.get("gardens") or ():  # ...and the morning lane east of a bed
        east, half = g[0] + g[2] / 2.0, g[3] / 2.0 + cr + 2.0
        rects.append((east - cr - 2.0 - m, g[1] - half - m, east + EAST_LANE_PX + cr + m, g[1] + half + m))
    return circles, rects


def bundle_parts(geom: Mapping[str, Any]) -> dict[str, Any]:
    """The parts of a homestead bundle (`_bundle_geom`) `copse_keepouts` reads: each at its drawn center and unturned size,
    the retirement house among the fixtures."""
    return {
        "house": geom["house"],
        "yard": geom.get("yard"),
        "gardens": list(geom.get("gardens") or ()),
        "shed": geom.get("shed"),
        "byre": geom.get("byre"),
        "well": geom.get("well"),
        "retirement": (geom.get("fixtures") or {}).get("retirement"),
    }


def in_keepouts(x: float, y: float, circles: Iterable[tuple[float, float, float]], rects: Iterable[tuple[float, float, float, float]]) -> bool:
    """Does a clump seated at (x, y) stand in any of these keep-outs - strictly inside a disc or an open rectangle, as the
    planting's own tests read (`circle_hit`, `rect_hit`)?"""
    return any((x - cx) ** 2 + (y - cy) ** 2 < r * r for cx, cy, r in circles) or any(x0 < x < x1 and y0 < y < y1 for x0, y0, x1, y1 in rects)


def ground_blocks(s: Settlement, clump: float) -> GroveBlocks:
    """The ground a dooryard copse clump may not stand on, indexed once: the crop within 12 px plus the clump's radius, the
    dry plots within 12, the dike outlines and the marsh (inside), open water within its half-width plus the clump's
    radius - `village_grove`'s hard keep-outs for the copse, each `BAR_MARGIN_PX` stricter. Only `hard` is asked of it."""
    cr, m = clump / 2.0, BAR_MARGIN_PX
    water = [(st["poly"], st.get("w", 9) / 2 + cr + m) for st in s.M.get("streams", [])]
    water += [(ch["poly"], ch.get("w", 2.5) / 2 + cr + m) for ch in s.M.get("channels", [])]
    if s.M.get("moat"):
        water.append((s.M["moat"], s.M.get("moat_width", 22) / 2 + cr + m))
    return GroveBlocks(
        outline=[(0.0, 0.0), (float(s.W), 0.0), (float(s.W), float(s.H)), (0.0, float(s.H))],
        crops=s.field_polys,
        crop_pad=12 + cr + m,
        dry=s.dry_polys,
        dry_pad=12 + m,
        # ...and the reed-marsh TOE, asked before it is drawn (`toe_band`, the one derivation `hinterland()` lays the reeds on):
        # the copse refuses a clump in the marsh as finished, and cohort 1-60 lost 24 seats reserved on ground the toe
        # marsh then took (feature 287 M8)
        dikes=[dk["outline"] for dk in s.M.get("dikes", [])] + marsh_ground(s.M) + [t for t in [[(float(a), float(b)) for a, b in (s.toe_band() or [])]] if len(t) >= 3],
        water=water,
        corridors=[],
        circles=[],
        displacers=[],
        rects=[],
        dike_pad=m,
    )


def open_water_discs(M: Mapping[str, Any], clump: float) -> list[tuple[float, float, float]]:
    """The copse's canopy keep-outs round the ponds and the sacred ground standing at seating (`village_grove`'s `occ`: the
    pond - the tameike or a polder's header reservoir - by its longer semi-axis, a crescent pond by its radius, a shrine's
    hall by half its diagonal, each plus 0.90 of the clump; a torii by its glyph), `BAR_MARGIN_PX` stricter: the planting
    refuses a clump inside them, and Kuwabata's header reservoir took a reserved seat 3.5 px off its fringe so (feature
    287 M8)."""
    reach = clump * 0.90 + BAR_MARGIN_PX
    out = [(float(o["x"]), float(o["y"]), 0.5 * math.hypot(float(o["w"]), float(o["h"])) + reach) for k in ("religious", "shrines") for o in M.get(k) or [] if "w" in o and "h" in o]
    out += [(float(t[0]), float(t[1]) + 4.0, math.hypot(19.0, 14.0) + reach) for t in M.get("torii") or []]
    out += [(float(cp["cx"]), float(cp["cy"]), float(cp["r"]) + reach) for cp in M.get("crescent_ponds") or []]
    pond = M.get("pond")
    if pond:
        out.append((float(pond[0]), float(pond[1]), max(float(pond[2]), float(pond[3])) + reach))
    return out


def seat_rank(dx: float, dy: float, back: Pt, side: Pt, depth: float) -> float:
    """The order a seat at (dx, dy) from its house is offered in: its distance from the point `depth` behind the house, a
    foot to the side counted `LATERAL_WEIGHT` times a foot along the back."""
    u, v = dx * side[0] + dy * side[1], dx * back[0] + dy * back[1]
    return LATERAL_WEIGHT * u * u + (v - depth) ** 2


def crown_cells(x: float, y: float, r: float, c: float) -> frozenset[tuple[int, int]]:
    """The raster cells a crown at (x, y) of radius `r` covers - `CanopyArea.add`'s cells (a cell whose center lies within
    the crown), found a column at a time: the column's span from the circle widened by a cell, its two ends then narrowed by the
    same test `CanopyArea` makes, so the set is the one it builds without its test of every cell of the crown's box (seed 17: 124,000
    probe crowns, a tenth of the seating)."""
    out: list[tuple[int, int]] = []
    r2 = r * r
    j_lo, j_hi = int((y - r) // c), int((y + r) // c)
    for i in range(int((x - r) // c), int((x + r) // c) + 1):
        dx2 = ((i + 0.5) * c - x) ** 2
        if dx2 > r2:
            continue
        s = math.sqrt(r2 - dx2)
        # a cell wider than the circle's span each side (the square root's rounding cannot reach a whole cell), narrowed
        lo, hi = max(j_lo, math.ceil((y - s) / c - 0.5) - 1), min(j_hi, math.floor((y + s) / c - 0.5) + 1)
        while lo <= hi and dx2 + ((lo + 0.5) * c - y) ** 2 > r2:
            lo += 1
        while hi >= lo and dx2 + ((hi + 0.5) * c - y) ** 2 > r2:
            hi -= 1
        out += [(i, j) for j in range(lo, hi + 1)]
    return frozenset(out)


def within_reach(segs: Iterable[tuple[Pt, Pt]], p: Pt, pad: float) -> list[tuple[Pt, Pt]]:
    """The segments whose box comes within `pad` of `p` - every one that can pass within `pad` of it."""
    return [(a, b) for a, b in segs if min(a[0], b[0]) - pad <= p[0] <= max(a[0], b[0]) + pad and min(a[1], b[1]) - pad <= p[1] <= max(a[1], b[1]) + pad]


class WoodShares:
    """The seating's reservations of the wood floor (installed on the settlement as `_wood` by `install_wood_shares`): the
    keep-outs of every homestead admitted, the seats every household reserved, and the canopy cells they cover."""

    def __init__(self, s: Settlement, floor_ft2: float, reach_ft: float, corridor_half: float) -> None:
        self.clump = COPSE_CLUMP_BS * s.bscale
        self.cr = round(self.clump / 2.0, 1)  # the radius the planted copse records and `wood_canopy` counts at
        self.pitch = SEAT_PITCH_BS * s.bscale
        self.floor = floor_ft2 * s.px(1.0) ** 2  # px^2
        self.reach = s.px(reach_ft)
        self.cell = 2.0 * s.bscale  # `wood_canopy`'s raster
        self.sun_depth = float(getattr(s, "_sun_corridor_ft", 22.0))
        self.well_vr = float(s._well_vr())
        # a clump keeps its crown off a lane's tread (`village_grove`'s corridor buffer); a corridor's way runs anywhere in
        # its strip, so a seat keeps the strip's half plus that buffer off the corridor's line - the buffer the copse plants
        # by, crowns drawn `3 * bs` up the sheet included (`crown_reach(lift=)`, feature 287 homes H43): without the lift a
        # reserved seat could stand where the copse's own lane buffer refuses it
        self.lane_gap = corridor_half + max(self.clump * 0.45 + 4, crown_reach(self.clump, lift=crown_lift(s.bscale))) + BAR_MARGIN_PX
        self.W, self.H = float(s.W), float(s.H)
        self.ground = ground_blocks(s, self.clump)
        self.banks = [((float(a[0]), float(a[1])), (float(b[0]), float(b[1]))) for f in s.M.get("streams") or [] for a, b in zip(f.get("poly") or [], (f.get("poly") or [])[1:], strict=False)]
        self.bars = PointGrid(64.0)  # the keep-outs of every admitted homestead: ("c", cx, cy, r) and ("r", x0, y0, x1, y1)
        self.seats = PointGrid(64.0)  # every reserved seat
        self.cells: set[tuple[int, int]] = set()
        # the crowns of the lattice last asked (`crowns`): the four garden sides of one seat ask the same lattice
        self._crowns: tuple[Pt, dict[tuple[float, float], frozenset[tuple[int, int]]]] = ((math.nan, math.nan), {})
        self.file_byre_pockets(s, getattr(s, "_byre_pockets", None) or ())
        self.file(open_water_discs(s.M, self.clump), [])

    def file_byre_pockets(self, s: Settlement, pockets: Iterable[Pt]) -> None:
        """File the shared sheds' pockets the seating reserved before any house (`reserve_commons_byres`): each a byre's
        keep-out, so no seat is reserved under a shed."""
        bw, bh = s.px(BYRE_FT[0]), s.px(BYRE_FT[1])
        for x, y in pockets:
            self.file([(float(x), float(y), 0.5 * math.hypot(bw, bh) + self.clump / 2.0 + 2.0 + BAR_MARGIN_PX)], [])

    def keepouts(self, geom: Mapping[str, Any]) -> tuple[list[tuple[float, float, float]], list[tuple[float, float, float, float]]]:
        return copse_keepouts(bundle_parts(geom), self.clump, self.sun_depth, self.well_vr)

    def seat_barred(self, x: float, y: float, house: Pt, own: tuple[Any, Any], corridors: Sequence[tuple[Pt, Pt]], banks: Sequence[tuple[Pt, Pt]] | None = None) -> bool:
        """THE ONE PREDICATE of a reserved seat: may the copse stand a clump at (x, y) for the house at `house`, among its own
        keep-outs `own` and the reserved `corridors`? Off the canvas, past the reach, in a keep-out of its own or of any
        homestead admitted, on hard ground, across a bank (`banks`: the stream reaches to ask, every one by default) or on
        a corridor, it may not."""
        if not (6.0 <= x <= self.W - 6.0 and 6.0 <= y <= self.H - 6.0):
            return True
        if math.dist((x, y), house) > self.reach - BAR_MARGIN_PX:
            return True
        if in_keepouts(x, y, *own):
            return True
        for it in self.bars.near(x, y):
            if it[0] == "c" and (x - it[1]) ** 2 + (y - it[2]) ** 2 < it[3] ** 2:
                return True
            if it[0] == "r" and it[1] < x < it[3] and it[2] < y < it[4]:
                return True
        if self.ground.hard(x, y):
            return True
        if any(segments_cross((x, y), house, a, b) for a, b in (self.banks if banks is None else banks)):
            return True
        return any(seg_dist(x, y, a, b) < self.lane_gap for a, b in corridors)

    def share(self, geom: Mapping[str, Any], rot: float, corridors: Sequence[tuple[Pt, Pt]]) -> list[tuple[float, float]] | None:
        """The seats this homestead would reserve: the lattice within reach of its house, nearest a point half the reach
        behind its back wall first, each seat kept where it is not barred (`seat_barred`) and its crown covers ground no
        other household reserved, until the crowns cover the floor. None when the ground within reach cannot hold it -
        the homestead is refused its seat."""
        hx, hy = float(geom["house"][0]), float(geom["house"][1])
        th = math.radians(rot)
        back, side = (math.sin(th), -math.cos(th)), (math.cos(th), math.sin(th))  # the house frame's -y and +x, turned with it
        depth = FOCUS_DEPTH * self.reach
        own = self.keepouts(geom)
        # only the corridors and the stream reaches that come within the reach of the house can bar a seat
        corridors = within_reach(corridors, (hx, hy), self.reach + self.lane_gap)
        banks = within_reach(self.banks, (hx, hy), self.reach)
        n = int(self.reach // self.pitch)
        lattice = [(round(hx + i * self.pitch, 1), round(hy + j * self.pitch, 1)) for i in range(-n, n + 1) for j in range(-n, n + 1)]
        lattice.sort(key=lambda q: seat_rank(q[0] - hx, q[1] - hy, back, side, depth))
        mine: set[tuple[int, int]] = set()
        seats: list[tuple[float, float]] = []
        for x, y in lattice:
            if self.seat_barred(x, y, (hx, hy), own, corridors, banks):
                continue
            fresh = self.crown(x, y, (hx, hy)) - self.cells - mine
            if not fresh:
                continue
            mine |= fresh
            seats.append((x, y))
            if len(mine) * self.cell * self.cell >= self.floor:
                return seats
        return None

    def crown(self, x: float, y: float, anchor: Pt) -> frozenset[tuple[int, int]]:
        """`crown_cells` of a seat at (x, y), REMEMBERED for the lattice anchored at `anchor` (a house's center) until a
        lattice anchored elsewhere is asked: the four garden sides of one seat ask the same lattice (seed 17: 122,610
        crowns, most of them asked again)."""
        if self._crowns[0] != anchor:
            self._crowns = (anchor, {})
        memo = self._crowns[1]
        got = memo.get((x, y))
        if got is None:
            got = memo[(x, y)] = crown_cells(x, y, self.cr, self.cell)
        return got

    def covers_a_seat(self, geom: Mapping[str, Any]) -> bool:
        """Would this homestead's parts, admitted, stand a keep-out over a seat another household reserved?"""
        circles, rects = self.keepouts(geom)
        for cx, cy, r in circles:
            if any((sx - cx) ** 2 + (sy - cy) ** 2 < r * r for sx, sy, *_ in self.seats.near(cx, cy, r)):
                return True
        return any(any(x0 < sx < x1 and y0 < sy < y1 for sx, sy, *_ in self.seats.near((x0 + x1) / 2, (y0 + y1) / 2, max(x1 - x0, y1 - y0) / 2)) for x0, y0, x1, y1 in rects)

    def seats_on(self, seats: Iterable[tuple[float, float]], corridor: tuple[Pt, Pt]) -> bool:
        """Does a corridor run within `lane_gap` of any of these seats?"""
        return any(seg_dist(x, y, corridor[0], corridor[1]) < self.lane_gap for x, y in seats)

    def corridor_bars(self, a: Pt, b: Pt) -> bool:
        """Would a corridor a-b run within `lane_gap` of a reserved seat?"""
        # THE SEATS' CELLS THE STRIP CAN REACH, each asked once: a seat is filed in the one cell holding it, and a seat within
        # the gap of the line stands in a cell whose center is within the gap and the cell's half-diagonal of it - so the
        # cells of the corridor's widened box farther than that are passed without reading them (seed 44: 2.9 million
        # grid lookups sampling long corridors every 32 px)
        grid, gap = self.seats, self.lane_gap
        c = grid.cell
        reach = gap + c * math.sqrt(0.5)
        i0, i1 = int((min(a[0], b[0]) - gap) // c), int((max(a[0], b[0]) + gap) // c)
        j0, j1 = int((min(a[1], b[1]) - gap) // c), int((max(a[1], b[1]) + gap) // c)
        if (i1 - i0 + 1) * (j1 - j0 + 1) <= len(grid.buckets):
            cells = [(i, j) for i in range(i0, i1 + 1) for j in range(j0, j1 + 1) if (i, j) in grid.buckets]
        else:
            cells = [k for k in grid.buckets if i0 <= k[0] <= i1 and j0 <= k[1] <= j1]
        for i, j in cells:
            if seg_dist((i + 0.5) * c, (j + 0.5) * c, a, b) >= reach:
                continue
            if any(seg_dist(sx, sy, a, b) < gap for sx, sy, *_ in grid.buckets[(i, j)]):
                return True
        return False

    def file(self, circles: Iterable[tuple[float, float, float]], rects: Iterable[tuple[float, float, float, float]]) -> None:
        """File keep-outs every later seat is read against."""
        self.bars.extend([("c", cx, cy, r, cx - r, cy - r, cx + r, cy + r) for cx, cy, r in circles])
        self.bars.extend([("r", x0, y0, x1, y1, x0, y0, x1, y1) for x0, y0, x1, y1 in rects])

    def commit(self, geom: Mapping[str, Any], seats: Sequence[tuple[float, float]]) -> float:
        """File an admitted homestead: its keep-outs, its seats and their crowns. Returns the ground the seats cover (px^2)."""
        self.file(*self.keepouts(geom))
        self.seats.extend([(x, y, x, y, x, y) for x, y in seats])
        fresh = set().union(*(crown_cells(x, y, self.cr, self.cell) for x, y in seats)) - self.cells
        self.cells |= fresh
        return len(fresh) * self.cell * self.cell


def install_wood_shares(s: Settlement, floor_ft2: float, reach_ft: float, corridor_half_ft: float) -> WoodShares:
    """Ask the seating to reserve each household's share of the wood floor (opt-in, as `sun_corridor` is): installed on the
    settlement as `_wood` for the seat pass, taken down when the seating ends."""
    s._wood = WoodShares(s, floor_ft2, reach_ft, s.px(corridor_half_ft))
    return s._wood


class ReservedSeats:
    """Every seat the households reserved, read off their records (`wood_share`) and indexed once, for a later placer to
    keep its keep-out off: `disc_covers(x, y, r)` - would a disc of radius `r` at (x, y) stand over one?"""

    __slots__ = ("grid",)

    def __init__(self, houses: Iterable[Mapping[str, Any]]) -> None:
        self.grid = PointGrid(64.0)
        self.grid.extend([(float(p[0]), float(p[1]), float(p[0]), float(p[1]), float(p[0]), float(p[1])) for h in houses for p in (h.get("wood_share") or {}).get("seats") or ()])

    def disc_covers(self, x: float, y: float, r: float) -> bool:
        return any((sx - x) ** 2 + (sy - y) ** 2 < r * r for sx, sy, *_ in self.grid.near(x, y, r))


def well_keepout(s: Settlement) -> float:
    """The disc a wellhead keeps the dooryard copse's clumps out of, from its center (`village_grove`'s `vr + 1.05 clumps
    + 1`), `BAR_MARGIN_PX` stricter."""
    return float(s._well_vr()) + COPSE_CLUMP_BS * s.bscale * 1.05 + 1.0 + BAR_MARGIN_PX
