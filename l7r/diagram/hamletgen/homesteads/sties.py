"""THE PIG STY AGAINST THE HOUSE (feature 374 wave 151): on a plain paddy hamlet about two households in three keep a small
pig sty against the farmhouse or one of its outbuildings, on the household's own plot (research/questions/0049-pigs-and-ducks-in-south-china-rice-villages.drawing.html).

It is seated once the ways stand, never laid in the homestead's bundle: laid there it moved the seating, and the web refused
maps that passed without it - 3 of the cohort and a valley roll, and more ground per homestead only moved the refusals
about (m:w151-sty-room; the GM, 2026-10-12, of the bamboo strip: the order is an implementation detail). Each sty is
offered along the walls of its farmstead's buildings in the house's own frame, the house's first, and asked of the
registry of what stands; a household with no wall free passes its sty to the next that keeps none, so the hamlet draws its
share's count wherever its walls allow.

Research: pig sty plumbing - NONE: the frame, the farmstead's parts read back from the record, the registry's question; the units that decide carry their own claims
"""

from __future__ import annotations

import math
from collections.abc import Mapping
from typing import Any

from l7r.diagram.settlement import Settlement
from l7r.diagram.settlement.farm_fixtures import STY_FT
from l7r.diagram.settlement.homestead_parts.fixture_seats import WALL_GAP_FT, WALL_SLIDE_FT, Rect, against_a_part
from l7r.diagram.settlement.homestead_parts.grove_rules import fixture_on_band, grove_bands
from l7r.diagram.settlement.rolling.lot import quota_carriers

from ..plan import SitePlan
from .fixtures import fixture_shares

#: The records that name their house by `of` and stand on its plot - every one a part its sty keeps clear of.
PART_KEYS = ("retirement_houses", "storehouses", "byres", "farm_sheds", "farm_fixtures", "threshing_yards", "gardens", "groves")
"""Research: kept clear of its plot's parts - GUESS research/questions/0036-groves-of-trees-around-farmhouses-yashikirin.drawing.html: the windward stand set back so the wood shed and the bath room keep out of it; the sty keeps out of its farm's grove bands, its yard, its beds and its other buildings by the fixtures' wall gap (a sty on its grove failed four cohort rolls, wave 151)"""

#: ...and those of them a sty may stand against.
WALL_KEYS = ("retirement_houses", "storehouses", "byres", "farm_sheds")
"""Research: the outbuildings - research/questions/0049-pigs-and-ducks-in-south-china-rice-villages.drawing.html: the farmhouse or one of its outbuildings - the retirement house, the storehouse, the byre, the shed, and the wood shed among the fixtures"""

STY_SALT = 109.0
"""Research: each farm's own first place - NONE: 109.0 is a hash salt for the walk's first place; another value only reshuffles which farm takes which side"""

ALIGN_TOL_DEG = 10.0
"""Research: a part square to its house - GUESS: no source could speak to it, a value of ours (feature 417 T29 pass C, 2026-10-25); within 10 degrees of the house's rake, a wall the sty may stand against"""


def to_frame(p: tuple[float, float], house: Mapping[str, Any]) -> tuple[float, float]:
    """A world point in the house's own frame: its center the origin, its length along x (`rot` undone).

    Research: plumbing - NONE: a rotation"""
    th = math.radians(float(house.get("rot") or 0.0))
    dx, dy = p[0] - float(house["x"]), p[1] - float(house["y"])
    return (dx * math.cos(th) + dy * math.sin(th), -dx * math.sin(th) + dy * math.cos(th))


def to_world(q: tuple[float, float], house: Mapping[str, Any]) -> tuple[float, float]:
    """A point of the house's frame in the world (`to_frame` undone).

    Research: plumbing - NONE: a rotation"""
    th = math.radians(float(house.get("rot") or 0.0))
    return (float(house["x"]) + q[0] * math.cos(th) - q[1] * math.sin(th), float(house["y"]) + q[0] * math.sin(th) + q[1] * math.cos(th))


def in_frame(rec: Mapping[str, Any], house: Mapping[str, Any]) -> tuple[Rect, bool]:
    """A record's box in the house's frame, and whether it stands square to the house (`ALIGN_TOL_DEG`): its own box, turned
    a quarter where it lies across the house; else the box round its turned corners.

    Research: plumbing - NONE: a box in a turned frame"""
    cx, cy = to_frame((float(rec["x"]), float(rec["y"])), house)
    w, h = float(rec.get("w", 0.0)), float(rec.get("h", 0.0))
    turn = (float(rec.get("rot") or 0.0) - float(house.get("rot") or 0.0)) % 180.0
    if min(turn, 180.0 - turn) <= ALIGN_TOL_DEG:
        return (cx, cy, w, h), True
    if abs(turn - 90.0) <= ALIGN_TOL_DEG:
        return (cx, cy, h, w), True
    a = math.radians(turn)
    return (cx, cy, abs(w * math.cos(a)) + abs(h * math.sin(a)), abs(w * math.sin(a)) + abs(h * math.cos(a))), False


def farmstead(M: Mapping[str, Any], house: Mapping[str, Any]) -> tuple[list[Rect], list[Rect]]:
    """The walls a sty of this house may stand against - the house first, then each outbuilding square to it, the wood shed
    among them - and every part of its plot it keeps clear of, each in the house's frame.

    Research: the farmstead's parts - research/questions/0028-the-farmstead-and-what-stood-on-it-yashiki.drawing.html: each names its house"""
    home = (round(float(house["x"]), 1), round(float(house["y"]), 1))
    walls: list[Rect] = [(0.0, 0.0, float(house["w"]), float(house["h"]))]
    parts: list[Rect] = list(walls)
    for key in PART_KEYS:
        for rec in M.get(key) or []:
            of = rec.get("of")
            if not of or "x" not in rec or (round(float(of[0]), 1), round(float(of[1]), 1)) != home:
                continue
            box, square = in_frame(rec, house)
            parts.append(box)
            if square and (key in WALL_KEYS or rec.get("kind") == "woodpile"):
                walls.append(box)
    return walls, parts


def sty_seat(s: Settlement, house: Mapping[str, Any]) -> dict[str, Any] | None:
    """The first place against a wall of the house or an outbuilding (`against_a_part`), clear of the plot's other parts by the
    fixture wall gap, that the registry of what stands admits: the record `farm_fixture` will write, or None.

    Research:
        against the farmhouse or an outbuilding - research/questions/0049-pigs-and-ducks-in-south-china-rice-villages.drawing.html: on the household's own plot
        the gap and the step - GUESS: no source could speak to it, a value of ours (feature 417 T29 pass C, 2026-10-25); the fixtures' 3.5 ft wall gap off the plot's other parts (`WALL_GAP_FT`), places 4 ft apart along each wall (`WALL_SLIDE_FT`)
        the sty raked with its house - research/questions/0029-farmhouses-minka.drawing.html: the homestead turns as one about the middle of the house
        no sty in a grove band - GUESS: searched, the record silent (feature 417 T29 pass C, 2026-10-25); no page keeps a sty off a farm's grove band; the placer asks the check's own predicate (`grove_rules.fixture_on_band`), every band as recorded (feature 385 T03, cohort seed 45)
        the sty's size - GUESS research/questions/0049-pigs-and-ducks-in-south-china-rice-villages.drawing.html: drawn 8 by 6 ft (`STY_FT`)"""
    walls, parts = farmstead(s.M, house)
    w, d = s.px(STY_FT[0]), s.px(STY_FT[1])
    taken = list(parts)
    while True:
        q = against_a_part(walls, w, d, s.px(WALL_GAP_FT), taken, s.px(WALL_SLIDE_FT), s._hjit(float(house["x"]), float(house["y"]), STY_SALT))
        if q is None:
            return None
        x, y = to_world((q[0], q[1]), house)
        rec = {
            "kind": "sty",
            "x": round(x, 1),
            "y": round(y, 1),
            "w": round(q[2], 1),
            "h": round(q[3], 1),
            "rot": round(float(house.get("rot") or 0.0), 1),
            "of": [round(float(house["x"]), 1), round(float(house["y"]), 1)],
        }
        if s.admits("farm_fixtures", rec) and not any(fixture_on_band(rec, g) for g in grove_bands(s.M)):  # ...the check's own test (385 D18)
            return rec
        taken.append((q[0], q[1], q[2], q[3]))  # refused by what stands: the next place along


def stage_sties(s: Settlement, plan: SitePlan) -> None:
    """Each plain paddy hamlet's sties, once the ways stand: the share's count of households (`quota_carriers`), each seated
    against its farmstead (`sty_seat`) and drawn; a household with no place passes its sty on to the next that keeps none.
    Recorded: the count asked (`meta.sty_target`) and the count no farmstead had room for (`meta.sty_short`).

    Steps:
        l7r.diagram.hamletgen.homesteads.sties.sty_seat
        l7r.diagram.settlement.farm_fixtures.FarmFixturesMixin.farm_fixture

    Research:
        about two households in three - research/questions/0049-pigs-and-ducks-in-south-china-rice-villages.drawing.html: the share counted to the households; none on a dike-pond hamlet, whose sties stand on its ponds
        passed to the next household - GUESS: no source could speak to it, a value of ours (feature 417 T29 pass C, 2026-10-25); a household with no place gives its sty to the next that keeps none, so the hamlet draws the share's count wherever its walls allow"""
    houses = list(s.M.get("houses") or [])
    share = fixture_shares(s.seed, plan.field_archetype)["sty"]
    carriers = quota_carriers(s.seed, "sty", len(houses), share)
    target = sum(carriers)
    order = [h for h, c in zip(houses, carriers, strict=True) if c] + [h for h, c in zip(houses, carriers, strict=True) if not c]
    drawn = 0
    for h in order:
        if drawn == target:
            break
        rec = sty_seat(s, h)
        if rec is None:
            continue
        s.farm_fixture("sty", rec["x"], rec["y"], rot=rec["rot"], of=rec["of"], size_ft=(rec["w"] / s.px(1.0), rec["h"] / s.px(1.0)))
        drawn += 1
    s.M["meta"]["sty_target"] = target
    s.M["meta"]["sty_short"] = target - drawn
