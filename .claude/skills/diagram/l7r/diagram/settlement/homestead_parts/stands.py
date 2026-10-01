"""Split from settlement/homestead_parts.py by feature 173 - see this package's CLAUDE.md for the index."""

import math
from collections.abc import Callable, Sequence
from typing import TYPE_CHECKING, Any

from .._geom import CanopyArea, point_in_poly
from ..land.wet import MARSH_FEATHER_BS, marsh_ground
from ._helpers import _BELT_GAP_FT, _belt_axis
from .bamboo_keepout import copse_bamboo_reach, grown_ring
from .bamboo_keepout import stand_spares_seats as stand_spares_seats
from .belt_law import settle_the_belt
from .grove_blocks import BankNear, GroveBlocks, Seats
from .groves import RANK_JITTER_FT, bamboo_mark, crown_lift

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
    """THE ONE PREDICATE of "no tree is planted in a path" (`test_no_tree_is_planted_in_a_path`; feature 287, woods W21 and
    homes H43): a trunk at (x, y) stands on a lane's TREAD - within the lane's own half-width of its centerline, the width
    read from the lane (GM 2026-09-12: a trunk beside a footpath is what a path looks like; one inside it is a tree in the
    path). `lanes` are manifest lane records (`pts`, `w`)."""
    from .._geom import seg_dist

    return any(
        seg_dist(x, y, (float(a[0]), float(a[1])), (float(b[0]), float(b[1]))) < float(ln.get("w", 6)) / 2.0
        for ln in lanes
        for a, b in zip(ln.get("pts") or [], (ln.get("pts") or [])[1:], strict=False)
    )


BELT_BEARING_MAX_DEG = 45.0  # the belt's center within this of the wind's quarter, seen from the cluster's center
BELT_SUBTENSE_MAX_DEG = 200.0  # ...and its crowns round the cluster on one or two sides: a hook, never a ring


def belt_bearing_and_subtense(clumps: Any, houses: Any, wind: tuple[float, float]) -> tuple[float, float]:
    """THE ONE PREDICATE of `test_every_pool_hamlet_has_its_belt_on_the_regional_northwest` (feature 287, woods W18), as
    (how far the belt's center bears off the wind's quarter, how many degrees its crowns subtend round the cluster), both
    seen from the houses' centroid. `wind` points toward where the wind comes from (the regional northwest on every pool
    hamlet). research/vegetation, "Does a shelter belt wrap the settlement?": the record's shape is a hook on the windward
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
    stood, the one way the trim left the rule broken; a belt with nothing on the wind is no windbreak, so none is kept."""
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
    the dry ground above the marsh and its reed MARGIN carries alder (research/vegetation.html, the marsh margin), so a
    grove clump may be based in the margin - drawn as alder - and never deeper. A ring the inset empties has no deep
    ground; a ring the inset splits gives each piece."""
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
    recorded radius plus 0.9 of the copse's clump), `BAR_MARGIN_PX` stricter, so the copse finds the seat undisplaced."""
    from .wood_share import BAR_MARGIN_PX, COPSE_CLUMP_BS

    r = round(clump / 2, 1) + COPSE_CLUMP_BS * bs * 0.90 + BAR_MARGIN_PX
    return [(float(x), float(y), r) for x, y in seats]


def grove_stocked(clumps: Any, w: float, h: float, floor: float = 1.5) -> bool:
    """THE ONE PREDICATE of `test_every_recorded_grove_holds_trees` (feature 287, woods W15): a recorded grove holds at least
    `floor` clumps per 100,000 sq px of its recorded w x h - a grove that declares an extent and draws almost nothing in it
    leaves the dooryards it should have greened bare."""
    return w * h <= 0 or len(clumps) * 1e5 / (w * h) >= floor


def stocked_copse(clumps: list[tuple[float, float]], pad: float, kept: frozenset[tuple[float, float]] = frozenset()) -> list[tuple[float, float]]:
    """A copse's clumps with its stragglers dropped - the clump farthest from the clumps' centroid, one at a time - until
    the extent the copse is recorded at (its clumps' box grown by `pad`) is `grove_stocked` (feature 287, woods W15). It
    terminates: one clump's extent is a square of `2 * pad`, far above the floor. A clump in `kept` - a household's
    reserved share of the wood floor (woods W25) - is never a straggler: the drop stops when only kept clumps are left."""
    out = list(clumps)
    while len(out) > 1:
        xs, ys = [c[0] for c in out], [c[1] for c in out]
        if grove_stocked(out, max(xs) - min(xs) + 2 * pad, max(ys) - min(ys) + 2 * pad):
            break
        mx, my = sum(xs) / len(out), sum(ys) / len(out)
        loose = [k for k in range(len(out)) if out[k] not in kept]
        if not loose:
            break
        del out[max(loose, key=lambda k: math.hypot(out[k][0] - mx, out[k][1] - my))]
    return out


Box = tuple[float, float, float, float]


def grove_extent(clumps: Sequence[Sequence[float]], pad: float) -> Box:
    """The box (x0, y0, x1, y1) a grove's clumps span, grown by `pad` - the extent it is drawn at."""
    xs, ys = [float(c[0]) for c in clumps], [float(c[1]) for c in clumps]
    return (min(xs) - pad, min(ys) - pad, max(xs) + pad, max(ys) + pad)


def stocked_at_grain(clumps: Sequence[Sequence[float]], box: Box) -> bool:
    """`grove_stocked` over `box` as the record writes it (`record_box`: `w`, `h` to 0.1 px), so the rounding cannot tip a
    grove at the floor under it."""
    return grove_stocked(clumps, round(box[2] - box[0], 1), round(box[3] - box[1], 1))


def main_stand(clumps: Sequence[Sequence[float]], pad: float) -> list[Sequence[float]]:
    """The grove's MAIN STAND: its clumps split, while a part's extent (`grove_extent`) is not `grove_stocked`, across the
    widest gap along that extent's longer side, keeping the part with more clumps (the lower side on a tie). Terminates -
    each split keeps a nonempty proper part, and one clump's extent is a `2 * pad` square, far above the floor - and the
    part it returns is stocked in its own extent (feature 287, woods W15)."""
    part = list(clumps)
    while len(part) > 1:
        x0, y0, x1, y1 = grove_extent(part, pad)
        if stocked_at_grain(part, (x0, y0, x1, y1)):
            break
        k = 0 if x1 - x0 >= y1 - y0 else 1
        vals = sorted(float(c[k]) for c in part)
        cut = max(range(len(vals) - 1), key=lambda i: vals[i + 1] - vals[i])
        lo = [c for c in part if float(c[k]) <= vals[cut]]
        hi = [c for c in part if float(c[k]) > vals[cut]]
        part = lo if len(lo) >= len(hi) else hi
    return part


def stocked_box(clumps: Sequence[Sequence[float]], box: Box, pad: float) -> Box:
    """THE EXTENT A GROVE IS RECORDED AT, `grove_stocked` by construction (feature 287, woods W15 - the one predicate of
    `test_every_recorded_grove_holds_trees`): `box` where its clumps stock it - a windbreak's band, whose position is its
    meaning - else the extent its clumps are drawn at, else the extent of its main stand (`main_stand`), which its clumps
    stock since they include the stand's. A grove with no clump records no extent (a zero box at `box`'s center)."""
    if not clumps:
        cx, cy = (box[0] + box[2]) / 2.0, (box[1] + box[3]) / 2.0
        return (cx, cy, cx, cy)
    if stocked_at_grain(clumps, box):
        return box
    ext = grove_extent(clumps, pad)
    if stocked_at_grain(clumps, ext):
        return ext
    return grove_extent(main_stand(clumps, pad), pad)


def record_box(g: dict[str, Any], box: Box) -> None:
    """Write `box` (x0, y0, x1, y1) into a grove record's `x`, `y`, `w`, `h`, at the record's grain."""
    g["x"], g["y"] = round((box[0] + box[2]) / 2, 1), round((box[1] + box[3]) / 2, 1)
    g["w"], g["h"] = round(box[2] - box[0], 1), round(box[3] - box[1], 1)


class StandsMixin:
    def bamboo_stand(self: Settlement, poly: Any, role: str = "homestead") -> int:  # type: ignore[misc]
        """A BAMBOO STAND - a take-yabu: a clonal thicket with a hard edge, drawn as a STAND-LEVEL glyph
        (feature 133 T47, GM 2026-08-27; research/vegetation.html "Bamboo: how common, where it stood, and
        how to show it").

        THE GLYPH IS A MAP DRAWING CONVENTION (feature 183's word; it read DEVIATION until the GM split the two), recorded like the oversized wellhead: a culm is
        inches across and cannot be drawn at 1 px = 1 ft, so the stand's POSITION and EXTENT (`poly`) are to
        scale and the marks inside it are symbolic - the convention Japan's own GSI topographic legend uses,
        a distinct bamboo-grove symbol beside the broadleaf and conifer ones, so a reader can tell the three
        apart at map scale. Each mark is a pair of culm strokes with a leafy fork, in bamboo's pale
        yellow-green, on a jittered grid dense enough to read as one block at fit zoom; nothing is filled,
        per the no-solid-fill rule for cover. `role` is "homestead" (the damp N/W strip of the cluster) or
        "thicket" (the take-yabu at the field margin). Recorded in M['bamboo_stands'] (bbox + role + poly);
        the marks are decoration keyed to the stand (positional randomness)."""
        pts = [(float(a), float(b)) for a, b in poly]
        xs, ys = [q[0] for q in pts], [q[1] for q in pts]
        x0, x1, y0, y1 = min(xs), max(xs), min(ys), max(ys)
        bs = self.bscale
        g = ['<g class="bamboo">']
        step = 7.0 * bs
        n = 0
        y = y0 + step * 0.5
        row = 0
        while y < y1:
            x = x0 + step * (0.5 if row % 2 == 0 else 1.0)
            while x < x1:
                jx, jy = x + (self._hjit(x, y, 91.0) - 0.5) * step * 0.6, y + (self._hjit(x, y, 92.0) - 0.5) * step * 0.6
                if point_in_poly(jx, jy, pts):
                    g.append(bamboo_mark(jx, jy, bs, self._hjit(x, y, 93.0), self._hjit(x, y, 94.0)))  # a mark 5-8 ft tall: legible, not a tree
                    n += 1
                x += step
            y += step * 0.86
            row += 1
        g.append("</g>")
        if n == 0:
            return 0
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
        wind: tuple[float, float] | None = None,
        page: Callable[[list[tuple[float, float]]], tuple[float, float, float, float]] | None = None,
        reach: float | None = None,
        seats: Sequence[tuple[float, float]] | None = None,
        keep_off: Sequence[tuple[float, float]] | None = None,
        seat_near: tuple[Any, ...] | None = None,
        bamboo_rings: Sequence[Any] = (),
    ) -> int:
        """A COMMUNAL village grove - the Chinese *fengshui* forest (风水林). Unlike the per-house *yashikirin*,
        a NUCLEATED village shelters behind ONE village-scale grove, in three roles (see research/vegetation.html 'What are the village's three groves' 'Village
        windbreak'):
          - `windbreak` - the dense belt on the WINDWARD/high BACK edge (后龙林 back-village grove); the winter-
            monsoon wall and the LARGEST vegetation feature. Nestles against and EMBRACES the cluster.
          - `water_mouth` - a smaller cluster of big old trees at the LOW entrance / water-mouth (水口林);
          - `copse` - the leafy bamboo / fruit-tree greenery scattered through the OPEN gaps among the houses.
        `poly` is the grove's FOOTPRINT - an IRREGULAR, terrain-following outline, NOT a rectangle (real groves
        hug the land and wrap the settlement, they are not ruled walls). It is FILLED with dense mixed-stand
        clumps on a jittered grid; a clump is SKIPPED wherever it would land on a HOUSE / threshing YARD /
        GARDEN / PADDY (so the wood settles into the open ground and hugs the cluster without ever drawing trees
        on a building or out in the crops - this is what lets the belt nestle right up to the village edge).
        `dense=True` packs overlapping clumps into a continuous belt/cluster; `dense=False` scatters them for the
        leafy fringe among houses. role tunes the species mix (windbreak/water_mouth = conifer-backed forest;
        copse = bamboo + fruit, no conifer). Recorded in M['village_groves'] (bbox + role + poly) IF any clump
        is drawn (a footprint entirely over houses/crops draws nothing and records nothing). `area` (px^2) is the canopy
        the stand is filled TO: seating stops once its clumps cover it, and a second pass offers more seats where the first
        fell short (269 B26, the copse sized by the homesteads' woods). `wind` (toward where the wind comes from), given for the
        windbreak, trims the belt's ends until it bears on the wind's quarter as a hook (`trim_to_the_wind`). `seats` are the
        households' reserved shares of the wood floor (feature 287, woods W25; `wood_share`), planted FIRST, each through the
        same rejection chain but `near`, and never dropped as a straggler; a seat's reach is its household's - the dooryard
        copse's, `seat_near` (points, reach, the brook's reaches: a house within reach on the seat's own bank) - asked of the
        seat as planted and again of any re-seat, where `near` is the siting's (feature 287, woods W02 and W25: the
        reservation reserved it within reach, and a seat moved round another grove's crown is asked again rather than
        trusted); `keep_off` are those seats for a grove that must leave them free (`reserved_seat_keepouts`). Returns the
        count."""
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
        # never draw a clump ON a home/yard/garden/byre/kura: keep the clump CENTER clear by the footprint's
        # circumscribing radius PLUS the clump's own drawn radius (clump/2) and a hair - so the tree blob settles
        # BESIDE the building, touching at most (grove_clumps_clear_of_structures gates it). (A grove may still hug
        # the eaves visually; the blob edge just may not cross the wall.) Was 0.35*clump - too small by ~0.15*clump,
        # which let a blob corner clip a small house.
        occ = [
            (o["x"], o["y"], 0.5 * math.hypot(o["w"], o["h"]) + clump * 0.5 + 2)
            for k in ("houses", "threshing_yards", "gardens", "byres", "farm_sheds", "retirement_houses")
            for o in self.M.get(k, [])
        ]
        # a WELL is a clean draw-point: no tree CANOPY may reach the wellhead (a well lost under the grove reads
        # wrong - wells_clear_of_trees gates it). Keep-out = the well's DRAWN half-size (vr) + the canopy reach
        # (~0.9*clump, as for a shrine), NOT the tight 0.35*clump a homestead eave gets. (o["r"] is the recorded
        # clearance radius; the DRAWN wellhead is vr, which is what a crown must not overhang.)
        occ += [
            (o["x"], o["y"], o.get("vr", o["r"]) + clump * 1.05 + 1.0) for o in self.M.get("wells", [])
        ]  # 1.05, not 0.90 (feature 145): a DRAWN crown runs to ~1.03 x clump (Kashikawa: 14.4 on a 14 clump reached a well 25.4 px away, vr 12.4), and the check measures the drawn crown
        # ...and NOT the notice board, which no longer exists when this runs (GM 2026-08-29). This
        # list used to give the kosatsuba a `30.0 + clump * 0.90` keep-out - about 55 ft, larger than
        # a well's and larger than a shrine's - so that a clump could not swallow the board or pierce
        # its caption. Two things retired it. The board is now the LAST thing placed on a hamlet, so
        # `M["kosatsuba"]` is empty here and the entry could only ever have matched nothing; and the
        # GM has ruled the clearing itself wrong: "it would be very easy to put the notice board at
        # the edge of the forest. We could even display it as being underneath the canopy because I
        # think in many cases it would be ... humans would not need to clear any amount of space in
        # order to put up a notice board at the side of a path." A village drives a plank in beside a
        # way; it does not fell 9,500 sq ft of its own shelter wood to do it. What protects the board
        # now is that it is sited last and can see the trees, not that the trees were kept off it.
        # A SHRINE and its TORII sit in a CLEAN clearing: no tree CANOPY may reach them (a hall/arch lost in the
        # wood reads wrong - shrine_clear_of_grove_trees / torii_clear_of_grove_trees gate it). The DRAWN canopy
        # overhangs the nominal clump radius (crowns spill past clump/2), reaching ~0.85*clump from the clump
        # center - so the keep-out uses that reach + a hair (0.90*clump), NOT the 0.35*clump a homestead uses
        # (there a grove may hug the eaves). A torii is recorded as [x, y, z]; glyph spans x +/-19, y -10..+18.
        occ += [(o["x"], o["y"], 0.5 * math.hypot(o["w"], o["h"]) + clump * 0.90) for k in ("religious", "shrines") for o in self.M.get(k, [])]
        occ += [(t[0], t[1] + 4, math.hypot(19, 14) + clump * 0.90) for t in self.M.get("torii", [])]
        # ... and OFF the fengshui CRESCENT POND (GM 2026-07-21): no tree canopy may cross the half-moon
        # pond's water (trees_clear_of_fengshui_ponds gates it). The keep-out circle spans the FULL disk
        # (radius r + canopy reach) even though the water is only the away-facing half - the flat side toward
        # the village is the pond's open FORECOURT (the banyuetang fronted the settlement's ceremony/work
        # ground), so keeping the copse fringe off that band too is the historically right reading, not slack.
        occ += [(cp["cx"], cp["cy"], cp["r"] + clump * 0.90) for cp in self.M.get("crescent_ponds", [])]
        # ... and OFF THE POND - the tameike or a polder's header reservoir (feature 150: the first
        # scripted dike-pond seated its village at the block's head, so the windbreak's band ran
        # over the reservoir and 15 clumps stood in open water; nothing in this list knew the pond).
        # `M["pond"]` is [cx, cy, rx, ry]; the keep-out is the longer semi-axis + the canopy reach,
        # the same reading as the crescent pond above. `trees_clear_of_water` gates it.
        _pnd = self.M.get("pond")
        if _pnd:
            occ.append((float(_pnd[0]), float(_pnd[1]), max(float(_pnd[2]), float(_pnd[3])) + clump * 0.90))
        # ... and OFF A GROVE THAT IS ALREADY PLANTED (settlement-review x1, 2026-08-19). Nothing here
        # kept one grove out of another, and the copse is seated AFTER the windbreak, so it simply
        # planted itself in the belt: measured on Inashiro, clump-to-nearest-belt-clump distances of
        # 9, 8, 6, 4, 6, 4, 11, 9, 26, 30 and 83 ft against a belt clump radius of 14 - **10 of 11
        # copse clumps inside the belt's own canopy**, spanning x 1096-1188 while the houses span
        # 1108-1331. So the dooryards east of the front rank got no greenery at all and a whole
        # feature was invisible, while `research/vegetation.html` ("What are the village's three groves")
        # says outright that "the copse, not the belt, fills the inner gaps".
        #
        # Sum of the two canopy reaches, so neither stand's ink laps the other. This also protects the
        # reverse order (a belt seated after a copse) without needing to know which ran first, and it
        # is why the keep-out is built from the RECORDED clumps rather than the grove's bbox - a belt's
        # bbox is a long rectangle whose corners are open ground the copse may legitimately use.
        # (the radius lives on the GROVE record, not the clump - a clump is a bare [x, y] pair)
        # Kept in its OWN list, not folded into `occ`, because `_reseat` has to tell this blocker
        # apart from the others - see the note there. (the radius lives on the GROVE record, not the
        # clump - a clump is a bare [x, y] pair)
        occ_grove = [(cl[0], cl[1], float(g.get("r") or 0.0) + clump * 0.90) for g in self.M.get("village_groves", []) for cl in (g.get("clumps") or [])]
        occ += occ_grove
        # ...AND OFF EVERY HOUSEHOLD'S RESERVED SHARE OF THE WOOD FLOOR (feature 287, woods W25; plan D9): another grove's
        # clump stands where the copse's crown at a reserved seat would not be displaced by it, so the seat stands when the
        # copse is planted. A local keep-out: the belt flows round it as round a shed. (The copse's own clumps keep half a
        # crown off the seats instead - `held` below - since the seats are its own.)
        if keep_off and role != "copse":
            occ += reserved_seat_keepouts(keep_off, clump, bs)
        # ... and keep trees OFF the lanes / streets / road - and every TRUNK the clump will draw off the tread, not only its seat
        # (feature 287, woods W21 and homes H43): a crown is thrown anywhere in the clump's box and a belt's row conifer a few
        # feet past it (`crown_reach`), so the seat keeps at least that reach beyond the tread, and no trunk the clump draws
        # can stand on it (`trunk_on_tread`). 0.45 x clump + 4 fell 0.4 px short of the belt's own crowns at the box corner
        corr = self._corridor_buffers(max(clump * 0.45 + 4, crown_reach(clump, self.px(RANK_JITTER_FT) if role == "windbreak" else 0.0, lift=crown_lift(bs))))
        cr = clump / 2
        # ... and OUT of the SOUTHERN sun-corridor of every threshing yard + garden (a tree just south of them
        # blocks the drying/growing sun - +y is south). A touch wider than the check so it stays strictly clear.
        sun = [(o["x"], o["y"] + o["h"] / 2, o["w"] / 2 + cr + 2) for k in ("threshing_yards", "gardens") for o in self.M.get(k, [])]
        # HOW DEEP THE SOUTHERN STRIP IS follows the generator's own sun corridor when it declares one (`_sun_corridor_ft`,
        # 39 ft on the scripted hamlets - the depth a FARMHOUSE owes the same bed), else the 22 px this strip always was.
        # The settlement-review of feature 226 (2026-09-12) measured the contradiction: the belt is the tallest thing on
        # the map, the west lane it keeps is 50 ft, a house keeps 39 ft south, and this strip kept 22 - so 7 of
        # Kashikawa's 22 beds had a 10 m clump 24-38 ft south of them with no rule firing.
        _sun_depth = float(getattr(self, "_sun_corridor_ft", 22.0))
        # ... and OUT of the EASTERN sun-lane of every kitchen GARDEN: a tree just east blocks the MORNING sun
        # (the sun rises in the E; +x is east), so a garden on a house's lee/E side keeps clear sky to its east.
        # Entry = (garden east edge, garden cy, half-height + reach). See gardens_unshaded_from_east.
        east = [(o["x"] + o["w"] / 2, o["y"], o["h"] / 2 + cr + 2) for o in self.M.get("gardens", [])]
        # ... and OUT of the WESTERN / SOUTHWESTERN sun-lane of every yard and garden - the AFTERNOON
        # sun (feature 133 T10, GM 2026-08-25). A belt is the tallest thing on the map: a working
        # igune measures ~10 m, and at 3pm in the shoulder month (sun at 28 deg, azimuth ~232) a
        # 33 ft belt throws ~63 ft of shadow to the NORTHEAST - ~50 ft of it eastward. So a
        # belt clump within `_west_sun_ft` of a plot's west edge, from the plot's north edge down to
        # `_west_sun_ft` below its south edge (the southwest, where the 3pm shadow starts), takes the
        # afternoon. Measured as a SQUARE, not a solar wedge, the same knowing departure the yard's
        # south corridor takes. WINDBREAK MIX ONLY: a copse clump is the dooryard's persimmon or
        # bamboo (3-10 m in the Sendai igune classes), and the record puts exactly those IN the
        # sunlit yard ("a persimmon in the yard center", Tonami model homestead) - so a dooryard
        # scatter is not held to a lane that a 10 m belt is. Opt-in via `west_sun_lane` (off on the
        # frozen pool); `village_trees_unshade_from_west` gates it. Derivation: research/homesteads.html.
        wl = float(getattr(self, "_west_sun_ft", 0.0)) if mix == "windbreak" else 0.0
        west = [(o["x"] - o["w"] / 2, o["y"] - o["h"] / 2, o["y"] + o["h"] / 2) for k in ("threshing_yards", "gardens") for o in self.M.get(k, [])] if wl else []
        water_lines = [(st_["poly"], st_.get("w", 9) / 2) for st_ in self.M.get("streams", [])]
        water_lines += [(c_["poly"], c_.get("w", 2.5) / 2) for c_ in self.M.get("channels", [])]
        if self.M.get("moat"):
            water_lines.append((self.M["moat"], self.M.get("moat_width", 22) / 2))

        # EVERY KEEP-OUT ABOVE IS INDEXED ONCE, HERE, AND ASKED PER CANDIDATE (feature 218, GM
        # 2026-09-08). Three closures used to answer these questions by walking the whole registry
        # per candidate - `_hard_blocked` ran `edge_dist` over every crop polygon and `seg_dist` over
        # every watercourse segment, `_lane_blocked` over every corridor segment - and the re-seat
        # search re-asked all of it eight times per ring: 7.19 million `seg_dist` calls and 77% of
        # the stage on the reference hamlet, to keep 150 clumps (specs/218 research R1). The split
        # the closures encoded is kept on the index's methods: `hard` (the crop, open water, the dike
        # bank - the edges a belt STOPS at, so a refusal drops the clump), `lane` (a lane that ends at
        # the belt is an edge, one that runs through it is an obstacle - interior-vs-rim separates
        # them below), `local` (a house, a yard, a wellhead's wide keep-out, a sun corridor, a light
        # lane - obstacles a real planted belt is planted AROUND, so an interior refusal re-seats).
        # The index prunes; the same expressions decide; the maps are byte-identical.
        blocks = GroveBlocks(
            outline=poly,
            crops=self.field_polys,
            crop_pad=12 + cr,
            dry=self.dry_polys,
            dry_pad=12,
            # ...AND THE MARSH, INSIDE ONLY, as a dike bank is: woody cover "stands on the dry ground above it"
            # (research/vegetation.html, the marsh margin), so no clump is BASED in the marsh - a Kashikawa copse clump
            # stood 3-21 ft inside the toe (settlement-review, feature 261) - while a crown may reach over its edge.
            # The COPSE only: applied to every grove it took Sawada's windward belt from 179 crowns to 104, and 20-34 of the
            # 68 crowns it refused stood on ground DRAWN dry - the toe marsh's recorded outline runs under the settlement's
            # cleared ground there, so the outline is not the drawn marsh. The crops' padded keep-out was tried before that
            # and was worse still. The copse is the grove the review measured, and the parcels' own marsh keep-out is the
            # precedent it asked for.
            # ...AND EVERY OTHER GROVE KEEPS OUT OF THE MARSH DEEPER THAN ITS REED MARGIN (feature 287, woods W06): the outline
            # that took Sawada's belt from 179 crowns to 104 was the wrong one - it ran under ground drawn dry - and since M7 the
            # record IS the drawn marsh, so the belt is held to it too, with the margin (`MARSH_FEATHER_BS`, the reeds' own
            # thinning band) left to it: a belt clump based in the margin is drawn as alder, one deeper is not seated
            dikes=[dk["outline"] for dk in self.M.get("dikes", [])]
            + (marsh_ground(self.M) if role == "copse" else deep_marsh(marsh_ground(self.M), MARSH_FEATHER_BS * bs))
            # ...AND OFF THE BAMBOO, grown by a crown: a take-yabu is a clonal near single-species stand (research/vegetation 150),
            # and once feature 280 seated the thicket behind the back row the copse's crowns stood inside it (settlement-reviews
            # of Kashikawa and Mizuguchi: four crowns centered inside, culms drawn over them)
            # The rings come from the CALLER (`bamboo_rings`, the plan's seated stands): the stands are drawn by a later stage, so
            # `M['bamboo_stands']` is still empty when the copse is seeded - reading it made the keep-out a no-op (round 3)
            # grown by TWO crowns: a clump draws its crowns scattered about its seat, so a seat one crown off the stand still
            # drew a crown centered inside it (measured on the round-3 fix: one to two a map). `copse_bamboo_reach` is that
            # margin, and every bamboo placer keeps the reserved copse seats outside it (`stand_spares_seats`, feature 287
            # woods W25), so no household's reserved share is refused here
            + ([grown_ring(b, copse_bamboo_reach(bs)) for b in bamboo_rings if len(b) >= 3] if role == "copse" else []),
            water=[(wl, whw + cr) for wl, whw in water_lines],
            corridors=corr,
            circles=occ,
            displacers=occ_grove,
            rects=[(sx - shw, se - cr - 2, sx + shw, se + _sun_depth + 2 + cr) for sx, se, shw in sun]
            + [(ex - cr - 2, ey - ehh, ex + 24 + cr, ey + ehh) for ex, ey, ehh in east]
            + [(wx0 - wl - cr - 3, wy0 - cr - 1, wx0 + cr + 1, wy1 + wl + cr + 1) for wx0, wy0, wy1 in west]
            # ...AND OFF GROUND SOMETHING ELSE HAS RESERVED (settlement-review, feature 230 pass 12). `reserved`
            # is a rectangle a later stage is holding - today the pocket the map's own NAME will stand in. The
            # caller used to defend it by pushing the grove's polygon VERTICES out of the rectangle, which cannot
            # work at the clump scale: an edge between two vertices outside the pocket still crosses it, and a
            # crown is drawn 14 ft round a center that is itself outside. Measured on Kuwabata: 35 of 87 belt
            # clumps had canopy inside the reserved pocket, the title's own search rejected the pocket it had
            # reserved, and the placard fell to the cover rung and printed over 174 ft of the belt's windward
            # end - the stretch sheltering the westernmost homesteads - hiding 28 of its clumps.
            + ([(reserved[0] - cr, reserved[1] - cr, reserved[2] + cr, reserved[3] + cr)] if reserved else []),
        )
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

        def _reseat(qx: float, qy: float, require_interior: bool, reach_of: Seats | BankNear | None = _near, exact: bool = False) -> tuple[float, float] | None:
            """A DENSE belt flows around a local obstacle instead of losing the column.

            Which obstacles, and why this is not "re-seat around everything": a clump refused by the
            CROP, by open WATER or by a lane it merely abuts is refused for a reason that moving it a
            few feet does not change, and those are the edges where a belt is supposed to stop. What
            it DOES flow around is a local keep-out standing IN its line - a house, a yard, a
            wellhead (whose keep-out is the widest of the lot), a lane that CROSSES rather than
            abuts, and a threshing yard's southern sun corridor.

            The sun corridor is the case that motivated folding these three ad-hoc nudges into one
            helper (cohort seed 10, 2026-08-19). A yard's no-tree strip ran straight through the
            belt and left a 40 ft hole with a farmhouse directly downwind of it - the wall breached
            at the one place it was sheltering someone. It is not a crop edge and not a page edge;
            it is a local obstacle, and a real planted belt is planted around it. NOTE the earlier
            ledger entry blamed a pinch in `belt_polygon`; that was wrong - the band is a
            constant-depth ribbon, and the clumps were being filtered out, not left outside.

            Interior-only: a clump blocked near the polygon's own rim is at the belt's edge, where
            stopping is correct."""
            # INTERIOR ONLY FOR A LANE, and this cost seed 10 a round. The rule reads "a clump blocked
            # near the polygon's own rim is at the belt's edge, where stopping is correct" - true of a
            # lane, false of everything else. A belt is 110 px deep and a clump is 28, so demanding
            # `edge_dist > clump` leaves only the middle 54 px eligible: measured on seed 10, every
            # sun-corridor clump sat 2-27 px from a face and the search never ran. A yard's sun
            # corridor crosses the whole depth of the belt; where in that depth a given clump sits
            # says nothing about whether the belt should plant around it.
            # A SPARSE GROVE RE-SEATS TOO (settlement-review, Inashiro 2026-08-20). This used to read
            # `if not dense or (...)`, so only a belt flowed around an obstacle and a scatter's blocked
            # clump was dropped. That guard was written FOR the belt - the docstring above says so, "a
            # DENSE belt flows around a local obstacle instead of losing the column" - and the sparse
            # case was never considered. It is also backwards for what a copse is: the copse fills the
            # open gaps among the houses, so a clump refused because a house is there should try the
            # next gap. Finding the next gap IS the job; dropping the clump is the one response that
            # defeats the feature.
            #
            # Measured cost of the old behavior: Inashiro's copse collapsed to ONE clump inside a
            # declared 255 x 741 ft footprint once gate 0616 reserved ground around the belt's 227
            # clumps, and Mizuguchi's went 11 -> 4 earlier for the same reason (homesteads.py:248).
            # `village_groves_visibly_stocked` now fails a grove in that state.
            #
            # ONLY local obstacles reach here. `_hard_blocked` (crop, open water, the dike bank) still
            # drops the clump outright and must - those are the edges a stand is supposed to stop at,
            # and moving a few feet does not change them.
            # A SPARSE GROVE RE-SEATS ONLY WHEN ANOTHER STAND DISPLACED IT, and the narrowness is the
            # point. Blanket `not dense` re-seating was tried first and OVERSHOT badly: Inashiro's
            # copse went 1 -> 55 clumps and density across the four hamlets jumped to 10-15 per 100k
            # against a historical 3.9-4.4, which turns a dooryard scatter into a stand and defeats
            # the `dense` flag's whole purpose. A scatter is SUPPOSED to leave gaps; a clump refused
            # because a house is there has found one of them.
            #
            # What is NOT a gap is ground another grove's canopy is standing on. That blocker did not
            # exist until gate 0616's keep-out added it, and it deletes clumps for a reason that has
            # nothing to do with the settlement's own texture - measured, it cost Inashiro 10 of its
            # 11 copse clumps. So exactly that class relocates, and every other refusal still drops.
            # This repairs the harm the keep-out did without redesigning the scatter.
            if not dense and not blocks.displaced(qx, qy):
                return None
            if require_interior and blocks.rim_within(qx, qy, clump):
                return None
            # THE RADII REACH PAST THE WIDEST LOCAL OBSTACLE, which is the sun corridor: a yard's
            # no-tree strip is ~25 px half-width across and ~31 px deep, so a search capped at
            # step*1.4 = 28 px could not clear one and seed 10 kept its hole. step*2.2 = 44 px can.
            # A DEAD END, MEASURED AND REVERTED (feature 134 T50, 2026-08-28). When T49's rolled yard
            # sizes opened a 197 ft hole in cohort seed 8's wind wall, the obvious suspect was this
            # ladder: its top rung `step * 2.2` = 44 px is a number measured against the widest local
            # obstacle OF ITS DAY, and a rolled 52 x 36 ft yard stands in `occ` with a keep-out near
            # 57 px, so no rung could clear one. Deriving the top rung from the blocker actually
            # standing at the point (`rr - dist`, capped at `step * 5`) was implemented and rolled:
            # seed 8 came back with the SAME 65 clumps and the SAME 197 ft gap, and seeds 32 and 40
            # were unchanged too. Instrumenting the seating loop's rejections said why - of the grid
            # points in the hole, 166 were refused by `point_in_poly` and 39 by `within`, and NOT ONE
            # reached `_reseat`. The belt's eastern arm had swung north OFF THE PAGE as the cluster
            # repacked, so there was nothing there to re-seat around; the lone clump at (1423, 324) is
            # the only column of that arm the frame still shows. Do not re-derive this radius to chase
            # a belt hole - measure the rejection reasons first, because a hole in the ink and a hole
            # in the ribbon look identical from the manifest.
            for _nr in (step * 0.6, step * 1.0, step * 1.4, step * 1.8, step * 2.2):
                for _na in range(0, 360, 45):
                    ax, ay = qx + _nr * math.cos(math.radians(_na)), qy + _nr * math.sin(math.radians(_na))
                    if not blocks.inside(ax, ay):
                        continue
                    if within is not None and (ax + clump * 0.9 < within[0] or ax - clump * 0.9 > within[2] or ay + clump * 0.9 < within[1] or ay - clump * 0.9 > within[3]):
                        continue
                    if not (blocks.exact_clear if exact else blocks.static_clear)(ax, ay):  # the fill's regions; a reserved seat's exactly (R16)
                        continue
                    if near_clumps.too_near(ax, ay):
                        continue
                    if reach_of is not None and not reach_of.too_near(ax, ay):
                        continue  # a re-seat is a clump like any other: it stays within its reach (feature 261; a reserved seat's, W25)
                    return (ax, ay)
            return None

        nx, ny = max(1, round((x1 - x0) / step)), max(1, round((y1 - y0) / step))
        clumps: list[Any] = []
        seated: list[tuple[float, float]] = []  # unrounded seats, inked after the face trim below
        canopy = CanopyArea(2.0 * bs)  # the ground the seated clumps cover, for an `area` goal (269 B26)

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
                _alt = _reseat(jx, jy, require_interior=_by != "local", reach_of=_reach, exact=reserved)
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
                # leniency: `research/presentation.html` (GM 2026-07-20) says the belt CLIPS at the
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
        # research/vegetation/210: each homestead that keeps a wood has ~6,000-28,000 sq ft of trees, its windward grove
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
        if role == "windbreak" and len(seated) >= 2:
            _wv = _belt_axis(seated)
            # A GAP THAT SEATED NOTHING IS NOT OFFERED AGAIN (feature 281, FR-008). The depth search offers a gap the same
            # points every round - they depend only on its two clumps, `_wv` and the outline - and every test they face is
            # fixed during the fill but the spacing test against clumps already down, whose refusals only grow as clumps
            # land. So a gap that took no seat in a round takes none in a later one: re-offering it was 5 fractions x 33
            # depths of refusals per round, most of the 253,704 outline tests on Sawada's belts. A gap whose clumps change
            # (one lands between them) is a new pair, offered its own points.
            _barren: set[tuple[tuple[float, float], tuple[float, float]]] = set()
            for _ in range(6):  # a 94 ft gap needs three rounds; six is headroom, and it stops when nothing lands
                _order = sorted(range(len(seated)), key=lambda _k: seated[_k][0] * _wv[0] + seated[_k][1] * _wv[1])
                _added = 0
                # A DEAD END, MEASURED AND REVERTED (2026-08-29, the acceptance re-check's ERROR 2; the
                # record: research/vegetation.html "Why does the belt run off the edge of the sheet?").
                # The review read Kuwabata's belt as stopping before its polygon did, and the obvious
                # repair was to bracket this run by the polygon's own across-wind extent so the END
                # stretches were offered seats like any interior gap. Implemented and rolled: it bought
                # ONE clump, on ONE map, at (2273.9, 393.6) on the page edge - because the unplanted
                # tail is off the page. Kuwabata's belt polygon runs 693..1440 along its own axis, the
                # view holds only 790..1327 of that, and the planting already covers 734..1330. The
                # honest fix was in the CHECK, which was demanding canopy on ground no reader can see;
                # `_column_in_belt` now clips its columns to the view. Do not re-add the end bracket to
                # chase a belt that "stops short" - measure whether the short end is on the page first.
                for _a, _b in zip(_order, _order[1:], strict=False):
                    _pa, _pb = seated[_a], seated[_b]
                    if math.dist(_pa, _pb) <= _BELT_GAP_FT or (_GAP_MEMORY and (_pa, _pb) in _barren):
                        continue
                    # FILL UP TO THE OBSTACLE FROM BOTH SIDES, not only at the midpoint. Where a lane
                    # crosses the belt the midpoint IS the lane, so a midpoint-only fill gives up and
                    # leaves the whole 40-50 ft hole - when what the record and the agronomy both want is
                    # the wall resuming on each side of the crossing. The agroforestry manual, on a windbreak that
                    # must be crossed: a gap funnels the wind and the air downwind of it often moves FASTER
                    # than over the open field, so a bare opening is a defect. (The record used to give the
                    # remedy as rebuilding the crossing to the belt's own height and porosity, which is on no
                    # page and would close the access; the attested remedy is to ANGLE the opening to the
                    # prevailing wind. What this code does - resuming the wall each side of the crossing -
                    # is unaffected.) So the gap is offered
                    # seats across its span and takes whichever the ground allows.
                    # ...AND ACROSS THE BELT'S DEPTH, not only along the straight line between the two
                    # clumps. `village_windbreak_is_continuous` walks COLUMNS of the belt's own span and
                    # asks whether each has canopy; a belt that bows around a plot has columns whose
                    # midpoint-between-neighbors lies outside its own polygon, so a fill that only tried
                    # that line refused every seat and left the column bare - measured on Kuwabata, where
                    # the run leaves the polygon after 14 of its 40 ft. So each fraction along the gap is
                    # also tried at several depths across the band, which is where the belt actually is.
                    # ...AT THE BELT'S OWN DEPTH FOR THAT COLUMN. The continuity check walks COLUMNS
                    # across the wind and asks whether each carries canopy, so a fill has to answer in
                    # the same terms: find where the belt's polygon actually lies at the bare column and
                    # seat there. Offsetting from the straight chord between two clumps does not do it -
                    # a belt that bows leaves that chord entirely, and measured on Kuwabata the polygon's
                    # depth at the bare columns sits in a band the chord never reaches.
                    _took = False
                    _perp = (-_wv[1], _wv[0])
                    _pd = [(q[0] * _perp[0] + q[1] * _perp[1]) for q in poly]
                    _d0, _d1 = min(_pd), max(_pd)
                    for _f in (0.5, 0.34, 0.66, 0.22, 0.78):
                        _col = (_pa[0] * _wv[0] + _pa[1] * _wv[1]) + ((_pb[0] * _wv[0] + _pb[1] * _wv[1]) - (_pa[0] * _wv[0] + _pa[1] * _wv[1])) * _f
                        _inside = []
                        for _k in range(33):
                            _d = _d0 + (_d1 - _d0) * _k / 32
                            _qx, _qy = round(_col * _wv[0] + _d * _perp[0], 1), round(_col * _wv[1] + _d * _perp[1], 1)  # the record's grain (W01)
                            if blocks.inside(_qx, _qy):
                                _inside.append((_qx, _qy))
                        for _qx, _qy in _inside[len(_inside) // 2 :] + _inside[: len(_inside) // 2]:  # the band's middle outward
                            if within is not None and (_qx + clump * 0.9 < within[0] or _qx - clump * 0.9 > within[2] or _qy + clump * 0.9 < within[1] or _qy - clump * 0.9 > within[3]):
                                continue
                            if not blocks.static_clear(_qx, _qy) or (_near is not None and not _near.too_near(_qx, _qy)):
                                continue
                            # ...AND NEVER ON TOP OF A CLUMP THAT IS ALREADY THERE (settlement-review
                            # 2026-08-29, acceptance re-check). The depth search is deterministic, so a gap
                            # that survives one round is offered the SAME point on the next and the fill
                            # piled crowns instead of converging. Measured by rolling Kuwabata with this
                            # clause disabled: 246 recorded windbreak clumps at 211 distinct positions,
                            # five of them at (1695.8, 576.9) alone, and 46 off-page clumps at 41
                            # positions. Refusing a seat within half a crown of one already taken brings
                            # the same belt in at 101 on-page clumps with nothing stacked. A stacked crown
                            # is invisible in ink and inflates every count taken off the record - including
                            # the one I first quoted for this feature.
                            if near_seats.too_near(_qx, _qy):
                                continue
                            seated.append((_qx, _qy))
                            clumps.append([round(_qx, 1), round(_qy, 1)])
                            near_seats.add(_qx, _qy)
                            near_clumps.add(round(_qx, 1), round(_qy, 1))
                            _took = True
                            break
                        if _took:
                            break
                    if _took:
                        _added += 1
                    else:
                        _barren.add((_pa, _pb))
                if not _added:
                    break
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
            seated = settle_the_belt(seated, r=round(clump / 2, 1), houses=_houses, wind=wind or (0.0, -1.0), ways=_ways, page=page, band=poly, seat=_settle_seat, reach=reach, trim=_trim)
        elif role == "windbreak" and wind is not None and seated:  # one crown too: a lone crown off the wind is no belt (W18)
            seated = trim_to_the_wind(seated, _houses, wind)
        if role == "copse" and len(seated) > 1:
            seated = stocked_copse(seated, clump / 2 + 4.0, kept)
        clumps = [[x, y] for x, y in seated]  # the seats are at the record's grain (W01), so the record is the ink
        # A BELT CROWN IN THE MARSH IS ALDER (feature 261, Sawada's belt on its toe's reed edge): the record's woody stage at
        # a reed margin is alder or willow (research/vegetation.html, the marsh margin), and alder is the tree of a
        # wetland's fertile edge, so where the windbreak's ground runs into the recorded marsh its trees are drawn as one
        _wet = marsh_ground(self.M, only=("toe", "waterside")) if role == "windbreak" else []
        alder = 0
        alder_clumps: list[list[float]] = []  # which seats are drawn as alder, so a recount after the page is known reads them (woods W05)
        bamboo = 0  # the bamboo marks inked low under the windbreak's crowns (269 B29, `_draw_grove`)
        # THE VILLAGE BELT IS DRAWN IN ITS ROLLED FORM (269 B30, `windbreak_belt`; research/vegetation/270): conifer-led, its
        # rows of conifers laid along the belt as drawn and seated before the clumps' lesser crowns, then painted over them
        # (`_belt_ranks`), or mixed broadleaf. The water-mouth grove keeps the older mix.
        form = self._windbreak_belt() if role == "windbreak" and seated else None
        crowns: dict[str, int] = {}
        rows_ink = ""
        if form == "conifer_led":
            _rows, rows_ink = self._belt_ranks(seated, clump, _wet)
            crowns["conifer"] = len(_rows)
        for jx, jy in seated:
            # feature 150: the belt and the copse are two highlight classes; a water_mouth grove has no
            # class in the vocabulary yet and stays unclassed so the census reports it
            if any(point_in_poly(jx, jy, w) for w in _wet):
                alder += 1
                alder_clumps.append([jx, jy])
                self._draw_grove(jx, jy, clump, clump, face=(0, -1), mix="alder", cls="alder")
                continue
            bamboo += self._draw_grove(jx, jy, clump, clump, face=(0, -1), mix=form or mix, cls={"windbreak": "windbreak", "copse": "copse"}.get(role), tally=crowns)
        if rows_ink:
            self.add(rows_ink, cls="windbreak")
        if clumps:
            # A COPSE IS RECORDED AT THE SIZE IT WAS DRAWN, not at the size it was asked for.
            #
            # The copse's requested footprint is the bounding box of the whole house cloud, and the
            # clumps inside it are skipped wherever they would land on a house, yard, garden or
            # crop - so the DECLARED area and the PLANTED area are two different things, and the
            # gap between them widens whenever the cluster spreads. Feature 126 spread it (houses
            # are no longer seated against pre-laid lanes), and `village_groves_visibly_stocked`
            # started firing: "copse 307x443px holds 1 clump (0.73/100k), floor 1.5". The trees had
            # not gone anywhere; the box around them had grown.
            #
            # The check is right and the record was wrong - a map that declares a feature it did not
            # draw is the defect, which is the same rule `M["lane"]` breaks when it keeps an untrimmed
            # spine. So a COPSE reports the extent of its own clumps. The WINDBREAK deliberately does
            # not: its position IS its meaning (`village_windbreak_on_windward_side` judges the
            # recorded center) and shrinking it to the leaves would walk that center off the windward
            # side - a defect this file already records having caused on cohort seeds 19 and 28.
            _pad = clump / 2 + 4.0
            if role == "copse":
                x0, y0, x1, y1 = grove_extent(clumps, _pad)
                poly = [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]
            # ...AND EVERY GROVE IS RECORDED AT AN EXTENT ITS CLUMPS STOCK (feature 287, woods W15): the band's box where they
            # stock it (the windbreak's position is its meaning, above), else the extent they are drawn at, else their main
            # stand's (`stocked_box`) - no role is left to a density nothing decided
            _rec: dict[str, Any] = {}
            record_box(_rec, stocked_box(clumps, (x0, y0, x1, y1), _pad))
            self.M["village_groves"].append(
                {
                    **_rec,
                    "rot": 0,
                    "role": role,
                    "r": round(clump / 2, 1),
                    "clumps": clumps,
                    "clumps_offpage": [],  # filled by `set_view`'s partition, the first moment the page is known
                    "alder": alder,  # of the clumps, those standing in the marsh and drawn as alder (feature 261)
                    "alder_clumps": alder_clumps,  # ...and which they are, for the recount once the page is known (feature 287, woods W05)
                    "bamboo": bamboo,  # bamboo marks inked in the gaps and along the edge (269 B29; 0 outside the windbreak mix)
                    "form": form,  # the village belt's rolled form (269 B30, meta.windbreak_belt); None off the belt
                    "crowns": crowns,  # the crowns drawn, by kind (conifer / broadleaf; the alder clumps are not counted)
                    "poly": [[round(px, 1), round(py, 1)] for px, py in poly],
                }
            )
        return len(clumps)
