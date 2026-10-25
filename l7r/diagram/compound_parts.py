"""compound_parts.py - what the compound draft seats AROUND the placed masses (split out of `compound.py`, feature
267): the faces of a building, the fire-water tubs, wells and privies at them, the house's service part (the bath), the gates in the walls, the doors, and the roji - each seated against the masses the placer set
down, clear of every one of them and of what was seated before it.
"""

from __future__ import annotations

import math
from collections.abc import Callable, Sequence

from .buildings.types import by_tier
from .compound_model import (
    BATH_H_FT,
    BATH_W_FT,
    DIVIDER_INK_FT,
    DOOR_D_FT,
    DOOR_FRACS,
    DOOR_KINDS,
    DOOR_W_FT,
    FIRE_GAP_FT,
    FTPX,
    GATE_POST_W_FT,
    KINDS,
    LATRINE_WELL_FT,
    NOTICE_BOARD_MAX_FT,
    PRIVY_FT,
    ROOF_POST_BAY_FT,
    ROOF_POST_FT,
    ROOFED_ZONES,
    STONE_STEP_FT,
    TUB_DOOR_MAX_FT,
    TUB_MAX_GAP_FT,
    WALL_FACE_CLEAR_FT,
    WALL_INK_FT,
    BuildingSpec,
    CompoundProgram,
    CourtZone,
    Envelope,
    Placed,
    PlaceResult,
    _gate_interval,
)
from .well_gear import gear_svg, water_depth, well_gear, well_roofed


def _face(p: Placed, side: str) -> tuple[float, float, float, float, float]:
    """One side ("N"|"S"|"E"|"W") of a placed building: its outward unit normal (nx, ny), its start point (the west or
    north end) and its length."""
    if side == "S":
        return 0.0, 1.0, p.x_ft, p.y2, p.spec.w_ft
    if side == "N":
        return 0.0, -1.0, p.x_ft, p.y_ft, p.spec.w_ft
    if side == "W":
        return -1.0, 0.0, p.x_ft, p.y_ft, p.spec.h_ft
    return 1.0, 0.0, p.x2, p.y_ft, p.spec.h_ft


def _court_side(p: Placed) -> str:
    """The side of a placed building that faces its court: away from the wall it hugs (an inner-court divider building
    faces north, an outer one south)."""
    wall = p.spec.wall if p.spec.wall != "divider" else ("S" if p.spec.court == "inner" else "N")
    return {"N": "S", "S": "N", "E": "W", "W": "E"}[wall]


def _court_face(p: Placed, env: Envelope) -> tuple[float, float, float, float]:
    """The side of a placed building that faces its court, as a unit normal (nx, ny) and the face's
    start point - what a gutter-fed tub, a well or a privy stands against."""
    return _face(p, _court_side(p))[:4]


def _roof_posts(z: CourtZone) -> list[tuple[float, float]]:
    """The top-left corners (ft) of the posts along a roofed court's open south side, one per ROOF_POST_BAY_FT bay,
    both corners included."""
    bays = max(1, round(z.w_ft / ROOF_POST_BAY_FT))
    step = (z.w_ft - ROOF_POST_FT) / bays
    return [(z.x_ft + i * step, z.y2 - ROOF_POST_FT) for i in range(bays + 1)]


Box = tuple[float, float, float, float]  # (x, y, x2, y2) in feet


def _middle_gate(env: Envelope, placed: list[Placed]) -> tuple[float, float] | None:
    """The middle gate's passage along the divider (x, x2), nearest the main axis where neither court has a building
    backing the divider across it or its posts - the gate opens onto ground on both sides. None where the envelope
    declares no middle gate or the divider is backed end to end."""
    if env.middle_gate_w_ft <= 0:
        return None
    half, reach = env.middle_gate_w_ft / 2, GATE_POST_W_FT + 1.0
    backs = [(p.x_ft, p.x2) for p in placed if p.y_ft - FIRE_GAP_FT <= env.divider_ft <= p.y2 + FIRE_GAP_FT]
    for step in range(int(env.w_ft / 2)):
        for c in (env.w_ft / 2 + step, env.w_ft / 2 - step):
            a, b = c - half, c + half
            if a - reach >= 0 and b + reach <= env.w_ft and all(b + reach <= x0 or x1 <= a - reach for x0, x1 in backs):
                return a, b
    return None


def _wall_runs(env: Envelope) -> list[tuple[str, float, float, float, float]]:
    """The compound wall as (side, x1, y1, x2, y2) runs in feet, each broken where a gate passes through it: the main gate
    in the south wall, each postern (`Envelope.posterns`) in its own."""
    runs = {"N": (0.0, 0.0, env.w_ft, 0.0), "W": (0.0, 0.0, 0.0, env.h_ft), "E": (env.w_ft, 0.0, env.w_ft, env.h_ft), "S": (0.0, env.h_ft, env.w_ft, env.h_ft)}
    gaps: dict[str, list[tuple[float, float]]] = {"S": [_gate_interval(env)]}
    for side, at, w in env.posterns:
        gaps.setdefault(side, []).append((at - w / 2, at + w / 2))
    out: list[tuple[str, float, float, float, float]] = []
    for side, (x1, y1, x2, y2) in runs.items():
        cuts = [x1 if y1 == y2 else y1, *[v for gap in sorted(gaps.get(side, [])) for v in gap], x2 if y1 == y2 else y2]
        for lo, hi in zip(cuts[::2], cuts[1::2], strict=True):
            out.append((side, lo, y1, hi, y2) if y1 == y2 else (side, x1, lo, x2, hi))
    return out


def _gate_posts(side: str, lo: float, hi: float, line: float, along: float, deep: float) -> list[Box]:
    """The two posts of a gate whose passage runs lo..hi along a wall on `line`, each `along` x `deep`, standing on the
    wall's cut ends outside the passage (GATE_POST_W_FT) - so the posts' clear gap is the passage."""
    if side in ("N", "S", "divider"):
        return [(lo - along, line - deep / 2, lo, line + deep / 2), (hi, line - deep / 2, hi + along, line + deep / 2)]
    return [(line - deep / 2, lo - along, line + deep / 2, lo), (line - deep / 2, hi, line + deep / 2, hi + along)]


def _engawa(p: Placed) -> Box:
    """The veranda strip along a building's court face, inside its footprint (`BuildingSpec.engawa_ft`)."""
    e = p.spec.engawa_ft
    return {"S": (p.x_ft, p.y2 - e, p.x2, p.y2), "N": (p.x_ft, p.y_ft, p.x2, p.y_ft + e), "W": (p.x_ft, p.y_ft, p.x_ft + e, p.y2), "E": (p.x2 - e, p.y_ft, p.x2, p.y2)}[_court_side(p)]


def _dais(p: Placed) -> Box:
    """The dais band (`BuildingSpec.dais`): flush inside the court face, centered along it."""
    w, d = p.spec.dais
    side = _court_side(p)
    if side in ("N", "S"):
        x0 = (p.x_ft + p.x2 - w) / 2
        return (x0, p.y2 - d, x0 + w, p.y2) if side == "S" else (x0, p.y_ft, x0 + w, p.y_ft + d)
    y0 = (p.y_ft + p.y2 - w) / 2
    return (p.x2 - d, y0, p.x2, y0 + w) if side == "E" else (p.x_ft, y0, p.x_ft + d, y0 + w)


def _lattice(p: Placed) -> list[Box]:
    """A cell's lattice front as (x1, y1, x2, y2) bars: 1.5 ft long, across its court face, every 2 ft along it.

    Research:
        its drawn sizes - CONVENTION: sizes on the sheet, not in the world - 1.5 (the same, on an east or west face)
    """
    nx, ny, fx, fy, length = _face(p, _court_side(p))
    out: list[Box] = []
    for i in range(1, int(length / 2.0)):
        a = i * 2.0
        if ny:
            out.append((fx + a, fy, fx + a, fy - 1.5 * ny))
        else:
            out.append((fx, fy + a, fx - 1.5 * nx, fy + a))
    return out


STALL_FT: float = 6.0  # one ken, a warrior's stall one bay wide (0108's drawing page)
"""Research: stall width - research/questions/0108-stables-umaya.drawing.html: a warrior's stall was one bay wide and our maps take a bay as one ken, so a stall is drawn about 6 ft wide."""
PASSAGE_FT: float = 6.0  # the earth-floored passage (kusa-no-ma) before the stalls; its depth a GUESS
"""Research: stable passage depth - GUESS: the earth-floored passage before the stalls is 6 ft deep; the record has the passage but gives no depth."""
GROOMS_ROOM_FT: float = 9.0  # the grooms' matted room (tozamurai) across the passage; its depth a GUESS
"""Research: grooms' room depth - GUESS: the grooms' matted room is 9 ft deep; the record has the grooms' quarters but gives no depth."""


def _stable_parts(p: Placed) -> tuple[Box, list[tuple[float, float, float, float, bool]]]:
    """A stable's inner form, the one every sheet draws (feature 374 wave 126; research/questions/0108-stables-umaya.drawing.html):
    three bays long along its court face; in its depth, from the court, the grooms' room, the earth passage running the
    building's length, and the stalls one ken wide at the back. Returns the passage's box and the partitions as (x1, y1, x2,
    y2, dashed) - the stalls' two walls from the passage to the back, the grooms' room's wall, the stall fronts dashed."""
    nx, ny, fx, fy, length = _face(p, _court_side(p))
    room, front = GROOMS_ROOM_FT, GROOMS_ROOM_FT + PASSAGE_FT  # depths from the court face
    if ny:
        d = -ny
        ya, yb, back = fy + d * room, fy + d * front, (p.y2 if d > 0 else p.y_ft)
        lines = [(fx + k * STALL_FT, yb, fx + k * STALL_FT, back, False) for k in (1, 2)]
        lines += [(fx, ya, fx + length, ya, False), (fx, yb, fx + length, yb, True)]
        return (fx, min(ya, yb), fx + length, max(ya, yb)), lines
    d = -nx
    xa, xb, back = fx + d * room, fx + d * front, (p.x2 if d > 0 else p.x_ft)
    lines = [(xb, fy + k * STALL_FT, back, fy + k * STALL_FT, False) for k in (1, 2)]
    lines += [(xa, fy, xa, fy + length, False), (xb, fy, xb, fy + length, True)]
    return (min(xa, xb), fy, max(xa, xb), fy + length), lines


def _rear_band(p: Placed) -> tuple[float, float, float, float]:
    """The strip (x, y, w, h) between a building and the wall it stands `inset_ft` off - its rear alley."""
    d = p.spec.inset_ft
    return {"S": (p.x_ft, p.y_ft - d, p.spec.w_ft, d), "N": (p.x_ft, p.y2, p.spec.w_ft, d), "E": (p.x_ft - d, p.y_ft, d, p.spec.h_ft), "W": (p.x2, p.y_ft, d, p.spec.h_ft)}[_court_side(p)]


def _hatch(env: Envelope, box: Box) -> Box | None:
    """The collection hatch through the compound wall behind a privy standing against it (within 3 ft of the wall's
    inner face): a 2 ft opening across the wall's ink, level with the privy's middle, the night-soil carter's way
    in from outside (the kumitori-guchi form - research 0101 has the pits emptied by outside carters toward a
    service wall; the hatch itself is a GUESS). None where the privy stands off every wall."""
    x, y, x2, y2 = box
    cx, cy, half = (x + x2) / 2, (y + y2) / 2, WALL_INK_FT / 2
    reach = half + 3.0  # a flush privy stands 1.5 ft off the face, one seated on a building's end a foot further (feature 374 batch 6)
    if y <= reach:
        return (cx - 1.0, -half, cx + 1.0, half)
    if env.h_ft - y2 <= reach:
        return (cx - 1.0, env.h_ft - half, cx + 1.0, env.h_ft + half)
    if x <= reach:
        return (-half, cy - 1.0, half, cy + 1.0)
    if env.w_ft - x2 <= reach:
        return (env.w_ft - half, cy - 1.0, env.w_ft + half, cy + 1.0)
    return None


def _clerk_seats(dais: Box, side: str) -> list[Box]:
    """The two clerks' positions flanking a dais on the building's `side` (its court face), each 8 ft along the face
    and 5 ft deep, flush on that face and 2 ft off the dais (docs/buildings.md "Office hall": two clerk positions flanking
    the dais; the size a GUESS, Ochiba's band drawn smaller).

    Research:
        its figures guessed on 0099 - GUESS research/questions/0099-the-hearing-court-shirasu.drawing.html: 5 (clerk seat depth)
        its clerks' seats - GUESS: searched, the record silent (feature 417 T38, 2026-10-25) - 10 (clerks' seats along the face); 2 (off the dais)
    """
    x, y, x2, y2 = dais
    if side in ("N", "S"):
        top = y2 - 5.0 if side == "S" else y
        return [(x - 10.0, top, x - 2.0, top + 5.0), (x2 + 2.0, top, x2 + 10.0, top + 5.0)]
    left = x2 - 5.0 if side == "E" else x
    return [(left, y - 10.0, left + 5.0, y - 2.0), (left, y2 + 2.0, left + 5.0, y2 + 10.0)]


def _mats(z: CourtZone) -> list[Box]:
    """The straw mats on a hearing court's floor (research buildings 440 'Who sat where at a hearing, and on what?'):
    the accused's, ~6 x 3 ft, at the center a third of the way in from the dais; the plaintiff's behind to one side and
    the village officials' (12 ft, several kneeling) behind to the other - spacing a GUESS, as the hand sheets draw them.

    Research:
        its figures guessed on 0099 - GUESS research/questions/0099-the-hearing-court-shirasu.drawing.html: 16 (plaintiff's and officials' mats' places ("spacing … a GUESS")); 6 (plaintiff's and officials' mats' places ("spacing … a GUESS")); 9 (plaintiff's and officials' mats' places ("spacing … a GUESS")); 22 (plaintiff's and officials' mats' places ("spacing … a GUESS"))
        its mats - research/questions/0099-the-hearing-court-shirasu.drawing.html: 6 (accused's mat 6 ft); 3 (3 ft deep); 10 (side mats off the centre)
    """
    cx, fy = z.x_ft + z.w_ft / 2, z.y_ft + z.h_ft / 3
    return [(cx - 3.0, fy, cx + 3.0, fy + 3.0), (cx - 16.0, fy + 6.0, cx - 10.0, fy + 9.0), (cx + 10.0, fy + 6.0, cx + 22.0, fy + 9.0)]


def _family_privy(env: Envelope, homes: Sequence[Placed], taken: list[Box], zones: list[Box], wells: tuple[Box, ...]) -> tuple[float, float] | None:
    """The top-left of the family's privy, attached to the house: on the first block of `homes` (largest first) with a
    clear seat, at its rear face, else at one of its ends (west or north first) - None where no block has one."""
    for home in homes:
        others = [t for t in taken if t != (home.x_ft, home.y_ft, home.x2, home.y2)]
        court = _court_side(home)
        rear = {"N": "S", "S": "N", "E": "W", "W": "E"}[court]
        ends = ("W", "E") if court in ("N", "S") else ("N", "S")
        for side in (rear, *ends):
            if seat := _attach(env, home, side, PRIVY_FT, PRIVY_FT, others + zones, wells):
                return seat
    return None


def _guest_privy(env: Envelope, home: Placed, boxes: list[Box]) -> Box | None:
    """A privy attached to the house's rear face behind its reception room, centered on the room (research buildings
    220: "at the rear of the guest parlor"); None without a reception room or where the ground there is taken."""
    room = next((r for r in home.spec.rooms if r[0] == "reception room"), None)
    if room is None:
        return None
    court = _court_side(home)
    if court in ("N", "S"):
        x = home.x_ft + room[1] + room[3] / 2 - PRIVY_FT / 2
        y = home.y_ft - PRIVY_FT if court == "S" else home.y2
    else:
        y = home.y_ft + room[2] + room[4] / 2 - PRIVY_FT / 2
        x = home.x_ft - PRIVY_FT if court == "E" else home.x2
    others = [b for b in boxes if b != (home.x_ft, home.y_ft, home.x2, home.y2)]
    return (x, y, x + PRIVY_FT, y + PRIVY_FT) if _is_clear(env, others, x, y, PRIVY_FT, PRIVY_FT) else None


#: A privy flush to a side wall stands this far beyond its building's court face: 1.5 ft since feature 374 wave 134, when the
#: wall's face clearance grew a foot and the servants' privy, set 2 ft out, no longer fit the 7 ft between the long-house's end
#: and the servants' row. The gap is a drawing convention (a privy's own eaves).
FLUSH_PRIVY_GAP_FT: float = 1.5
"""Research: flush privy gap - GUESS: no page gives it; a privy flush to a side wall stands 1.5 ft beyond its building's court face, room for the privy's own eaves."""


def _flush_privy(env: Envelope, p: Placed, boxes: list[Box], avoid: tuple[Box, ...]) -> Box | None:
    """A privy flush against the compound side wall a building's end stands by, just beyond the building on its court
    side - the service wall its pit is emptied through; None where the building stands by no side wall or the ground
    is taken.

    Research:
        its search steps and tolerances - GUESS: no source could speak to it, a value of ours (feature 417 T38 pass N13, 2026-10-25) - 5 (threshold for a building "standing by" a side wall)
    """
    court = _court_side(p)
    face = WALL_INK_FT / 2 + WALL_FACE_CLEAR_FT  # a foot or two clear of the wall's face (feature 374 wave 134)
    reach = 5.0  # a building this near a side wall stands by it
    cands: list[Box] = []
    if court in ("N", "S"):
        y = p.y2 + FLUSH_PRIVY_GAP_FT if court == "S" else p.y_ft - FLUSH_PRIVY_GAP_FT - PRIVY_FT
        if p.x_ft <= reach:
            cands.append((face, y, face + PRIVY_FT, y + PRIVY_FT))
        if env.w_ft - p.x2 <= reach:
            cands.append((env.w_ft - face - PRIVY_FT, y, env.w_ft - face, y + PRIVY_FT))
    else:
        x = p.x2 + FLUSH_PRIVY_GAP_FT if court == "E" else p.x_ft - FLUSH_PRIVY_GAP_FT - PRIVY_FT
        if p.y_ft <= reach:
            cands.append((x, face, x + PRIVY_FT, face + PRIVY_FT))
        if env.h_ft - p.y2 <= reach:
            cands.append((x, env.h_ft - face - PRIVY_FT, x + PRIVY_FT, env.h_ft - face))
    others = [b for b in boxes if b != (p.x_ft, p.y_ft, p.x2, p.y2)]
    return next((b for b in cands if _is_clear(env, others, b[0], b[1], PRIVY_FT, PRIVY_FT, 0.5) and all(_gap(b, a) >= LATRINE_WELL_FT for a in avoid)), None)


def _door(env: Envelope, p: Placed, boxes: list[Box], side: str = "") -> tuple[Box, Box] | None:
    """A door flush inside `p`'s door face (DOOR_W_FT x DOOR_D_FT), at the first DOOR_FRACS spot whose approach - the
    door's width plus a foot each side, 3 ft out - is clear of every box (never `p` itself): the door and its approach,
    or None where no spot is clear."""
    nx, ny, fx, fy, length = _face(p, side or p.spec.door_face or _court_side(p))
    for frac in p.spec.door_fracs or DOOR_FRACS:
        mid = frac * length
        if ny:
            x0 = fx + mid - DOOR_W_FT / 2
            door = (x0, fy - DOOR_D_FT, x0 + DOOR_W_FT, fy) if ny > 0 else (x0, fy, x0 + DOOR_W_FT, fy + DOOR_D_FT)
            ax, ay, aw, ah = x0 - 1.0, (fy if ny > 0 else fy - 3.0), DOOR_W_FT + 2.0, 3.0
        else:
            y0 = fy + mid - DOOR_W_FT / 2
            door = (fx - DOOR_D_FT, y0, fx, y0 + DOOR_W_FT) if nx > 0 else (fx, y0, fx + DOOR_D_FT, y0 + DOOR_W_FT)
            ax, ay, aw, ah = (fx if nx > 0 else fx - 3.0), y0 - 1.0, 3.0, DOOR_W_FT + 2.0
        if door[0] >= p.x_ft and door[2] <= p.x2 and door[1] >= p.y_ft and door[3] <= p.y2 and _is_clear(env, boxes, ax, ay, aw, ah, 0.0):
            return door, (ax, ay, ax + aw, ay + ah)
    return None


GROOMS_PRIVY_FT: float = 55.0
"""How far a servants' privy may stand from the stables and still serve their grooms too (pass 6 merged the two at ~49 ft
apart; feature 374 wave 124 kept the stables' own where the servants' range stood ~106 ft away). A drawing convention.

Research: shared privy reach - GUESS: a servants' privy serves the stables' grooms too when within 55 ft; 0101 has a servants' row sharing the stables' privy and is silent on the distance."""
GATE_PRIVY_FT: float = 30.0
"""How far a lodgers' privy keeps from the main gate's opening along the south wall (feature 374 batch 4, plan R4-3; a GUESS).

Research: lodgers' privy distance from the gate - GUESS: a lodgers' privy keeps 30 ft from the main gate's opening along the south wall; no page gives it."""


def _gap(a: Box, b: Box) -> float:
    """The clear distance between two boxes (0 where they touch or overlap)."""
    dx = max(b[0] - a[2], a[0] - b[2], 0.0)
    dy = max(b[1] - a[3], a[1] - b[3], 0.0)
    return (dx * dx + dy * dy) ** 0.5


def _attach(env: Envelope, p: Placed, side: str, w: float, h: float, boxes: list[Box], avoid: tuple[Box, ...] = ()) -> tuple[float, float] | None:
    """The top-left of a w x h addition flush against `side` of `p`, the first clear foot along it from the end nearest
    `p`'s court; None where the side has no clear run. `boxes` are what it must clear (never `p` itself), and it stands
    at least LATRINE_WELL_FT off every `avoid` box."""
    nx, ny, fx, fy, length = _face(p, side)
    run = w if ny else h
    court = _court_side(p)
    # the court end: the south end of a north-south side when the court lies south, the east end of a west-east side
    # when it lies east; otherwise the side's start
    from_far = (court == "S" and not ny) or (court == "E" and bool(ny))
    steps = [length - run - s if from_far else s for s in range(int(length - run) + 1)]
    seats = [(fx + s, fy if ny > 0 else fy - h) for s in steps] if ny else [(fx if nx > 0 else fx - w, fy + s) for s in steps]
    return next(((x, y) for x, y in seats if _is_clear(env, boxes, x, y, w, h) and all(_gap((x, y, x + w, y + h), a) >= LATRINE_WELL_FT for a in avoid)), None)


def _roji(start: tuple[float, float], end: tuple[float, float], boxes: list[Box]) -> list[tuple[float, float]]:
    """The stepping stones of a straight roji from `start` to `end`, one every STONE_STEP_FT, the first a step in from
    the start and the last a step short of the end (the shoe stone stands there); a stone that would land within a
    foot of a box is left out."""
    (x0, y0), (x1, y1) = start, end
    n = int(((x1 - x0) ** 2 + (y1 - y0) ** 2) ** 0.5 / STONE_STEP_FT)
    pts = [(x0 + (x1 - x0) * i / n, y0 + (y1 - y0) * i / n) for i in range(1, n)]
    return [(x, y) for x, y in pts if all(x < bx - 2.0 or x > bx2 + 2.0 or y < by - 2.0 or y > by2 + 2.0 for bx, by, bx2, by2 in boxes)]


def _is_clear(env: Envelope, boxes: list[Box], x: float, y: float, w: float, h: float, margin: float = 1.0) -> bool:
    """A w x h rect at (x, y) stands inside the envelope and at least `margin` ft off every box."""
    if x < margin or y < margin or x + w > env.w_ft - margin or y + h > env.h_ft - margin:
        return False
    return all(x + w + margin <= tx or tx2 + margin <= x or y + h + margin <= ty or ty2 + margin <= y for tx, ty, tx2, ty2 in boxes)


def _abut(env: Envelope, p: Placed, w: float, h: float, boxes: list[Box]) -> tuple[float, float] | None:
    """The top-left of a w x h addition ABUTTING `p`'s court face - flush against it, the first clear foot along it
    from its start - or None where the face has no clear run. `boxes` are what it must clear (never `p` itself)."""
    nx, ny, fx, fy = _court_face(p, env)
    if ny:
        y = fy if ny > 0 else fy - h
        seats = [(p.x_ft + s, y) for s in range(int(p.spec.w_ft - w) + 1)]
    else:
        x = fx if nx > 0 else fx - w
        seats = [(x, p.y_ft + s) for s in range(int(p.spec.h_ft - h) + 1)]
    return next(((x, y) for x, y in seats if _is_clear(env, boxes, x, y, w, h)), None)


def _roomiest(points: list[tuple[float, float]], boxes: list[Box]) -> tuple[float, float]:
    """The point with the most open ground around it: the farthest from its SECOND-nearest box - every tub stands against
    the building it serves, so the nearest box says nothing - with a box holding the point (its own) not counted; the
    first on a tie."""

    def room(pt: tuple[float, float]) -> float:
        x, y = pt
        gaps = [((max(bx - x, 0.0, x - bx2)) ** 2 + (max(by - y, 0.0, y - by2)) ** 2) ** 0.5 for bx, by, bx2, by2 in boxes if not (bx <= x <= bx2 and by <= y <= by2)]
        return sorted(gaps)[1] if len(gaps) > 1 else float("inf")

    return max(points, key=room)


def requires(program: CompoundProgram, kind: str) -> bool:
    """Does the program's declared type (`CompoundProgram.tier`) require an item of `kind` that is not optional? False for
    a program of no declared type."""
    btype = by_tier(program.tier) if program.tier is not None else None
    return btype is not None and any(r.kind == kind and not r.optional for r in btype.required)


WELL_HALF_FT = 3.65
"""Half a well curb's side: the draft draws every well as a 7.3 ft square (`_point_features`).

Research: well curb half-side - GUESS: the draft draws every well curb as a 7.3 ft square (half-side 3.65 ft), about 1.8 times the real curb of about 4 ft square that 0196 gives; the page is silent on how a building plan draws the curb, so the enlargement is ours, as the settlement map's marker is (feature 417 T28; the gap is T33's)"""


def garden_well(env: Envelope, garden: CourtZone, taken: Sequence[Box]) -> tuple[float, float] | None:
    """The garden well's center: the first seat, from the garden's north-east corner westward along its north edge and
    then down its east edge, whose curb stands inside the garden and clear of everything already seated (`_is_clear`'s
    1 ft margin) - None where the garden holds no such seat (feature 287 wave 6, homes H29b: the well was stamped at the
    corner whether or not the corner was free).

    Research:
        its search steps and tolerances - GUESS: no source could speak to it, a value of ours (feature 417 T38 pass N13, 2026-10-25) - 1.35 (leftover arithmetic, (10 − 7.3)/2; the well itself SEARCHED-SILENT building-programs.md:37)
    """
    lo, hi = garden.x_ft + WELL_HALF_FT + 1.35, garden.x2 - WELL_HALF_FT - 1.35
    top, bot = garden.y_ft + WELL_HALF_FT + 1.35, garden.y2 - WELL_HALF_FT - 1.35
    seats = [(hi - k, top) for k in range(int(hi - lo) + 1)] + [(hi, top + k) for k in range(1, int(bot - top) + 1)]
    side = 2 * WELL_HALF_FT
    return next(((cx, cy) for cx, cy in seats if _is_clear(env, list(taken), cx - WELL_HALF_FT, cy - WELL_HALF_FT, side, side)), None)


def tub_by_its_eaves(tub: tuple[float, float], host: Box) -> bool:
    """THE ONE PREDICATE of `fire_water_adrift` (feature 287, homes H29b), in feet: a fire-water tub's CENTER stands within
    `TUB_MAX_GAP_FT` of the building whose gutter feeds it. The draft's tub seat asserts it of every seat it offers, and
    the pack audit (`tools/pack_audit/checks.py:fire_water_adrift`) calls it on every tub of every sheet, generated or hand
    drawn - one rule, one measure. (Until wave 4a this measured the drawn circle's EDGE, 1.27 ft looser than the audit's
    center measure, so a seat 3.5-4.8 ft off its eaves passed the placer and failed the audit.)"""
    return _gap((tub[0], tub[1], tub[0], tub[1]), host) <= TUB_MAX_GAP_FT


# Where a tub stands along a face from a door's center (feature 372 wave 106): past the door's held approach (its half-width
# plus a foot, 4 ft), the seat's 1 ft clearance and the tub's own half (1.3 ft), then farther - the last the kitchen's second
# tub beside its first (TUB_DOOR_MAX_FT) - each still inside TUB_DOOR_MAX_FT at 2.5 ft out
_BESIDE_DOOR_FT: tuple[float, ...] = (6.35, 7.0, 8.0, 10.0)
"""Research: tub offsets beside a door - GUESS: no page gives it; a fire-water tub stands 6.35-10 ft along the face from its door's center (6.35, 7, 8, 10 ft tried in order), each inside TUB_DOOR_MAX_FT."""
# the corner seat's distance in from the corner nearest a door, on the face round that corner
_CORNER_IN_FT = 1.5
"""Research: tub corner seat - GUESS: no page gives it; a corner tub stands 1.5 ft in from the corner nearest its door."""


def beside_door_fracs(p: Placed, side: str, door: tuple[float, float]) -> tuple[float, ...]:
    """The fracs along `p`'s `side` face either side of the door centered at `door` (feet), nearest first, kept by the face:
    where the draft seats a fire-water tub at its building's entrance (research 0100).

    Research:
        its salts, guards and sentinels - NONE: they decide nothing about the place - 0.15 (slack past a face's end)
    """
    _nx, ny, fx, fy, length = _face(p, side)
    at = (door[0] - fx) if ny else (door[1] - fy)
    fracs = [(at + sign * d) / length for d in _BESIDE_DOOR_FT for sign in (-1, 1)]
    # a seat a hair past the face's end is kept (0.15 ft: the round-trip kitchen's second tub, 0.1 ft past); none farther -
    # a tub 0.35 ft past the corner stood in the main gate's track beside the gatehouse (feature 372 wave 106,
    # building-review E1): a short face takes `round_the_corner`
    slack = 0.15 / length
    return tuple(f for f in fracs if -slack <= f <= 1.0 + slack)


def round_the_corner(p: Placed, side: str, door: tuple[float, float]) -> list[tuple[str, float]]:
    """The seats round the corners of `p` beside its door on `side`: each face meeting `side`, at the end nearest `side`,
    `_CORNER_IN_FT` in - kept only where a tub 2.5 ft out stands by the door (`tub_by_its_door`). For a face too short to
    seat a tub beside its door (a gatehouse's 12 ft end, feature 372 wave 106). (face, frac) pairs.

    Research:
        its figures guessed on 0100 - GUESS research/questions/0100-fire-and-the-fireproof-storehouses-dozo.drawing.html: 2.5 (tub's distance off the face)
    """
    out: list[tuple[str, float]] = []
    for adj in ("N", "S") if side in ("E", "W") else ("W", "E"):
        nx, ny, fx, fy, length = _face(p, adj)
        far = side in ("E", "S")  # the door's side is the face's far (east or south) end
        frac = 1.0 - _CORNER_IN_FT / length if far else _CORNER_IN_FT / length
        tub = (fx + length * frac, fy + ny * 2.5) if ny else (fx + nx * 2.5, fy + length * frac)
        if tub_by_its_door(tub, [door]):
            out.append((adj, frac))
    return out


def tub_by_its_door(tub: tuple[float, float], doors: Sequence[tuple[float, float]]) -> bool:
    """THE ONE PREDICATE of `tubs_off_their_doors` (feature 372 wave 106), in feet: a fire-water tub's CENTER stands within
    `TUB_DOOR_MAX_FT` of the center of one of its building's doors - research 0100's water kept at the entrance."""
    return any(math.hypot(tub[0] - dx, tub[1] - dy) <= TUB_DOOR_MAX_FT for dx, dy in doors)


def board_by_a_gate(board: Box, openings: Sequence[tuple[float, float]]) -> bool:
    """THE ONE PREDICATE of `notice_board_adrift` (feature 287, homes H29b), in feet: a notice board is read where people
    pass, so the nearest edge of its box stands within `NOTICE_BOARD_MAX_FT` of the middle of a gate opening. The pack
    audit calls it with every opening it reads off a sheet's ink; the draft (`board_by_the_gate`) with its main gate."""
    return any(_gap((ox, oy, ox, oy), board) <= NOTICE_BOARD_MAX_FT for ox, oy in openings)


def board_by_the_gate(env: Envelope, board: Box) -> bool:
    """`board_by_a_gate` at the draft's main gate, whose opening is centered on the south wall (`_gate_interval`)."""
    return board_by_a_gate(board, [(env.w_ft / 2, env.h_ft)])


SHRINE_TREE_CROWN_FT: float = 20.0  # the shrine's tree's crown across; a GUESS (no source sizes a household god's tree)
"""Research: shrine tree crown - GUESS: the compound shrine's tree has a crown 20 ft across; no source sizes a household god's tree."""
SHRINE_TREE_CLEAR_FT: float = 2.0  # its crown clear of the hall, every mass and the wall's ink (half the 3 ft wall, and a little)
"""Research: shrine tree clearance - GUESS: the tree's crown stands 2 ft clear of the hall, every mass and the wall's ink, the wall's half-thickness and a little more; no page gives it."""


def _shrine_tree(env: Envelope, result: PlaceResult, taken: list[Box]) -> tuple[float, float] | None:
    """The trunk of the tree beside the compound shrine (feature 374 wave 130): off an end face of the shrine first - along
    its wall, toward the corner it stands in - then its court face, its crown SHRINE_TREE_CLEAR_FT clear of the hall and
    of everything seated; None where no seat is clear (the pack audit's `shrine_tree` then reports the shrine bare).

    Research:
        a tree beside the compound's shrine - research/questions/0218-the-compounds-own-shrine-yashikigami.drawing.html: "Every compound our maps draw has one modest shrine, in a corner of its grounds beside a tree" - a household kept its god in a corner of its lot, at a small shrine or an old tree taken as its seat, and our maps give the compound's shrine the tree as well
        the tree's seat - GUESS: off the shrine's end face toward its wall, then the court face, the crown 2 ft clear of the hall; no source says on which side of a household's shrine its tree stood, or how near (research/questions/0218-the-compounds-own-shrine-yashikigami.drawing.html)
        the crown's size - GUESS: 20 ft across; no source sizes a household god's tree (research/questions/0218-the-compounds-own-shrine-yashikigami.drawing.html)
        its figures guessed on 0218 - GUESS research/questions/0218-the-compounds-own-shrine-yashikigami.drawing.html: 0.85 (tree seats toward the corner); 0.15 (tree seats toward the corner)
    """
    shrine = next((p for p in result.placed if p.spec.feature == "compound shrine"), None)
    if shrine is None:
        return None
    r = SHRINE_TREE_CROWN_FT / 2
    court = _court_side(shrine)
    wall = {"N": "S", "S": "N", "E": "W", "W": "E"}[court]
    ends = ("E", "W") if court in ("N", "S") else ("N", "S")
    toward_wall = (0.85, 0.5, 0.15) if wall in ("S", "E") else (0.15, 0.5, 0.85)
    off = r + SHRINE_TREE_CLEAR_FT
    others = [t for t in taken if t != (shrine.x_ft, shrine.y_ft, shrine.x2, shrine.y2)]
    for side in (*ends, court):
        nx, ny, fx, fy, length = _face(shrine, side)
        for frac in toward_wall:
            cx, cy = (fx + length * frac, fy + ny * off) if ny else (fx + nx * off, fy + length * frac)
            if _is_clear(env, others, cx - r, cy - r, 2 * r, 2 * r, SHRINE_TREE_CLEAR_FT):
                return cx, cy
    return None


def _point_features(program: CompoundProgram, result: PlaceResult, rect: Callable[..., str], caption: Callable[..., str], ox: float, oy: float) -> list[str]:
    """The program's point features, seated by the composition (feature 254): fire-water tubs at every
    wooden building's court face (two at the kitchen), a well at the kitchen, the garden and the stables,
    a privy beside the barracks, the stables and the servants' row, the notice board outside the main gate -
    and the house's service part (feature 267): the bath as a small addition abutting the kitchen's court face (the
    kitchen itself is an ell the placer abuts to the house, `BuildingSpec.joins`). The placer arranges the wall-ranging masses; these follow them, each
    seated at the first spot along its building's court face that is CLEAR of every mass and of every
    feature already seated - a draft swept by the gate carries the whole program, not the masses alone.

    Research:
        its figures guessed on 0101 - GUESS research/questions/0101-privies-setchin.drawing.html: 7 (privy center off the building's face); 4.5 (privy center off the building's face); 3.5 (privy center off the building's face)
        its drawn sizes - CONVENTION: sizes on the sheet, not in the world - 8 (bath caption font); 1.5 (bath stroke)
        its search steps and tolerances - GUESS: no source could speak to it, a value of ours (feature 417 T38 pass N13, 2026-10-25) - 6 (well's search ladder (stables' well SEARCHED-SILENT building-programs.md:37)); 9 (well's search ladder (stables' well SEARCHED-SILENT building-programs.md:37)); 12 (well's search ladder (stables' well SEARCHED-SILENT building-programs.md:37)); 15 (well's search ladder (stables' well SEARCHED-SILENT building-programs.md:37)); 0.85 (fallback seat order along the court face); 0.15 (fallback seat order along the court face); 0.2 (well beside the door, not before it (no page places one, building-programs.md:105)); 0.8 (well beside the door, not before it (no page places one, building-programs.md:105)); 0.3 (well beside the door, not before it (no page places one, building-programs.md:105)); 0.7 (well beside the door, not before it (no page places one, building-programs.md:105)); 0.4 (fallback seat order along the court face); 0.6 (fallback seat order along the court face); 0.05 (fallback seat order along the court face); 0.95 (fallback seat order along the court face); 0.03 (fallback seat order along the court face); 0.97 (fallback seat order along the court face)
        its figures guessed on 0105 - GUESS research/questions/0105-baths-furo.drawing.html: 20 (kitchen well as far as 20 ft out)
        its figures against 0196 - research/questions/0196-communal-wells-ido.drawing.html: 7.3 (well curb square, where the page's curb is about 4 ft square with a 4 ft apron) - a departure the code keeps until feature 417 T33
        its figures against 0196's curb - research/questions/0196-communal-wells-ido.drawing.html: 3.65 (well boxes privies keep off, the 7.3 ft curb halved) - a departure the code keeps until feature 417 T33
        its figures guessed on 0100 - GUESS research/questions/0100-fire-and-the-fireproof-storehouses-dozo.drawing.html: 2.6 (as above); 2.5 (as above)
        its tub count - research/questions/0100-fire-and-the-fireproof-storehouses-dozo.drawing.html: 2 (two tubs at the kitchen); 1 (one at each other wooden building)
        no tub at a kura - research/questions/0100-fire-and-the-fireproof-storehouses-dozo.drawing.html: an earth-walled kura takes no tub
        its kitchen well - GUESS research/questions/0105-baths-furo.drawing.html: the kitchen's well past the bath, within 20 ft of the kitchen
        its privy seats - GUESS: searched, the record silent (feature 417 T38, 2026-10-25) - 4.5 (a privy flush on the side wall first); 7 (then the wall ends); 3.5 (the court face last)
        its shared privy - GUESS: a servants' privy serves the stables' grooms too within GROOMS_PRIVY_FT; 0101 has a servants' row sharing the stables' privy and is silent on the distance
        no privy by the gate - GUESS: no lodgers' privy within GATE_PRIVY_FT of the main gate's opening; no page gives it
        its bath - GUESS research/questions/0105-baths-furo.drawing.html: the bath against the kitchen's court face, clear of every spine court
        its other wells - research/questions/0104-the-formal-entrance-and-a-guests-arrival-genkan.drawing.html: the stables' well on the service side, as the page has an official compound's well; the garden well in the inner court, off the service side - a departure the code keeps until feature 417 T33
    """
    env = program.envelope
    parts: list[str] = []
    taken: list[tuple[float, float, float, float]] = [(p.x_ft, p.y_ft, p.x2, p.y2) for p in result.placed]
    # a ROOFED court is a footprint like a building's (ROOFED_ZONES): no tub, well or privy stands under its roof - a
    # tub there is fed by no gutter (the office hall's stood inside the hearing court until feature 267's pass 3)
    taken += [(z.x_ft, z.y_ft, z.x2, z.y2) for z in program.spine if z.name in ROOFED_ZONES]
    # the divider's ink is a wall's: nothing seated stands in it (the round-trip draft's garrison privy, seated on the
    # barracks' north end face, reached 2 ft into it)
    taken.append((0.0, env.divider_ft - DIVIDER_INK_FT / 2, env.w_ft, env.divider_ft + DIVIDER_INK_FT / 2))
    by_name = {p.spec.name: p for p in result.placed}

    def seat(
        p: Placed,
        size: float,
        fracs: tuple[float, ...],
        offs: tuple[float, ...],
        side: str = "",
        avoid: tuple[Box, ...] = (),
        block: tuple[Box, ...] = (),
    ) -> tuple[float, float] | None:
        """The center of a `size`-square feature against a side of `p` (its court face unless `side` names another):
        the first clear (frac, off) - clear of `block` too - and at least LATRINE_WELL_FT off every `avoid` box."""
        nx, ny, fx, fy, length = _face(p, side or _court_side(p))
        for off in offs:
            for frac in fracs:
                cx, cy = (fx + length * frac, fy + ny * off) if ny else (fx + nx * off, fy + length * frac)
                box = (cx - size / 2, cy - size / 2, cx + size / 2, cy + size / 2)
                if _is_clear(env, taken + list(block), box[0], box[1], size, size) and all(_gap(box, a) >= LATRINE_WELL_FT for a in avoid):
                    taken.append(box)
                    return cx, cy
        return None

    tubs: list[tuple[float, float]] = []
    wells: list[tuple[float, float]] = []
    privies: list[tuple[float, float, str]] = []  # center, and the building it is a part of (an attached privy)
    # The bath is a small addition abutting the kitchen's court face - the house's service side (BATH_W_FT); seated
    # before the wells so the kitchen well takes what the bath leaves, and clear of every spine court, since a bath in
    # the garden is the pavilion the research does not find
    zones = [(z.x_ft, z.y_ft, z.x2, z.y2) for z in program.spine]
    bath: tuple[float, float] | None = None
    if "kitchen" in by_name:
        host = by_name["kitchen"]
        others = [t for t in taken if t != (host.x_ft, host.y_ft, host.x2, host.y2)]
        if bath := _abut(env, host, BATH_W_FT, BATH_H_FT, others + zones):
            bx, by = bath
            taken.append((bx, by, bx + BATH_W_FT, by + BATH_H_FT))
            parts.append(rect(bx, by, BATH_W_FT, BATH_H_FT, KINDS["service"][0], KINDS["service"][1], 1.5, "", "bath"))
            caption("area", bx, by, BATH_W_FT, BATH_H_FT, "bath", 8, False, "#3A2E1C", "bath")
    # the shrine's tree, before the wells and the privies, which then keep clear of its crown
    if tree := _shrine_tree(env, result, taken):
        tx, ty, r = *tree, SHRINE_TREE_CROWN_FT / 2
        taken.append((tx - r, ty - r, tx + r, ty + r))
        rect(tx - r, ty - r, 2 * r, 2 * r, "none", "none", 0)  # registers the crown with the captions; its circle follows
        parts.append(
            f'<g data-kind="sacred tree" data-part-of="compound shrine" fill="#7A8C5C" stroke="#3E5230" stroke-width="1.4"><circle cx="{ox + tx * FTPX:.0f}" cy="{oy + ty * FTPX:.0f}" r="{r * FTPX:.0f}" data-id="shrine-tree"/></g>'
        )
        caption("point", tx - r, ty - r, 2 * r, 2 * r, "shrine tree", 7, True, "#3A4A28", "sacred tree", names=("shrine-tree",))
    # wells next. A well stands BESIDE a door, never before it (pass 6, building-review round 5: the stables' well stood
    # 5 ft in front of the stable door and wider than it) - the fracs off the middle first, the middle last - and 9 ft
    # out before 6: a kitchen well may stand as far as 20 ft out, past the bath that abuts the kitchen, serving both,
    # as the Takayama residence's bath stood with its well and kitchen (research 0105)
    for p in result.placed:
        # the stables' 6 ft out first: their well stands in the band before them that is the outer court's way west, and at
        # 9 ft it left ~2.3 ft either side of it (feature 374 batch 5, building-review E1)
        offs = (6.0, 9.0, 12.0, 15.0, 20.0) if p.spec.feature == "stables" else (9.0, 12.0, 15.0, 20.0, 6.0)
        if p.spec.feature in ("kitchen", "stables") and (w := seat(p, 7.3, (0.2, 0.8, 0.3, 0.7, 0.5), offs)):
            wells.append(w)
    for z in program.spine:
        # the garden well stands at the garden's EAST end, where the bath stood before it joined the house: at the west
        # end it stood 8 ft from the kitchen well seated past the bath, and read as its duplicate. ASKED, NOT STAMPED
        # (feature 287 wave 6, homes H29b): it was set at the corner unconditionally, over whatever stood there
        if z.name == "garden" and (gw := garden_well(env, z, taken)):
            wells.append(gw)
            taken.append((gw[0] - WELL_HALF_FT, gw[1] - WELL_HALF_FT, gw[0] + WELL_HALF_FT, gw[1] + WELL_HALF_FT))
    if not wells and requires(program, "well"):
        # THE PROGRAM'S WELL IS DRAWN OR THE DRAFT IS REFUSED (homes H29b; plan D7): a magistracy's program requires one
        # (`buildings/types.json`), and a draft with none fails `program_complete` - never a sheet drawn without it
        raise ValueError(f"{program.title}: no seat for a well - the kitchen's and the stables' faces and the garden are all taken; change the program")
    # THE PRIVIES (feature 267, research 0101 'Privies attach to the house; night-soil drives their placement':
    # "privy count scales with occupancy (~1 per functional zone, ~3-4 at a county manor), the residence privy attaches
    # to the house with its cesspit to the rear/service wall, and servants'/outer privies line service walls near a
    # gate"; a well-appointed house had a guests' privy at the rear of the guest parlor besides). Never on a spine
    # court, never within LATRINE_WELL_FT of a well; one against a compound wall is emptied through a hatch in it
    # (`_hatch`, drawn below).
    well_boxes = tuple((wx - 3.65, wy - 3.65, wx + 3.65, wy + 3.65) for wx, wy in wells)
    # THE HOUSE IS FOUND BY ITS FEATURE, NOT ITS NAME (feature 294 B17): the round-trip draft names its two blocks
    # "residence (W)" and "residence (E)", so a lookup by the name "residence" found no house and seated no family privy -
    # `privies_by_zone` caught it. A house in several blocks takes the privy on the first block, largest first, that has
    # a clear seat.
    homes = sorted((p for p in result.placed if p.spec.feature == "residence"), key=lambda p: -p.spec.w_ft * p.spec.h_ft)
    if homes:
        home = by_name.get("residence", homes[0])
        # the family's: IN THE HOUSE, attached at its rear corner by the family's rooms (research 0101: "within
        # the residence the privy came to be built in a corner of the corridor"), its cesspit toward the rear wall. Pass
        # 7 (building-review round 6): pass 6 had stood it flush to the rear wall for a hatch, ~140 ft outdoors round
        # the house from the inner entrance; the hatch was a guess and is dropped for it - the 10 ft alley keeps 5 ft.
        # Where the rear is the compound wall itself (a block set against it), the privy is attached to an end of the
        # block instead, west or north first (feature 294 B17: still the house's own) - `_family_privy`.
        if fam := _family_privy(env, homes, taken, zones, well_boxes):
            taken.append((fam[0], fam[1], fam[0] + PRIVY_FT, fam[1] + PRIVY_FT))
            privies.append((fam[0] + PRIVY_FT / 2, fam[1] + PRIVY_FT / 2, "residence"))
        # the guests': attached to the house behind the reception room (pass 6; research 220's "at the rear of the guest
        # parlor")
        if guest := _guest_privy(env, home, taken + zones):
            taken.append(guest)
            privies.append(((guest[0] + guest[2]) / 2, (guest[1] + guest[3]) / 2, "residence"))
    # the grooms lodge by the stables where a servants' row stands in the stables' court: their one privy serves both
    # (pass 6: the stables' and the grooms' stood ~49 ft apart, the stables' hatch by the main gate)
    # - where the servants' privy SEATED, and near the stables: the servants are seated first, and stables whose court's
    # servants' privy found no seat, or stands farther than GROOMS_PRIVY_FT from them, keep their own (feature 374 wave
    # 124: the round-trip sheet's street range stands ~106 ft from its stables, and the stables lost their privy to it)
    grooms: list[tuple[str, float, float]] = []
    # NO LODGERS' PRIVY BY THE MAIN GATE (feature 374 batch 4, plan R4-3, building-review E3): the stables' latrine seated
    # flush beside them on the gatehouse side, 6 ft from it, the formal entrance - a privy's pit faces a service edge
    # (docs/buildings.md, "Latrines"). GATE_PRIVY_FT along the south wall either side of the opening is held; its 30 ft a GUESS.
    gl, gr = _gate_interval(env)
    gate_hold = (gl - GATE_PRIVY_FT, env.h_ft - GATE_PRIVY_FT, gr + GATE_PRIVY_FT, env.h_ft)
    lodgers = sorted((p for p in result.placed if p.spec.feature in ("servants' quarters", "stables", "barracks")), key=lambda p: p.spec.feature != "servants' quarters")
    for p in lodgers:
        if p.spec.feature == "stables" and any(c == p.spec.court and _gap((x, y, x, y), (p.x_ft, p.y_ft, p.x2, p.y2)) <= GROOMS_PRIVY_FT for c, x, y in grooms):
            continue
        before = len(privies)
        # FLUSH AGAINST THE SIDE WALL beside the building first, the service wall its carter empties it through (pass 6:
        # the servants' stood ~20 ft out in the court), then an end face at its wall end, the court face last
        if flush := _flush_privy(env, p, [*taken, *zones, gate_hold], well_boxes):
            taken.append(flush)
            privies.append(((flush[0] + flush[2]) / 2, (flush[1] + flush[3]) / 2, ""))
        else:
            court = _court_side(p)
            wall = {"N": "S", "S": "N", "E": "W", "W": "E"}[court]
            ends = ("E", "W") if court in ("N", "S") else ("N", "S")
            toward_wall = (0.85, 0.5, 0.15) if wall in ("S", "E") else (0.15, 0.5, 0.85)
            # 3.5 ft off (its face 1 ft out) last: into a narrow gap between two blocks on one wall (feature 374 batch 4, plan R4-3: the county
            # stables' only seat clear of the gate and of their well is the 7 ft gap to the servants' row)
            # against the wall at either end before anywhere else (feature 374 batch 5, building-review E2: the stables'
            # east end's court-ward seat won, a privy loose in the forecourt with no hatch)
            for side, fracs in ((ends[0], toward_wall[:1]), (ends[1], toward_wall[:1]), (ends[0], toward_wall), (ends[1], toward_wall), (court, (0.85, 0.15, 0.5))):
                if v := seat(p, PRIVY_FT, fracs, (4.5, 7.0, 3.5), side, well_boxes, (*zones, gate_hold)):
                    privies.append((*v, ""))
                    break
        if p.spec.feature == "servants' quarters" and len(privies) > before:
            grooms.append((p.spec.court, privies[-1][0], privies[-1][1]))
    # a door on each lodging block's face (DOOR_KINDS, `_door`), a part of its building: seated after the bath, the
    # wells and the privies and BEFORE the tubs, which have seats to spare. The door and the ground before it are held
    # clear of what follows. A building may carry more than one (`BuildingSpec.extra_doors`).
    doors: dict[str, list[tuple[str, tuple[float, float]]]] = {}  # each building's doors: the face and the door's center
    for p in result.placed:
        if p.spec.feature not in DOOR_KINDS:
            continue
        for side in (p.spec.door_face or _court_side(p), *p.spec.extra_doors):
            if found := _door(env, p, [t for t in taken if t != (p.x_ft, p.y_ft, p.x2, p.y2)], side):
                (dx, dy, dx2, dy2), approach = found
                doors.setdefault(p.spec.name, []).append((side, ((dx + dx2) / 2, (dy + dy2) / 2)))
                taken += [(dx, dy, dx2, dy2), approach]
                parts.append(rect(dx, dy, dx2 - dx, dy2 - dy, "#4A3318", "none", 0, "", "door", p.spec.feature))
    hosts = list(result.placed)
    if "kitchen" in by_name and bath:
        # the bath is fire-prone too: a tub at its yard face (pass 6; programs.md "Fire-water tubs")
        hosts.append(Placed(BuildingSpec("bath", "service", BATH_W_FT, BATH_H_FT, by_name["kitchen"].spec.court, by_name["kitchen"].spec.wall), *bath))
    for p in hosts:
        if p.spec.kind == "kura":
            continue  # a plaster storehouse carries no tub (docs/buildings.md, "Fire-water tubs")
        court = _court_side(p)
        ends = ("E", "W") if court in ("N", "S") else ("N", "S")
        toward_court = (0.85, 0.5, 0.15) if court in ("S", "E") else (0.15, 0.5, 0.85)
        for _ in range(2 if p.spec.feature == "kitchen" else 1):
            # the court face first, its ends last (0.05, 0.95: where a roofed court covers the rest of it); then an end
            # face at its court end (pass 6: the kitchen's yard face, crowded by the bath, the well and the door, kept
            # neither of its two tubs)
            # beside a door first: research 0100 keeps the standing water at a wooden building's entrance (feature 372
            # wave 106); a building with no door drawn, or none with a clear seat beside it, takes the court face
            tub = next((t for side, c in doors.get(p.spec.name, []) if (t := seat(p, 2.6, beside_door_fracs(p, side, c), (2.5,), side))), None)
            corners = [corner for side, c in doors.get(p.spec.name, []) for corner in round_the_corner(p, side, c)]
            tub = tub or next((t for adj, frac in corners if (t := seat(p, 2.6, (frac,), (2.5,), adj))), None)
            tub = tub or seat(p, 2.6, (0.15, 0.85, 0.4, 0.6, 0.05, 0.95, 0.03, 0.97), (2.5,))
            # (the west or north end before the east or south: the example's kitchen's east end abuts the house, its
            # west end the servants' yard)
            tub = tub or seat(p, 2.6, toward_court, (2.5,), ends[1]) or seat(p, 2.6, toward_court, (2.5,), ends[0])
            # EVERY SEAT OFFERED STANDS BY ITS EAVES (feature 287, homes H29b): 2.5 ft off the face is inside the gutter's
            # reach by construction - held here by the rule's one predicate, the number the pack audit registers
            assert tub is None or tub_by_its_eaves(tub, (p.x_ft, p.y_ft, p.x2, p.y2)), "a tub seated past its eaves"
            if tub:
                tubs.append(tub)
    _roji_parts(program, result, taken, rect, parts, ox, oy)
    _draw_point_parts(env, wells, privies, tubs, taken, rect, caption, parts, ox, oy, program.seed_name or program.title)
    return parts


def _draw_point_parts(
    env: Envelope,
    wells: list[tuple[float, float]],
    privies: list[tuple[float, float, str]],
    tubs: list[tuple[float, float]],
    taken: list[Box],
    rect: Callable[..., str],
    caption: Callable[..., str],
    parts: list[str],
    ox: float,
    oy: float,
    seed: str = "",
) -> None:
    """Draw the point features `_point_features` seated - the wells, the privies with their hatches, the fire-water
    tubs under one caption, and the notice board by the gate (lifted out of it by feature 370, the 100-statement cap;
    same order, so the same ink and the same caption seats).

    Research:
        its figures against 0190 - research/questions/0190-notice-boards-kosatsuba.html: 6 (caption box is the board's wrong size); 1.5 (caption box is the board's wrong size) - a departure the code keeps until feature 417 T33
        its drawn sizes - CONVENTION: sizes on the sheet, not in the world - 7 (board caption font); 0.6 (board stroke); 1.2 (curb stroke); 0.8 (privy stroke)
        its figures against 0196 - research/questions/0196-communal-wells-ido.drawing.html: 7.3 (caption box is the curb, drawn 7.3 ft where the page's curb is about 4 ft square); 3.65 (the same, halved) - a departure the code keeps until feature 417 T33
        its figures from 0090 - research/questions/0090-magistrates-compounds-jinya-and-yamen.drawing.html: 8 (board 8-14 ft west of the gate's edge)
        its figures guessed on 0101 - GUESS research/questions/0101-privies-setchin.drawing.html: 5 (caption box is the privy); 2.5 (caption box is the privy)
        its figures guessed on 0100 - GUESS research/questions/0100-fire-and-the-fireproof-storehouses-dozo.drawing.html: 2.54 (tubs caption box); 1.27 (tubs caption box)
        its figures from 0090's drawing page - research/questions/0090-magistrates-compounds-jinya-and-yamen.drawing.html: 14 (caption box at the board, within about 15 ft of the gate)
        its figures against 0190's drawing page - research/questions/0190-notice-boards-kosatsuba.drawing.html: 4.5 (board's far edge (3 + 1.5 ft depth; the record draws 6 ft deep)) - a departure the code keeps until feature 417 T33
        its board set-out - GUESS: searched, the record silent (feature 417 T38, 2026-10-25) - 3 (notice board 3 ft south of the south wall's line)
        its tub glyph - GUESS research/questions/0100-fire-and-the-fireproof-storehouses-dozo.drawing.html: 3.8 (tub drawn about 2.5 ft across)
    """
    depth = water_depth(seed)  # a generated draft records no landform: its water depth rolls from its name (0196's drawing page)
    for i, (cx, cy) in enumerate(wells, 1):
        parts.append(rect(cx - 3.65, cy - 3.65, 7.3, 7.3, "#9C8C70", "#5C4830", 1.2, "", "well"))
        parts.append(gear_svg(ox + cx * FTPX, oy + cy * FTPX, 3.65 * FTPX, well_gear(seed, i, depth), well_roofed(seed, i)))
        caption("point", cx - 3.65, cy - 3.65, 7.3, 7.3, "well", 8, True, "#3A2E1C", "well")
    for cx, cy, whole in privies:
        parts.append(rect(cx - 2.5, cy - 2.5, 5.0, 5.0, "#7E726A", "#4A3318", 0.8, "", "latrine", whole))
        if hatch := _hatch(env, (cx - 2.5, cy - 2.5, cx + 2.5, cy + 2.5)):
            hx, hy, hx2, hy2 = hatch
            parts.append(rect(hx, hy, hx2 - hx, hy2 - hy, "#4A3318", "none", 0, "", "latrine"))
        caption("point", cx - 2.5, cy - 2.5, 5.0, 5.0, "latrine", 7, True, "#3A2E1C", "latrine")
    if tubs:
        parts.append('<g fill="#8FB0C6" stroke="#3A5060" stroke-width="1" data-kind="fire-water tubs">')
        parts += [f'<circle cx="{ox + cx * FTPX:.0f}" cy="{oy + cy * FTPX:.0f}" r="3.8" data-id="tub-{k}"/>' for k, (cx, cy) in enumerate(tubs)]
        parts.append("</g>")
        for tx, ty in tubs:  # every tub is drawn - and so is an obstacle to every caption
            rect(tx - 1.27, ty - 1.27, 2.54, 2.54, "none", "none", 0)  # registers the tub; its drawn circle follows
        # the group's one caption goes on the tub with the most open ground around it: the first tub can stand hemmed
        # in (the residence's, between the wall and the kitchen), and a caption pushed off it is
        # drawn far from any tub it names - a group's name stands beside one of the glyphs it names
        tx, ty = _roomiest(tubs, taken)
        caption("point", tx - 1.27, ty - 1.27, 2.54, 2.54, "fire-water tubs", 7, True, "#3A5060", "fire-water tubs", names=tuple(f"tub-{k}" for k in range(len(tubs))))  # declared: every tub
    gl, _gr = _gate_interval(env)
    assert board_by_the_gate(env, (gl - 14.0, env.h_ft + 3.0, gl - 8.0, env.h_ft + 4.5)), "the board stands 8 ft west of the gate, by construction"
    parts.append(rect(gl - 14.0, env.h_ft + 3.0, 6.0, 1.5, "#4A3318", "#2D2A24", 0.6, "", "notice board"))
    caption("point", gl - 14.0, env.h_ft + 3.0, 6.0, 1.5, "notice board", 7, True, "#3A2E1C", "notice board")


def _roji_parts(program: CompoundProgram, result: PlaceResult, taken: list[Box], rect: Callable[..., str], parts: list[str], ox: float, oy: float) -> None:
    """The guest's way (R07's no-genkan form, research 0104): from the middle gate a stepping-stone path, the
    roji, straight to a shoe stone at the reception room's veranda - drawn where the program has a middle gate and a
    building with a `reception room` and an engawa. The stones are a part of the garden they cross (Hayakawa's form).

    Research:
        guest's way out of doors - research/questions/0104-the-formal-entrance-and-a-guests-arrival-genkan.html: the roji form - a gate in the roji wall, then a garden path straight to the principal room's veranda - is attested only at a middle-rank retainer's house with no office (Koseki); that a guest goes on from an OFFICE to the residence this way, out of doors, is a GUESS - the record leaves open whether that way ran indoors, and no page places a middle gate against an office hall
        stepping stones - GUESS: the walled garden path drawn as stepping stones of 2 x 1.33 ft (Hayakawa's form); the record names the path, not its stones
        shoe stone - GUESS: a 4 x 1.67 ft shoe stone at the veranda's edge, centered on the reception room, where the path arrives; the record names none
        gate seat - CONVENTION: the path starts 2.5 ft off the divider at the middle gate's midpoint and ends 2 ft out from the court face, keeping the stones clear of the walls
        roji wherever a middle gate stands - research/questions/0104-the-formal-entrance-and-a-guests-arrival-genkan.html: drawn wherever the program has a middle gate and a reception room with a veranda; 0104 records two forms of a guest's arrival, the genkan (Takayama) and the roji (Koseki), and this code does not roll between them
        its drawn sizes - CONVENTION: sizes on the sheet, not in the world - 0.8 (shoe-stone stroke)
        its unstated figures - GUESS: searched, the record silent (feature 417 T38 pass N13, 2026-10-25) - 0.67 (stone half-depth)
    """
    env = program.envelope
    mid = _middle_gate(env, result.placed)
    host = next((p for p in result.placed if p.spec.engawa_ft and any(r[0] == "reception room" for r in p.spec.rooms)), None)
    if mid is None or host is None:
        return
    rx, rw = next((host.x_ft + x, w) for k, x, _y, w, _h in host.spec.rooms if k == "reception room")
    _nx, ny, _fx, fy = _court_face(host, env)
    shoe = (rx + rw / 2 - 2.0, fy + (0.0 if ny > 0 else -1.67), 4.0, 1.67)
    gate = ((mid[0] + mid[1]) / 2, env.divider_ft + (-2.5 if host.spec.court == "inner" else 2.5))
    stones = _roji(gate, (rx + rw / 2, fy + 2.0 * ny), taken)
    parts.append('<g data-kind="garden"><g fill="#B8B0A0" stroke="#7A7060" stroke-width="0.5">')
    for x, y in stones:
        rect(x - 1.0, y - 0.67, 2.0, 1.33, "none", "none", 0)  # registers the stone with the captions; its ellipse follows
        parts.append(f'<ellipse cx="{ox + x * FTPX:.0f}" cy="{oy + y * FTPX:.0f}" rx="3" ry="2"/>')
    parts.append(rect(*shoe, "#9C9488", "#5C5448", 0.8, "shoe-stone"))  # declared: the reception's entrance (pack_audit)
    parts.append("</g></g>")
