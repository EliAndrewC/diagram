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

Every seat table is the one the late placer read (research/homesteads.html "The farmstead's fixtures", the attested seats
labeled there), in the house's unturned frame: +y the sunny front where the yard is, -y the back wall, the kura on the
north wall. A seat is taken when its box clears every part laid before it by the wall gap; failing every recorded seat, a
fixture is offered the same seats stepped outward a pace at a time - still its own plot, where the ground past the parts
is free by construction (the parts are finite, the steps are not) - except the two forms whose rule is the seat itself:
the eaves stack stands against a wall of its steading (`against_a_wall`, homes H35) and the joined bath at a corridor's
length off a wall (269 B12), each offered every place along the walls instead.
"""

from __future__ import annotations

import math
from collections.abc import Callable, Iterable, Iterator, Mapping, Sequence
from dataclasses import dataclass
from itertools import chain
from typing import Any

from ..farm_fixtures import FIXTURE_FT, PERSIMMON_CROWN_FT, PIT_FT, WOODPILE_FORM_FT

Rect = tuple[float, float, float, float]  # (center x, center y, width, height), the house's unturned frame

#: The order the kinds are laid in: the retirement house first - a second roof of the family, off the back wall or a flank
#: (269 B42), the largest part after the kura; then the two whose rule IS the seat - the joined bath a corridor off a
#: wall, the eaves stack against one (which has the kura's, the byre's and the retirement house's walls besides) - so the
#: walls are theirs before the free-standing kinds take the ground by them; then the late placer's order (the buildings,
#: then the stack, which has the most seats); the persimmon last - its crown may overhang the yard and the beds, never a
#: roof.
FIXTURE_ORDER = ("retirement", "bath", "woodpile", "privy", "manure", "coop", "shrine", "persimmon")

WALL_GAP_FT = 3.5  # a fixture's edge off the wall or part it stands by: the review measured -0.3 ft at 3.0 against the drawn wall
STEP_FT = 8.0  # the outward pace a fixture takes when every recorded seat is taken (the late placer's own rung)
OUT_STEPS = 24  # paces offered: 192 ft, past any bundle's parts
WALL_SLIDE_FT = 4.0  # the spacing of the places offered along a wall to an eaves stack or a joined bath
PRIVY_YARD_STEP_FT = 6.0  # the yard outhouse a ken off the back wall (GUESS)
PRIVY_FRONT_STEP_FT = 8.0  # the front-yard privy a step out from the front wall (GUESS)
PRIVY_SUN_MIN_FT = 18.0  # the sun-side search's radii, 18 to 48 ft (`PRIVY_SUN_MAX_FT`'s reasons, fixtures.py)
PRIVY_SUN_MAX_FT = 48.0
PRIVY_SUNNY_SHARE = 0.727  # Wang & Ochiai 2022: 72.7% of outhouses SE to S (the GM, 2026-08-29: used literally)
WOODSHED_STEP_FT = 6.0  # the woodshed a ken off the wall it serves (GUESS)
BATH_CORRIDOR_FT = 6.0  # the joined bath's corridor, one ken long (GUESS)
BATH_CORRIDOR_W_FT = 3.0  # and half a ken wide (GUESS)
SHRINE_CORNER_FT = 14.0  # the household shrine a plot corner off the house's corner
TRUNK_FT = 4.0  # the persimmon's trunk box
CANOPY_PAD = 0.6  # the crown's placement clearance off a roof (`Settlement.CANOPY_PAD`)
PERSIMMON_STEPS_FT = (10.0, 20.0)  # the persimmon's ring a step out, and two

SHRINE_CORNERS = (("NW", 0.45), ("NE", 0.35), ("SW", 0.20))
CORNER_SIGNS = {"NW": (-1.0, -1.0), "NE": (1.0, -1.0), "SW": (-1.0, 1.0)}
SALT = {"privy": 101.0, "manure": 102.0, "woodpile": 103.0, "bath": 104.0, "coop": 105.0, "shrine": 106.0, "persimmon": 107.0, "retirement": 131.7}


@dataclass(frozen=True)
class FixtureForms:
    """The hamlet's fixture forms, rolled once per map (`hamletgen/homesteads/fixtures.py`, `fixture_forms`): the privy
    seats' weights, the bath's seat, the woodpile's form, the persimmon's front share and the manure's form."""

    privy_weights: tuple[tuple[str, float], ...] = (("yard", 0.35), ("front", 0.30), ("stable", 0.20), ("barn", 0.15))
    bath_seat: str = "front_yard"
    woodpile_form: str = "eaves"
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


def fixture_size(kind: str, forms: FixtureForms, px: Callable[[float], float]) -> tuple[float, float]:
    """A fixture's footprint `(along its wall, out from it)` at the map's scale, in the form the hamlet rolled."""
    if kind == "manure" and forms.manure_form == "pit":
        return px(PIT_FT), px(PIT_FT)
    if kind == "woodpile" and forms.woodpile_form == "shed":
        ft = WOODPILE_FORM_FT["shed"]
        return px(ft[0]), px(ft[1])
    if kind == "persimmon":
        return px(PERSIMMON_CROWN_FT) * 2.0, px(PERSIMMON_CROWN_FT) * 2.0
    if kind == "retirement":
        return px(forms.retirement_ft[0]), px(forms.retirement_ft[1])
    ft = FIXTURE_FT[kind]
    return px(ft[0]), px(ft[1])


def clears(r: Rect, taken: Sequence[Rect], gap: float) -> bool:
    """Does `r` stand clear of every rect in `taken` by `gap`?"""
    return all(abs(r[0] - t[0]) >= (r[2] + t[2]) / 2 + gap or abs(r[1] - t[1]) >= (r[3] + t[3]) / 2 + gap for t in taken)


def steading_rects(hw: float, hh: float, kura_side: str | None) -> list[Rect]:
    """The walls an eaves stack may stand against, in the house's unturned frame: the house, and its kura where it keeps
    one (north, or the west end - `Settlement.house`'s own kura footprint)."""
    rects = [(0.0, 0.0, hw, hh)]
    if kura_side == "N":
        rects.append((0.0, -0.60 * hh, 0.46 * hw, 0.30 * hh))
    elif kura_side is not None:
        rects.append((-0.64 * hw, 0.0, 0.32 * hw, 0.56 * hh))
    return rects


def against_a_wall(seat: Sequence[float], rects: Sequence[Rect], g: float, tol: float = 1.5) -> bool:
    """Does a seat `(lx, ly, w, d)` in the house frame stand against a wall of its steading - its edge within the wall gap
    `g` (plus `tol`) of one of `rects`, and overlapping it along that wall (feature 287, homes H35: 5-7 of Mizuguchi's 10
    stacks stood 10.5-27.8 ft off any building)? The one predicate the placer and its test read."""
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
) -> dict[str, Rect]:
    """Each of `kinds` laid beside the parts already laid, in the house's unturned frame centered on it: `{kind: (x, y, w,
    h)}`, the box AS LAID (a flank seat turned to lie along its flank), plus `bath_corridor` for a joined bath. `roofs` are
    the built parts - the house first, the kura, the byre, the well-house - and `ground` the open ones, the yard and the
    beds, which a persimmon's crown may shade; `yard` is the threshing yard, `kura` whether the house keeps one on its
    north wall, `annex` the byre where the household keeps one (its walls take an eaves stack too); `roll` the household's
    position roll (`Settlement._hjit` at its seat). Every kind is laid: the outward
    paces reach free ground past any parts. Raises only for an eaves stack or a joined bath with no place along any wall,
    which the bundle's own parts cannot cause (they cover at most three sides of a house)."""
    g = px(WALL_GAP_FT)
    taken: list[Rect] = [*roofs, *ground]
    built: list[Rect] = list(roofs)
    laid: dict[str, Rect] = {}
    for kind in [k for k in FIXTURE_ORDER if k in kinds]:
        w, d = fixture_size(kind, forms, px)
        u = roll(SALT[kind] + 0.5)
        if kind == "persimmon":
            seat = _persimmon(hw, hh, yard, taken, built, u < forms.persimmon_front, px)
        elif kind == "woodpile" and forms.woodpile_form != "shed":
            walls = steading_rects(hw, hh, "N" if kura else None) + ([annex] if annex is not None else []) + ([laid["retirement"]] if "retirement" in laid else [])
            found = _first(wall_places(walls, w, d, g, px(WALL_SLIDE_FT)), taken, g)
            if found is None:
                raise ValueError("an eaves stack found no place along any wall of its steading")
            seat = found
        elif kind == "bath" and forms.bath_seat == "corridor":
            seat, corridor = _joined_bath(hw, hh, w, d, taken, g, px)
            laid["bath_corridor"] = corridor
            taken.append(corridor)
            built.append(corridor)
        else:
            seats = _seats(kind, hw, hh, w, d, g, yard, laid.get("privy"), roll, u, forms, px)
            found = _first(chain(seats, outward(seats, px(STEP_FT), OUT_STEPS)), taken, g)
            assert found is not None, "the outward paces reach free ground"  # noqa: S101 - finite parts, 192 ft of paces
            seat = found
        laid[kind] = seat
        taken.append(_trunk(seat, px) if kind == "persimmon" else seat)
        if kind != "persimmon":
            built.append(seat)
    return laid


def _first(seats: Iterable[Rect], taken: Sequence[Rect], g: float) -> Rect | None:
    return next((q for q in seats if clears(q, taken, g)), None)


def _trunk(crown: Rect, px: Callable[[float], float]) -> Rect:
    return (crown[0], crown[1], px(TRUNK_FT), px(TRUNK_FT))


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
        sun: list[Rect] = []
        for r_ft in range(int(PRIVY_SUN_MIN_FT), int(PRIVY_SUN_MAX_FT) + 1, 4):
            for b in range(1125, 2026, 75):  # 112.5 to 202.5 degrees, tenths
                rr, bd = px(float(r_ft)), math.radians(b / 10.0)
                sun.append((rr * math.sin(bd), -rr * math.cos(bd), w, d))
        return sun + attested
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
    if kind == "bath":  # IN THE FRONT YARD BESIDE THE WORK YARD (269 B12), then the old back-wall and flank seats
        lead: list[Rect] = []
        if yard is not None:
            side = yard[2] / 2 + g + w / 2
            lead = [(yard[0] + sx * side, yard[1] + oy, w, d) for oy in (0.0, yard[3] / 2 - d / 2) for sx in (1.0, -1.0)]
        fr = hh / 2 + g + d / 2
        lead += [(hw * 0.35, fr, w, d), (-hw * 0.35, fr, w, d), (hw * 0.35, fr + px(8.0), w, d), (-hw * 0.35, fr + px(8.0), w, d)]
        return lead + [
            (-hw * 0.3, -(hh / 2 + g + d / 2), w, d),
            (-(hw / 2 + g + d / 2), hh * 0.2, d, w),
            (hw / 2 + g + d / 2, -hh * 0.3, d, w),
            (-hw * 0.3, -(hh / 2 + g + d * 1.5 + g), w, d),
            (hw * 0.3, -(hh / 2 + g + d * 1.5 + g), w, d),
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
    if kind == "woodpile":  # THE WOODSHED (269 B15): the stack's walls, a ken further out - a building of its own
        st, back = px(WOODSHED_STEP_FT), -(hh / 2 + g + d / 2)
        return [(-hw * 0.25, back - st, w, d), (hw * 0.25, back - st, w, d), (hw / 2 + g + st + d / 2, hh * 0.1, d, w), (-(hw / 2 + g + st + d / 2), hh * 0.1, d, w)]
    # the household shrine: a plot corner, rolled by compass name (NW the likeliest, 17 of 37; NE the kimon; SW Tokushima)
    off = px(SHRINE_CORNER_FT)
    corner = {k: (sx * (hw / 2 + off), sy * (hh / 2 + off), w, d) for k, (sx, sy) in CORNER_SIGNS.items()}
    first = weighted(SHRINE_CORNERS, u)
    return [corner[first]] + [corner[k] for k, _ in SHRINE_CORNERS if k != first]


def _joined_bath(hw: float, hh: float, w: float, d: float, taken: Sequence[Rect], g: float, px: Callable[[float], float]) -> tuple[Rect, Rect]:
    """A bath joined to its house by a corridor (269 B12): the shed a corridor's length off the back wall or a flank, the
    corridor between them - both clear of the parts laid. Every place along the back wall and the flanks is offered."""
    cl, cw = px(BATH_CORRIDOR_FT), px(BATH_CORRIDOR_W_FT)
    for sx, lx, ly in _corridor_walls(hw, hh, w, d, cl, px(WALL_SLIDE_FT)):
        shed = (lx, ly, d, w) if sx else (lx, ly, w, d)
        corridor = (math.copysign(hw / 2 + cl / 2, lx), ly, cl, cw) if sx else (lx, math.copysign(hh / 2 + cl / 2, ly), cw, cl)
        if clears(shed, taken, g) and clears(corridor, taken, 0.0):
            return shed, corridor
    raise ValueError("a joined bath found no wall with room for its corridor")


def _corridor_walls(hw: float, hh: float, w: float, d: float, cl: float, step: float) -> list[tuple[int, float, float]]:
    """`(on a flank?, x, y)` places for a joined bath's shed: along the back wall from its middle out, then along each flank,
    then along the front wall beside the yard - a corridor's length off the wall. The front is the last resort, a GUESS: the
    interview names a corridor, not the wall it leaves (269 B12), and Sugiura's indoor baths stood in the back corner."""
    out: list[tuple[int, float, float]] = [(0, u, -(hh / 2 + cl + d / 2)) for u in along((hw - w) / 2, step)]
    out += [(1, sx * (hw / 2 + cl + d / 2), u) for sx in (1.0, -1.0) for u in along((hh - w) / 2, step)]
    return out + [(0, u, hh / 2 + cl + d / 2) for u in along((hw - w) / 2, step)]


def _persimmon(hw: float, hh: float, yard: Rect | None, taken: Sequence[Rect], roofs: Sequence[Rect], front_first: bool, px: Callable[[float], float]) -> Rect:
    """The yard persimmon (269 B14): the dooryard in front - at the work yard's side edges, then the front corners and
    straight out - or behind the house, rolled against the hamlet's front share; its trunk clear of every part, its crown
    over no roof (it may shade the yard and the beds). Stepped out until it stands."""
    r = px(PERSIMMON_CROWN_FT)
    trunk = px(TRUNK_FT)
    reach = math.hypot(hw / 2, hh / 2) + r + CANOPY_PAD + 1.0
    front = [(sx * reach * 0.75, reach * 0.75) for sx in (1.0, -1.0)] + [(0.0, reach)]
    back = [(sx * reach * 0.75, -reach * 0.75) for sx in (1.0, -1.0)] + [(0.0, -reach)]
    edge = [] if yard is None else [(yard[0] + sx * (yard[2] / 2 + trunk / 2 + 3.0), yard[1] + oy) for oy in (0.0, yard[3] / 2) for sx in (1.0, -1.0)]
    ring = front + back if front_first else back + front
    pts = (edge + ring) if front_first else (ring + edge)
    steps = [px(s) for s in PERSIMMON_STEPS_FT] + [px(STEP_FT) * k + px(PERSIMMON_STEPS_FT[-1]) for k in range(1, OUT_STEPS + 1)]
    paced = ((lx * (reach + st) / reach, ly * (reach + st) / reach) for st in steps for lx, ly in ring)
    seat = next(((lx, ly, 2 * r, 2 * r) for lx, ly in chain(pts, paced) if clears((lx, ly, trunk, trunk), taken, 2.0) and clears((lx, ly, 2 * r, 2 * r), roofs, CANOPY_PAD)), None)
    assert seat is not None, "the persimmon's paces reach free ground"  # noqa: S101 - finite parts, 200 ft of paces
    return seat


def world_fixtures(laid: Mapping[str, Any]) -> list[tuple[str, Rect]]:
    """The laid fixtures in drawing order, the corridor after its bath."""
    return [(k, laid[k]) for k in (*FIXTURE_ORDER, "bath_corridor") if k in laid]
