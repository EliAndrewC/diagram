"""Split from settlement/homestead_parts.py by feature 173 - see this package's CLAUDE.md for the index.
Research: plumbing - NONE"""

import math
from collections.abc import Callable, Sequence
from typing import TYPE_CHECKING, Any

from .._geom import CanopyArea, point_in_poly
from ..land.tiles import pattern_id
from .bamboo_keepout import grown_ring as grown_ring  # re-exported: its one caller moved to grove_fill.py (feature 370)
from .bamboo_keepout import stand_spares_seats as stand_spares_seats
from .belt_law import settle_the_belt
from .grove_blocks import BankNear, Seats
from .grove_fill import close_belt_gaps, grove_blocks, ink_and_record_grove, reseat_clump
from .stocking import Box as Box
from .stocking import grove_extent as grove_extent
from .stocking import grove_stocked as grove_stocked
from .stocking import main_stand as main_stand
from .stocking import record_box as record_box
from .stocking import stocked_at_grain as stocked_at_grain
from .stocking import stocked_box as stocked_box
from .stocking import stocked_copse as stocked_copse
from .wood_goal import canopy_of, trim_to_goal

if TYPE_CHECKING:
    from ..core import Settlement


_GAP_MEMORY = True
"""The windbreak gap fill skips a gap that seated nothing (feature 281, FR-008); off only in the test that proves the
clumps are unchanged."""


def crown_reach(clump: float, jitter: float = 0.0, lift: float = 0.0) -> float:
    """How far from its clump's seat a crown's trunk can be drawn (feature 287, woods W21 and homes H43): `_draw_grove`
    throws each crown inside the clump's box less 2 px a side and then draws it `lift` higher on the sheet (`groves.crown_lift`,
    its `cy + py - lift` - 3.66 px on a hamlet, taken as 3.0 until feature 287 M8 found a trunk 15.3 px out), and a conifer-led belt's row trunk stands inside a clump's box and moves up to `jitter` each way
    (`_belt_ranks`) - so the box's half-diagonal, grown by the jitter, with the lift on the vertical half. The lift was
    missing until cohort seed 3 drew a copse crown 15.0 px from a seat whose reach was taken as 12.7, and 0.8 px from a
    footpath's centerline."""
    return math.hypot(clump / 2.0 - 2.0 + jitter, clump / 2.0 - 2.0 + jitter + lift)


def trunk_on_tread(x: float, y: float, lanes: Any) -> bool:
    """THE ONE PREDICATE of "no tree is planted in a path" (`test_no_tree_is_planted_in_a_path`; feature 287, woods W21 and homes H43): a trunk at
    (x, y) stands on a lane's TREAD - within the lane's own half-width of its centerline, the width read from the lane (GM 2026-09-12: a trunk beside
    a footpath is what a path looks like; one inside it is a tree in the path). `lanes` are manifest lane records (`pts`, `w`).
    Research: no trunk within a lane's half-width - CANON: the GM's ruling of 2026-09-12, no question
        its salts, guards and sentinels - NONE: they decide nothing about the place - 6 (lane width fallback, never reached)
    """
    from .._geom import seg_dist

    return any(
        seg_dist(x, y, (float(a[0]), float(a[1])), (float(b[0]), float(b[1]))) < float(ln.get("w", 6)) / 2.0
        for ln in lanes
        for a, b in zip(ln.get("pts") or [], (ln.get("pts") or [])[1:], strict=False)
    )


BELT_BEARING_MAX_DEG = 45.0  # the belt's center within this of the wind's quarter, seen from the cluster's center
"""Research: belt on the windward side - research/questions/0072-shelter-belts-on-a-villages-windward-side-bofurin.drawing.html: its center within 45 degrees of the wind's quarter"""
BELT_SUBTENSE_MAX_DEG = 200.0  # ...and its crowns round the cluster on one or two sides: a hook, never a ring
"""Research: belt never a ring - research/questions/0072-shelter-belts-on-a-villages-windward-side-bofurin.drawing.html: at most 200 degrees round the cluster"""


def belt_bearing_and_subtense(clumps: Any, houses: Any, wind: tuple[float, float]) -> tuple[float, float]:
    """THE ONE PREDICATE of `test_every_pool_hamlet_has_its_belt_on_the_regional_northwest` (feature 287, woods W18), as
    (how far the belt's center bears off the wind's quarter, how many degrees its crowns subtend round the cluster), both
    seen from the houses' centroid. `wind` points toward where the wind comes from (the regional northwest on every pool
    hamlet). research/contents.json#vegetation, "Shelter belts on a village's windward side": the record's shape is a hook on the windward
    side, one or two sides of the houses, never round them."""
    cx = sum(float(h["x"]) for h in houses) / len(houses)
    cy = sum(float(h["y"]) for h in houses) / len(houses)
    bx = sum(float(c[0]) for c in clumps) / len(clumps)
    by = sum(float(c[1]) for c in clumps) / len(clumps)
    off = abs((math.degrees(math.atan2(bx - cx, -(by - cy))) - math.degrees(math.atan2(wind[0], -wind[1])) + 180.0) % 360.0 - 180.0)
    angs = sorted(math.degrees(math.atan2(float(c[0]) - cx, -(float(c[1]) - cy))) % 360.0 for c in clumps)
    gap = max([b - a for a, b in zip(angs, angs[1:], strict=False)] + [angs[0] + 360.0 - angs[-1]])
    return off, 360.0 - gap


def trim_to_the_wind(clumps: list[tuple[float, float]], houses: Any, wind: tuple[float, float]) -> list[tuple[float, float]]:
    """The belt's seats with END crowns taken off until it bears within `BELT_BEARING_MAX_DEG` of the wind's quarter and
    subtends at most `BELT_SUBTENSE_MAX_DEG` round the cluster (feature 287, woods W18 - repaired where it is planted, not
    checked after). The ends are the two crowns either side of the widest angular gap round the cluster, and the one lying
    farther round from the wind's bearing goes first: that shortens the hook and draws the belt's center toward the wind at
    once, and it never opens a hole inside a run, so the depth and the continuity of what stays are untouched. Converges -
    at worst on the crowns nearest the wind's bearing, the belt's middle stretch (a single crown subtends nothing).

    ...AND WHERE THAT CONVERGES OFF THE WIND, NO BELT (feature 287, woods W18): the crown nearest the wind's bearing is never
    the end taken off (the other end lies farther round), so the one crown the loop can converge on is that one - and where
    even it bears more than `BELT_BEARING_MAX_DEG` off, no crown stands in the wind's quarter at all. It was returned as it
    stood, the one way the trim left the rule broken; a belt with nothing on the wind is no windbreak, so none is kept.
    Research: belt trimmed to a windward hook - research/questions/0072-shelter-belts-on-a-villages-windward-side-bofurin.drawing.html: end crowns off, or no belt"""
    if not houses:
        return list(clumps)
    out = _trim_ends(clumps, houses, wind)
    off, sub = belt_bearing_and_subtense(out, houses, wind) if out else (0.0, 0.0)
    return out if off <= BELT_BEARING_MAX_DEG and sub <= BELT_SUBTENSE_MAX_DEG else []


def _trim_ends(clumps: Sequence[tuple[float, float]], houses: Any, wind: tuple[float, float]) -> list[tuple[float, float]]:
    """`trim_to_the_wind`'s end-crown loop: the ends off until the belt bears on the wind as a hook, or one crown is left."""
    out = list(clumps)
    cx = sum(float(h["x"]) for h in houses) / len(houses)
    cy = sum(float(h["y"]) for h in houses) / len(houses)
    home = math.degrees(math.atan2(wind[0], -wind[1])) % 360.0
    while len(out) > 1:
        off, sub = belt_bearing_and_subtense(out, houses, wind)
        if off <= BELT_BEARING_MAX_DEG and sub <= BELT_SUBTENSE_MAX_DEG:
            break
        ang = sorted(((math.degrees(math.atan2(c[0] - cx, -(c[1] - cy))) % 360.0, k) for k, c in enumerate(out)))
        gaps = [(ang[(i + 1) % len(ang)][0] - ang[i][0]) % 360.0 for i in range(len(ang))]
        i = max(range(len(ang)), key=lambda j: gaps[j])
        ends = (ang[i][1], ang[(i + 1) % len(ang)][1])  # the last crown before the widest gap, and the first after it
        far = max(ends, key=lambda k: abs((math.degrees(math.atan2(out[k][0] - cx, -(out[k][1] - cy))) - home + 180.0) % 360.0 - 180.0))
        del out[far]
    return out


def deep_marsh(rings: Any, margin: float) -> list[list[tuple[float, float]]]:
    """The marsh deeper than its reed margin: each ring inset by `margin` (feature 287, woods W06). Woody cover stands on
    the dry ground above the marsh and its reed MARGIN carries alder (research/contents.json#vegetation, Reed beds and the marsh's edge), so a
    grove clump may be based in the margin - drawn as alder - and never deeper. A ring the inset empties has no deep
    ground; a ring the inset splits gives each piece.
    Research: belt no deeper than the reed margin - research/questions/0074-reed-beds-and-the-marshs-edge-yoshihara.drawing.html: alder in the margin only"""
    from shapely.geometry import Polygon

    out: list[list[tuple[float, float]]] = []
    for ring in rings:
        if len(ring) < 3:
            continue
        g = Polygon([(float(q[0]), float(q[1])) for q in ring]).buffer(0).buffer(-margin)
        out += [[(float(x), float(y)) for x, y in part.exterior.coords[:-1]] for part in getattr(g, "geoms", [g]) if part.geom_type == "Polygon" and not part.is_empty]
    return out


def reserved_seat_keepouts(seats: Sequence[tuple[float, float]], clump: float, bs: float) -> list[tuple[float, float, float]]:
    """THE ONE PREDICATE of a grove leaving a reserved copse seat free (feature 287, woods W25), as keep-out discs: a clump
    of `clump` stands off each seat by the copse's own displacement test (`village_grove`'s `occ_grove`: the other grove's
    recorded radius plus 0.9 of the copse's clump), `BAR_MARGIN_PX` stricter, so the copse finds the seat undisplaced.

    Research:
        its salts, guards and sentinels - NONE: they decide nothing about the place - 0.9 (mirrors the copse's own displacement test (the 0.90 is SEARCHED-SILENT at wood_share:197))
    """
    from .wood_share import BAR_MARGIN_PX, COPSE_CLUMP_BS

    r = round(clump / 2, 1) + COPSE_CLUMP_BS * bs * 0.90 + BAR_MARGIN_PX
    return [(float(x), float(y), r) for x, y in seats]


class StandsMixin:
    def bamboo_stand(self: Settlement, poly: Any, role: str = "homestead") -> int:  # type: ignore[misc]
        """A BAMBOO STAND - a take-yabu: a clonal thicket with a hard edge, drawn as a STAND-LEVEL glyph
        (feature 133 T47, GM 2026-08-27; research/questions/0075-bamboo-groves-chikurin.html;
        research/questions/0075-bamboo-groves-chikurin.drawing.html).

        THE GLYPH IS A MAP DRAWING CONVENTION (feature 183's word; it read DEVIATION until the GM split the two), recorded like the oversized wellhead: a culm is
        inches across and cannot be drawn at 1 px = 1 ft, so the stand's POSITION and EXTENT (`poly`) are to
        scale and the marks inside it are symbolic - the convention Japan's own GSI topographic legend uses,
        a distinct bamboo-grove symbol beside the broadleaf and conifer ones, so a reader can tell the three
        apart at map scale. Each mark is a pair of culm strokes with a leafy fork, in bamboo's pale
        yellow-green, on a jittered grid dense enough to read as one block at fit zoom - laid once in the bamboo tile and the
        stand's ring filled with it (feature 298); no solid fill, per the no-solid-fill rule for cover. `role` is "homestead" (a strip beside a farmstead that keeps one) or
        "thicket" (the take-yabu behind the back row). Recorded in M['bamboo_stands'] (bbox + role + poly);
        the marks are decoration keyed to the stand (positional randomness).
        Research: bamboo stand glyph - research/questions/0075-bamboo-groves-chikurin.drawing.html: area to scale, culm marks a convention on a 7 bscale grid
            its drawn sizes - CONVENTION: sizes on the sheet, not in the world - 0.86 (staggered row step of the glyph grid); 0.6 (jitter of the glyph grid (0075 drawing))
            its salts, guards and sentinels - NONE: they decide nothing about the place - 91 (salts); 92 (salts)
        """
        pts = [(float(a), float(b)) for a, b in poly]
        xs, ys = [q[0] for q in pts], [q[1] for q in pts]
        x0, x1, y0, y1 = min(xs), max(xs), min(ys), max(ys)
        bs = self.bscale
        step = 7.0 * bs
        n = 0
        y = y0 + step * 0.5
        row = 0
        while y < y1:  # the stand's size in marks: the seats of its jittered grid inside the ring (`marks` on the record)
            x = x0 + step * (0.5 if row % 2 == 0 else 1.0)
            while x < x1:
                jx, jy = x + (self._hjit(x, y, 91.0) - 0.5) * step * 0.6, y + (self._hjit(x, y, 92.0) - 0.5) * step * 0.6
                n += point_in_poly(jx, jy, pts)
                x += step
            y += step * 0.86
            row += 1
        if n == 0:
            return 0
        # THE MARKS ARE A TILE (feature 298, the GM 2026-10-01 - bamboo "is too small to show up on these maps", so "would we be
        # able to use a similar approach here?"): the stand's ring filled with the bamboo tile (`land.tiles.bamboo_tile`, the
        # same mark on the same grid), at the stand's own place in the stack, where its marks were drawn
        self._cover_kinds.add(("bamboo", bs))
        d = "M" + "L".join(f"{a:.1f},{b:.1f}" for a, b in pts) + "Z"
        g = [f'<g class="bamboo"><path d="{d}" fill="url(#{pattern_id("bamboo", bs)})"/></g>']
        z = self.add("".join(g), cls="homestead bamboo" if role == "homestead" else "shared bamboo grove")  # feature 150
        self.M.setdefault("bamboo_stands", []).append(
            {
                "x": round((x0 + x1) / 2, 1),
                "y": round((y0 + y1) / 2, 1),
                "w": round(x1 - x0, 1),
                "h": round(y1 - y0, 1),
                "rot": 0,
                "role": role,
                "z": z,
                "marks": n,
                "poly": [[round(a, 1), round(b, 1)] for a, b in pts],
            }
        )
        return n

    def village_grove(  # type: ignore[misc]
        self: Settlement,
        poly: Any,
        role: str = "windbreak",
        dense: bool = True,
        within: tuple[float, float, float, float] | None = None,
        face_margin: float | None = None,
        reserved: tuple[float, float, float, float] | None = None,
        near: tuple[Any, ...] | None = None,
        area: float | None = None,
        area_from: Callable[[float, float], float] | None = None,
        wind: tuple[float, float] | None = None,
        page: Callable[[list[tuple[float, float]]], tuple[float, float, float, float]] | None = None,
        reach: float | None = None,
        seats: Sequence[tuple[float, float]] | None = None,
        keep_off: Sequence[tuple[float, float]] | None = None,
        seat_near: tuple[Any, ...] | None = None,
        bamboo_rings: Sequence[Any] = (),
    ) -> int:
        """A COMMUNAL village grove - the Chinese *fengshui* forest (风水林). Unlike the per-house *yashikirin*,
        a NUCLEATED village shelters behind ONE village-scale grove, in three roles (see research/questions/0071-groves-around-a-southern-chinese-village-the-fengshui-woods-fengshuilin-and-the-dooryard-copse.drawing.html, research/questions/0072-shelter-belts-on-a-villages-windward-side-bofurin.drawing.html):
          - `windbreak` - the dense belt on the WINDWARD/high BACK edge (后龙林 back-village grove); the winter-
            monsoon wall and the LARGEST vegetation feature. Nestles against and EMBRACES the cluster.
          - `water_mouth` - a smaller cluster of big old trees at the LOW entrance / water-mouth (水口林);
          - `copse` - the leafy bamboo / fruit-tree greenery scattered through the OPEN gaps among the houses.
        `poly` is the grove's FOOTPRINT - an IRREGULAR, terrain-following outline, NOT a rectangle (real groves hug the land and wrap the
        settlement, they are not ruled walls). It is FILLED with dense mixed-stand clumps on a jittered grid; a clump is SKIPPED wherever it would land
        on a HOUSE / threshing YARD / GARDEN / PADDY (so the wood settles into the open ground and hugs the cluster without ever drawing trees on a
        building or out in the crops - this is what lets the belt nestle right up to the village edge). `dense=True` packs overlapping clumps into a
        continuous belt/cluster; `dense=False` scatters them for the leafy fringe among houses. role tunes the species mix (windbreak/water_mouth =
        conifer-backed forest; copse = fruit and other broadleaf, no bamboo, no conifer). Recorded in M['village_groves'] (bbox + role + poly) IF any clump is drawn (a footprint entirely over houses/crops draws nothing and records nothing). `area` (px^2) is the canopy
        the stand is filled TO: seating stops once its clumps cover it, and a second pass offers more seats where the first
        fell short (269 B26, the copse sized by the homesteads' woods); `area_from`, given instead, fills to the ground's capacity
        and trims back to the goal it returns for that capacity and the reserved seats' canopy (feature 294 B9, `wood_goal`). `wind` (toward where the wind comes from), given for the
        windbreak, trims the belt's ends until it bears on the wind's quarter as a hook (`trim_to_the_wind`). `seats` are the households' reserved shares
        of the wood floor (feature 287, woods W25; `wood_share`), planted FIRST, each through the same rejection chain but `near`, and never dropped as a
        straggler; a seat's reach is its household's - the dooryard copse's, `seat_near` (points, reach, the brook's reaches: a house within reach on the
        seat's own bank) - asked of the seat as planted and again of any re-seat, where `near` is the siting's (feature 287, woods W02 and W25: the
        reservation reserved it within reach, and a seat moved round another grove's crown is asked again rather than trusted); `keep_off` are those
        seats for a grove that must leave them free (`reserved_seat_keepouts`). Returns the count.

        Research:
            three groves - research/questions/0071-groves-around-a-southern-chinese-village-the-fengshui-woods-fengshuilin-and-the-dooryard-copse.drawing.html: the back grove, the water-mouth grove and the dooryard copse
            clump grid - GUESS: searched, the record silent (feature 417 T36 pass P1, 2026-10-25); a 20 or 32 bscale step, clumps 28 or 22 bscale units
            clump inside the page window - CONVENTION: a clump kept only where some of its drawn crowns fall inside the page - a clump's crowns are drawn out to 0.9 of a clump from its seat (`_draw_grove`; the keep-outs' "a DRAWN crown runs to ~1.03 x clump"), so a seat up to 0.9 of a clump past the edge is kept
            copse mix - research/questions/0036-groves-of-trees-around-farmhouses-yashikirin.drawing.html: the dooryard mix, fruit and broadleaf, no bamboo or conifer
            water-mouth grove drawn in the conifer-backed windbreak mix - research/questions/0071-groves-around-a-southern-chinese-village-the-fengshui-woods-fengshuilin-and-the-dooryard-copse.html: big old trees, Huangling's mainly yew; the village belt takes the same mix, drawn in its rolled form (`grove_fill.ink_and_record_grove`)
            clumps kept apart - GUESS: no source could speak to it, a value of ours (feature 417 T36 pass P1, 2026-10-25); a re-seat 0.55 of a grid step from any clump down, a gap-fill seat and the grid's own seats half a clump from a seat taken or reserved
            copse filled to the homesteads' wood - research/questions/0036-groves-of-trees-around-farmhouses-yashikirin.drawing.html: reserved seats first, then the grid
            no wind declared - research/questions/0072-shelter-belts-on-a-villages-windward-side-bofurin.drawing.html: the regional northwest (every map takes it unless its spec declares a local wind); a hamlet always passes its plan's wind
            belt a windward hook - research/questions/0072-shelter-belts-on-a-villages-windward-side-bofurin.drawing.html: ends trimmed to the wind's quarter
            belt deep and whole - research/questions/0072-shelter-belts-on-a-villages-windward-side-bofurin.drawing.html: interior gaps over `_BELT_GAP_FT`, 30 ft at every grain, filled
            clumps off lanes - research/questions/0072-shelter-belts-on-a-villages-windward-side-bofurin.drawing.html: where a lane crosses the belt the planting resumes on both sides
            copse stragglers dropped to its stocking - GUESS: no source could speak to it, a value of ours (feature 417 T36 pass P1, 2026-10-25); `stocked_copse` drops the farthest clumps until the copse holds half a clump plus 4 px
            its search steps and tolerances - GUESS: no source could speak to it, a value of ours (feature 417 T38 pass N9, 2026-10-25) - 0.25 (refill grid offsets); 0.75 (refill grid offsets)
            its salts, guards and sentinels - NONE: they decide nothing about the place - 21 (salt); 0.7071 (northwest wind fallback; the caller always passes the wind); 23 (salt); 24 (salt)
        """
        xs = [p[0] for p in poly]
        ys = [p[1] for p in poly]
        x0, x1, y0, y1 = min(xs), max(xs), min(ys), max(ys)
        mix = "windbreak" if role in ("windbreak", "water_mouth") else "dooryard"
        bs = self.bscale
        # 32, NOT 52, FOR A SPARSE STAND (feature 152 T09). A copse's job is to fill the gaps AMONG the
        # homesteads, and a 52 ft grid cannot see a 30 ft gap: Inashiro drew 2 clumps in a 98 x 313 ft
        # record and Mizuguchi 2 in a 205 x 58 one - two stray bushes recorded as a wood. The grid is the
        # only thing that decides where a clump is even TRIED, so a stand that has to thread a dense
        # cluster needs a finer one. It stays well coarser than the belt's 20 ft, which is what keeps a
        # copse reading as scattered trees rather than the canopy the windbreak draws.
        step = (20 if dense else 32) * bs
        clump = (28 if dense else 22) * bs
        cr = clump / 2
        blocks = grove_blocks(self, poly, role, clump, keep_off, reserved, bamboo_rings)
        # the clumps seated so far, filed as they land: the re-seat search keeps `step * 0.55` off the
        # ROUNDED clumps and the gap fill keeps half a crown off the unrounded seats, as each always did
        near_clumps, near_seats = Seats(step * 0.55), Seats(clump * 0.5)
        # `near`: (points, reach) - a clump stands only within `reach` of one of the points (feature 261: the dooryard
        # copse within a dooryard of a house, the against-the-belt copse at the belt's back). One index, asked per clump.
        _near: Seats | BankNear | None = None
        if near is not None and len(near) > 2:
            _near = BankNear(near[0], near[1], near[2])  # type: ignore[misc]
        elif near is not None:
            _near = Seats(near[1])
            for _p in near[0]:
                _near.add(float(_p[0]), float(_p[1]))
        # `seat_near`: the reserved seats' own reach - the dooryard copse's, a house within reach on the seat's bank (W25)
        _seat_near = BankNear(seat_near[0], seat_near[1], seat_near[2]) if seat_near is not None else None

        nx, ny = max(1, round((x1 - x0) / step)), max(1, round((y1 - y0) / step))
        clumps: list[Any] = []
        seated: list[tuple[float, float]] = []  # unrounded seats, inked after the face trim below
        canopy = CanopyArea(2.0 * bs)  # the ground the seated clumps cover, for an `area` goal (269 B26)
        if area_from is not None:  # fill to the ground's capacity; the goal is decided from it below (feature 294 B9, `wood_goal`)
            area = math.inf

        def _goal_met() -> bool:
            return area is not None and canopy.area >= area

        # the reserved seats (woods W25): a clump of the grove's own grid keeps half a crown off each, as the gap fill keeps
        # off a clump already down, so no crown is stacked on a household's share
        held: Seats | None = None
        if seats:
            held = Seats(clump * 0.5)
            for _p in seats:
                held.add(round(float(_p[0]), 1), round(float(_p[1]), 1))

        def _seat(jx: float, jy: float, reserved: bool = False) -> None:
            """One grid seat through the rejection chain: a HARD blocker drops it, a LOCAL one re-seats it (see below).
            DECIDED AT THE RECORD'S GRAIN (feature 287, woods W01, W03, W05): the seat is rounded to the 0.1 px the manifest
            records before any test is asked of it, so the point every rule reads - the reach, the bank, the marsh, the alder -
            is the point the placer admitted, and no margin stands in for the rounding. A `reserved` seat is a household's
            share of the wood floor: its reach is its household's (`seat_near`) rather than the siting's `near` - asked of it
            here and of its re-seat alike, so a seat is never planted past the reach it was reserved within - and the
            grid's other seats keep off it (`held`)."""
            jx, jy = round(jx, 1), round(jy, 1)
            _reach = _seat_near if reserved else _near
            _far = (
                (lambda x, y: _reach is not None and not _reach.too_near(x, y))
                if reserved
                else (lambda x, y: (_near is not None and not _near.too_near(x, y)) or (held is not None and held.too_near(x, y)))
            )
            # THE FILL'S REGIONS DECIDE (feature 297, plan B3): which family holds the ground, if any - and a household's reserved seat,
            # which the seating proved clear, is asked of the exact families (the regions' margin refused one, woods W25 - R16)
            _by = blocks.exact_taken_by(jx, jy) if reserved else blocks.taken_by(jx, jy)
            if _by == "hard" or _far(jx, jy):
                return
            if _by is not None:
                _alt = reseat_clump(blocks, near_clumps, dense, step, clump, within, jx, jy, _by != "local", _reach, reserved)
                if _alt is None:
                    return
                jx, jy = round(_alt[0], 1), round(_alt[1], 1)
                if not (blocks.exact_clear if reserved else blocks.static_clear)(jx, jy) or _far(jx, jy):
                    return  # the re-seat's point, at the record's grain, is asked again - a rounding can carry it over an edge
            seated.append((jx, jy))
            clumps.append([round(jx, 1), round(jy, 1)])
            near_seats.add(jx, jy)
            near_clumps.add(round(jx, 1), round(jy, 1))
            canopy.add(jx, jy, cr)

        # THE HOUSEHOLDS' RESERVED SHARES STAND FIRST (feature 287, woods W25; plan D9): each seat the seating reserved for a
        # household's share of the wood floor is planted before the grid offers a single seat, so no goal the grid fills to
        # and no clump of its own can take the seat's ground first, and the stragglers' drop below never takes one out.
        for _p in seats or ():
            _seat(float(_p[0]), float(_p[1]), reserved=True)
        kept = frozenset(seated)
        for iy in range(ny + 1):
            for ix in range(nx + 1):
                gx = x0 + ix * (x1 - x0) / nx
                gy = y0 + iy * (y1 - y0) / ny
                jx = gx + (self._hjit(gx, gy, 21.0) - 0.5) * step  # jitter the grid so the stand + its edge read ragged
                jy = gy + (self._hjit(gx, gy, 22.0) - 0.5) * step
                if not blocks.inside(jx, jy):
                    continue
                # ...AND NOT WHOLLY OFF THE PAGE, when the caller gives a `within`. ONLY wholly - a
                # clump whose crown merely CROSSES the frame edge is kept, and that is doctrine, not
                # leniency: `research/contents.json#map-conventions` (GM 2026-07-20) says the belt CLIPS at the
                # view edge and "a partially visible belt reads as 'the wood continues'", which is
                # why `hard_features_within_frame` demands partial visibility of a village grove
                # rather than containment. Only a clump with NO visible ink is waste.
                #
                # THE FIRST VERSION INSET THE WINDOW INSTEAD, AND THAT WAS BACKWARDS - recorded
                # because it shipped and two independent reviews caught it. Requiring the whole crown
                # inside (`within[2] - 0.9*clump`) deleted every clump the edge merely touched, and on
                # Mizuguchi that traded 3 invisible clumps for 40 dropped ones - 37 of them at least
                # partly visible, 12 not touching the frame at all - punching a ~100 ft bare channel
                # through the middle of the wind wall on the windward side. Sawada lost 46% of its
                # canopy the same way. The earlier review that asked for "58 clumps touching the
                # frame" to be fixed was itself against the presentation doctrine above; the only
                # real defect was the 23 with no ink on the page.
                if within is not None and (jx + clump * 0.9 < within[0] or jx - clump * 0.9 > within[2] or jy + clump * 0.9 < within[1] or jy - clump * 0.9 > within[3]):
                    continue
                # A DENSE BELT FLOWS AROUND AN OBSTACLE INSTEAD OF LOSING THE COLUMN (settlement-review,
                # Inashiro 2026-08-18). `occ` keeps a clump off a house, a yard, a byre and - the case
                # that bit - a WELLHEAD, whose keep-out is the widest of the lot (`vr + 0.9*clump`,
                # because a well lost under the canopy reads wrong). A wellhead seated inside the belt
                # therefore deleted every clump around it, and the belt acquired a zero-canopy latitude
                # on its WINDWARD side - a hole straight through the wind wall, which is the one thing
                # a windbreak exists not to have. Measured on Inashiro: the 40 ft band at y1360-1400
                # went 8 clumps -> 1, in a 930 ft run that had never had a gap.
                #
                # Fixing it at the WELL was tried first and is the wrong lever - recorded because it
                # shipped for a moment. Ranking "not in the belt" ahead of coverage in the well
                # tie-break closed Inashiro's hole and cost Mizuguchi 61 ft of worst walk, on a map
                # whose own belt hole turned out not to be well-caused at all. The belt is what should
                # give: a real planted windbreak is not laid out on a grid and abandoned where a shed
                # stands, it is planted around the shed.
                #
                # So a blocked clump in a DENSE grove gets a short re-seat search before it is
                # dropped, and only for `occ` - a clump refused by the CROP, open WATER or a LANE is
                # refused for a reason that re-seating does not change, and those are the edges where
                # a belt is supposed to stop. The nudge re-asks every other test, and keeps its
                # distance from the clumps already down so a re-seat cannot just pile up on its
                # neighbor.
                # ONE rejection chain, three nudge blocks folded into it (2026-08-19). A HARD blocker
                # (crop, water, dike) drops the clump - those are edges a belt stops at. A LOCAL one
                # (a house, a yard, a wellhead, a lane, a sun corridor) gets a short re-seat search,
                # because a planted belt is planted AROUND a shed rather than abandoned at it. Three
                # separate causes have now punched holes in a wind wall here - a wellhead inside the
                # belt, a peer session's lane crossing it, and a threshing yard's sun corridor - and
                # each was fixed with its own ad-hoc nudge until the third made the pattern obvious.
                if _goal_met():
                    continue  # the copse has its homesteads' wood (269 B26): the rest of the grid stays open ground
                _seat(jx, jy)
        # ...AND A COPSE IS FILLED TO THE HOMESTEADS' WOOD, not left at what one grid's gaps gave (269 B26;
        # research/questions/0036-groves-of-trees-around-farmhouses-yashikirin.drawing.html: each homestead that keeps a wood has ~6,000-28,000 sq ft of trees, its windward grove
        # and its share of the copse together). The grid above tries one seat a `step`; where it falls short of `area`,
        # the grid is offered again at its three half-step offsets, each seat asking every test the first pass asked.
        # Nothing is relaxed: a copse the ground cannot hold stays short, and the caller records by how much.
        for _ox, _oy in ((0.5, 0.0), (0.0, 0.5), (0.5, 0.5), (0.25, 0.25), (0.75, 0.25), (0.25, 0.75), (0.75, 0.75)) if area is not None else ():
            for iy in range(ny + 1):
                for ix in range(nx + 1):
                    if _goal_met():
                        break
                    gx = x0 + (ix + _ox) * (x1 - x0) / nx
                    gy = y0 + (iy + _oy) * (y1 - y0) / ny
                    jx = gx + (self._hjit(gx, gy, 23.0) - 0.5) * step
                    jy = gy + (self._hjit(gx, gy, 24.0) - 0.5) * step
                    if (
                        blocks.inside(jx, jy)
                        and not near_clumps.too_near(jx, jy)
                        and (within is None or not (jx + clump * 0.9 < within[0] or jx - clump * 0.9 > within[2] or jy + clump * 0.9 < within[1] or jy - clump * 0.9 > within[3]))
                    ):
                        _seat(jx, jy)
        # AND CLOSE THE INTERIOR HOLES (feature 152, acceptance review; the GM's own complaint in its
        # last form - "it's not clear that it will, in fact, be breaking much wind"). The grid decides
        # where a clump is TRIED, and where a try is refused the belt carries a hole: Kuwabata shipped
        # gaps of 73, 67 and 34 ft at 29%, 88% and 79% of the way ALONG its belt, and
        # `village_windbreak_is_continuous` failed on it - identically on main, so this is old.
        #
        # The rejection chain above deliberately does NOT re-seat a clump refused by the crop, open water
        # or a lane, on the grounds that those "are the edges where a belt is supposed to stop". That is
        # right at an END and wrong in the MIDDLE: a hole 29% of the way along is not the belt stopping.
        # So the run is walked once more along its own axis and each interior gap over `_BELT_GAP_FT` is
        # offered a seat at its midpoint, re-asking every test the loop asks. Nothing is relaxed - a gap
        # the ground truly refuses stays a gap.
        # ...and it SUBDIVIDES until the gap closes or the ground refuses. One clump at the midpoint turns
        # a 94 ft hole into two 47 ft holes, which is still a hole - measured on Kuwabata's first pass.
        close_belt_gaps(self, poly, role, seated, clumps, near_seats, near_clumps, blocks, within, clump, _near, _GAP_MEMORY)
        # THE FACE TRIM, then the ink (GM 2026-08-26, feature 133 T10). With `face_margin` the
        # caller says the frame will follow this belt's INNER FACE by that margin (`crop_boxes`
        # reads the same `windbreak_face`), so a clump whose whole crown lies deeper than
        # face + margin has no page to be seen on and is not inked - the same "only wholly off the
        # page" rule the `within` window applies on the other edges. Seating first and drawing
        # after is what makes this possible: the face is known only once every clump is down.
        # Draw order and positions are those of the seating loop, so nothing else moves.
        # THE PAGE IS THE PAGE, NOT A PROXY FOR IT (feature 152 T02, GM 2026-08-29: "it's not clear that
        # it will, in fact, be breaking much wind. Given how many houses appear uncovered"). A trim used to
        # run HERE, against the belt's own inner face plus `face_margin` - 48 ft - as a stand-in for the
        # page's windward edge. That proxy is right only when the belt is what sets that edge; whenever
        # other content (fields, marsh, a pond) holds the frame open wider, it under-estimates the page and
        # deletes canopy a reader can see. Measured over the pool against each map's FINAL `meta.view`:
        # Kashikawa discarded 61 clumps of which ALL 61 were wholly inside the rendered view, Kuwabata 21
        # of 45, Sawada 30 of 84 - and those three are exactly the maps with houses standing beyond their
        # belt's ends (8 of 20, 3 of 16, 8 of 19). Inashiro and Mizuguchi discarded only genuinely off-page
        # clumps and have no house beyond the belt. The belt was not too short: a third of it was being
        # thrown away on the page it belongs to.
        #
        # The trim is not gone - it MOVED to `Settlement.set_view`, the first moment the real page is
        # known. Everything the `within` window admits is drawn here (ink past the page is clipped by the
        # render, which is the documented behavior for a communal grove - see the note at `set_view`'s
        # frame list), and the RECORD is partitioned against the actual view once there is one. (The `_offpage` list this
        # trim left behind, empty ever since, is gone with it - feature 287, woods W20.)
        # THE BELT BEARS ON THE WIND'S QUARTER AS A HOOK, repaired here, before a crown is inked (feature 287, woods W18):
        # its end crowns are taken off until its center bears within 45 degrees of the wind and it subtends no more than 200
        # round the houses (`trim_to_the_wind`, asked by the same predicate the rule's test reads). A COPSE is held to its own
        # stocking the same way (woods W15): its stragglers are dropped until the extent it is recorded at holds its clumps.
        # ...AND, GIVEN THE PAGE IT WILL BE FRAMED TO, DEEP AND WHOLE ON IT (feature 287, woods W16-W19; plan D8): `page` answers
        # the view the crop takes with these crowns, and `settle_the_belt` trims the hook on the crowns that view shows,
        # deepens every thin stretch and closes every hole with seats this fill's own tests admit - up to 60 ft past the
        # band's far face - and ends the belt where none is admitted, so no rule is left to a check of the finished map.
        _houses = self.M.get("houses") or []
        if role == "windbreak" and page is not None and seated and _houses:

            def _settle_seat(x: float, y: float) -> tuple[float, float] | None:
                """A settling seat at the record's grain, through the gap fill's tests but the band's outline (the band is
                pushed back for a thin column), or None."""
                x, y = round(x, 1), round(y, 1)
                if within is not None and (x + clump * 0.9 < within[0] or x - clump * 0.9 > within[2] or y + clump * 0.9 < within[1] or y - clump * 0.9 > within[3]):
                    return None
                if not blocks.static_clear(x, y) or (_near is not None and not _near.too_near(x, y)) or near_seats.too_near(x, y):
                    return None
                near_seats.add(x, y)
                near_clumps.add(x, y)
                return (x, y)

            _ways = [ln.get("pts") or [] for ln in self.M.get("lanes") or []] + [st_.get("poly") or [] for st_ in self.M.get("streams") or []]
            _trim = (lambda cs: trim_to_the_wind(cs, _houses, wind)) if wind is not None else None
            seated = settle_the_belt(seated, r=round(clump / 2, 1), houses=_houses, wind=wind or (-0.7071, -0.7071), ways=_ways, page=page, band=poly, seat=_settle_seat, reach=reach, trim=_trim)
        elif role == "windbreak" and wind is not None and seated:  # one crown too: a lone crown off the wind is no belt (W18)
            seated = trim_to_the_wind(seated, _houses, wind)
        if role == "copse" and len(seated) > 1:
            seated = stocked_copse(seated, clump / 2 + 4.0, kept)
        if area_from is not None:  # ...and trimmed back to the goal the ground's capacity gives the roll (feature 294 B9)
            seated = trim_to_goal(seated, kept, cr, 2.0 * bs, area_from(canopy_of(seated, cr, 2.0 * bs), canopy_of([p for p in seated if p in kept], cr, 2.0 * bs)))
            seated = stocked_copse(seated, clump / 2 + 4.0, kept) if role == "copse" and len(seated) > 1 else seated
        return ink_and_record_grove(self, seated, poly, (x0, y0, x1, y1), role, mix, clump)
