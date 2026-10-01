"""A kitchen garden's sun on a hand-drawn sheet (feature 283; research homesteads 044).

The GM, 2026-09-28: *"a garden needs a certain amount of sunlight per day ... That feels like it should be an automated
check that gets run on hand-drawn diagrams that have gardens for distance between the gardens and things that are known
to produce shade, such as buildings and trees."* The scripted maps seat a bed by the sun rules of research homesteads 030,
040 and 043; this check holds what a person draws to the same sun.

HOW IT COUNTS (research homesteads 044, "The rule a hand-drawn plan is checked by"): the record's sun - 38 degrees north in
the autumn shoulder month, the season a bed's open ground is set by - is walked through the day in half hours; at each
step every drawn thing that stands up casts its shadow away from the sun, as far as its height over the tangent of the sun's
elevation, and the half hour counts as lit when at least half the bed is out of every shadow. A sun bed (the default)
needs 6 lit hours; a half-shade bed, declared on the garden's element as `data-bed="half-shade"`, needs 3, and for it a
tree's shadow is dappled light rather than shade (the source: half-shade crops also grow under light through leaves all
day). Every height is the LEAST the record gives, so a bed the check fails is surely shaded.
"""

from __future__ import annotations

import math
import re
from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:  # the names for the type checker; each function imports shapely when it runs (the engine loads no heavy
    # library at import time - tests/test_memory.py)
    from shapely.geometry import Polygon
    from shapely.geometry.base import BaseGeometry

from ...interactive.sheet import element_kinds
from .grids import FTPX
from .parse import ParsedPlan, Rect

LAT_DEG: float = 38.0  # the record's latitude for every shadow it casts (research 0038)
DECL_DEG: float = -8.5  # the shoulder month: at 38N it gives the record's 3pm sun, 27-28 deg high at azimuth ~232 (0038)
STEP_H: float = 0.5  # the day walked in half hours
LIT_SHARE: float = 0.5  # a half hour is lit when at least half the bed is out of shadow (homesteads 044, a guess)
SUN_BED_H: float = 6.0  # sun crops - daikon, eggplant, cucumber, beans - want about 6 hours or more (homesteads 044)
HALF_SHADE_BED_H: float = 3.0  # half-shade crops do with 3 to 4 (homesteads 044)
BUILDING_FT: float = 20.0  # the farmhouse ridge the record casts a building's shadow from (homesteads 043) - a least height
WALL_FT: float = 1.6 / 0.3048  # the surviving earth wall's 1.6 m (buildings 490)
TREE_FT: float = 10.0 / 0.3048  # a working, pruned belt's 10 m (0038); an untended stand is 15-25 m
SMALL_BUILDING_FT: float = 6.0  # a roofed thing under SMALL_BUILDING_SQFT - a privy, a hokora, a covered way - at the least height a person stands under (a guess)
SMALL_BUILDING_SQFT: float = 100.0
# What a sheet draws that does not stand up to cast a garden's shadow: ground and water features, a building's own parts (under
# its roof, which casts for them) and furniture below head height. Everything else the parser counts as a structure casts.
NOT_STANDING: frozenset[str] = frozenset(
    {"basin", "door", "engawa", "hearth", "notice board", "weapon rack", "stone lantern", "tax barge", "magistrate's dais", "clerks' seats", "well", "shrine altar", "wood-kami altar"}
)
MIN_SUN_DEG: float = 3.0  # below this the sun is on the horizon: its shadows run off the sheet and it grows nothing
MIN_BED_PX: float = 300.0  # a garden element smaller than this (a label box, a border tick) is not a bed
GARDEN_KIND = "vegetable garden"
_BED_ATTR = re.compile(r'data-bed="([^"]+)"')


@dataclass(frozen=True)
class Caster:
    """One thing that stands up and casts a shadow: its footprint, its height in ft, what it is, whether it is a tree."""

    shape: Polygon
    height_ft: float
    what: str
    tree: bool = False


def sun_at(hour: float, lat_deg: float = LAT_DEG, decl_deg: float = DECL_DEG) -> tuple[float, float]:
    """The sun's (elevation, azimuth) in degrees at solar `hour`; azimuth clockwise from north."""
    h = math.radians(15.0 * (hour - 12.0))
    la, d = math.radians(lat_deg), math.radians(decl_deg)
    el = math.asin(math.sin(la) * math.sin(d) + math.cos(la) * math.cos(d) * math.cos(h))
    az = math.atan2(math.sin(h), math.cos(h) * math.sin(la) - math.tan(d) * math.cos(la)) + math.pi
    return math.degrees(el), math.degrees(az) % 360.0


def shadow(caster: Caster, el_deg: float, az_deg: float) -> BaseGeometry:
    """The ground a caster darkens with the sun at (el, az): its footprint swept away from the sun by its shadow's length.
    On a sheet north is up and a px is 1/FTPX ft, so the shadow runs (-sin az, +cos az) in px."""
    from shapely.geometry import Polygon
    from shapely.ops import unary_union

    length = caster.height_ft / math.tan(math.radians(el_deg)) * FTPX
    dx, dy = -math.sin(math.radians(az_deg)) * length, math.cos(math.radians(az_deg)) * length
    ends = [(x + dx, y + dy) for x, y in caster.shape.exterior.coords]
    return unary_union([caster.shape, Polygon(ends), Polygon(list(caster.shape.exterior.coords) + ends).convex_hull])


def lit_hours(bed: Polygon, casters: list[Caster], half_shade: bool = False) -> float:
    """Hours of the day at least LIT_SHARE of the bed is in direct sun (for a half-shade bed a tree's shadow is dappled light)."""
    from shapely.ops import unary_union

    hours = 0.0
    steps = int(24 / STEP_H)
    for k in range(steps):
        el, az = sun_at(k * STEP_H)
        if el < MIN_SUN_DEG:
            continue
        shade = [shadow(c, el, az) for c in casters if not (half_shade and c.tree)]
        lit = bed.difference(unary_union(shade)).area if shade else bed.area
        if lit >= LIT_SHARE * bed.area:
            hours += STEP_H
    return hours


def _rect_poly(r: Rect) -> Polygon:
    from shapely.geometry import box

    return box(r.x, r.y, r.x + r.w, r.y + r.h)


def gardens(plan: ParsedPlan, text: str) -> list[tuple[Rect, bool]]:
    """Every drawn kitchen bed - a rect of the `vegetable garden` kind - and whether it is declared a half-shade bed. A
    sheet that tags no bed is not parsed for kinds (a bare test sheet has no tagged structure to parse)."""
    if f'data-kind="{GARDEN_KIND}"' not in text:
        return []
    kinds = element_kinds(text)
    out = []
    for r in plan.fills:
        if kinds.get(r.pos) == GARDEN_KIND and r.w * r.h >= MIN_BED_PX:
            tag = text[r.pos : text.find(">", r.pos)]
            m = _BED_ATTR.search(tag)
            out.append((r, bool(m and m.group(1) == "half-shade")))
    return out


def casters(plan: ParsedPlan, text: str, bed: Polygon) -> list[Caster]:
    """Everything the sheet draws that stands up: its buildings, its walls (the compound's and its court dividers) and its
    trees - never the bed itself, nor what NOT_STANDING names."""
    from shapely.geometry import Point

    kinds = element_kinds(text)
    out: list[Caster] = []
    for r in plan.structures:
        p = _rect_poly(r)
        kind = kinds.get(r.pos)
        if kind == GARDEN_KIND or kind in NOT_STANDING or p.intersection(bed).area > 0.5 * bed.area:
            continue
        small = r.w * r.h / (FTPX * FTPX) < SMALL_BUILDING_SQFT
        out.append(Caster(p, SMALL_BUILDING_FT if small else BUILDING_FT, kind or "building"))
    out += [Caster(_rect_poly(w), WALL_FT, "wall") for w in (*plan.wall_segs, *plan.dividers)]  # a court divider is a wall too
    out += [Caster(Point(t.x + t.w / 2, t.y + t.h / 2).buffer(t.w / 2, 16), TREE_FT, "trees", tree=True) for t in plan.trees]
    return out


def shaders(bed: Polygon, cs: list[Caster], half_shade: bool = False) -> list[str]:
    """What takes the bed's sun: the casters whose shadow reaches it in some daylight half hour, by what they are."""
    hit: dict[str, int] = {}
    steps = int(24 / STEP_H)
    for c in cs:
        if half_shade and c.tree:
            continue
        for k in range(steps):
            el, az = sun_at(k * STEP_H)
            if el >= MIN_SUN_DEG and shadow(c, el, az).intersects(bed):
                hit[c.what] = hit.get(c.what, 0) + 1
                break
    return [f"{what} ({n})" if n > 1 else what for what, n in sorted(hit.items(), key=lambda kv: (-kv[1], kv[0]))]


def garden_sun(plan: ParsedPlan, text: str) -> list[str]:
    """Each kitchen bed that gets too little sun, with its hours, the hours it needs and what shades it."""
    out = []
    for r, half in gardens(plan, text):
        bed = _rect_poly(r)
        cs = casters(plan, text, bed)
        got = lit_hours(bed, cs, half)
        need = HALF_SHADE_BED_H if half else SUN_BED_H
        if got < need:
            what = ", ".join(shaders(bed, cs, half)) or "nothing drawn"
            out.append(
                f"the {'half-shade ' if half else ''}kitchen bed at ({r.x:.0f},{r.y:.0f}), {r.w / FTPX:.0f} by {r.h / FTPX:.0f} ft, "
                f"has {got:g} h of sun in the shoulder month and needs {need:g} (research homesteads 044) - shaded by {what}"
            )
    return out
