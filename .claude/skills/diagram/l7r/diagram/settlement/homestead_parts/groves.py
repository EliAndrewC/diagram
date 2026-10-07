"""Split from settlement/homestead_parts.py by feature 173 - see this package's CLAUDE.md for the index.

Research: plumbing - NONE
"""

import heapq
import math
import random
from collections.abc import Sequence
from typing import TYPE_CHECKING, Any

from .._geom import CrownIndex, PointGrid, _union_area, boxed_grid, boxed_polys, boxes_meeting, nearest_seg_dist, point_in_poly, seg_dist, seg_reach_index
from .._knobs import CITY_TIER_SCALES, Knob, knob_rng, register_knob
from ._helpers import _belt_axis
from .grove_sides import GROVE_FLANKS, GROVE_SIDES, GROVE_SIDES_FLOOD, THIN_BAND_FT, grove_faces
from .tree_shade import BAMBOO_SHADE_FT

#: The grain a grove's clump is rendered at, relative to the town grain the glyphs were calibrated at (`_draw_grove`'s `bs`).
GROVE_RENDER_GRAIN = 0.82
"""Research: clump render grain - CONVENTION: 0.82 of the town grain"""


def crown_lift(bscale: float) -> float:
    """How far up the sheet `_draw_grove` draws every crown from the point it threw it at: `3 * bs` at the grove's render
    grain (`bscale / GROVE_RENDER_GRAIN`) - 3.66 px on a hamlet, not the 3.0 the reach was once taken at (feature 287 M8:
    cohort seed 31 drew a copse trunk 15.3 px from its clump against a reach of 15.0, on a lane's tread). `crown_reach`'s
    `lift` is this, so the reach IS the drawn reach.

    Research: crown drawn above its throw - CONVENTION: 3 bscale units up the sheet at the grove's grain
    """
    return 3.0 * bscale / GROVE_RENDER_GRAIN


if TYPE_CHECKING:
    from ..core import Settlement


ALDER_GREENS = ("#5E7F6A", "#6B8A74")  # the alder crowns' tint (a map drawing convention, `_draw_grove`)
"""Research: alder tint - research/questions/0074-reed-beds-and-the-marshs-edge-yoshihara.drawing.html: blue-gray green, a convention"""
# A household's bamboo stand, rolled per farmstead from its position (`_hjit(x, y, 95.0)` under this share): the presence
# rate is a GUESS - no source gives a share; "one of several secondary species" says common but not universal
# (hamletgen/homesteads/bamboo.py carries the full note). Here since feature 291, because a farm with its own grove carries
# its bamboo IN that grove, so the grove drawer makes the same roll.
HOUSEHOLD_BAMBOO_PREVALENCE = 0.6
"""Research: farms with bamboo - research/questions/0075-bamboo-groves-chikurin.drawing.html, research/questions/0036-groves-of-trees-around-farmhouses-yashikirin.html: three in five"""
GROVE_CLUMP_CROWNS = 28  # how many crowns' ground one piece of a band holds where `band_clumps` cuts it (`farmsteads`)
"""Research: crowns a band piece holds - UNRESEARCHED: a band cut along its length into pieces of 28 crowns' ground, so every band is drawn at the one density"""
GROVE_CROWN_AREA = 48.0  # sq px of clump per crown at the town grain (~one 5 m crown); scaled by (bscale / 0.82) ** 2
"""Research: grove crown density - research/questions/0080-how-thickly-trees-stood-in-a-wood-and-how-wide-their-crowns.drawing.html: one crown per 48 sq px at the town grain"""


def band_clumps(cx: float, cy: float, w: float, h: float, cap_area: float) -> list[tuple[float, float, float, float]]:
    """A grove band cut along its longer side into equal pieces of at most `cap_area` each (feature 291), so a band
    larger than one clump's cap is drawn as several clumps at the one density rather than one sparse clump."""
    k = max(1, math.ceil(w * h / cap_area)) if cap_area > 0 else 1
    if w >= h:
        return [(cx - w / 2 + w * (i + 0.5) / k, cy, w / k, h) for i in range(k)]
    return [(cx, cy - h / 2 + h * (i + 0.5) / k, w, h / k) for i in range(k)]


GROVE_BAMBOO_SHARE = 0.08  # of a windbreak clump's items, the bamboo under its crowns: a GUESS (269 B29, research/questions/0075-bamboo-groves-chikurin.html)
"""Research: bamboo in a windbreak clump - research/questions/0075-bamboo-groves-chikurin.drawing.html: 8% of its items, in the
village belt even where the bamboo knob rolled none (only the farm groves check `_farm_rolls_bamboo`)"""

GROVE_BAMBOO_PATCH_FT = (22.0, 16.0)
"""A farm's household bamboo, where it rolled a stand and keeps it in its own grove (feature 291, research/questions/0075-bamboo-groves-chikurin.html): a patch
this size - along the band, then across it - on the house side of each windward (deep) band, every item in it bamboo,
so it is inked as culms rather than a crown. The size is the household strip's (`hamletgen/homesteads/bamboo.py`
`HOUSEHOLD_BAMBOO_FT`, a GUESS); each windward band, because the Tonami grove held its bamboo "from the west round to the
north". Drawn only as the share of `GROVE_BAMBOO_SHARE` - in the gaps between crowns - 8 of Kashikawa's 15 bamboo farms
drew no culm at all (settlement-review, 2026-09-30).

Research: grove bamboo patch - research/questions/0075-bamboo-groves-chikurin.drawing.html: 22 x 16 ft on each windward band
"""


def in_box(x: float, y: float, box: tuple[float, float, float, float] | None) -> bool:
    """Is (x, y) inside the axis-aligned `box` (x0, y0, x1, y1)? False with no box."""
    return box is not None and box[0] <= x <= box[2] and box[1] <= y <= box[3]


def bamboo_patch(cx: float, cy: float, w: float, h: float, face: tuple[float, float], along: float, across: float) -> tuple[float, float, float, float]:
    """The household bamboo patch of a band centered (`cx`, `cy`), `w` x `h`, whose outward face is `face`: `along` x
    `across` (clamped to the band), in the band's middle, against its HOUSE side (the side opposite `face`).

    Research: patch on the house side - research/questions/0075-bamboo-groves-chikurin.drawing.html: the band's middle
    """
    fx, fy = face
    if abs(fx) > abs(fy):  # an east or west band: along it is y, across it is x
        pw, ph = min(across, w), min(along, h)
        x = cx - fx * (w - pw) / 2
        return (x - pw / 2, cy - ph / 2, x + pw / 2, cy + ph / 2)
    pw, ph = min(along, w), min(across, h)
    y = cy - fy * (h - ph) / 2
    return (cx - pw / 2, y - ph / 2, cx + pw / 2, y + ph / 2)


# THE VILLAGE BELT HAS TWO ATTESTED FORMS, SO IT IS A KNOB (269 B30; research/questions/0072-shelter-belts-on-a-villages-windward-side-bofurin.html,
# on what a belt was planted with). Neither is a line of one kind of tree. `conifer_led` is the Japanese farmstead grove drawn at village
# scale - planted in rows round one tall conifer (cedar at every homestead of three surveyed regions, the igune's four tall
# trees), with many lesser kinds among it; the village scale is an interpolation the entry names, every survey being of one
# farmstead's grove. `mixed_broadleaf` is the Chinese village fengshui wood - ~47 kinds a patch, measuring as evergreen
# broadleaf forest - drawn as an irregular wood of rounded crowns like the woods around it. The clipped pine wall of Izumo is
# one house's, not a village's, and is not drawn. The roll is even: no source says which was commoner. The homestead
# yashikirin (`_find_grove_arms`) and the water-mouth grove keep the `windbreak` mix; the knob is the village belt's.
WINDBREAK_BELT_FORMS = ("conifer_led", "mixed_broadleaf")
"""Research: belt planting forms - research/questions/0072-shelter-belts-on-a-villages-windward-side-bofurin.drawing.html: two forms, even odds"""
register_knob(Knob("windbreak_belt", list(WINDBREAK_BELT_FORMS), default="conifer_led"))

# THE RANKS OF A CONIFER-LED BELT (269 B30, research/questions/0072-shelter-belts-on-a-villages-windward-side-bofurin.html): the conifers stand in rows laid ALONG THE BELT AS DRAWN - each
# row an offset of the belt's own centerline (`belt_centerline`, `rank_points`), so on a bent belt the rows bend with it
# (settlement-review 2026-09-28: one straight axis fitted to Inashiro's crescent set the east arm's rows ~76 deg across it).
# They are laid once for the whole belt, seated before any lesser crown and painted over them all (`_belt_ranks`). The
# survey says "planted in a row" and gives no spacing, so both numbers are a GUESS chosen to be read: along a row the crowns
# just meet (the row's conifer is ~20-22 ft across, `RANK_CONIFER_S`), and the rows stand a little wider apart so the lesser
# broadleaf between them shows. The conifer is the commonest crown in this form, which the entry states as a guess.
RANK_ALONG_FT = 20.0
"""Research: conifers along a row - research/questions/0072-shelter-belts-on-a-villages-windward-side-bofurin.drawing.html: 20 ft"""
RANK_APART_FT = 26.0
"""Research: rows apart - research/questions/0072-shelter-belts-on-a-villages-windward-side-bofurin.drawing.html: 26 ft"""
# a planted tree stands a little off its mark, so the rows do not read as a surveyed grid: a GUESS (the same review; its round
# 2 measured 1.5 ft as ~2 px on a 27 px pitch, invisible at any zoom)
RANK_JITTER_FT = 3.0
"""Research: planted off its mark - GUESS: up to 3 ft"""
RANK_BIN_FT = 40.0  # the centerline's vertex spacing along the belt: two rows' width, fine enough to follow a crescent's bend (a GUESS)
RANK_CONIFER_S = (1.0, 1.1)  # a planted row is even-aged: one size band (x CANOPY_R_FT x 1.15), not the emergent mix
"""Research: row conifer size - research/questions/0080-how-thickly-trees-stood-in-a-wood-and-how-wide-their-crowns.drawing.html: 1.0 to 1.1 of the mean crown, x 1.15"""
LESSER_BROADLEAF_S = (
    0.75,
    0.85,
)  # "lesser broadleaf crowns among them" (research/questions/0072-shelter-belts-on-a-villages-windward-side-bofurin.drawing.html): smaller than the woods' crowns
"""Research: lesser broadleaf size - research/questions/0080-how-thickly-trees-stood-in-a-wood-and-how-wide-their-crowns.drawing.html: 0.75 to 0.85 of the mean radius, within the page's 0.75 to 1.4"""
# ...and FEWER than the conifers: of a clump's usual rolls, this share is thrown for the broadleaf and the bamboo between the
# rows, so the conifer stays the commonest crown (the entry's guess; the share itself a GUESS, measured against the maps'
# `crowns` tallies, 269 B30). Measured on Inashiro's belt with the rows laid per clump: 0.3 drew 182 conifers to 330
# broadleaf (a belt's clumps overlap, so each throws its own), 0.15 drew 189 to 230, 0.1 drew 197 to 114 - about one roll a clump.
LESSER_ROLL_SHARE = 0.1
"""Research: conifer the commonest crown - research/questions/0072-shelter-belts-on-a-villages-windward-side-bofurin.drawing.html: a tenth of a clump's rolls"""


def belt_walk(pts: list[tuple[float, float]], link: float, start: int = 0) -> list[float]:
    """Each seat's distance from seat `start` WALKING THROUGH THE BELT: Dijkstra over the seats, each joined to those
    within `link` (a grid index, never a scan), and a seat the walk cannot reach joined by the shortest hop from the
    seats it has reached (a gap the belt's own fill left open)."""
    grid = PointGrid(link)
    grid.extend([(i, x, y, x, y) for i, (x, y) in enumerate(pts)])
    dist = [math.inf] * len(pts)
    dist[start] = 0.0
    heap = [(0.0, start)]
    done: set[int] = set()
    while len(done) < len(pts):
        if not heap:  # the walk ran out: bridge the nearest unreached seat to the reached ones
            d, u = min((dist[r] + math.hypot(pts[r][0] - pts[u][0], pts[r][1] - pts[u][1]), u) for u in range(len(pts)) if u not in done for r in done)
            dist[u] = d
            heap.append((d, u))
        d, i = heapq.heappop(heap)
        if i in done:
            continue
        done.add(i)
        for j, x, y, *_ in grid.near(pts[i][0], pts[i][1], link):
            e = math.hypot(x - pts[i][0], y - pts[i][1])
            if j not in done and e <= link and d + e < dist[j]:
                dist[j] = d + e
                heapq.heappush(heap, (d + e, j))
    return dist


def belt_centerline(pts: list[tuple[float, float]], step: float) -> list[tuple[float, float]]:
    """A belt's centerline as drawn, from its clump seats: the seats binned `step` apart by how far each lies from the
    belt's END WALKING THROUGH THE BELT (`belt_walk`: the end is the seat farthest from a seat farthest along the principal
    axis), each bin's mean a vertex, the inner vertices smoothed by a three-point mean, and the line carried on a step past
    each end so an end clump's rows reach it. Walking, not projecting: Inashiro's crescent turns back on its own principal
    axis at its east tip, and binning along that axis averaged across the turn and left the tip with no rows (the
    settlement-review's round 2, 2026-09-28).

    Research: rows follow the belt - research/questions/0072-shelter-belts-on-a-villages-windward-side-bofurin.drawing.html
    """
    ax, ay = _belt_axis(pts)
    first = min(range(len(pts)), key=lambda i: pts[i][0] * ax + pts[i][1] * ay)
    probe = belt_walk(pts, step, first)
    walked = belt_walk(pts, step, max(range(len(pts)), key=lambda i: probe[i]))
    bins: dict[int, list[tuple[float, float]]] = {}
    for (x, y), u in zip(pts, walked, strict=True):
        bins.setdefault(int(u // step), []).append((x, y))
    verts = [(sum(p[0] for p in b) / len(b), sum(p[1] for p in b) / len(b)) for _, b in sorted(bins.items())]
    if len(verts) == 1:
        verts = [(verts[0][0] - ax * step / 2, verts[0][1] - ay * step / 2), (verts[0][0] + ax * step / 2, verts[0][1] + ay * step / 2)]
    elif len(verts) >= 3:
        verts = [verts[0], *(((a[0] + b[0] + c[0]) / 3, (a[1] + b[1] + c[1]) / 3) for a, b, c in zip(verts, verts[1:], verts[2:], strict=False)), verts[-1]]

    def carried(a: tuple[float, float], b: tuple[float, float]) -> tuple[float, float]:  # a step on past `b`, away from `a`
        d = math.hypot(b[0] - a[0], b[1] - a[1]) or 1.0
        return (b[0] + (b[0] - a[0]) / d * step, b[1] + (b[1] - a[1]) / d * step)

    return [carried(verts[1], verts[0]), *verts, carried(verts[-2], verts[-1])]


def rank_points(line: list[tuple[float, float]], half_depth: float, along: float, apart: float) -> list[tuple[float, float]]:
    """The rows of a ranked belt: offsets of `line` every `apart` out to `half_depth` on both sides, and on each offset a
    point every `along` of its own length (so a row on the outside of a bend is not stretched, nor one inside crowded). A
    vertex's normal is the mean of its two segments' normals."""
    segs = list(zip(line, line[1:], strict=False))
    seg_n = []
    for (x0, y0), (x1, y1) in segs:
        d = math.hypot(x1 - x0, y1 - y0) or 1.0
        seg_n.append((-(y1 - y0) / d, (x1 - x0) / d))
    vert_n = []
    for k in range(len(line)):
        nx = seg_n[max(0, k - 1)][0] + seg_n[min(len(segs) - 1, k)][0]
        ny = seg_n[max(0, k - 1)][1] + seg_n[min(len(segs) - 1, k)][1]
        d = math.hypot(nx, ny) or 1.0
        vert_n.append((nx / d, ny / d))
    out: list[tuple[float, float]] = []
    rows = math.ceil(half_depth / apart)
    for j in range(-rows, rows + 1):
        off = [(x + nx * j * apart, y + ny * j * apart) for (x, y), (nx, ny) in zip(line, vert_n, strict=True)]
        walked = 0.0  # arc length along this row up to the start of the current segment
        nxt = 0.0  # where the next point falls
        for (x0, y0), (x1, y1) in zip(off, off[1:], strict=False):
            seg = math.hypot(x1 - x0, y1 - y0)
            while nxt <= walked + seg and seg > 0:
                t = (nxt - walked) / seg
                out.append((x0 + (x1 - x0) * t, y0 + (y1 - y0) * t))
                nxt += along
            walked += seg
    return out


HOMESTEAD_WOOD_FT2 = (6000.0, 28000.0)
"""The trees one homestead keeps, its windward grove and its share of the copse together, in sq ft (269 B26;
research/questions/0036-groves-of-trees-around-farmhouses-yashikirin.drawing.html): a 1684 Mito register lists three homestead woods of about 6,100, 10,700 and 27,800 sq ft. A
calibration against three households, not a survey; counting grove and copse as one wood is the entry's decision.

Research: homestead wood range - research/questions/0036-groves-of-trees-around-farmhouses-yashikirin.drawing.html: 6,000 to 28,000 sq ft
"""


#: How far two crowns' discs may overlap before the later one is drawn OVER the earlier: their centers nearer than this share
#: of their radii summed (feature 294 B5b; a GUESS - at 0.8 the overlap is a broad lens, not an edge touching).
CROWN_OVER_SHARE = 0.8
"""Research: overlap drawn over - CONVENTION: centers nearer than 0.8 of the radii summed"""


def over_a_conifer(x: float, y: float, r: float, conifers: Sequence[tuple[float, float, float]], slack: float = 0.2) -> bool:
    """Would a crown at (x, y) of radius `r`, drawn now, lie OVER one of the `conifers` already drawn (feature 294 B5b, the
    review's broadleaf-over-conifer case: a later clump's broadleaf inked over an earlier clump's cedar, 269 B30)? The conifer
    is the taller and darker crown and reads on top: a lesser crown that would be painted over one is not drawn. `slack` (px) is the
    ink's rounding: the SVG writes a crown to 0.1 px, so the placer asks a little wider than the test that reads the ink.

    Research: conifer reads on top - CONVENTION: a lesser crown painted over a conifer is not drawn
    """
    return any((x - cx) ** 2 + (y - cy) ** 2 < (CROWN_OVER_SHARE * (r + cr) + slack) ** 2 for cx, cy, cr in conifers)


def _boxes_meet(a: Any, b: Any) -> bool:
    """Whether two (cx, cy, w, h) boxes overlap."""
    return bool(abs(a[0] - b[0]) < (a[2] + b[2]) / 2 and abs(a[1] - b[1]) < (a[3] + b[3]) / 2)


#: A bamboo stand's culms and leaves (a map drawing convention): the cool jade green of living culms, which no grass, reed or
#: crown on the map uses. They were the scrub grass's yellow-greens (#9AAE3C / #B9CC5A against #94A063 / #A7A860), and the
#: stand read as a denser patch of grass (glyph checks: Sawada's homestead bamboo, feature 302; the belt's, Sawada F3 and
#: Mizuguchi N1 before it).
BAMBOO_CULM = "#2F8F4E"
"""Research: culm color - CONVENTION"""
BAMBOO_LEAF = "#4BA35F"
"""Research: leaf color - CONVENTION"""


def bamboo_mark(x: float, y: float, bs: float, tall: float, lean: float) -> str:
    """ONE bamboo mark - two culms leaning together and a leafy fork at the top of the taller one - the stand glyph's
    map drawing convention (`bamboo_stand`; a culm is inches across and cannot be drawn to scale). `tall` and `lean`
    are the two positional rolls in [0, 1): a mark 5-8 ft tall, leaning up to 0.8 ft.

    Research: bamboo mark - research/questions/0075-bamboo-groves-chikurin.drawing.html: paired culm strokes and a leafy fork
    """
    h = (5.0 + 3.0 * tall) * bs
    ln = (lean - 0.5) * 1.6 * bs
    tx, ty = x - 1.2 * bs + ln, y - h
    return (
        f'<path d="M{x - 1.2 * bs:.1f},{y:.1f} l{ln:.1f},{-h:.1f} M{x + 1.2 * bs:.1f},{y:.1f} l{-ln * 0.6:.1f},{-h * 0.8:.1f}" stroke="{BAMBOO_CULM}" stroke-width="{0.9 * bs:.2f}" fill="none" stroke-linecap="round"/>'
        f'<path d="M{tx:.1f},{ty:.1f} l{-2.2 * bs:.1f},{-1.6 * bs:.1f} M{tx:.1f},{ty:.1f} l{2.4 * bs:.1f},{-1.2 * bs:.1f} M{tx:.1f},{ty:.1f} l{0.4 * bs:.1f},{-2.6 * bs:.1f}" stroke="{BAMBOO_LEAF}" stroke-width="{0.8 * bs:.2f}" fill="none" stroke-linecap="round"/>'
    )


class GrovesMixin:
    """The homestead grove's mixin: its arms, its fit, its clumps.

    Research:
        which faces for each wind - research/questions/0036-groves-of-trees-around-farmhouses-yashikirin.html: `_GROVE_ARMS`, the windward pair (N + W for NW), the N arm wrapping the corner
    """

    # the windward faces a homestead grove (yashikirin) shelters, by where the prevailing cold wind comes
    # FROM (its compass key). The grove is an L-BELT: a deep stand on each windward face (for a diagonal
    # like NW, an N arm + a W arm wrapping the corner; for a cardinal, one deep band). Default NW - the
    # East Asian winter monsoon (the Siberian high) blows NW across China AND Japan, so N+W is windward and
    # the S/E is the sheltered, sunny side. A map keys it off its geography with meta(windward=...). Each
    # arm is (face, perp): `face` is the cardinal it sits on; `perp` is the sign the N/S arm extends along
    # to wrap the corner (0 for a lone cardinal arm). See research/questions/0036-groves-of-trees-around-farmhouses-yashikirin.html.
    _GROVE_ARMS = {
        "NW": [((0, -1), -1), ((-1, 0), 0)],
        "NE": [((0, -1), 1), ((1, 0), 0)],
        "SW": [((0, 1), -1), ((-1, 0), 0)],
        "SE": [((0, 1), 1), ((1, 0), 0)],
        "N": [((0, -1), 0)],
        "S": [((0, 1), 0)],
        "E": [((1, 0), 0)],
        "W": [((-1, 0), 0)],
    }

    def _windward(self: Settlement) -> str:  # type: ignore[misc]
        """The map's prevailing-wind compass key (where the cold wind blows FROM), default NW.

        Research: northwest wind by default - research/questions/0072-shelter-belts-on-a-villages-windward-side-bofurin.drawing.html
        """
        w = str(self.M["meta"].get("windward", "NW")).upper().strip()
        return w if w in self._GROVE_ARMS else "NW"

    def _windbreak_belt(self: Settlement) -> str:  # type: ignore[misc]
        """The village belt's form, `conifer_led` or `mixed_broadleaf` (269 B30, research/questions/0072-shelter-belts-on-a-villages-windward-side-bofurin.html): pinned or rolled from the
        map's seed, and declared as meta.windbreak_belt.

        Research: belt form rolled per map - research/questions/0072-shelter-belts-on-a-villages-windward-side-bofurin.drawing.html
        """
        form = str(self.resolve("windbreak_belt"))
        self.M["meta"]["windbreak_belt"] = form
        return form

    def _belt_ranks(self: Settlement, seated: list[tuple[float, float]], clump: float, wet: list[Any]) -> tuple[list[tuple[float, float, float]], str]:  # type: ignore[misc]
        """Seat a conifer-led belt's rows of conifers (269 B30, research/questions/0072-shelter-belts-on-a-villages-windward-side-bofurin.html) over the whole belt at once, BEFORE its clumps
        draw their lesser crowns, and return (the crowns, their ink). The caller paints the ink after every clump, so no lesser
        crown is inked over a conifer - painted per clump, a later clump's broadleaf lay over an earlier clump's conifers (the
        settlement-review of 2026-09-28 counted 29 of the 73 broadleaf on Inashiro's page). A row point is kept only on the
        belt's ground (inside a seated clump's box: each seat passed the belt's keep-outs, the ground between them did not), off
        the marsh (`wet`, where the belt is alder), and where the crown covers no building or wellhead and stands under no
        other crown - the tests every crown of `_draw_grove` answers, asked of indexes built once here.

        Research:
            conifer rows - research/questions/0072-shelter-belts-on-a-villages-windward-side-bofurin.drawing.html: rows along
                the belt, seated before the lesser crowns
            no row conifer in the marsh - research/questions/0074-reed-beds-and-the-marshs-edge-yoshihara.drawing.html
            crowns out of the plots' sun - research/questions/0038-sunlight-and-shade-on-the-farm.drawing.html
            crown over no roof - research/questions/0071-groves-around-a-southern-chinese-village-the-fengshui-woods-fengshuilin-and-the-dooryard-copse.drawing.html
            crown under no crown - research/questions/0080-how-thickly-trees-stood-in-a-wood-and-how-wide-their-crowns.drawing.html
        """
        line = belt_centerline(seated, self.px(RANK_BIN_FT))
        # THE BELT'S HALF-DEPTH FROM THE CENTERLINE'S NEAR SEGMENTS (feature 306, the GM: a check against many things means
        # a line was not drawn to stay beside). Each seat measured its distance to EVERY centerline segment - nearly all of
        # the 15,005 comparisons a call on the pool - to take the nearest; the segments are filed once and each seat asks
        # outward from a clump's width (`nearest_seg_dist`), which returns the same minimum.
        axis = seg_reach_index([(line, 0.0)], 0.0)
        half = max(nearest_seg_dist(axis, x, y, clump) for x, y in seated) + clump / 2
        ground = PointGrid(clump)
        ground.extend([(x - clump / 2 + 2, y - clump / 2 + 2, x + clump / 2 - 2, y + clump / 2 - 2) for x, y in seated])
        bb = (min(p[0] for p in seated) - clump, min(p[1] for p in seated) - clump, max(p[0] for p in seated) + clump, max(p[1] for p in seated) + clump)
        krect, kcirc = self._canopy_keepouts(bb)
        krect += self._sun_keepouts(bb)  # ...and every yard's and bed's sun ground (feature 310: no canopy tree exempt)
        rects, circs = PointGrid(64.0), PointGrid(64.0)
        rects.extend([(cx, cy, hw, hh, cx - hw, cy - hh, cx + hw, cy + hh) for cx, cy, hw, hh in krect])
        circs.extend([(wx, wy, wr, wx - wr, wy - wr, wx + wr, wy + wr) for wx, wy, wr in kcirc])
        crowns = CrownIndex(self._crowns_near(*bb))
        # THE MARSH FROM ITS BOXES (feature 306, the GM: a check against many things means a box was not drawn): a point
        # outside a ring's box is outside the ring, so the rings whose box (a pixel wider) holds the row point are the only
        # ones `point_in_poly` can find it in, and it decides as before.
        marsh = boxed_grid(boxed_polys(wet, 1.0))
        jit, base = self.px(RANK_JITTER_FT), self.px(self.CANOPY_R_FT) * 1.15
        lo, hi = RANK_CONIFER_S
        drawn: list[tuple[float, float, float]] = []
        ink: list[str] = []
        for rx, ry in rank_points(line, half, self.px(RANK_ALONG_FT), self.px(RANK_APART_FT)):
            if not any(b[0] <= rx <= b[2] and b[1] <= ry <= b[3] for b in ground.near(rx, ry)):
                continue
            if any(point_in_poly(rx, ry, it[0]) for it in boxes_meeting(marsh, rx, ry, rx, ry)):
                continue
            x = rx + (self._hjit(rx, ry, 95.0) - 0.5) * 2 * jit
            y = ry + (self._hjit(rx, ry, 96.0) - 0.5) * 2 * jit
            rr = base * (lo + (hi - lo) * self._hjit(rx, ry, 97.0))
            reach = rr + self.CANOPY_PAD
            if self._crown_covers(x, y, rr, [it[:4] for it in rects.near(x, y, reach)], [it[:3] for it in circs.near(x, y, reach)], self.CANOPY_PAD):
                continue
            if not crowns.clear(x, y, rr):
                continue
            crowns.add(x, y, rr)
            drawn.append((x, y, rr))
            ink.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{rr:.1f}" fill="#496733" stroke="#3C5526" stroke-width="0.8"/>')
        self._record_crowns(drawn)
        return drawn, f"<g>{''.join(ink)}</g>"

    def _grove_sides(self: Settlement) -> int:  # type: ignore[misc]
        """How many sides each farm's grove takes on this map (feature 291, `grove_sides.GROVE_SIDES`): the map's own
        `meta.grove_sides` (the scripted plan rolls and records it, a map may pin it), else rolled here from the map's
        seed - on the flood table where `meta.flood_ground` says the farms stand on flood-prone ground - and recorded.

        Research:
            sides rolled per settlement - research/questions/0036-groves-of-trees-around-farmhouses-yashikirin.drawing.html: the
                flood table on flood-prone ground
        """
        meta = self.M["meta"]
        if meta.get("grove_sides") is None:
            table = GROVE_SIDES_FLOOD if meta.get("flood_ground") else GROVE_SIDES
            meta["grove_sides"] = table[knob_rng(self.seed, "grove_sides").randrange(len(table))]
        return int(meta["grove_sides"])

    def _grove_flank(self: Settlement) -> int:  # type: ignore[misc]
        """Which flank completes a cardinal wind's windward pair (`grove_sides.windward_pair`): the map's own
        `meta.grove_flank`, else rolled from its seed and recorded.

        Research: cardinal wind's second face - UNRESEARCHED: rolled per settlement
        """
        meta = self.M["meta"]
        if meta.get("grove_flank") is None:
            meta["grove_flank"] = GROVE_FLANKS[knob_rng(self.seed, "grove_flank").randrange(len(GROVE_FLANKS))]
        return int(meta["grove_flank"])

    def _windward_x(self: Settlement) -> int:  # type: ignore[misc]
        """The horizontal sign of the windward direction: -1 if the wind is from the W (NW/W/SW), +1 if from
        the E (NE/E/SE), 0 for a due N/S wind. Used to keep the garden off the windward wall (the grove's side)."""
        wk = self._windward()
        return -1 if "W" in wk else (1 if "E" in wk else 0)

    def _grove_candidate(self: Settlement, hx: float, hy: float) -> bool:  # type: ignore[misc]
        """Whether this farmhouse is a grove candidate. UNIVERSAL by default (the yashikirin ringed every
        dispersed farmstead, so a grove is drawn wherever there is windward room); meta(grove_prevalence=N<1)
        dials it down for an atypical/sheltered microclimate. Deterministic in the house position (stable
        across regenerations, RNG-independent).

        Research:
            every farm a grove - research/questions/0036-groves-of-trees-around-farmhouses-yashikirin.drawing.html: universal
                unless the map dials it down
        """
        rate = float(self.M["meta"].get("grove_prevalence", 1.0))
        return rate >= 1.0 or int(abs(hx) * 31 + abs(hy) * 17) % 100 < rate * 100

    def _grove_arm_rect(self: Settlement, hx: float, hy: float, hw: float, hh: float, fdx: float, fdy: float, perp: float, d: float, gap: float, lf: float = 1.0) -> tuple[float, float, float, float]:  # type: ignore[misc]
        """One belt ARM's footprint (cx, cy, w, h), depth `d`, just outside the house wall it shelters. An
        N/S arm runs E-W as wide as the house plus `d` (extending `perp` toward the windward corner so the
        two arms wrap it); an E/W arm runs N-S as tall as the house. The depth `d` is how many trees deep the
        stand is - sized so the whole grove is the LARGEST homestead appurtenance (bigger than the house);
        `lf` shortens the arm's run to slip a partial belt past a close neighbor. See research/questions/0036-groves-of-trees-around-farmhouses-yashikirin.html ('How deep is
        the stand?').

        Research:
            arm wraps the windward corner - research/questions/0036-groves-of-trees-around-farmhouses-yashikirin.drawing.html:
                an N or S arm the house's width plus its depth
            arm off the wall - research/questions/0036-groves-of-trees-around-farmhouses-yashikirin.drawing.html: the gap
                the caller gives
        """
        if fdy:  # N or S arm (runs E-W); wraps `perp` toward the windward corner
            return hx + perp * d / 2, hy + fdy * (hh / 2 + d / 2 + gap), (hw + d) * lf, d
        return hx + fdx * (hw / 2 + d / 2 + gap), hy, d, hh * lf  # E or W arm (runs N-S)

    def _grove_fits(self: Settlement, x: float, y: float, w: float, h: float, own: Any) -> bool:  # type: ignore[misc]
        """A grove fits where it is in-bounds, on DRY ground (trees do not grow IN a flooded paddy - but a real
        homestead grove HUGS the paddy bund, so the footprint may abut a field, it just may not overlap it),
        off any lane, and clear of every placed footprint EXCEPT its OWN house. Axis-aligned, so an exact AABB
        test serves - not the conservative half-diagonal circle, which would over-reject the elongated bands.

        Research:
            grove off the crops - research/questions/0071-groves-around-a-southern-chinese-village-the-fengshui-woods-fengshuilin-and-the-dooryard-copse.drawing.html: may abut a paddy or dry plot, never overlap it
            grove off the lanes - research/questions/0071-groves-around-a-southern-chinese-village-the-fengshui-woods-fengshuilin-and-the-dooryard-copse.drawing.html: off every lane corridor (the drawing names the main road)
            grove off the town wall - UNRESEARCHED: every corner 12 px off the rampart
            off a yard's south strip - research/questions/0038-sunlight-and-shade-on-the-farm.drawing.html: a 22 px strip
                south of every threshing yard
        """
        if x < 55 or x > self.W - 55 or y < 88 or y > self.H - 26:
            return False
        if self.bound and not point_in_poly(x, y, self.bound):
            return False
        if self._near_corridor(x, y):  # NOT `_in_blocked`: a grove may sit right at the
            return False  # paddy edge (the 14px field set-back is for buildings, not the windbreak)
        if self._rect_hits((x, y, w, h), self.field_polys):  # the whole grove stays OUT of the flooded paddy
            return False  # (same corner/vertex/edge test, with the bbox pre-filter)
        if self._rect_hits((x, y, w, h), self.dry_polys):  # ...and out of the dry crop strips (hems / garden
            return False  # tracts): trees do not grow in the barley either
        for px, py, pw, ph, *_ in self.placed:  # clear of every footprint but its OWN homestead
            if any(abs(px - ox) < 1.5 and abs(py - oy) < 1.5 for ox, oy in own):
                continue
            if abs(x - px) < (w + pw) / 2 + 2 and abs(y - py) < (h + ph) / 2 + 2:
                return False
        # the town RAMPART blocks a belt arm at the FOOTPRINT level: the corridor test above is
        # center-only, so a wide arm centered clear of the wall could still lap the stroke
        # (first hit: a Hirameki farm's west arm crossing the east face, 2026-07)
        wallp = self.M.get("wall")
        if wallp and any(
            seg_dist(gx, gy, wallp[k], wallp[k + 1]) < 12 for gx, gy in ((x - w / 2, y - h / 2), (x + w / 2, y - h / 2), (x + w / 2, y + h / 2), (x - w / 2, y + h / 2)) for k in range(len(wallp) - 1)
        ):
            return False
        # a threshing yard needs clear sky to its SOUTH (the drying sun); a grove squarely in that sun-corridor
        # would shade it, so keep the grove out of the narrow strip directly south of any yard. (Its OWN grove
        # is N/W, far from its own yard's southern corridor, so this only steers it off a NEIGHBOR's yard.)
        for yd in self.M.get("threshing_yards", []):
            cyx, cyy = yd["x"], yd["y"] + yd["h"] / 2 + 11  # corridor center: a ~22px-deep strip south of the yard
            if abs(x - cyx) < (w + yd["w"]) / 2 and abs(y - cyy) < (h + 22) / 2:
                return False
        return True

    GROVE_RATIO = 6.0  # target grove footprint as a multiple of the house (~6:1 - see research/questions/0036-groves-of-trees-around-farmhouses-yashikirin.html, research/questions/0036-groves-of-trees-around-farmhouses-yashikirin.drawing.html)

    def _find_grove_arms(self: Settlement, hx: float, hy: float, hw: float, hh: float, reserve: Any = None, avoid: Any = ()) -> list[Any]:  # type: ignore[misc]
        """The windward grove's belt arms, AREA-TARGETED to ~GROVE_RATIO x the house footprint (the historical
        ~6:1). Each windward face (N + W for an NW wind) is grown to the deepest belt that fits; if the total
        still falls short of target - because a paddy or neighbor blocks one face - the OTHER, open arm is
        deepened to compensate, so a typical farm's grove still reaches the full ~6:1 and reads as ~40 trees.
        A farm boxed in on BOTH windward faces gets only what fits (a small grove - the genuinely cramped
        minority). Arms are NOT in `placed`, so adjacent groves abut into one continuous windbreak. Returns a
        list of (cx, cy, w, h, face, depth).

        EVERY FACE THE SETTLEMENT ROLLED IS PLANTED (feature 291, FR-010): the windward pair as the deep stand, the others
        as a thin band one tree deep (`_grove_arm_specs`), clear of `avoid` (the farm's own yard and garden). Each face's
        ladder ends on `reserve` - the least grove `_grove_reserve` held for this farm when it was seated, in the same
        face order - so a farm seated with room plants every face; a face with neither (a farm no seat search reserved
        for) is counted in `meta.grove_faces_unplanted`, never dropped unseen.

        Research:
            grove area - research/questions/0036-groves-of-trees-around-farmhouses-yashikirin.drawing.html: about 6 times
                the house, held within 6,000-28,000 sq ft
            windward depth - research/questions/0036-groves-of-trees-around-farmhouses-yashikirin.drawing.html: 1.4 house
                depths, deepened to 3.6 to cover a blocked face
            narrow run - UNRESEARCHED: an arm shortened to 0.55 or 0.5 of its run where a neighbor is close
            every rolled face planted - research/questions/0036-groves-of-trees-around-farmhouses-yashikirin.drawing.html:
                the windward pair deep, the rest one tree
            windward ladder floor - UNRESEARCHED: no shallower than 12 bscale units
            windward stand off the wall - research/questions/0036-groves-of-trees-around-farmhouses-yashikirin.drawing.html: seated 1.5 px off the house wall, against a ~24 ft service strip
        """
        # ...HELD INSIDE THE REGISTER'S RANGE (269 B26; research/questions/0036-groves-of-trees-around-farmhouses-yashikirin.drawing.html): a homestead's own wood is ~6,000-28,000 sq
        # ft, and a lone yashikirin is all the wood its homestead has, so the ~6:1 target never asks for less or more
        _lo, _hi = (self.px(1.0) ** 2 * v for v in HOMESTEAD_WOOD_FT2)
        target = min(_hi, max(_lo, self.GROVE_RATIO * hw * hh))
        own = [(hx, hy)]
        d0 = 1.4 * hh  # base belt depth; the loop deepens to hit the area target
        dcap = 3.6 * hh  # an open arm may deepen this far to cover a blocked one
        dmin = 12 * self.bscale
        step = max(2.0, 0.16 * hh)
        depths: list[Any] = []  # the windward stand: [[(fdx,fdy), perp, depth, run, "deep"], ...]
        thin_arms: list[Any] = []  # the thin bands, seated once: (cx, cy, w, h, face, "thin")
        for i, ((fdx, fdy), perp, kind) in enumerate(self._grove_arm_specs()):
            held = reserve[i] if reserve else None
            if kind == "thin":
                seat = self._thin_arm_seat(hx, hy, hw, hh, fdx, fdy, own, avoid)
                if seat is not None:
                    thin_arms.append((*self._grove_arm_rect(hx, hy, hw, hh, fdx, fdy, 0, self._grove_room_depth("thin"), seat[0], seat[1]), (fdx, fdy), "thin"))
                elif held is not None:
                    thin_arms.append((*held, (fdx, fdy), "thin"))
                else:
                    self.M["meta"]["grove_faces_unplanted"] = int(self.M["meta"].get("grove_faces_unplanted", 0)) + 1
                continue
            last = self._grove_room_depth(kind)
            ladder = [(d0 - k * step, 1.0) for k in range(int((d0 - dmin) // step) + 1)]
            ladder += [(d, 0.55) for d, _ in ladder]  # tight face: a NARROW clump still reads as a windbreak
            ladder.append((last, 0.5))  # ...and last, the footprint `_grove_reserve` held the seat for
            for d, run in ladder:
                cx, cy, w, h = self._grove_arm_rect(hx, hy, hw, hh, fdx, fdy, perp, d, 1.5, run)
                if self._grove_fits(cx, cy, w, h, own) and not any(_boxes_meet((cx, cy, w, h), a) for a in avoid):
                    depths.append([(fdx, fdy), perp, d, run, kind])
                    break
            else:
                if held is not None:  # the held ground IS the last rung; nothing seated after this farm could take it
                    depths.append([(fdx, fdy), perp, last, 0.5, kind])
                else:
                    self.M["meta"]["grove_faces_unplanted"] = int(self.M["meta"].get("grove_faces_unplanted", 0)) + 1

        def total_area() -> float:
            rects = [self._grove_arm_rect(hx, hy, hw, hh, fdx, fdy, perp, d, 1.5, lf) for (fdx, fdy), perp, d, lf, _k in depths]
            return _union_area([(cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2) for cx, cy, w, h in rects])

        guard = 0
        while depths and total_area() < target and guard < 300:  # compensate: deepen the open arm(s)
            grew = False
            for arm in depths:
                if arm[4] != "deep" or arm[2] >= dcap:  # only the windward stand deepens; a thin band stays one tree
                    continue
                nd = min(dcap, arm[2] + step)
                cx, cy, w, h = self._grove_arm_rect(hx, hy, hw, hh, arm[0][0], arm[0][1], arm[1], nd, 1.5, arm[3])
                if self._grove_fits(cx, cy, w, h, own):
                    arm[2] = nd
                    grew = True
                    if total_area() >= target:
                        break
            if not grew:
                break
            guard += 1
        return [(*self._grove_arm_rect(hx, hy, hw, hh, fdx, fdy, perp, d, 1.5, lf), (fdx, fdy), kind) for (fdx, fdy), perp, d, lf, kind in depths] + thin_arms

    def _thin_arm_seat(self: Settlement, hx: float, hy: float, hw: float, hh: float, fdx: int, fdy: int, own: Any, avoid: Any = ()) -> tuple[float, float] | None:  # type: ignore[misc]
        """Where a THIN band stands off its house on the house-first path, as (gap, run), or None. The windward stand hugs
        the wall; a thin band stands on the lee, where the yard and the garden are, so it steps outward from the wall
        until it clears them - `avoid`, the farm's own yard and garden before they are drawn - and until no garden loses
        its morning sun to it (the reach `_east_trees` reads), its run shortened as the deep ladder's is where a neighbor
        is close. Out to two house spans: past that the band is no longer this farm's.

        Research:
            thin band off the plots - research/questions/0036-groves-of-trees-around-farmhouses-yashikirin.drawing.html:
                stepped out past the yard and garden
            band leaves the morning sun - research/questions/0038-sunlight-and-shade-on-the-farm.drawing.html
            band within two house spans - UNRESEARCHED
        """
        t = self._grove_room_depth("thin")
        step = max(2.0, 0.16 * hh)
        gap = 1.5
        while gap <= 2 * max(hw, hh):
            for run in (1.0, 0.5):
                r = self._grove_arm_rect(hx, hy, hw, hh, fdx, fdy, 0, t, gap, run)
                if self._grove_fits(*r, own) and not any(_boxes_meet(r, a) for a in avoid) and not self._shades_a_garden(r, avoid):
                    return gap, run
            gap += step
        return None

    def _shades_a_garden(self: Settlement, rect: tuple[float, float, float, float], extra: Any = ()) -> bool:  # type: ignore[misc]
        """Whether a grove band at `rect` stands hard against a garden's EAST across its height - within the reach
        `_east_trees` reads - and so takes its morning sun: every drawn garden, and `extra` (x, y, w, h) boxes.

        Research:
            garden's morning sun - research/questions/0038-sunlight-and-shade-on-the-farm.drawing.html: a band within 22
                bscale units east of a garden
        """
        cx, cy, w, h = rect
        west, reach = cx - w / 2, 22 * self.bscale
        for gx, gy, gw, gh in [(g["x"], g["y"], g["w"], g["h"]) for g in self.M.get("gardens") or ()] + list(extra):
            gx1 = gx + gw / 2
            if gx1 - 2 <= west < gx1 + reach and cy - h / 2 < gy + gh / 2 and gy - gh / 2 < cy + h / 2:
                return True
        return False

    def _grove_reserve(self: Settlement, hx: float, hy: float, hw: float, hh: float, avoid: Any = ()) -> list[tuple[float, float, float, float]] | None:  # type: ignore[misc]
        """The LEAST grove on every face the settlement rolled, as the rects to hold for it while its neighbors are seated
        (feature 291, plan D8), or None where a face has no room. The house-first path plants its groves in a second pass,
        after every farm is seated, so a grove never takes a neighbor's mandatory yard - and so, unreserved, the room a
        farm was seated for could be taken by a neighbor seated after it (measured: the legacy fixture left 1 to 6 faces
        unplanted). Held in `placed` until the farm's own grove is planted; the second pass's ladders end on these rects."""
        out = []
        for (fdx, fdy), perp, kind in self._grove_arm_specs():
            if kind == "thin":
                seat = self._thin_arm_seat(hx, hy, hw, hh, fdx, fdy, [(hx, hy)], avoid)
                if seat is None:
                    return None
                out.append(self._grove_arm_rect(hx, hy, hw, hh, fdx, fdy, 0, self._grove_room_depth("thin"), seat[0], seat[1]))
                continue
            r = self._grove_arm_rect(hx, hy, hw, hh, fdx, fdy, perp, self._grove_room_depth(kind), 1.5, 0.5)
            if not self._grove_fits(*r, [(hx, hy)]) or any(_boxes_meet(r, a) for a in avoid):
                return None
            out.append(r)
        return out

    def _grove_arm_specs(self: Settlement) -> list[tuple[tuple[int, int], int, str]]:  # type: ignore[misc]
        """The arms of this map's farmstead grove on the house-first path, as ((fdx, fdy), perp, "deep" | "thin"): the faces
        `grove_faces` names for the map's wind and rolled side count (feature 291). A deep north or south arm wraps the
        corner toward the other deep face (`perp`, as `_GROVE_ARMS` always did); a thin band runs the wall alone.

        Research: deep pair and thin bands - research/questions/0036-groves-of-trees-around-farmhouses-yashikirin.drawing.html
        """
        deep, thin, _front = grove_faces(self._windward(), self._grove_sides(), self._grove_flank())
        out: list[tuple[tuple[int, int], int, str]] = []
        for face in deep:
            other = deep[1] if face == deep[0] else deep[0]
            out.append((face, other[0] if face[1] else 0, "deep"))
        return out + [(face, 0, "thin") for face in thin]

    def _grove_room_depth(self: Settlement, kind: str) -> float:  # type: ignore[misc]
        """The depth of the least arm a face may take - what `_grove_room` reserves a seat for, and the last rung of
        `_find_grove_arms`' ladder: 13 ft for the windward stand (one to two crowns), one tree for a thin band.

        Research:
            least windward arm - UNRESEARCHED: 13 bscale units
            least thin band - research/questions/0036-groves-of-trees-around-farmhouses-yashikirin.drawing.html: one tree, 17 ft
        """
        return 13 * self.bscale if kind == "deep" else self.px(THIN_BAND_FT)

    def _grove_room(self: Settlement, hx: float, hy: float, hw: float, hh: float, avoid: Any = ()) -> bool:  # type: ignore[misc]
        """Whether the LEAST grove fits on EVERY face the settlement rolled (feature 291), clear of `avoid` (the farm's
        own yard and garden) - the homestead solver seats a grove farm only where it does and holds that ground
        (`_grove_reserve`); the actual, possibly larger, grove is placed in the second pass."""
        return self._grove_reserve(hx, hy, hw, hh, avoid) is not None

    def _wants_grove(self: Settlement, x: float, y: float) -> bool:  # type: ignore[misc]
        """Whether a house-first farm at (x, y) has a grove at all: none inside a CITY wall (an intramural plot is
        sheltered by the urban fabric and too precious for a tree belt; `meta.inwall_groves` overrides), else
        `_grove_candidate`. How many sides it takes is the settlement's roll, never the farm's.

        Research: no grove inside a city wall - UNRESEARCHED: unless the map overrides
        """
        meta = self.M["meta"]
        wall: Any = self.M.get("wall")
        if wall and meta.get("scale") in CITY_TIER_SCALES and not meta.get("inwall_groves", False) and point_in_poly(x, y, wall):
            return False
        return self._grove_candidate(x, y)

    def _draw_grove(  # type: ignore[misc]
        self: Settlement,
        cx: float,
        cy: float,
        w: float,
        h: float,
        face: Any,
        mix: str = "windbreak",
        cls: str | None = None,
        tally: dict[str, int] | None = None,
        bamboo: bool = True,
        bamboo_box: tuple[float, float, float, float] | None = None,
    ) -> int:
        """Draw one windbreak/grove clump as a DENSE MIXED STAND - overlapping canopies packed into a real
        grove (not a few scattered trees), of three species: tall EVERGREEN conifer (darker, larger crown - the
        windbreak backbone, cedar/pine), DECIDUOUS broadleaf (mid green - timber and fruit, zelkova/persimmon),
        and, in the windbreak mix, BAMBOO low under the crowns, inked only in the gaps and along the edge (269 B29;
        `GROVE_BAMBOO_SHARE`). Returns the count of bamboo marks inked. `mix` picks the species blend: 'windbreak' is
        conifer-backed (the sheltering wall - the yashikirin and the fengshui back belt); 'dooryard' is fruit and other
        broadleaf with NO bamboo and NO conifer (the leafy fruit greenery scattered among village houses).
        The village belt draws one of the `windbreak_belt` knob's two forms (269 B30, research/questions/0072-shelter-belts-on-a-villages-windward-side-bofurin.html): a 'conifer_led'
        clump draws only the lesser broadleaf and the bamboo between the belt's rows of conifers, which `_belt_ranks`
        seats for the whole belt first; 'mixed_broadleaf' is rounded broadleaf crowns in the woods' irregular size mix,
        no conifer. `tally`, when given, counts the crowns drawn by kind. `bamboo=False` draws no bamboo in any mix: a farm
        grove whose household rolled no bamboo stand (feature 291).
        Distinct from the big s.forest area feature and the striped kitchen-garden bed. Species and placement
        are seeded by position (stable across regenerations). Canopy count scales with footprint area.

        Research:
            windbreak conifer share - research/questions/0072-shelter-belts-on-a-villages-windward-side-bofurin.html: 48% of a windbreak's crowns cedar (the 1987 Kashima count), the dominant tree (Takehara)
            crowns per clump - research/questions/0080-how-thickly-trees-stood-in-a-wood-and-how-wide-their-crowns.drawing.html: one crown per `GROVE_CROWN_AREA` of clump (48 sq px at the town grain), rounded, with no floor and no cap
            bamboo under the crowns - research/questions/0075-bamboo-groves-chikurin.drawing.html: 8% of a windbreak clump,
                inked only in the gaps; none in the dooryard or alder mixes
            dooryard mix - research/questions/0036-groves-of-trees-around-farmhouses-yashikirin.drawing.html:
                fruit broadleaf, no conifer
            crown size - research/questions/0080-how-thickly-trees-stood-in-a-wood-and-how-wide-their-crowns.drawing.html: the
                mean crown radius, 0.72-1.05 or a quarter 1.25-1.7 of it, a conifer 15% wider
            thin band end to end - UNRESEARCHED: a thin band's few trees spread along its length
            crown over no roof or wellhead - research/questions/0071-groves-around-a-southern-chinese-village-the-fengshui-woods-fengshuilin-and-the-dooryard-copse.drawing.html, research/questions/0072-shelter-belts-on-a-villages-windward-side-bofurin.drawing.html: no crown on a building, and none round a wellhead in a belt
            bamboo patch forced - GUESS research/questions/0075-bamboo-groves-chikurin.drawing.html: a farm grove keeps its bamboo as a patch inside it, an item there drawn as bamboo in any mix
            crowns out of the plots' sun - research/questions/0038-sunlight-and-shade-on-the-farm.drawing.html: every mark held out of the sun ground, bamboo at BAMBOO_SHADE_FT
            crown under no crown - research/questions/0080-how-thickly-trees-stood-in-a-wood-and-how-wide-their-crowns.drawing.html
            alder in the marsh - research/questions/0074-reed-beds-and-the-marshs-edge-yoshihara.drawing.html
            conifer crown under a persimmon's crown - research/questions/0046-fruit-trees-in-the-farmyard-persimmon-chestnut-and-plum-kaki.drawing.html: a conifer crown refused under a yard persimmon's crown, the grove giving way round it
            lesser crown over an earlier stand's conifer - CONVENTION: a lesser crown refused over an earlier stand's conifer, which decides only paint order (conifers painted last)
            clump glyph - CONVENTION: one disc per crown, conifers dark and painted last, no trunks
            conifer-led clump's lesser share - GUESS research/questions/0072-shelter-belts-on-a-villages-windward-side-bofurin.drawing.html: a conifer-led clump throws LESSER_ROLL_SHARE (0.1) of its crowns as lesser broadleaf; the page names the lesser broadleaf, the share a guess
            lesser broadleaf crown size - research/questions/0080-how-thickly-trees-stood-in-a-wood-and-how-wide-their-crowns.drawing.html: LESSER_BROADLEAF_S, 0.75 to 0.85 of the mean radius (the page's 0.75 to 1.4)
        """
        # SCOPED (2026-08-08): a homestead grove's crowns are decoration keyed to the grove itself.
        with self.rng_scope("grove", cx, cy, w, h):
            bs = self.bscale / GROVE_RENDER_GRAIN  # render scale relative to the town grain
            lift = crown_lift(self.bscale)  # every crown is drawn this far up the sheet from its throw (`crown_reach` reads it)
            st = random.getstate()
            random.seed(int(abs(cx) * 5 + abs(cy) * 3 + round(w)))
            n = round(w * h / (bs * bs * GROVE_CROWN_AREA))  # one crown per ~48 px^2 at 2 ft/px (a ~5 m crown), the page's density alone (0080)
            # BAMBOO LEFT THE MIX (feature 133 T47, GM 2026-08-27). It used to be 20% of a windbreak's
            # crowns and 45% of a dooryard copse's, drawn one culm at a time - 315 six-foot glyphs on
            # Inashiro that no one could see as bamboo, and not how bamboo grows: a stand is a clonal
            # thicket with a hard edge, not a seasoning through a cedar belt. Bamboo is now its own
            # feature (`bamboo_stand`, the `bamboo` knob). The windbreak is cedar-backed with broadleaf;
            # the dooryard copse is fruit broadleaf.
            # ...AND CAME BACK LOW, UNDER THE TREES (269 B29; research/questions/0075-bamboo-groves-chikurin.html). The Tonami grove held many bamboo stands mixed with its cedar from the west round to the north,
            # and the Sendai igune's bamboo filled the bare lower part of the trees against the wind: bamboo was one of
            # the windbreak's own plants, low under its crowns. So the windbreak mix carries a small share of bamboo
            # items, and each is drawn only where a plan view would see it - in a gap between the crowns or past the
            # clump's edge - as the stand glyph's culm mark (`bamboo_stand`, a map drawing convention), not a crown.
            # The share is a GUESS (no page gives one; "a grove is mostly trees with bamboo among them"): 8% of the
            # items, taken from the broadleaf so the cedar backbone keeps its 48%. The dooryard and alder mixes carry none.
            # The village belt's two forms (269 B30) carry the same bamboo share; a conifer-led belt's conifers are its rows,
            # seated for the whole belt by `_belt_ranks`, so its clumps throw only the lesser crowns; a mixed broadleaf belt has none.
            b_th = (
                GROVE_BAMBOO_SHARE if bamboo and mix in ("windbreak", *WINDBREAK_BELT_FORMS) else 0.0
            )  # `bamboo=False`: a farm that rolled none (feature 291)  # dooryard = fruit broadleaf, no conifer; alder = broadleaf only
            c_th = b_th + 0.48 if mix == "windbreak" else b_th
            if mix == "conifer_led":
                rows = max(0.0, (w - 4) * (h - 4)) / (self.px(RANK_ALONG_FT) * self.px(RANK_APART_FT))  # the row conifers this clump's box holds
                n = max(1, round(n * LESSER_ROLL_SHARE))
                # ...and the bamboo stays GROVE_BAMBOO_SHARE of ALL the clump's items (269 B29), rows included, not of the fewer rolls
                b_th = c_th = min(1.0, GROVE_BAMBOO_SHARE * (rows + n) / n)
            items: list[Any] = []
            # A THIN BAND'S FEW TREES RUN ITS WHOLE LENGTH (feature 310, the homestead grove's glyph-check on Kashikawa): a farm
            # grove's thin side (the dooryard mix, a band at least twice as long as it is wide) carries four or five items, and
            # thrown anywhere in the box they left the band's end bare on 2 farms in 20 - a tree standing 20-30 ft clear of the
            # north band it joins. So the items are spread END TO END along the long axis, the first and last at the band's
            # two ends and the rest jittered round their even steps: an item in each of n equal stretches still left the
            # first crown up to a stretch from the joint (12.7 and 17.1 ft clear of the north band on Kashikawa, the
            # homestead grove's third glyph-check round), where the band must run on from the north band's corner.
            strata = mix == "dooryard" and max(w, h) >= 2.0 * min(w, h)
            for k in range(n):
                px = random.uniform(-w / 2 + 2, w / 2 - 2)
                py = random.uniform(-h / 2 + 2, h / 2 - 2)
                if strata:
                    jig = random.random() - 0.5
                    t = 0.5 if n == 1 else (k if k in (0, n - 1) else k + 0.6 * jig) / (n - 1)  # ends pinned, the rest near their steps
                    if h >= w:
                        py = -h / 2 + 2 + t * (h - 4)
                    else:
                        px = -w / 2 + 2 + t * (w - 4)
                roll = random.random()
                kind = "bamboo" if roll < b_th or in_box(cx + px, cy + py, bamboo_box) else ("conifer" if roll < c_th else "broadleaf")
                band = LESSER_BROADLEAF_S if mix == "conifer_led" else ((1.25, 1.7) if random.random() < 0.25 else (0.72, 1.05))  # a few emergent crowns over many small
                size = random.uniform(*band)
                items.append((px, py, kind, size))
            # ORDER-SENSITIVE: this reads M, so it can only avoid structures that ALREADY EXIST when the
            # grove is drawn. That is why the yashikirin arms draw after their farmstead's house and why
            # village_grove() is called late in a gen (see "DRAW ORDER" in CLAUDE.md before moving either).
            # NO CROWN ON A ROOF OR A WELLHEAD (GM 2026-07-25). A yashikirin belt is drawn hard against the
            # house it shelters and a village copse threads between the dwellings, so the stand is filtered
            # tree-by-tree rather than pushed back as a whole: it THINS where it would cover a building and
            # keeps its shape everywhere else. Crown centers below are relative to (cx, cy); keep-outs absolute.
            # THE PREFILTER MUST REACH AS FAR AS A CROWN DOES (feature 134 T50, 2026-08-29). Both lists
            # below are PREFILTERED to this box, and the pad was a flat `9 * bs` while a crown's own
            # radius is `px(CANOPY_R_FT) * s * 1.15` with `s` as high as 1.7 - about 14.5 px on a hamlet.
            # So a building standing 10-14 px outside the stand's box was not in `krect` at all, and
            # `_crown_covers` then cleared a crown that plainly covered it: cohort seed 9's farmhouse at
            # (1938, 2655) sat under a 14.4 ft crown from a copse whose box ended 10.7 px short of it,
            # and `structures_clear_of_trees` read it correctly. A prefilter that prunes a candidate the
            # test would have rejected is not an optimization, it is a silent wrong answer - the same
            # rule this engine states for every other index ("the index prunes; it never decides").
            _cpad = max(9.0 * bs, self.px(self.CANOPY_R_FT) * 1.7 * 1.15 + 1.0)
            krect, kcirc = self._canopy_keepouts((cx - w / 2 - _cpad, cy - h / 2 - _cpad, cx + w / 2 + _cpad, cy + h / 2 + _cpad))
            # ...AND EVERY YARD'S AND BED'S SUN GROUND for the crowns (feature 310, GM 2026-10-02: "no canopy trees should be exempt"),
            # and every culm mark below the same at bamboo's own reach (feature 315: the timber bamboos stand as tall as the tree)
            ksun = krect + self._sun_keepouts((cx - w / 2 - _cpad, cy - h / 2 - _cpad, cx + w / 2 + _cpad, cy + h / 2 + _cpad))
            _near = self._crowns_near(cx - w / 2 - _cpad, cy - h / 2 - _cpad, cx + w / 2 + _cpad, cy + h / 2 + _cpad)  # the crowns of earlier clumps and stands (GM 2026-08-28)
            drawn: list[tuple[float, float, float]] = []
            # THE CONIFERS ARE PAINTED LAST (feature 294 B5b): the clump's lesser crowns first, its conifers over them, and a
            # lesser crown that would lie over an earlier clump's conifer is not drawn (`over_a_conifer`) - so no broadleaf is
            # ever inked over a cedar (Kashikawa's and Mizuguchi's farm groves drew 199 and 108 when this was written)
            _cones = [
                c
                for c in (getattr(self, "_conifer_crowns", None) or [])
                if cx - w / 2 - _cpad - c[2] <= c[0] <= cx + w / 2 + _cpad + c[2] and cy - h / 2 - _cpad - c[2] <= c[1] <= cy + h / 2 + _cpad + c[2]
            ]  # a conifer whose DISC reaches the box
            # ...AND NO CONIFER WHERE A YARD PERSIMMON WILL BE PAINTED OVER IT (GM 2026-10-02): the persimmon is seated with its
            # household, behind the house where a front yard keeps its sun, which is where the farm's grove stands; it is inked
            # on top after every grove, so a cedar under its crown would read as the broadleaf-over-conifer case (B5b)
            _trees = [
                (t[0], t[1], t[2] / 2)
                for t in ((rec.get("geom") or {}).get("fixtures", {}).get("persimmon") for rec in self.M.get("houses") or ())
                if t is not None and cx - w / 2 - _cpad - t[2] <= t[0] <= cx + w / 2 + _cpad + t[2] and cy - h / 2 - _cpad - t[2] <= t[1] <= cy + h / 2 + _cpad + t[2]
            ]
            high: list[str] = []
            # ...TRANSLATED TO THE TENTH, as its crowns are written (feature 315): rounded to the whole pixel, every crown was inked up
            # to half a pixel from where its tests seated it, and a Mizuguchi broadleaf tested clear of a cedar was drawn over it (B5b)
            g = [f'<g transform="translate({cx:.1f},{cy:.1f})">']
            # Draw back-to-front so the stand layers with depth. Each CROWN is one tree at real size (~5-6 m; a few
            # emergents larger) - that is the to-scale reading, and it is unchanged. We deliberately DROP two kinds
            # of detail that cost ~half the stand's SVG elements without buying scale accuracy: the per-tree trunk
            # (hidden under the closed canopy anyway), and the 6-culm bamboo clump - a real *take* is DOZENS of
            # culms, so any handful is already symbolic, and one compact culm+top reads the same. See the foliage
            # comparison (the 'to scale, compact bamboo' option) for the before/after; groves stay to scale, the
            # SVG + rsvg raster roughly halve.
            for px, py, kind, s in sorted(items, key=lambda t: t[1]):
                # THE BAMBOO ITEM WAS UNREACHABLE (feature 146: `b_th` was 0.0 in both mixes) until 269 B29 gave the
                # windbreak a share; a bamboo item draws no crown - it stands under them, and is inked below, after
                # every crown of the clump is known, only where it shows.
                if kind == "bamboo":
                    continue
                # ONE CROWN AT THE RESEARCHED SIZE (GM 2026-08-28, feature 134 T36). This was `(4.6 | 4.0) * s * bs`,
                # a pixel radius calibrated at the village's 2 ft/px ("a ~5-6 m canopy") and never rescaled by ftpx:
                # at the hamlet's 1 ft/px the belt drew 9 ft crowns beside the commons' 18 ft ones (measured on
                # Inashiro: belt median r 4.5 ft, commons 9.0). Now the same CANOPY_R_FT the woods and the commons
                # use, in real feet (research/questions/0080-how-thickly-trees-stood-in-a-wood-and-how-wide-their-crowns.drawing.html); a conifer 15% wider,
                # the old ratio. A village (ftpx 2, bscale 1) gets 4.25 px, within a pixel of what it drew before.
                rr = self.px(self.CANOPY_R_FT) * s * (1.15 if kind == "conifer" else 1.0)
                # ALDER AT THE REED EDGE (feature 261): the woody stage of a marsh margin is alder or willow, never pine
                # (research/contents.json#vegetation, Reed beds and the marsh's edge), so a belt crown standing in the marsh is drawn as one - a
                # blue-gray green set apart from the belt's own two greens and its cedar, a map drawing convention (the
                # real foliage is a plain dark green; the tint is chosen so the wet stand reads apart)
                col = random.choice(ALDER_GREENS) if mix == "alder" else ("#496733" if kind == "conifer" else random.choice(["#7C9A4E", "#6E8B43"]))
                if self._crown_covers(cx + px, cy + py - lift, rr, ksun, kcirc, self.CANOPY_PAD):
                    continue
                # TWO SCANS, NOT A GRID (feature 284, A6 withdrawn, specs/284 research R7): a crown grid per clump was exact but
                # slower - a clump's nearby crowns are few, and filing them cost more than walking them (the windbreak 8-12%
                # slower on three pool hamlets against main).
                if not self._crown_seat_clear(cx + px, cy + py - lift, rr, _near) or not self._crown_seat_clear(cx + px, cy + py - lift, rr, drawn):
                    continue  # a crown centered under an already-drawn crown is an understory stem, not canopy (GM 2026-08-28; woods._crown_seat_clear)
                if kind != "conifer" and over_a_conifer(cx + px, cy + py - lift, rr, _cones):
                    continue
                if kind == "conifer" and any(over_a_conifer(tx, ty, tr, [(cx + px, cy + py - lift, rr)]) for tx, ty, tr in _trees):
                    continue
                drawn.append((cx + px, cy + py - lift, rr))
                # ONE DISC PER CROWN, conifer included (GM 2026-09-27). A conifer used to carry a second, darker
                # disc at 40% of its radius (a "dense dark apex"); the GM read it as a trunk, which a plan view
                # cannot show, and it was an unrecorded map convention. The darker fill and the 15% larger
                # crown already tell a conifer from a broadleaf.
                (high if kind == "conifer" else g).append(f'<circle cx="{px:.1f}" cy="{py - lift:.1f}" r="{rr:.1f}" fill="{col}" stroke="#3C5526" stroke-width="0.8"/>')
                if kind == "conifer":
                    self._conifer_crowns = [*(getattr(self, "_conifer_crowns", None) or []), (cx + px, cy + py - lift, rr)]
                if tally is not None:
                    tally[kind] = tally.get(kind, 0) + 1
            # THE BAMBOO SHOWS IN THE GAPS AND ALONG THE EDGE (269 B29, research/questions/0075-bamboo-groves-chikurin.html): a bamboo item under a drawn
            # crown, this clump's or an earlier one's, is hidden from above and not inked; one in the open, clear of
            # every building and wellhead, is the culm mark, painted UNDER the crowns (first in the group) because it
            # is the low layer.
            culms: list[str] = []
            _mark_r = 3.0 * bs  # the mark's own reach: two culms 1.2 ft apart and a leafy fork ~2.5 ft round their tops
            # ...AND NONE IN A YARD'S OR BED'S SUN (feature 315, GM 2026-10-02): a bamboo stand throws the shadow of the timber
            # bamboos' 10 m, so a culm mark keeps out of every plot's sun ground at `BAMBOO_SHADE_FT`, as the crowns above do at theirs
            kbam = krect + self._sun_keepouts((cx - w / 2 - _cpad, cy - h / 2 - _cpad, cx + w / 2 + _cpad, cy + h / 2 + _cpad), BAMBOO_SHADE_FT)
            marks: list[tuple[float, float, float]] = []
            for px, py, kind, _s in items:
                if kind != "bamboo":
                    continue
                bx, by = cx + px, cy + py
                if any((bx - ox) ** 2 + (by - oy) ** 2 < orr**2 for ox, oy, orr in (*drawn, *_near)):
                    continue
                if self._crown_covers(bx, by, _mark_r, kbam, kcirc, self.CANOPY_PAD):
                    continue
                culms.append(bamboo_mark(px, py, bs, self._hjit(bx, by, 93.0), self._hjit(bx, by, 94.0)))
                marks.append((round(bx, 1), round(by, 1), round(_mark_r, 1)))
            self.M.setdefault("bamboo_marks", []).extend([list(m) for m in marks])  # every inked mark, for the map's check (feature 315)
            g[1:1] = culms
            g.extend(high)
            g.append('</g>')
            self.add(''.join(g), cls=cls)
            self._record_crowns(drawn)
            random.setstate(st)
            return len(culms)
