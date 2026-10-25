"""A household's farmstead fixtures laid as PARTS of its homestead bundle (feature 287, homes H32, plan M5 and D9).

THE GM'S OWN DESIGN, 2026-09-12 (the fixtures' docstring): *"Our entire approach to homesteads is to place them and then
determine what they have and then move on and place more homesteads."* The privy, the heap, the bath, the coop, the
woodpile, the household shrine and the yard persimmon were seated after the lane web, in whatever ground the web and the
neighbors had left, and a fixture with no seat was recorded short (`meta.farm_fixtures_unseated`: Kuwabata drew 3 of its
15 woodpiles). They are the household's now: the lot decides which kinds a household keeps (`rolling/lot.py`, a quota by
seat ordinal), and this module lays each one in the house's own frame beside the parts already laid - the house, the
yard, the garden beds, the kura, the byre, the well pocket - so the bundle's envelope admits the household only with room
for its fixtures, and no later stage can take that room (it is inside the bundle's reserved box). What is laid here is
drawn where it was laid (`hamletgen/homesteads/fixtures.py`). The retirement house (269 B42), the family's second roof,
is laid the same way and first, on the settlements that keep the form (`hamletgen/homesteads/retirement.py`): searched
for after the fixtures, 7 of cohort seed 54's 9 found room.

Every seat table is the one the late placer read (research/contents.json#homesteads, each fixture's own section - the privy's at "Farm privies and their night soil (benjo)" - the attested seats
labeled there), in the house's unturned frame: +y the sunny front where the yard is, -y the back wall, the kura on the
north wall. A seat is taken when its box clears every part laid before it by the wall gap; failing every recorded seat, a
fixture is offered the same seats stepped outward a pace at a time - still its own plot, where the ground past the parts
is free by construction (the parts are finite, the steps are not) - except the two kinds whose rule is the seat itself
(feature 280, the modern-only forms eliminated): the BATH is a room of the house, abutting its front wall beside the main
door, the stable wing's end wall or the floored rooms' end wall (`bath_room_seats`, `joined_to_house`; M22), offered every
place along those walls; and the WOOD SHED stands a ken off a wall of its steading, never walked out across the dooryard
(`shed_off_a_wall`; M21), offered every place a ken off the walls. The privy and the bath room take a size rolled per
household (`fixture_ft`: the Kakimochi table's sixteen privies, a room 6 ft out by 6-12 ft along).

Research: plumbing - NONE
"""

from __future__ import annotations

import math
from collections.abc import Callable, Iterable, Iterator, Mapping, Sequence
from dataclasses import dataclass
from functools import lru_cache
from itertools import chain
from typing import Any

from ..farm_fixtures import FIXTURE_FT, PERSIMMON_CROWN_FT, PIT_FT, kura_rect
from .tree_shade import crown_in_ground, sun_ground

Rect = tuple[float, float, float, float]  # (center x, center y, width, height), the house's unturned frame

#: The order the kinds are laid in: the retirement house first - a second roof of the family, off the back wall or a flank
#: (269 B42), the largest part after the kura; then the two whose rule IS the seat - the bath room on a wall of the house,
#: the wood shed a ken off a wall of the steading - so the walls are theirs before the free-standing kinds take the ground
#: by them; then the late placer's order; the persimmon last - its crown over no roof and out of the yard's and beds' sun.
FIXTURE_ORDER = ("retirement", "bath", "woodpile", "privy", "manure", "coop", "shrine", "grave", "persimmon")
"""Research: laying order - GUESS: no source could speak to it, a value of ours (feature 417 T36 pass P1, 2026-10-25); the retirement house, the bath room and the wood shed take the walls first"""

WALL_GAP_FT = 3.5  # a fixture's edge off the wall or part it stands by: the review measured -0.3 ft at 3.0 against the drawn wall
"""Research: fixture wall gap - GUESS: searched, the record silent (feature 417 T36 pass P1, 2026-10-25); 3.5 ft off the wall or part it stands by"""
STEP_FT = 8.0  # the outward pace a fixture takes when every recorded seat is taken (the late placer's own rung)
"""Research: outward pace - GUESS: no source could speak to it, a value of ours (feature 417 T36 pass P1, 2026-10-25); 8 ft further out when every recorded seat is taken"""
OUT_STEPS = 24  # paces offered: 192 ft, past any bundle's parts
WALL_SLIDE_FT = 4.0  # the spacing of the places offered along a wall to a bath room or a wood shed
PRIVY_YARD_STEP_FT = 6.0  # HELD (feature 328 wave 9): the yard outhouse a ken past the wall gap - its edge a ken plus the gap off the wall
"""Research: yard outhouse off the back wall - research/questions/0047-farm-privies-and-their-night-soil-benjo.drawing.html: held at a ken plus the wall gap, past the page's ken - at a ken Kuwabata's re-seated homesteads leave one household only a way that zigzags across its neighbor's door end; the found row settlement/rolling/gap_ways.py::_way_for#a household whose only ways zigzag re-seated"""
PRIVY_FRONT_STEP_FT = 8.0 - WALL_GAP_FT  # the front-yard privy's edge 8 ft out from the front wall, past the wall gap (GUESS)
"""Research: front privy off the front wall - GUESS research/questions/0047-farm-privies-and-their-night-soil-benjo.drawing.html: 8 ft, the page's own guess"""
PRIVY_SUN_MIN_FT = 18.0  # the sun-side search's radii, 18 to 48 ft (`PRIVY_SUN_MAX_FT`'s reasons, fixtures.py)
"""Research: sun-side search start - research/questions/0047-farm-privies-and-their-night-soil-benjo.drawing.html: from 18 ft"""
PRIVY_SUN_MAX_FT = 48.0
"""Research: sun-side search reach - research/questions/0047-farm-privies-and-their-night-soil-benjo.drawing.html: to 48 ft"""
PRIVY_SUNNY_SHARE = 0.727  # Wang & Ochiai 2022: 72.7% of outhouses SE to S (the GM, 2026-08-29: used literally)
"""Research: privies on the sunny side - research/questions/0047-farm-privies-and-their-night-soil-benjo.drawing.html: 72.7%"""
WOODSHED_STEP_FT = 6.0  # HELD (feature 328 wave 9, re-measured wave 51): the wood shed a ken past the wall gap - its edge a ken plus the gap off its wall
"""Research: wood shed off its wall - GUESS research/questions/0043-firewood-stacks-and-sheds-kigoya.drawing.html: held at a ken plus the wall gap, the gap the page's DEVIATION - at a ken three scaling rolls of the reference refuse their web (20 households seed 39; 40 households seeds 4 and 25: farmhouses or the field left off the network; seed 39 re-measured 2026-10-08 with the shed off the house's own walls); the found row hamletgen/ways/last_resort.py::refuse_unreached#every household reached at 20 and 40 households"""
# THE PRIVY'S SIZE (feature 280, research/questions/0047-farm-privies-and-their-night-soil-benjo.html): each homestead's privy is one of the sixteen of the Kakimochi table
# (Meiji 18, read back to the last years of the shogunate), frontage by depth in feet at 6 ft to the ken - each as likely as
# the next. A calibration against one village's table; the old 6 x 6 ft one-ken module was a GUESS.
PRIVY_SIZES_FT: tuple[tuple[float, float], ...] = (
    (27.0, 15.0),
    (6.0, 5.0),
    (12.0, 6.0),
    (18.0, 12.0),
    (15.0, 12.0),
    (15.0, 9.0),
    (24.0, 12.0),
    (24.0, 12.0),
    (5.0, 5.0),
    (24.0, 12.0),
    (18.0, 12.0),
    (15.0, 9.0),
    (9.0, 6.0),
    (24.0, 12.0),
    (24.0, 12.0),
    (6.0, 6.0),
)
"""Research: privy sizes - research/questions/0047-farm-privies-and-their-night-soil-benjo.drawing.html: the Kakimochi table's sixteen, equally likely"""
# THE BATH ROOM (feature 280 M22, research/homesteads/740): joined to the main house - beside its main door, at the far end
# of its stable wing (the house's -x end, where the doma and its stable are), or joined to its floored rooms (the +x end) -
# a room of 1-2 tsubo: one ken out from the wall, one to two ken along it, rolled per household (a calibration on the
# registers' 1-2 tsubo). The free-standing bath shed is found only in the twentieth century, and is not drawn.
BATH_DEPTH_FT = 6.0
"""Research: bath room depth - research/questions/0044-baths-on-the-farm-furo.drawing.html: one ken out from the wall"""
BATH_LENGTH_FT = (6.0, 12.0)
"""Research: bath room length - research/questions/0044-baths-on-the-farm-furo.drawing.html: one to two ken along the wall"""
BATH_WALLS = ("main_door", "stable_end", "floored_rooms")
"""Research: bath room walls - research/questions/0044-baths-on-the-farm-furo.drawing.html: the main door, the stable end, the floored rooms"""
SHRINE_CORNER_FT = 14.0  # the household shrine a plot corner off the house's corner
"""Research: shrine off the house corner - research/questions/0219-household-shrines-yashikigami.html: the household shrine stood at a corner of the plot, northwest, northeast or southwest; the 14 ft is ours; 14 ft out each way"""
TRUNK_FT = 4.0  # the persimmon's trunk box
"""Research: persimmon trunk box - GUESS: no source could speak to it, a value of ours (feature 417 T36 pass P1, 2026-10-25); 4 ft"""
CANOPY_PAD = 0.6  # the crown's placement clearance off a roof (`Settlement.CANOPY_PAD`)
"""Research: crown clearance off a roof - CONVENTION: 0.6, the map's own placement clearance, so a kept crown survives the record's rounding"""
PERSIMMON_STEPS_FT = (10.0, 20.0)  # the persimmon's ring a step out, and two
"""Research: persimmon stepped out - GUESS: searched, the record silent (feature 417 T36 pass P1, 2026-10-25); 10 and 20 ft past its first ring"""
#: THE DOORYARD'S REACH (feature 315; research/questions/0046-fruit-trees-in-the-farmyard-persimmon-chestnut-and-plum-kaki.drawing.html:
#: the fruit trees stand "within about 30 ft of the house"): the persimmon's paces stop where its crown's edge would stand farther
#: than this from the house's walls. Paced on without it, a crowded farm's persimmon walked 80 ft out onto the row's street
#: (cohort seed 23), no dooryard tree at all; a farm with no seat within it keeps no persimmon, as a farm with no room keeps no bamboo.
PERSIMMON_DOORYARD_FT = 30.0
"""Research: persimmon near the house - GUESS research/questions/0046-fruit-trees-in-the-farmyard-persimmon-chestnut-and-plum-kaki.drawing.html: the crown's edge within 30 ft of the walls"""
SHADE_MARGIN_FT = 2.0  # the seat stricter than the map's check by a hair, as the sun corridor's placer is (`fit._sun_corridor_ok`)
"""Research: shade margin - CONVENTION: the seat 2 ft stricter than the map's sun check, so a seat the placer takes the check passes"""

SHRINE_CORNERS = (("NW", 0.45), ("NE", 0.35), ("SW", 0.20))
"""Research: shrine corner weights - research/questions/0219-household-shrines-yashikigami.drawing.html: NW 45, NE 35, SW 20"""
CORNER_SIGNS = {"NW": (-1.0, -1.0), "NE": (1.0, -1.0), "SW": (-1.0, 1.0), "SE": (1.0, 1.0)}
#: THE HOUSEHOLD GRAVE'S CORNERS (feature 374 wave 136): research/questions/0236's house-plot graves stood at the plot's
#: southeast corner and, in another family's record, its northwest corner (the Hatara district, before 1688-1704) - so
#: those two at even odds, then the other two corners, as the shrine takes its corner off the house's corner
GRAVE_CORNERS = (("SE", 0.5), ("NW", 0.5))
"""Research: household grave corner - research/questions/0236-where-a-village-buries-its-dead-its-own-ground-the-temple-yard-the-fields-or-the-home-plot.html: the plot's southeast or northwest corner, even odds (a GUESS)"""
SALT = {"privy": 101.0, "manure": 102.0, "woodpile": 103.0, "bath": 104.0, "coop": 105.0, "shrine": 106.0, "persimmon": 107.0, "retirement": 131.7, "grave": 108.0}


class FixtureUnlaid(ValueError):
    """A kind whose rule is its seat found none in this bundle (feature 280 M21, M22, carried into feature 287): a bath
    room with no free place on the house's three attested walls, or a wood shed with no place a ken off a wall of its
    steading. The bundle is then NOT the household's (`BundleGeomMixin._lay_fixtures` marks it `unlaid` and the fit refuses
    it, `_bundle_side_fits`): the envelope admits a household only with room for every part its lot keeps, so another
    garden side or another seat is sought - never a room walked out into the yard, and never a fixture recorded short."""


@dataclass(frozen=True)
class FixtureForms:
    """The hamlet's fixture forms, rolled once per map (`hamletgen/homesteads/fixtures.py`, `fixture_forms`): the privy
    seats' weights, the bath room's wall, the persimmon's front share and the manure's form. The woodpile has one form
    left, the wood shed (feature 280 M21: the eaves stack and the kizuma are modern-only), so it rolls none.

    Research:
        privy seat weights - research/questions/0047-farm-privies-and-their-night-soil-benjo.drawing.html: stable 35, yard 30,
            front 20, barn 15 (the default; a hamlet rolls its own about them, `hamletgen/homesteads/fixtures.py`)
        bath room beyond the stable wing - research/questions/0044-baths-on-the-farm-furo.html: most baths there, 17 of 21 at Shimohasuda and 12 of 15 at Ukiya, so 0.8
        the main door the rest - research/questions/0044-baths-on-the-farm-furo.drawing.html: the registers give the rest no place; drawing it by the main door, where the earliest registers' baths stood, is this project's choice, each house rolled
        bath room joined to the floored rooms - research/questions/0044-baths-on-the-farm-furo.html, research/questions/0044-baths-on-the-farm-furo.drawing.html: of the two registers' 36 baths, one joined to the floored rooms was a peasant's (the other a headman's; a third, at Kozutsumi in 1771, a headman's too) - so 1 in 36, 0.03, on a hamlet, which has no headman
        persimmon front share - research/questions/0046-fruit-trees-in-the-farmyard-persimmon-chestnut-and-plum-kaki.drawing.html:
            0.7 by default
        manure form - research/questions/0042-manure-heaps-and-compost-kyuhi.drawing.html: heap by default, or pit
        retirement house size and gaps - research/questions/0028-the-farmstead-and-what-stood-on-it-yashiki.drawing.html: eight of 16 households kept a retirement house, at 3 to 15 tsubo, a 9 tsubo one a middling one, all but one 2.5 ken (~15 ft) deep or less; no page gives how far from the main house it stood; 18 x 15 ft
        retirement house gaps - GUESS research/questions/0028-the-farmstead-and-what-stood-on-it-yashiki.drawing.html: no page gives how far from the main house it stood; 6 or 12 ft off the house"""

    privy_weights: tuple[tuple[str, float], ...] = (("stable", 0.35), ("yard", 0.30), ("front", 0.20), ("barn", 0.15))  # the page's order (feature 328 wave 61: the places were misassigned)
    bath_stable_share: float = 0.8
    bath_floored_share: float = 0.03
    persimmon_front: float = 0.7
    manure_form: str = "heap"
    retirement_ft: tuple[float, float] = (18.0, 15.0)  # `hamletgen/homesteads/retirement.py` RETIREMENT_FT
    retirement_gaps: tuple[float, ...] = (6.0, 12.0)  # and RETIREMENT_GAP_FT


def weighted(weights: Sequence[tuple[str, float]], u: float) -> str:
    """The name `u` in [0, 1) falls on across cumulative `weights` (the last name past their sum)."""
    acc = 0.0
    for name, w in weights:
        acc += w
        if u < acc:
            return name
    return weights[-1][0]


def privy_sun_reach_ft(w_ft: float, d_ft: float) -> float:
    """How far from its house's center the sun-side search may seat a privy of `w_ft` x `d_ft`: `PRIVY_SUN_MAX_FT`, whatever
    its size (feature 280's widening for a large privy, after 7 of 17 privies of 18 x 12 ft or more fell to the north-east
    seat at Sawada, is gone). A SEARCH BOUND only, measured to the privy's center: whether a seat is within the reach 0047
    gives is `within_reach_of`'s far-corner-to-walls measure (feature 368).

    Research:
        sun-side reach by size - research/questions/0047-farm-privies-and-their-night-soil-benjo.drawing.html: the search bound for the sun-side seats, 48 ft to the privy's center whatever its size; the reach 0047 gives runs from the privy's far corner to the house's walls, which within_reach_of tests"""
    return PRIVY_SUN_MAX_FT  # the search bound, to the privy's center; the reach itself is within_reach_of's (0047)


def fixture_ft(kind: str, forms: FixtureForms, roll: Callable[[float], float] | None = None) -> tuple[float, float]:
    """A fixture's size in real feet, `(along its wall, out from it)`, in the form the hamlet rolled: the privy one of the
    Kakimochi table's sixteen and the bath room 6 ft out by 6-12 ft along, each rolled off the household's own position roll
    `roll` (feature 280, research/questions/0047-farm-privies-and-their-night-soil-benjo.html and 740; the kinds' one-ken default without one); every other kind its one
    size (`FIXTURE_FT`), the pit's, the crown's or the retirement house's.

    Research:
        one-ken default - research/questions/0047-farm-privies-and-their-night-soil-benjo.drawing.html, research/questions/0044-baths-on-the-farm-furo.drawing.html: a privy or bath room with no size rolled (a caller passing no roll) is 6 x 6 ft (`FIXTURE_FT`) - one of the sixteen privy sizes, and the bath page's one tsubo, the low end of its range; a hamlet always rolls its own
        privy size - research/questions/0047-farm-privies-and-their-night-soil-benjo.drawing.html: rolled from the sixteen
        bath room size - research/questions/0044-baths-on-the-farm-furo.drawing.html: 6 ft out by 6 to 12 ft along
        persimmon crown - research/questions/0046-fruit-trees-in-the-farmyard-persimmon-chestnut-and-plum-kaki.drawing.html:
            twice the crown radius each way
        other fixtures' sizes - research/questions/0028-the-farmstead-and-what-stood-on-it-yashiki.drawing.html: the wood shed 24 x 12 ft
        manure heap size - research/questions/0042-manure-heaps-and-compost-kyuhi.drawing.html: 8 x 6 ft
        coop size - research/questions/0045-chickens-and-chicken-coops.drawing.html: 5 x 5 ft
        shrine size - research/questions/0219-household-shrines-yashikigami.drawing.html: 6 x 6 ft, larger than life
        manure pit size - research/questions/0042-manure-heaps-and-compost-kyuhi.html: 3.5 ft, inside the night-soil jar's mouth of about 3-5 ft
        retirement house size - research/questions/0028-the-farmstead-and-what-stood-on-it-yashiki.drawing.html: eight of 16 households kept a retirement house, at 3 to 15 tsubo, a 9 tsubo one a middling one, all but one 2.5 ken (~15 ft) deep or less; no page gives how far from the main house it stood; 18 x 15 ft
        its salts, guards and sentinels - NONE: they decide nothing about the place - 104.3 (roll salt for the bath's length)
    """
    if kind == "privy" and roll is not None:
        return PRIVY_SIZES_FT[int(roll(101.3) * len(PRIVY_SIZES_FT)) % len(PRIVY_SIZES_FT)]
    if kind == "bath" and roll is not None:
        lo, hi = BATH_LENGTH_FT
        return (float(round(lo + (hi - lo) * roll(104.3))), BATH_DEPTH_FT)
    if kind == "manure" and forms.manure_form == "pit":
        return PIT_FT, PIT_FT
    if kind == "persimmon":
        return PERSIMMON_CROWN_FT * 2.0, PERSIMMON_CROWN_FT * 2.0
    if kind == "retirement":
        return forms.retirement_ft
    return FIXTURE_FT[kind]


def fixture_size(kind: str, forms: FixtureForms, px: Callable[[float], float], roll: Callable[[float], float] | None = None) -> tuple[float, float]:
    """A fixture's footprint `(along its wall, out from it)` at the map's scale (`fixture_ft`, in px)."""
    ft = fixture_ft(kind, forms, roll)
    return px(ft[0]), px(ft[1])


def within_reach_of(r: Rect, house: Rect, reach: float) -> bool:
    """Does `r` stand with its far edge no more than `reach` from `house`'s walls - every corner of it within `reach` of
    the house's outline, measured true (a box test let a privy off a corner stand about 68 ft out)?

    Research: the privy's reach - research/questions/0047-farm-privies-and-their-night-soil-benjo.drawing.html: no more than 48 ft from its house"""
    # THE FAR CORNER ALONE (feature 328, perf-audit of batch 3): each axis's gap is largest at the corner farther from the
    # house, so that corner is the only one that can fail - one squared comparison, the same answer as four hypots (asked
    # ~150,000 times on a 40-household roll)
    gx = max(0.0, abs(r[0] - house[0]) + r[2] / 2 - house[2] / 2)
    gy = max(0.0, abs(r[1] - house[1]) + r[3] / 2 - house[3] / 2)
    return gx * gx + gy * gy <= reach * reach


def clears(r: Rect, taken: Sequence[Rect], gap: float) -> bool:
    """Does `r` stand clear of every rect in `taken` by `gap` - apart by the two half-sizes and the gap on one axis at
    least? A plain loop that stops at the first rect it meets (the seating asks it 1.3 million times a map, seed 44)."""
    rx, ry, rw, rh = r[0], r[1], r[2], r[3]
    for t in taken:  # noqa: SIM110 - a loop, not all() over a generator: the generator was half this test's cost
        if abs(rx - t[0]) < (rw + t[2]) / 2 + gap and abs(ry - t[1]) < (rh + t[3]) / 2 + gap:
            return False
    return True


def steading_rects(hw: float, hh: float, kura_side: str | None, ppf: float) -> list[Rect]:
    """The walls of a steading's buildings in the house's unturned frame: the house, and its kura where it keeps one
    (north, or the west end - `kura_rect`, the table `Settlement.house` draws from).

    Research:
        storehouse annex - DEVIATION research/questions/0040-farm-storehouses-kura.drawing.html: on the north wall or the west end"""
    rects = [(0.0, 0.0, hw, hh)]
    if kura_side is not None:
        rects.append(kura_rect(hw, hh, kura_side, ppf))
    return rects


def against_a_wall(seat: Sequence[float], rects: Sequence[Rect], g: float, tol: float = 1.5) -> bool:
    """Does a seat `(lx, ly, w, d)` in the house frame stand against a wall of its steading - its edge within the wall gap
    `g` (plus `tol`) of one of `rects`, and overlapping it along that wall (feature 287, homes H35)? The one predicate the
    wood shed's (`shed_off_a_wall`) and the bath room's (`joined_to_house`) placers and their tests read.

    Research:
        its salts, guards and sentinels - NONE: they decide nothing about the place - 1.5 (slack in the "stands against a wall" test)
    """
    lx, ly, cw, ch = seat[0], seat[1], seat[2], seat[3]
    for rx, ry, rw, rh in rects:
        gx = abs(lx - rx) - (cw + rw) / 2
        gy = abs(ly - ry) - (ch + rh) / 2
        if (gx <= g + tol and gy < 0.0) or (gy <= g + tol and gx < 0.0):
            return True
    return False


def along(half: float, step: float) -> list[float]:
    """Offsets along a wall from its middle out, `step` apart, and its two ends (`+-half`) - so a place at the very end of
    a wall is offered where the grid would step past it."""
    n = max(0, int(half // step)) if half > 0.0 else 0
    pts = [k * step for k in sorted(range(-n, n + 1), key=abs)]
    return pts + ([-half, half] if half > 0.0 and n * step < half else [])


def wall_places(rects: Sequence[Rect], w: float, d: float, off: float, step: float) -> list[Rect]:
    """Every place along the outside of each rect's four walls, `off` out from it, `step` apart and at each wall's ends: a
    seat `w` along a wall and `d` out from it (turned to lie along a flank), overlapping the wall along it by a foot at
    least (`against_a_wall`)."""
    out: list[Rect] = []
    for rx, ry, rw, rh in rects:
        for sy in (-1.0, 1.0):  # the back wall first, then the front
            out += [(rx + u, ry + sy * (rh / 2 + off + d / 2), w, d) for u in along((rw + w) / 2 - 1.0, step)]
        for sx in (-1.0, 1.0):
            out += [(rx + sx * (rw / 2 + off + d / 2), ry + u, d, w) for u in along((rh + w) / 2 - 1.0, step)]
    return out


def outward(seats: Sequence[Rect], step: float, n: int) -> Iterator[Rect]:
    """The seats stepped `step` further from the house center, `n` times: each along its own bearing from the center -
    yielded as asked, since the first free one ends the search."""
    for k in range(1, n + 1):
        for lx, ly, w, d in seats:
            r = math.hypot(lx, ly) or 1.0
            yield (lx + lx / r * step * k, ly + ly / r * step * k, w, d)


def privy_places(forms: FixtureForms) -> tuple[str, ...]:
    """The attested places a hamlet farm's privy is rolled over (`_seats`): the yard, the front and the stable - never the barn,
    which a hamlet draws none of.

    Research: privy places - research/questions/0047-farm-privies-and-their-night-soil-benjo.drawing.html: the page's four places less the barn, its share spread over the yard, the front and the stable while a hamlet draws no barn (`farm_fixtures.py`) - drawing the barn is the open found row `_seats#privy seats - the barn 0047 names`"""
    return tuple(k for k, _p in forms.privy_weights if k in ("stable", "yard", "front"))


def along_its_wall(seat: Rect, step: float, n: int, half_wall: float = math.inf) -> Iterator[Rect]:
    """`seat` slid along the wall it stands off (the house frame's x), `step` at a time toward its own end of the wall, `n`
    times - never back across the middle, where the door's way out leaves (batch 4's timing pair: slid both ways, a front
    privy stood across a door's way on seed 4 at 10 households, and the web's orphan joins took 1.2 -> 16 s).

    Research:
        slid only while along its wall - research/questions/0047-farm-privies-and-their-night-soil-benjo.drawing.html: "while the whole privy still stands along the wall"
        slid toward its own end only - GUESS: no source could speak to it, a value of ours (feature 417 T36 pass P1, 2026-10-25); never back across the house's middle, where the door's way out leaves (batch 4's timing pair)"""
    x, y, w, d = seat
    sign = 1.0 if x >= 0 else -1.0
    for k in range(1, n + 1):
        nx = x + sign * step * k
        if abs(nx) + w / 2 > half_wall + 1e-9:  # ...and only while the WHOLE seat stands along the wall: its outer edge never past the gable
            return  # (batch 4's glyph-check: slid on unbounded, two stable privies stood 38 ft past their gable on Kashikawa)
        yield (nx, y, w, d)


def rolled_first(seats: Sequence[Rect], k: int, step: float, n: int, half_wall: float = math.inf) -> Iterator[Rect]:
    """The seats as offered when the first `k` are the household's ROLLED place - the sun-side sector on a sunny roll, else the
    one attested place it rolled. The sector already offers every radius to its reach, so it is followed by the attested
    places and then every pace. One attested place is SLID ALONG ITS WALL toward its own end, while it still stands along the
    wall (`half_wall`), then the other places at their first spots, then every place stepped out.

    Two orders were tried and withdrawn (feature 328 wave 61, batch 4's close): stepping the rolled place straight out before
    the other places carried a front or stable privy and its heap across the threshing yard onto the household's way out
    (cohort seeds 4 and 23, refused; Kashikawa's ways unreached once the slide was bounded), and a slide with no stop at the
    wall's end stood two stable privies 38 ft past their gable (the glyph-check of batch 4's close). Bounded, the slide honors
    no roll on the shipped hamlets: the 16 households whose privy rolled the stable or the front are all refused it, the drawn
    threshing yard covering the rolled spot and no step fitting along the wall (row 564, held E3: the yard and the privy's seat
    laid out together).

    Research: privy's rolled place kept - research/questions/0047-farm-privies-and-their-night-soil-benjo.drawing.html: a privy not seated on the sunny side takes the place rolled per house, slid along its wall while it stands by the wall, before another place is tried; a sunny roll that finds no room on the sunny side falls back to the places at their first spots (the page's bullets for each; no source gives an order)"""
    head, rest = list(seats[:k]), list(seats[k:])
    if k > 1:  # the sun-side sector already offers every radius to its reach: its paces are the attested places' turn
        return chain(head, rest, outward(seats, step, n))
    return chain(
        head, along_its_wall(head[0], step, n, half_wall), rest, outward(seats, step, n)
    )  # no straight step out first: across the dooryard it stood on a way out (seeds 4, 23; Kashikawa once the slide stopped at the wall's end)


def lay_fixtures(
    kinds: Sequence[str],
    hw: float,
    hh: float,
    roofs: Sequence[Rect],
    ground: Sequence[Rect],
    yard: Rect | None,
    kura: bool,
    roll: Callable[[float], float],
    forms: FixtureForms,
    px: Callable[[float], float],
    annex: Rect | None = None,
    notes: dict[str, Any] | None = None,
    shade: float = 0.0,
    turns: Sequence[float] = (0.0,),
    fruit: Sequence[Rect] = (),
    keep: Sequence[Rect] = (),
) -> dict[str, Rect]:
    """Each of `kinds` laid beside the parts already laid, in the house's unturned frame centered on it: `{kind: (x, y, w,
    h)}`, the box AS LAID (a flank seat turned to lie along its flank). `roofs` are the built parts - the house first, the
    kura, the byre, the well-house - and `ground` the open ones, the yard and the beds, whose sun a persimmon's crown keeps
    out of: `shade` px east, west and south of each (`CANOPY_SHADE_FT`), at every rake in `turns` (degrees - the house
    is turned after its parts are laid, and the sun is not);
    `yard` is the threshing yard, `kura` whether the house keeps one on its north wall, `annex` the byre where the household
    keeps one; `roll` the household's position roll (`Settlement._hjit` at its seat).
    `notes`, where given, receives what the drawing needs beyond the box: each rolled size in feet (`ft`, `fixture_ft`) and
    the wall the bath room took (`bath_seat`). Every kind is laid: the outward paces reach free ground past any parts. Raises
    only for a bath room with no place along the house's three attested walls, or a wood shed with no place a ken off a
    wall of its steading, each named - a refusal, never a room walked out into the yard (feature 280 M21, M22).

    Research:
        fixture gap 3.5 ft off every other part and bath room slide 4 ft - GUESS research/questions/0043-firewood-stacks-and-sheds-kigoya.drawing.html: the gap of about 3.5 ft our maps keep between a house wall and anything built in its yard; the 4 ft slide is ours; WALL_GAP_FT (3.5 ft) clears the drawn wall of any part a fixture stands by, WALL_SLIDE_FT (4 ft) the bath room's slide along its wall
        seating order - GUESS: no source could speak to it, a value of ours (feature 417 T36 pass P1, 2026-10-25); FIXTURE_ORDER (retirement house, bath, wood shed, privy, manure, coop, shrine, grave, persimmon) is the order the fixtures take seats
        stepped outward - GUESS: no source could speak to it, a value of ours (feature 417 T36 pass P1, 2026-10-25); a fixture with no recorded seat free is offered the same seats a pace further out
        the privy's reach - research/questions/0047-farm-privies-and-their-night-soil-benjo.drawing.html: never stepped past 48 ft from its house; a farmstead with no seat within it refuses its privy by name
        wood shed's walls - GUESS research/questions/0043-firewood-stacks-and-sheds-kigoya.drawing.html: the house's walls, a short
            step off the house - never the byre's or the retirement house's
        the kura's walls too - GUESS: the house's storehouse annex counts as a wall of the house for the shed
        persimmon front or behind - research/questions/0046-fruit-trees-in-the-farmyard-persimmon-chestnut-and-plum-kaki.drawing.html: in front of the house or behind it, rolled per house at `forms.persimmon_front`
        persimmon in its own grove bands - research/questions/0046-fruit-trees-in-the-farmyard-persimmon-chestnut-and-plum-kaki.drawing.html: it may stand in the grove behind the house - its own grove, no other farm's
        bath room joined - research/questions/0044-baths-on-the-farm-furo.drawing.html: refused rather than walked out
        bath room's wall per house - research/questions/0044-baths-on-the-farm-furo.html: each house rolls among the three walls (`bath_wall`)
        no seat, no persimmon - research/questions/0046-fruit-trees-in-the-farmyard-persimmon-chestnut-and-plum-kaki.drawing.html: the farm keeps none
        no fixture on the way in - research/questions/0036-groves-of-trees-around-farmhouses-yashikirin.drawing.html: the way in by the open front, through the ring's break - every kind but the bath room kept off `keep`
        no fixture on the door's room - GUESS: no source could speak to it, a value of ours (feature 417 T36 pass P1, 2026-10-25); the square about the door in `keep` (`DOOR_ROOM_HALF_FT`)
        its salts, guards and sentinels - NONE: they decide nothing about the place - 0.25 (salt offset for the bath-wall roll)
    """
    g = px(WALL_GAP_FT)
    # (A grove farm's bands stay roofs here: letting a persimmon's crown reach over them, feature 315 found, let it take the
    # service strip a wood shed or bath room needed, and five cohort rolls could no longer seat their households.)
    # `keep`: the ground a grove farm's way in crosses (`way_in_strip`) - no fixture stands on it but the bath room, which is
    # joined to its house (feature 374 wave 146: a privy and a manure heap across a row farm's way in left it no path)
    taken: list[Rect] = [*roofs, *fruit, *ground, *keep]  # `fruit`: a grove farm's bands, ground for its persimmon alone (feature 315)
    built: list[Rect] = list(roofs)
    laid: dict[str, Rect] = {}
    ft: dict[str, tuple[float, float]] = {}
    for kind in [k for k in FIXTURE_ORDER if k in kinds]:
        ft[kind] = fixture_ft(kind, forms, roll)
        w, d = px(ft[kind][0]), px(ft[kind][1])
        u = roll(SALT[kind] + 0.5)
        if kind == "persimmon":
            seat = _persimmon(hw, hh, [t for t in taken if t not in fruit], built, u < forms.persimmon_front, px, _sunlit(ground, shade, turns))
            if seat is None:  # no seat in the dooryard: this farm keeps no persimmon (feature 315)
                del ft[kind]
                continue
        elif kind == "woodpile":
            walls = steading_rects(hw, hh, "N" if kura else None, px(1.0))  # the house's own walls (0043), never the byre's or the retirement house's
            seat = _wood_shed(hw, hh, w, d, g, walls, taken, px)
        elif kind == "bath":
            # EACH HOUSE'S OWN WALL (feature 328): the registers count the wall house by house, most beyond the stable wing
            wall = bath_wall(roll(SALT[kind] + 0.25), forms)
            named = bath_room_seats(wall, hw, hh, w, d, (yard[0], yard[2] / 2) if yard is not None else None)
            named += bath_room_slides(wall, hw, hh, w, d, px(WALL_SLIDE_FT))
            house = roofs[0]
            others = [t for t in taken if t is not house and t not in keep]
            got = next(((q, n) for q, n in named if clears(q, [house], -1e-6) and clears(q, others, g)), None)
            if got is None:
                raise FixtureUnlaid("a bath room found no place on the house's front wall or either end wall")
            seat = got[0]
            if notes is not None:
                notes["bath_seat"] = got[1]
        else:
            seats = _seats(kind, hw, hh, w, d, g, yard, laid.get("privy"), roll, u, forms, px)
            if kind == "privy":  # the household's rolled place stepped out before the next place is tried (feature 328 wave 61)
                sun = len(seats) - len(privy_places(forms))  # the sun-side sector's seats lead the list on a sunny household's roll
                offered = rolled_first(seats, sun or 1, px(STEP_FT), OUT_STEPS, hw / 2)
            else:
                offered = chain(seats, outward(seats, px(STEP_FT), OUT_STEPS))
            if kind == "privy":  # its own farmstead's: no further than 48 ft from its house (0047), never stepped past it
                offered = (q for q in offered if within_reach_of(q, roofs[0], px(PRIVY_SUN_MAX_FT)))
            found = _first(offered, taken, g)
            if found is None:
                raise FixtureUnlaid("a privy found no place within 48 ft of its house")
            seat = found
        laid[kind] = seat
        taken.append(_trunk(seat, px) if kind == "persimmon" else seat)
        if kind != "persimmon":
            built.append(seat)
    if notes is not None:
        notes["ft"] = ft
    return laid


def against_a_part(built: Sequence[Rect], w: float, d: float, g: float, taken: Sequence[Rect], step: float, start: float = 0.0) -> Rect | None:
    """The first place touching a wall of one of `built` - the house's walls, then each outbuilding's as laid - clear of every
    other part in `taken` by the wall gap `g`: a seat `w` along the wall and `d` out from it (`wall_places`), or None. `start`
    (0 to 1) turns where the walk begins, so one household's first place is not every household's: from the house's own back
    wall, every sty of a hamlet stood stamped at the middle of it (glyph-check of Inashiro, feature 374 wave 151).

    Research: against the farmhouse or one of its outbuildings - GUESS research/questions/0049-pigs-and-ducks-in-south-china-rice-villages.drawing.html: the sty stands against the farmhouse or an outbuilding, a GUESS the page names"""
    offers = [(part, q) for part in built for q in wall_places([part], w, d, 0.0, step)]
    k = int(start * len(offers)) % len(offers) if offers else 0
    for part, q in offers[k:] + offers[:k]:
        if clears(q, [part], -1e-6) and clears(q, [t for t in taken if t is not part], g):
            return q
    return None


def shed_off_a_wall(seat: Rect, walls: Sequence[Rect], g: float, px: Callable[[float], float]) -> bool:
    """THE WOOD SHED'S RULE (feature 280 M21; history: the settlement-reviews of Inashiro and Kuwabata found sheds 25-37 ft out,
    between farmsteads): a building of its own a ken off its house - clear of the house by the wall gap and `WOODSHED_STEP_FT`
    - and never walked out across the dooryard: exactly the gap and a ken off a wall of its HOUSE (`against_a_wall` at no
    tolerance, `walls[0]` the house centered on the frame's origin; feature 328 dropped the extra outward pace), overlapping
    that wall along it, clear of EVERY wall of the steading by the gap and the ken (405 T26: the kura's too - a seat stood
    3.5 ft off it), and no part of it forward of the front wall (`forward_of_front`; 405 T26: a flank shed stood half in the
    dooryard). The one predicate the placer and its test read.

    Research:
        wood shed a ken off a wall - GUESS research/questions/0043-firewood-stacks-and-sheds-kigoya.drawing.html: never out across
            the dooryard
        a ken off the house, clear of the kura - GUESS research/questions/0043-firewood-stacks-and-sheds-kigoya.drawing.html: a short step off a house wall, and the kura's wall kept as far, a building of its own
        no part forward of the front wall - GUESS research/questions/0043-firewood-stacks-and-sheds-kigoya.drawing.html: never the front yard
        the ken past the wall gap - GUESS research/questions/0043-firewood-stacks-and-sheds-kigoya.drawing.html: a ken (`WOODSHED_STEP_FT`) past the wall gap, about 9.5 ft out, the ken the page's GUESS and the added gap its DEVIATION - exactly, at no tolerance"""
    return clears(seat, walls, g + px(WOODSHED_STEP_FT) - 1e-6) and against_a_wall(seat, walls[:1], g + px(WOODSHED_STEP_FT) + 1e-6, tol=0.0) and not forward_of_front(seat, walls[0][3] / 2)


def forward_of_front(seat: Rect, hh: float) -> bool:
    """Does any part of `seat` (in the house's frame, the front wall at +`hh`) stand past the front wall, into the dooryard?

    Research: the front yard - GUESS research/questions/0043-firewood-stacks-and-sheds-kigoya.drawing.html: never the front yard"""
    return seat[1] + seat[3] / 2 > hh + 1e-6


def joined_to_house(seat: Rect, hw: float, hh: float, tol: float = 1e-6) -> bool:
    """THE BATH ROOM'S RULE (feature 280 M22): a room of the house - one edge on a wall of the `hw` x `hh` house, overlapping
    it along that wall, and not inside it. The one predicate the placer and its test read.

    Research: bath room of the house - research/questions/0044-baths-on-the-farm-furo.drawing.html"""
    gx = abs(seat[0]) - (seat[2] + hw) / 2
    gy = abs(seat[1]) - (seat[3] + hh) / 2
    return (abs(gx) <= tol and gy < 0.0) or (abs(gy) <= tol and gx < 0.0)


def _wood_shed(hw: float, hh: float, w: float, d: float, g: float, walls: Sequence[Rect], taken: Sequence[Rect], px: Callable[[float], float]) -> Rect:
    """The wood shed (feature 280 M21): the recorded seats - off the back wall and the flanks, a ken out - then every place a
    ken off each wall of the house but its front (feature 328: the front wall's places stood in the dooryard); the first that
    clears the parts laid and keeps `shed_off_a_wall`.

    Research:
        wood shed seats - GUESS research/questions/0043-firewood-stacks-and-sheds-kigoya.drawing.html: behind or beside the house,
            never the front yard
        wall places a ken out - GUESS research/questions/0043-firewood-stacks-and-sheds-kigoya.drawing.html: offered a ken (`WOODSHED_STEP_FT`, the page's GUESS) beyond the wall gap (the page's DEVIATION)"""
    seats = _seats("woodpile", hw, hh, w, d, g, None, None, lambda _salt: 0.0, 0.0, FixtureForms(), px)
    offered = chain(seats, (q for q in wall_places(walls[:1], w, d, g + px(WOODSHED_STEP_FT), px(WALL_SLIDE_FT)) if not forward_of_front(q, hh / 2)))  # the house's walls (0043)
    found = _first((q for q in offered if shed_off_a_wall(q, walls, g, px)), taken, g)
    if found is None:
        raise FixtureUnlaid("a wood shed found no place a ken off any wall of its steading")
    return found


def bath_wall(u: float, forms: FixtureForms) -> str:
    """The wall a house's bath room is joined to, from its roll `u`: beyond the stable wing at `bath_stable_share`, the
    floored rooms at `bath_floored_share` (0.03), else beside the main door (feature 328: the floored rooms were only a fallback).

    Research:
        the three walls rolled - research/questions/0044-baths-on-the-farm-furo.html: most beyond the stable, a few at the floored rooms
        the rest by the main door - research/questions/0044-baths-on-the-farm-furo.drawing.html: this project's choice, where the earliest registers' baths stood"""
    if u < forms.bath_stable_share:
        return "stable_end"
    return "floored_rooms" if u < forms.bath_stable_share + forms.bath_floored_share else "main_door"


def bath_room_seats(first: str, hw: float, hh: float, w: float, d: float, yard: tuple[float, float] | None = None) -> list[tuple[Rect, str]]:
    """The bath room's seats in the house frame (feature 280 M22, research/homesteads/740), `first` tried first then the
    other attested seats: beside the MAIN DOOR (the front wall, either side of the door at its middle), at the far end of
    the STABLE WING (the -x end wall, where the doma and its stable are), or joined to the FLOORED ROOMS (the +x end wall).
    Each abuts its wall - a room of the house, not a building beside it. Each seat carries its name, and the record keeps the
    one taken: the work yard lies before the front wall, and where it covers the wall the bath falls to the next seat - the
    reviews of Kuwabata and Sawada (feature 280) found a declared `main_door` never drawn, and then an end-wall corner offered
    as `main_door` that read as the floored rooms' seat, so the record now says which seat each bath room took.

    Research:
        three attested walls - research/questions/0044-baths-on-the-farm-furo.drawing.html: the rolled wall first
        bath room seat fallback - GUESS: where the rolled wall has no room the other attested walls are tried in table order; 0044 gives each house's place and its share but no fallback
        places along each wall - research/questions/0044-baths-on-the-farm-furo.html: the bath stood by the main door, at the stable wing's far end or by the floored rooms; the 0.22 is ours; 0.22 of the house either side of the door or just past the yard; an end
            wall's middle and quarters
        its figures guessed on 0044 - GUESS research/questions/0044-baths-on-the-farm-furo.drawing.html: 0.25 (the same, on the floored-rooms end wall)
    """
    front, side = hh / 2 + d / 2, hw / 2 + d / 2
    # ...AND JUST PAST THE YARD'S SIDES (`yard`: its center x and half-width in the house frame), still on the front wall: the
    # yard is centered before the door and covered both door-side seats on every house, so the seat was never drawn
    # (settlement-review of Kuwabata, feature 280); the room stands under the eaves beside the door, the yard beside it
    past = [yard[0] + sx * (yard[1] + w / 2 + 3.0) for sx in (1.0, -1.0)] if yard else []  # 3 ft: the placer keeps 2 ft off a footprint
    door = [(hw * 0.22 + w / 2, front, w, d), (-(hw * 0.22 + w / 2), front, w, d)] + [(x, front, w, d) for x in past if abs(x) + w / 2 <= hw / 2]
    table = {
        "main_door": door,
        "stable_end": [(-side, 0.0, d, w), (-side, -hh * 0.25, d, w), (-side, hh * 0.25, d, w)],
        "floored_rooms": [(side, 0.0, d, w), (side, -hh * 0.25, d, w), (side, hh * 0.25, d, w)],
    }
    return [(q, first) for q in table[first]] + [(q, k) for k, v in table.items() if k != first for q in v]


def bath_room_slides(first: str, hw: float, hh: float, w: float, d: float, step: float) -> list[tuple[Rect, str]]:
    """Every place along the bath room's three attested walls (`bath_room_seats`' walls), `step` apart and at each wall's
    ends, `first`'s wall first: offered after the recorded seats, so a house whose recorded seats are taken by its yard,
    beds, byre or retirement house still joins its bath to a wall where the room fits (feature 287: every kind is laid).

    Research:
        the three walls - research/questions/0044-baths-on-the-farm-furo.drawing.html: by the main door, at the far end of the stable wing, joined to the floored rooms
        anywhere along the walls - GUESS: the spot along a wall slid toward either end, and the fall to the other walls in table order; 0044 gives the walls, not the spot"""
    front, side = hh / 2 + d / 2, hw / 2 + d / 2
    table = {
        "main_door": [(u, front, w, d) for u in along(max(0.0, (hw - w) / 2), step)],
        "stable_end": [(-side, u, d, w) for u in along(max(0.0, (hh - w) / 2), step)],
        "floored_rooms": [(side, u, d, w) for u in along(max(0.0, (hh - w) / 2), step)],
    }
    return [(q, first) for q in table[first]] + [(q, k) for k, v in table.items() if k != first for q in v]


def way_in_strip(house: Rect, bands: Sequence[Rect], faces: Sequence[Sequence[float]]) -> Rect | None:
    """The ground a grove farm's way in crosses: from its house's front wall to the break in its front band, as wide as the
    break - None where no band is broken (a farm with no ring). The front is the face whose band is laid in two pieces, the
    break between them (`rolling/dispersed.py`, `WAY_IN_FT`); bands and house in one frame, each `(cx, cy, w, h)`.

    Research: the way in kept open - research/questions/0036-groves-of-trees-around-farmhouses-yashikirin.drawing.html: the way in by the open front"""
    by_face: dict[tuple[float, float], list[Rect]] = {}
    for r, f in zip(bands, faces, strict=False):
        by_face.setdefault((float(f[0]), float(f[1])), []).append(r)
    front = next(((f, rs) for f, rs in by_face.items() if len(rs) >= 2), None)
    if front is None:
        return None
    (fx, fy), pieces = front
    ax = 0 if fx == 0 else 1  # the axis the band runs along: x for a north or south front, y for an east or west one
    lo = max((r[ax] + r[ax + 2] / 2 for r in pieces if r[ax] < house[ax]), default=None)  # the inner end of the piece before the break
    hi = min((r[ax] - r[ax + 2] / 2 for r in pieces if r[ax] > house[ax]), default=None)  # and of the piece after it
    if lo is None or hi is None:  # both pieces on one side of the house: no break to keep open
        return None
    near = house[1 - ax] + (fy if ax == 0 else fx) * house[3 - ax] / 2  # the house's front wall
    band = min((r[1 - ax] - (fy if ax == 0 else fx) * r[3 - ax] / 2 for r in pieces), key=lambda v: abs(v - near))  # the band's inner edge
    mid, span = (lo + hi) / 2, max(hi - lo, 0.0)
    across, depth = (near + band) / 2, abs(band - near)
    return (mid, across, span, depth) if ax == 0 else (across, mid, depth, span)


DOOR_OUT_FT = 8.0
"""How far past the yard's far edge a grove farm's front door stands, as the web places it (`ways/serve.front_door`: a footpath's
fabric gap plus 4 ft). Not `hamletgen/homesteads/rows.py`'s `FOOTPATH_DOOR_OUT_FT` (12 ft): that one is a row seat's door
measured off its FRAME's front edge, this one off the yard - the point the web's path starts from.

Research: the door past the yard - research/questions/0036-groves-of-trees-around-farmhouses-yashikirin.drawing.html: past the yard on the grove's open side"""

DOOR_ROOM_HALF_FT = 12.0
"""Half the square of ground kept clear about a grove farm's front door, so its path can leave it: a footpath's fabric gap (4 ft)
and most of the router's 10 ft cell beside its 3 ft tread - a map drawing convention, the router's own tolerance. Not
`rows.py`'s `DOOR_ROOM_FT` (16 ft): that is how far a row seat's door stands off the HARD ground, this how far the farm's own
fixtures stand off its door.

Research: the door's room - GUESS: no source could speak to it, a value of ours (feature 417 T36 pass P1, 2026-10-25); 12 ft each way, a routing tolerance a path needs to start"""


def door_room(house: Rect, yard: Rect | None, out: float, half: float) -> Rect | None:
    """The square kept clear about a grove farm's front door - `out` past the yard's far edge, straight out along the line
    from the house through the yard, `half` each way - or None with no yard (feature 374 wave 146: a privy laid on that spot
    left a row farm no path from its door).

    Research:
        the door past the yard - research/questions/0036-groves-of-trees-around-farmhouses-yashikirin.drawing.html: straight out past the yard's middle on the open front
        the door's room - GUESS: no source could speak to it, a value of ours (feature 417 T36 pass P1, 2026-10-25); `half` each way, a routing tolerance"""
    if yard is None:
        return None
    dx, dy = yard[0] - house[0], yard[1] - house[1]
    if abs(dx) >= abs(dy):
        s = 1.0 if dx >= 0 else -1.0
        return (yard[0] + s * (yard[2] / 2 + out), yard[1], 2 * half, 2 * half)
    s = 1.0 if dy >= 0 else -1.0
    return (yard[0], yard[1] + s * (yard[3] / 2 + out), 2 * half, 2 * half)


def _first(seats: Iterable[Rect], taken: Sequence[Rect], g: float) -> Rect | None:
    """The first of `seats` that `clears` every rect in `taken` by `g` - its test written inline (73,000 searches a map)."""
    rects = [(t[0], t[1], t[2], t[3]) for t in taken]
    for q in seats:
        qx, qy, qw, qh = q[0], q[1], q[2], q[3]
        for tx, ty, tw, th in rects:
            if abs(qx - tx) < (qw + tw) / 2 + g and abs(qy - ty) < (qh + th) / 2 + g:  # `clears`, the same arithmetic
                break
        else:
            return q
    return None


def _trunk(crown: Rect, px: Callable[[float], float]) -> Rect:
    return (crown[0], crown[1], px(TRUNK_FT), px(TRUNK_FT))


@lru_cache(maxsize=64)
def _sun_sector(w: float, d: float, radii: tuple[float, ...]) -> tuple[Rect, ...]:
    """The privy's sun-side seats, SE to S (112.5 to 202.5 degrees, every 7.5), at each of `radii` (px), nearest first - the
    same for every household of one privy size, so built once (seed 44: 73,000 privies each built 91 seats).

    Research:
        sunny-side sector - research/questions/0047-farm-privies-and-their-night-soil-benjo.drawing.html: bearings 112.5 to
            202.5 degrees, nearest first
        its cache size - NONE: a memo's size, which decides nothing about the place - 64
        its bearings in tenths - research/questions/0047-farm-privies-and-their-night-soil-benjo.drawing.html: 1125 to 2026 tenths of a degree, 112.5 to 202.5, every 75 (7.5 degrees, the search's step, ours)
    """
    sun: list[Rect] = []
    for rr in radii:
        for b in range(1125, 2026, 75):  # 112.5 to 202.5 degrees, tenths
            bd = math.radians(b / 10.0)
            sun.append((rr * math.sin(bd), -rr * math.cos(bd), w, d))
    return tuple(sun)


def _seats(
    kind: str, hw: float, hh: float, w: float, d: float, g: float, yard: Rect | None, privy: Rect | None, roll: Callable[[float], float], u: float, forms: FixtureForms, px: Callable[[float], float]
) -> list[Rect]:
    """The recorded seats of one fixture kind in the house frame, first choice first (the late placer's tables).

    Research:
        privy seats - research/questions/0047-farm-privies-and-their-night-soil-benjo.drawing.html: the sun-side sector on
            72.7%, else the attested places a hamlet farm has - the yard, the front, by the stable; not the barn while a hamlet
            draws none (the open found row `_seats#privy seats - the barn 0047 names`)
        privy sun-side radii - research/questions/0047-farm-privies-and-their-night-soil-benjo.drawing.html: tried from 18 ft (`PRIVY_SUN_MIN_FT`) out to the reach
        privy sun-side step - research/questions/0047-farm-privies-and-their-night-soil-benjo.html: most privies stood south or southeast of the house (Wang and Ochiai, Meiji); the 4 ft step is ours; the radii tried 4 ft apart
        privy in the front yard - GUESS research/questions/0047-farm-privies-and-their-night-soil-benjo.drawing.html: its edge 8 ft out from the front wall - the wall gap `g` (`WALL_GAP_FT`) and `PRIVY_FRONT_STEP_FT` past it - the page's own guess
        privy by the stable - research/questions/0047-farm-privies-and-their-night-soil-benjo.drawing.html: by the stable, at the house's stable end against the front wall's clear strip
        privy in the yard off the back wall - research/questions/0047-farm-privies-and-their-night-soil-benjo.drawing.html: held at a ken plus the wall gap (`PRIVY_YARD_STEP_FT`), past the page's ken, behind the found row at the constant
        shrine off its corner - research/questions/0219-household-shrines-yashikigami.html: the household shrine stood at a corner of the plot, northwest, northeast or southwest; the 14 ft is ours; 14 ft (`SHRINE_CORNER_FT`) out from the house's corner on both axes
        manure beyond the privy - research/questions/0042-manure-heaps-and-compost-kyuhi.drawing.html: on the side of the privy away from the house, along the line from its center; jittered a few feet;
            behind or beside the house where there is no privy
        manure heap fallback spots - GUESS research/questions/0042-manure-heaps-and-compost-kyuhi.drawing.html: beside the privy at 1.1 and 1.9
            of its width, then 10 ft further out; with no privy, at 0.3 of the house's width and depth
        retirement house - research/questions/0047-farm-privies-and-their-night-soil-benjo.html: storehouses and retirement houses stood to the southwest and west of the house (Wang and Ochiai, Meiji) - the side is rolled evenly over the back wall and both flanks, a departure the code keeps until feature 417 T33; off the back wall or a flank, the side rolled
        coop seats - research/questions/0045-chickens-and-chicken-coops.drawing.html: the east flank, the back wall or the
            west flank, rolled
        wood shed seats - GUESS research/questions/0043-firewood-stacks-and-sheds-kigoya.drawing.html: off the back wall and
            the flanks
        shrine corner - research/questions/0219-household-shrines-yashikigami.drawing.html: NW, NE or SW of the house
        household grave corner - research/questions/0236-where-a-village-buries-its-dead-its-own-ground-the-temple-yard-the-fields-or-the-home-plot.html: SE or NW of the house, then the other two corners
        household grave off the house's corner - research/questions/0236-where-a-village-buries-its-dead-its-own-ground-the-temple-yard-the-fields-or-the-home-plot.html: a household's grave stood at its plot's corner, southeast or northwest first, and also beside the plot, up the slope behind, in the front garden or in a field's corner - only the corner form is drawn, a departure the code keeps until feature 417 T33; the 14 ft is ours; 14 ft out each way (`SHRINE_CORNER_FT`) standing for the plot's corner; no plot's size is recorded with its grave
        seat positions along each wall - GUESS: no source could speak to it, a value of ours (feature 417 T36 pass P1, 2026-10-25); privy 0.3 / 0.40 / -0.35 hw, coop 0.34 hw spread and
            0.3 hh, wood shed 0.25 hw and 0.1 hh
        its unstated figures - GUESS: searched, the record silent (feature 417 T38 pass N9, 2026-10-25) - 0.4 (sideways place of the front privy (0.40 of the house's half-width))
        its figures guessed on 0042 - GUESS research/questions/0042-manure-heaps-and-compost-kyuhi.drawing.html: 9 (heap's distance from the privy varies over a 9 ft spread ("varies by a few feet"))
        its salts, guards and sentinels - NONE: they decide nothing about the place - 102.4 (salt); 105.9 (salt); 105.5 (salt)
    """
    if kind == "privy":
        seat = {  # the four attested seats (269 B10); -x is the shed end of the house, where the doma and its stable are
            "yard": (hw * 0.3, -(hh / 2 + g + px(PRIVY_YARD_STEP_FT) + d / 2), w, d),
            "front": (hw * 0.40, hh / 2 + g + px(PRIVY_FRONT_STEP_FT) + d / 2, w, d),
            "stable": (-hw * 0.35, hh / 2 + g + d / 2, w, d),
        }
        # NO BARN, NO BARN SEAT (feature 328; 0047 puts the privy "inside the barn", a building of its own, and a hamlet draws
        # no barn - `farm_fixtures.py`): the barn's share goes to the three places a hamlet farm has, at their own weights
        weights = tuple((k, p) for k, p in forms.privy_weights if k in privy_places(forms))
        first = weighted(weights, u * sum(p for _k, p in weights))  # the roll spread over the places left
        attested = [seat[first]] + [seat[k] for k, _ in weights if k != first]
        # THE OUTHOUSE FACES THE SUN, AT THE RATE THE RECORD GIVES (feature 152 T07): SE to S on 72.7% of households, the
        # sector walked nearest first - bearings in the house's frame, where its front is the south it was seated facing
        if roll(SALT[kind] + 0.25) >= PRIVY_SUNNY_SHARE:
            return attested
        # ...THE RADIUS IS TO THE PRIVY'S CENTER, so a privy of a rolled size reaches the same NEAR EDGE as a one-ken one
        # (`privy_sun_reach_ft`, feature 280)
        reach_ft = privy_sun_reach_ft(w / px(1.0), d / px(1.0))
        return [*_sun_sector(w, d, tuple(px(float(r_ft)) for r_ft in range(int(PRIVY_SUN_MIN_FT), int(reach_ft) + 1, 4))), *attested]
    if kind == "manure":
        if privy is None:
            return [(hw * 0.3, -(hh / 2 + g + d / 2), w, d), (hw / 2 + g + d / 2, hh * 0.3, d, w)]
        plx, ply = privy[0], privy[1]
        # BEYOND THE PRIVY (feature 152 T16/T17) means AWAY FROM THE HOUSE along the line from its center to the privy's
        # (feature 328; 0042: "on the side away from the house") - a sign on y alone stepped a flank privy's heap sideways
        n = math.hypot(plx, ply)
        ux, uy = (plx / n, ply / n) if n > 1e-9 else (0.0, 1.0)
        sx, sy = -uy, ux  # across that line
        # at a distance jittered off the household's own roll: the privy's and the heap's half-extents along the line, the gap
        pout = abs(ux) * privy[2] / 2 + abs(uy) * privy[3] / 2 + g + abs(ux) * w / 2 + abs(uy) * d / 2 + px(9.0) * (roll(102.4) - 0.5)

        def at(along: float, across: float) -> Rect:
            return (plx + ux * along + sx * across, ply + uy * along + sy * across, w, d)

        return [at(pout, 0.0), at(0.0, w * 1.1), at(0.0, -w * 1.1), at(pout, w * 1.1), at(pout, -w * 1.1), at(pout + px(10.0), 0.0), at(0.0, w * 1.9), at(0.0, -w * 1.9)]
    if kind == "retirement":  # OFF THE BACK WALL OR A FLANK, a ken out and then two (269 B42), the side rolled per homestead
        sides = [(0.0, -1.0), (1.0, 0.0), (-1.0, 0.0)]
        k = int(u * 3) % 3
        out: list[Rect] = []
        for gap in (px(v) for v in forms.retirement_gaps):
            for sx, sy in sides[k:] + sides[:k]:
                out.append((0.0, -(hh / 2 + gap + d / 2), w, d) if sy else (sx * (hw / 2 + gap + d / 2), 0.0, d, w))
        return out
    if kind == "coop":  # the rear yard, the first seat turned by the household's roll so no two stand at one bearing
        cjx = hw * 0.34 * (roll(105.9) - 0.5) * 2.0
        seats = [(hw / 2 + g + d / 2, hh * 0.3, d, w), (cjx, -(hh / 2 + g + d / 2), w, d), (-(hw / 2 + g + d / 2), -hh * 0.3, d, w)]
        k = int(roll(105.5) * len(seats)) % len(seats)
        return seats[k:] + seats[:k]
    if kind == "woodpile":  # THE WOOD SHED (feature 280 M21): the old stack's walls, a ken further out - a building of its own
        st, back = px(WOODSHED_STEP_FT), -(hh / 2 + g + d / 2)
        return [(-hw * 0.25, back - st, w, d), (hw * 0.25, back - st, w, d), (hw / 2 + g + st + d / 2, hh * 0.1, d, w), (-(hw / 2 + g + st + d / 2), hh * 0.1, d, w)]
    # the household shrine: a plot corner, rolled by compass name (NW the likeliest, 17 of 37; NE the kimon; SW Tokushima);
    # the household grave the same distance off the house's corner, at the SE or NW (0236), then the other two
    off = px(SHRINE_CORNER_FT)
    corner = {k: (sx * (hw / 2 + off), sy * (hh / 2 + off), w, d) for k, (sx, sy) in CORNER_SIGNS.items()}
    table = GRAVE_CORNERS if kind == "grave" else SHRINE_CORNERS
    first = weighted(table, u)
    rest = [k for k, _ in table if k != first] + ([k for k in ("NE", "SW") if k not in dict(table)] if kind == "grave" else [])
    return [corner[first]] + [corner[k] for k in rest]


#: The rakes a persimmon's seat is tested at, every `SUN_TURN_STEP_DEG` across the map's range: the sun ground is the
#: world's, the seat the house's unturned frame, and the house is turned after its template is laid (`_bundle_geom`).
SUN_TURN_STEP_DEG = 5.0


def sun_turns(lo: float, hi: float) -> tuple[float, ...]:
    """The rakes from `lo` to `hi` degrees, both ends and every `SUN_TURN_STEP_DEG` between."""
    n = max(1, math.ceil((hi - lo) / SUN_TURN_STEP_DEG))
    return tuple(lo + (hi - lo) * k / n for k in range(n + 1))


def _sunlit(ground: Sequence[Rect], shade: float, turns: Sequence[float]) -> Callable[[float, float, float], bool]:
    """Is a crown of radius r at (x, y) clear of every plot's sun ground at every rake? Each rake turns the crown and the
    plots together about the house's center, the plots' boxes as `turned_box` draws them, and asks `crown_in_ground` (the predicate `crown_shades` reads) in the
    world's axes, where the sun is.

    Research: persimmon out of the plots' sun - research/questions/0038-sunlight-and-shade-on-the-farm.drawing.html"""
    if shade <= 0.0 or not ground:
        return lambda x, y, r: True
    frames = []
    for t in turns:
        th = math.radians(t)
        c, s, ac, as_ = math.cos(th), math.sin(th), abs(math.cos(th)), abs(math.sin(th))
        # each plot's sun ground taken once per rake (`sun_ground`), not once per crown asked of it
        frames.append((c, s, [sun_ground((q[0] * c - q[1] * s, q[0] * s + q[1] * c, q[2] * ac + q[3] * as_, q[2] * as_ + q[3] * ac), shade) for q in ground]))

    def clear(x: float, y: float, r: float) -> bool:
        return not any(crown_in_ground(x * c - y * s, x * s + y * c, r, g) for c, s, grounds in frames for g in grounds)

    return clear


def _persimmon(hw: float, hh: float, taken: Sequence[Rect], roofs: Sequence[Rect], front_first: bool, px: Callable[[float], float], sunlit: Callable[[float, float, float], bool]) -> Rect | None:
    """The yard persimmon (269 B14): the dooryard in front - the front corners and straight out - or behind the house,
    rolled against the hamlet's front share; its trunk clear of every part, its crown over no roof and out of every yard's
    and bed's sun (`sunlit`, GM 2026-10-02), so a farm that dries its grain in a front yard keeps its persimmon behind the
    house. Stepped out until it stands, within the dooryard (`PERSIMMON_DOORYARD_FT`); None where no seat there does.

    Research:
        persimmon in front or behind - research/questions/0046-fruit-trees-in-the-farmyard-persimmon-chestnut-and-plum-kaki.drawing.html:
            the front corners and straight out, or the same behind
        crown over no roof - CONVENTION: the crown kept off every roof so the building stays visible
        within the dooryard - research/questions/0046-fruit-trees-in-the-farmyard-persimmon-chestnut-and-plum-kaki.drawing.html: paced out no farther than `PERSIMMON_DOORYARD_FT`, else none
        its search steps and tolerances - GUESS: no source could speak to it, a value of ours (feature 417 T38 pass N9, 2026-10-25) - 0.75 (the same, behind the house)
    """
    r = px(PERSIMMON_CROWN_FT)
    trunk = px(TRUNK_FT)
    reach = math.hypot(hw / 2, hh / 2) + r + CANOPY_PAD + 1.0
    front = [(sx * reach * 0.75, reach * 0.75) for sx in (1.0, -1.0)] + [(0.0, reach)]
    back = [(sx * reach * 0.75, -reach * 0.75) for sx in (1.0, -1.0)] + [(0.0, -reach)]
    ring = front + back if front_first else back + front
    steps = [px(s) for s in PERSIMMON_STEPS_FT] + [px(STEP_FT) * k + px(PERSIMMON_STEPS_FT[-1]) for k in range(1, OUT_STEPS + 1)]
    paced = ((lx * (reach + st) / reach, ly * (reach + st) / reach) for st in steps for lx, ly in ring)
    seat = next(
        (
            (lx, ly, 2 * r, 2 * r)
            for lx, ly in chain(ring, paced)
            if in_dooryard(lx, ly, r, hw, hh, px(PERSIMMON_DOORYARD_FT))
            and clears((lx, ly, trunk, trunk), taken, 2.0)
            and clears((lx, ly, 2 * r, 2 * r), roofs, CANOPY_PAD)
            and sunlit(lx, ly, r + px(SHADE_MARGIN_FT))
        ),
        None,
    )
    return seat


def in_dooryard(lx: float, ly: float, r: float, hw: float, hh: float, reach: float) -> bool:
    """Does a crown of radius `r` at (`lx`, `ly`) in the house's frame keep its edge within `reach` of the house's walls?"""
    dx, dy = max(abs(lx) - hw / 2, 0.0), max(abs(ly) - hh / 2, 0.0)
    return math.hypot(dx, dy) - r <= reach


def world_fixtures(laid: Mapping[str, Any]) -> list[tuple[str, Rect]]:
    """The laid fixtures in drawing order."""
    return [(k, laid[k]) for k in FIXTURE_ORDER if k in laid]
