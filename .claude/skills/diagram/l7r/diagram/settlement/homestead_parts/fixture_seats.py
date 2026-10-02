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
FIXTURE_ORDER = ("retirement", "bath", "woodpile", "privy", "manure", "coop", "shrine", "persimmon")

WALL_GAP_FT = 3.5  # a fixture's edge off the wall or part it stands by: the review measured -0.3 ft at 3.0 against the drawn wall
STEP_FT = 8.0  # the outward pace a fixture takes when every recorded seat is taken (the late placer's own rung)
OUT_STEPS = 24  # paces offered: 192 ft, past any bundle's parts
WALL_SLIDE_FT = 4.0  # the spacing of the places offered along a wall to a bath room or a wood shed
PRIVY_YARD_STEP_FT = 6.0  # the yard outhouse a ken off the back wall (GUESS)
PRIVY_FRONT_STEP_FT = 8.0  # the front-yard privy a step out from the front wall (GUESS)
PRIVY_SUN_MIN_FT = 18.0  # the sun-side search's radii, 18 to 48 ft (`PRIVY_SUN_MAX_FT`'s reasons, fixtures.py)
PRIVY_SUN_MAX_FT = 48.0
PRIVY_SUNNY_SHARE = 0.727  # Wang & Ochiai 2022: 72.7% of outhouses SE to S (the GM, 2026-08-29: used literally)
WOODSHED_STEP_FT = 6.0  # the wood shed a ken off the wall it serves, a building of its own (GUESS: where on the plot no page says)
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
# THE BATH ROOM (feature 280 M22, research/homesteads/740): joined to the main house - beside its main door, at the far end
# of its stable wing (the house's -x end, where the doma and its stable are), or joined to its floored rooms (the +x end) -
# a room of 1-2 tsubo: one ken out from the wall, one to two ken along it, rolled per household (a calibration on the
# registers' 1-2 tsubo). The free-standing bath shed is found only in the twentieth century, and is not drawn.
BATH_DEPTH_FT = 6.0
BATH_LENGTH_FT = (6.0, 12.0)
BATH_WALLS = ("main_door", "stable_end", "floored_rooms")
SHRINE_CORNER_FT = 14.0  # the household shrine a plot corner off the house's corner
TRUNK_FT = 4.0  # the persimmon's trunk box
CANOPY_PAD = 0.6  # the crown's placement clearance off a roof (`Settlement.CANOPY_PAD`)
PERSIMMON_STEPS_FT = (10.0, 20.0)  # the persimmon's ring a step out, and two
SHADE_MARGIN_FT = 2.0  # the seat stricter than the map's check by a hair, as the sun corridor's placer is (`fit._sun_corridor_ok`)

SHRINE_CORNERS = (("NW", 0.45), ("NE", 0.35), ("SW", 0.20))
CORNER_SIGNS = {"NW": (-1.0, -1.0), "NE": (1.0, -1.0), "SW": (-1.0, 1.0)}
SALT = {"privy": 101.0, "manure": 102.0, "woodpile": 103.0, "bath": 104.0, "coop": 105.0, "shrine": 106.0, "persimmon": 107.0, "retirement": 131.7}


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
    left, the wood shed (feature 280 M21: the eaves stack and the kizuma are modern-only), so it rolls none."""

    privy_weights: tuple[tuple[str, float], ...] = (("yard", 0.35), ("front", 0.30), ("stable", 0.20), ("barn", 0.15))
    bath_seat: str = "main_door"
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
    """How far from its house's center the sun-side search may seat a privy of `w_ft` x `d_ft`: `PRIVY_SUN_MAX_FT`, plus the
    half-length it has past the one-ken default, so its near edge stands no farther out than a one-ken privy's (feature
    280, settlement-review of Sawada: every privy of 18 x 12 ft or more fell through to the north-east seat, 7 of 17)."""
    return PRIVY_SUN_MAX_FT + max(0.0, (max(w_ft, d_ft) - 6.0) / 2.0)


def fixture_ft(kind: str, forms: FixtureForms, roll: Callable[[float], float] | None = None) -> tuple[float, float]:
    """A fixture's size in real feet, `(along its wall, out from it)`, in the form the hamlet rolled: the privy one of the
    Kakimochi table's sixteen and the bath room 6 ft out by 6-12 ft along, each rolled off the household's own position roll
    `roll` (feature 280, research/questions/0047-farm-privies-and-their-night-soil-benjo.html and 740; the kinds' one-ken default without one); every other kind its one
    size (`FIXTURE_FT`), the pit's, the crown's or the retirement house's."""
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
    (north, or the west end - `kura_rect`, the table `Settlement.house` draws from)."""
    rects = [(0.0, 0.0, hw, hh)]
    if kura_side is not None:
        rects.append(kura_rect(hw, hh, kura_side, ppf))
    return rects


def against_a_wall(seat: Sequence[float], rects: Sequence[Rect], g: float, tol: float = 1.5) -> bool:
    """Does a seat `(lx, ly, w, d)` in the house frame stand against a wall of its steading - its edge within the wall gap
    `g` (plus `tol`) of one of `rects`, and overlapping it along that wall (feature 287, homes H35)? The one predicate the
    wood shed's (`shed_off_a_wall`) and the bath room's (`joined_to_house`) placers and their tests read."""
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
) -> dict[str, Rect]:
    """Each of `kinds` laid beside the parts already laid, in the house's unturned frame centered on it: `{kind: (x, y, w,
    h)}`, the box AS LAID (a flank seat turned to lie along its flank). `roofs` are the built parts - the house first, the
    kura, the byre, the well-house - and `ground` the open ones, the yard and the beds, whose sun a persimmon's crown keeps
    out of: `shade` px east, west and south of each (`PERSIMMON_SHADE_FT`), at every rake in `turns` (degrees - the house
    is turned after its parts are laid, and the sun is not);
    `yard` is the threshing yard, `kura` whether the house keeps one on its north wall, `annex` the byre where the household
    keeps one (its walls take a wood shed too); `roll` the household's position roll (`Settlement._hjit` at its seat).
    `notes`, where given, receives what the drawing needs beyond the box: each rolled size in feet (`ft`, `fixture_ft`) and
    the wall the bath room took (`bath_seat`). Every kind is laid: the outward paces reach free ground past any parts. Raises
    only for a bath room with no place along the house's three attested walls, or a wood shed with no place a ken off a
    wall of its steading, each named - a refusal, never a room walked out into the yard (feature 280 M21, M22)."""
    g = px(WALL_GAP_FT)
    taken: list[Rect] = [*roofs, *ground]
    built: list[Rect] = list(roofs)
    laid: dict[str, Rect] = {}
    ft: dict[str, tuple[float, float]] = {}
    for kind in [k for k in FIXTURE_ORDER if k in kinds]:
        ft[kind] = fixture_ft(kind, forms, roll)
        w, d = px(ft[kind][0]), px(ft[kind][1])
        u = roll(SALT[kind] + 0.5)
        if kind == "persimmon":
            seat = _persimmon(hw, hh, taken, built, u < forms.persimmon_front, px, _sunlit(ground, shade, turns))
        elif kind == "woodpile":
            walls = steading_rects(hw, hh, "N" if kura else None, px(1.0)) + ([annex] if annex is not None else []) + ([laid["retirement"]] if "retirement" in laid else [])
            seat = _wood_shed(hw, hh, w, d, g, walls, taken, px)
        elif kind == "bath":
            named = bath_room_seats(forms.bath_seat, hw, hh, w, d, (yard[0], yard[2] / 2) if yard is not None else None)
            named += bath_room_slides(forms.bath_seat, hw, hh, w, d, px(WALL_SLIDE_FT))
            house = roofs[0]
            others = [t for t in taken if t is not house]
            got = next(((q, n) for q, n in named if clears(q, [house], -1e-6) and clears(q, others, g)), None)
            if got is None:
                raise FixtureUnlaid("a bath room found no place on the house's front wall or either end wall")
            seat = got[0]
            if notes is not None:
                notes["bath_seat"] = got[1]
        else:
            seats = _seats(kind, hw, hh, w, d, g, yard, laid.get("privy"), roll, u, forms, px)
            found = _first(chain(seats, outward(seats, px(STEP_FT), OUT_STEPS)), taken, g)
            assert found is not None, "the outward paces reach free ground"  # noqa: S101 - finite parts, 192 ft of paces
            seat = found
        laid[kind] = seat
        taken.append(_trunk(seat, px) if kind == "persimmon" else seat)
        if kind != "persimmon":
            built.append(seat)
    if notes is not None:
        notes["ft"] = ft
    return laid


def shed_off_a_wall(seat: Rect, walls: Sequence[Rect], g: float, px: Callable[[float], float]) -> bool:
    """THE WOOD SHED'S RULE (feature 280 M21; settlement-reviews of Inashiro and Kuwabata, where sheds stood 25-37 ft out,
    between farmsteads): a building of its own a ken off its house - clear of the house by the wall gap and `WOODSHED_STEP_FT`
    - and never walked out across the dooryard: within the gap, a ken and one outward pace (`STEP_FT`) of a wall of its
    steading (`against_a_wall`), overlapping that wall along it. The one predicate the placer and its test read."""
    return clears(seat, walls[:1], g + px(WOODSHED_STEP_FT) - 1e-6) and against_a_wall(seat, walls, g + px(WOODSHED_STEP_FT) + px(STEP_FT))


def joined_to_house(seat: Rect, hw: float, hh: float, tol: float = 1e-6) -> bool:
    """THE BATH ROOM'S RULE (feature 280 M22): a room of the house - one edge on a wall of the `hw` x `hh` house, overlapping
    it along that wall, and not inside it. The one predicate the placer and its test read."""
    gx = abs(seat[0]) - (seat[2] + hw) / 2
    gy = abs(seat[1]) - (seat[3] + hh) / 2
    return (abs(gx) <= tol and gy < 0.0) or (abs(gy) <= tol and gx < 0.0)


def _wood_shed(hw: float, hh: float, w: float, d: float, g: float, walls: Sequence[Rect], taken: Sequence[Rect], px: Callable[[float], float]) -> Rect:
    """The wood shed (feature 280 M21): the recorded seats - off the back wall and the flanks, a ken further out than a stack
    stood - then those a pace further, then every place a ken off each wall of the steading; the first that clears the parts
    laid and keeps `shed_off_a_wall`. None of them walks it out into the dooryard."""
    seats = _seats("woodpile", hw, hh, w, d, g, None, None, lambda _salt: 0.0, 0.0, FixtureForms(), px)
    offered = chain(seats, outward(seats, px(STEP_FT), 1), wall_places(walls, w, d, g + px(WOODSHED_STEP_FT), px(WALL_SLIDE_FT)))
    found = _first((q for q in offered if shed_off_a_wall(q, walls, g, px)), taken, g)
    if found is None:
        raise FixtureUnlaid("a wood shed found no place a ken off any wall of its steading")
    return found


def bath_room_seats(first: str, hw: float, hh: float, w: float, d: float, yard: tuple[float, float] | None = None) -> list[tuple[Rect, str]]:
    """The bath room's seats in the house frame (feature 280 M22, research/homesteads/740), `first` tried first then the
    other attested seats: beside the MAIN DOOR (the front wall, either side of the door at its middle), at the far end of
    the STABLE WING (the -x end wall, where the doma and its stable are), or joined to the FLOORED ROOMS (the +x end wall).
    Each abuts its wall - a room of the house, not a building beside it. Each seat carries its name, and the record keeps the
    one taken: the work yard lies before the front wall, and where it covers the wall the bath falls to the next seat - the
    reviews of Kuwabata and Sawada (feature 280) found a declared `main_door` never drawn, and then an end-wall corner offered
    as `main_door` that read as the floored rooms' seat, so the record now says which seat each bath room took."""
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
    beds, byre or retirement house still joins its bath to a wall where the room fits (feature 287: every kind is laid)."""
    front, side = hh / 2 + d / 2, hw / 2 + d / 2
    table = {
        "main_door": [(u, front, w, d) for u in along(max(0.0, (hw - w) / 2), step)],
        "stable_end": [(-side, u, d, w) for u in along(max(0.0, (hh - w) / 2), step)],
        "floored_rooms": [(side, u, d, w) for u in along(max(0.0, (hh - w) / 2), step)],
    }
    return [(q, first) for q in table[first]] + [(q, k) for k, v in table.items() if k != first for q in v]


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
    same for every household of one privy size, so built once (seed 44: 73,000 privies each built 91 seats)."""
    sun: list[Rect] = []
    for rr in radii:
        for b in range(1125, 2026, 75):  # 112.5 to 202.5 degrees, tenths
            bd = math.radians(b / 10.0)
            sun.append((rr * math.sin(bd), -rr * math.cos(bd), w, d))
    return tuple(sun)


def _seats(
    kind: str, hw: float, hh: float, w: float, d: float, g: float, yard: Rect | None, privy: Rect | None, roll: Callable[[float], float], u: float, forms: FixtureForms, px: Callable[[float], float]
) -> list[Rect]:
    """The recorded seats of one fixture kind in the house frame, first choice first (the late placer's tables)."""
    if kind == "privy":
        seat = {  # the four attested seats (269 B10); -x is the shed end of the house, where the doma and its stable are
            "yard": (hw * 0.3, -(hh / 2 + g + px(PRIVY_YARD_STEP_FT) + d / 2), w, d),
            "front": (hw * 0.40, hh / 2 + g + px(PRIVY_FRONT_STEP_FT) + d / 2, w, d),
            "stable": (-hw * 0.35, hh / 2 + g + d / 2, w, d),
            "barn": (hw / 2 + g + d / 2, -hh * 0.25, d, w),
        }
        first = weighted(forms.privy_weights, u)
        attested = [seat[first]] + [seat[k] for k, _ in forms.privy_weights if k != first]
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
        out_ = -1.0 if ply < 0 else 1.0
        # BEYOND THE PRIVY (feature 152 T16/T17), at a distance jittered off the household's own roll
        pout = privy[3] / 2 + g + d / 2 + px(9.0) * (roll(102.4) - 0.5)
        return [
            (plx, ply + out_ * pout, w, d),
            (plx + w * 1.1, ply, w, d),
            (plx - w * 1.1, ply, w, d),
            (plx + w * 1.1, ply + out_ * pout, w, d),
            (plx - w * 1.1, ply + out_ * pout, w, d),
            (plx, ply + out_ * (pout + px(10.0)), w, d),
            (plx + w * 1.9, ply, w, d),
            (plx - w * 1.9, ply, w, d),
        ]
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
    # the household shrine: a plot corner, rolled by compass name (NW the likeliest, 17 of 37; NE the kimon; SW Tokushima)
    off = px(SHRINE_CORNER_FT)
    corner = {k: (sx * (hw / 2 + off), sy * (hh / 2 + off), w, d) for k, (sx, sy) in CORNER_SIGNS.items()}
    first = weighted(SHRINE_CORNERS, u)
    return [corner[first]] + [corner[k] for k, _ in SHRINE_CORNERS if k != first]


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
    world's axes, where the sun is."""
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


def _persimmon(hw: float, hh: float, taken: Sequence[Rect], roofs: Sequence[Rect], front_first: bool, px: Callable[[float], float], sunlit: Callable[[float, float, float], bool]) -> Rect:
    """The yard persimmon (269 B14): the dooryard in front - the front corners and straight out - or behind the house,
    rolled against the hamlet's front share; its trunk clear of every part, its crown over no roof and out of every yard's
    and bed's sun (`sunlit`, GM 2026-10-02), so a farm that dries its grain in a front yard keeps its persimmon behind the
    house. Stepped out until it stands."""
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
            if clears((lx, ly, trunk, trunk), taken, 2.0) and clears((lx, ly, 2 * r, 2 * r), roofs, CANOPY_PAD) and sunlit(lx, ly, r + px(SHADE_MARGIN_FT))
        ),
        None,
    )
    assert seat is not None, "the persimmon's paces reach free ground"  # noqa: S101 - finite parts, 200 ft of paces behind the house
    return seat


def world_fixtures(laid: Mapping[str, Any]) -> list[tuple[str, Rect]]:
    """The laid fixtures in drawing order."""
    return [(k, laid[k]) for k in FIXTURE_ORDER if k in laid]
