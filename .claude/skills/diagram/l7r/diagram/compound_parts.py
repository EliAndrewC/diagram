"""compound_parts.py - what the compound draft seats AROUND the placed masses (split out of `compound.py`, feature
267): the faces of a building, the fire-water tubs, wells and privies at them, the house's service parts (the kitchen's
corridor, the bath), the gates in the walls, the doors, and the roji - each seated against the masses the placer set
down, clear of every one of them and of what was seated before it.
"""

from __future__ import annotations

from collections.abc import Callable

from .compound_model import (
    BATH_H_FT,
    BATH_W_FT,
    CORRIDOR_W_FT,
    DOOR_D_FT,
    DOOR_FRACS,
    DOOR_KINDS,
    DOOR_W_FT,
    FIRE_GAP_FT,
    FTPX,
    GATE_POST_W_FT,
    KINDS,
    ROOF_POST_BAY_FT,
    ROOF_POST_FT,
    ROOFED_ZONES,
    STONE_STEP_FT,
    CompoundProgram,
    CourtZone,
    Envelope,
    Placed,
    PlaceResult,
    _gate_interval,
    _kind_attr,
)


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
    in the south wall, the postern (`Envelope.postern`) in its own."""
    runs = {"N": (0.0, 0.0, env.w_ft, 0.0), "W": (0.0, 0.0, 0.0, env.h_ft), "E": (env.w_ft, 0.0, env.w_ft, env.h_ft), "S": (0.0, env.h_ft, env.w_ft, env.h_ft)}
    gaps = {"S": _gate_interval(env)}
    if env.postern:
        side, at, w = env.postern
        gaps[side] = (at - w / 2, at + w / 2)
    out: list[tuple[str, float, float, float, float]] = []
    for side, (x1, y1, x2, y2) in runs.items():
        if side not in gaps:
            out.append((side, x1, y1, x2, y2))
            continue
        lo, hi = gaps[side]
        if y1 == y2:
            out += [(side, x1, y1, lo, y2), (side, hi, y1, x2, y2)]
        else:
            out += [(side, x1, y1, x2, lo), (side, x1, hi, x2, y2)]
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


def _door(env: Envelope, p: Placed, boxes: list[Box]) -> tuple[Box, Box] | None:
    """A door flush inside `p`'s door face (DOOR_W_FT x DOOR_D_FT), at the first DOOR_FRACS spot whose approach - the
    door's width plus a foot each side, 3 ft out - is clear of every box (never `p` itself): the door and its approach,
    or None where no spot is clear."""
    nx, ny, fx, fy, length = _face(p, p.spec.door_face or _court_side(p))
    for frac in DOOR_FRACS:
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


def _corridor(a: Placed, b: Placed, width: float, max_gap: float) -> Box | None:
    """A covered corridor `width` wide across the gap between two buildings that face each other across no more than
    `max_gap` ft (CORRIDOR_W_FT), centered on the run they share; None if they share no such run."""
    lo, hi = max(a.x_ft, b.x_ft), min(a.x2, b.x2)
    if hi - lo >= width:
        top, bot = (a.y2, b.y_ft) if a.y2 <= b.y_ft else (b.y2, a.y_ft)
        if 0 < bot - top <= max_gap:
            mid = (lo + hi) / 2
            return (mid - width / 2, top, mid + width / 2, bot)
    lo, hi = max(a.y_ft, b.y_ft), min(a.y2, b.y2)
    if hi - lo >= width:
        left, right = (a.x2, b.x_ft) if a.x2 <= b.x_ft else (b.x2, a.x_ft)
        if 0 < right - left <= max_gap:
            mid = (lo + hi) / 2
            return (left, mid - width / 2, right, mid + width / 2)
    return None


def _roomiest(points: list[tuple[float, float]], boxes: list[Box]) -> tuple[float, float]:
    """The point with the most open ground around it: the farthest from its SECOND-nearest box - every tub stands against
    the building it serves, so the nearest box says nothing - with a box holding the point (its own) not counted; the
    first on a tie."""

    def room(pt: tuple[float, float]) -> float:
        x, y = pt
        gaps = [((max(bx - x, 0.0, x - bx2)) ** 2 + (max(by - y, 0.0, y - by2)) ** 2) ** 0.5 for bx, by, bx2, by2 in boxes if not (bx <= x <= bx2 and by <= y <= by2)]
        return sorted(gaps)[1] if len(gaps) > 1 else float("inf")

    return max(points, key=room)


def _point_features(program: CompoundProgram, result: PlaceResult, rect: Callable[..., str], caption: Callable[..., str], ox: float, oy: float) -> list[str]:
    """The program's point features, seated by the composition (feature 254): fire-water tubs at every
    wooden building's court face (two at the kitchen), a well at the kitchen, the garden and the stables,
    a privy beside the barracks, the stables and the servants' row, the notice board outside the main gate -
    and the house's service parts (feature 267): a covered corridor joining the kitchen to the residence, and
    the bath as a small addition abutting the kitchen's court face. The placer arranges the wall-ranging masses; these follow them, each
    seated at the first spot along its building's court face that is CLEAR of every mass and of every
    feature already seated - a draft swept by the gate carries the whole program, not the masses alone."""
    env = program.envelope
    parts: list[str] = []
    taken: list[tuple[float, float, float, float]] = [(p.x_ft, p.y_ft, p.x2, p.y2) for p in result.placed]
    # a ROOFED court is a footprint like a building's (ROOFED_ZONES): no tub, well or privy stands under its roof - a
    # tub there is fed by no gutter (the office hall's stood inside the hearing court until feature 267's pass 3)
    taken += [(z.x_ft, z.y_ft, z.x2, z.y2) for z in program.spine if z.name in ROOFED_ZONES]
    by_name = {p.spec.name: p for p in result.placed}

    def clear(x: float, y: float, w: float, h: float, margin: float = 1.0) -> bool:
        return _is_clear(env, taken, x, y, w, h, margin)

    def seat(p: Placed, size: float, fracs: tuple[float, ...], offs: tuple[float, ...]) -> tuple[float, float] | None:
        """The center of a `size`-square feature against `p`'s court face: the first clear (frac, off)."""
        nx, ny, fx, fy = _court_face(p, env)
        for off in offs:
            for frac in fracs:
                cx, cy = (fx + p.spec.w_ft * frac, fy + ny * off) if ny else (fx + nx * off, fy + p.spec.h_ft * frac)
                if clear(cx - size / 2, cy - size / 2, size, size):
                    taken.append((cx - size / 2, cy - size / 2, cx + size / 2, cy + size / 2))
                    return cx, cy
        return None

    tubs: list[tuple[float, float]] = []
    wells: list[tuple[float, float]] = []
    privies: list[tuple[float, float]] = []
    # The kitchen is part of the house: a short covered corridor joins it to the residence where they face each other
    # across a fire-gap (CORRIDOR_W_FT), drawn as a part of the residence
    if "kitchen" in by_name and "residence" in by_name and (cor := _corridor(by_name["kitchen"], by_name["residence"], CORRIDOR_W_FT, FIRE_GAP_FT)):
        taken.append(cor)
        fill, stroke = KINDS["lord"]
        parts += [f"<g{_kind_attr('residence')}>", rect(cor[0], cor[1], cor[2] - cor[0], cor[3] - cor[1], fill, stroke, 1.2, "", "residence corridor"), "</g>"]
    # The bath is a small addition abutting the kitchen's court face - the house's service side (BATH_W_FT); seated
    # before the wells so the kitchen well takes what the bath leaves, and clear of every spine court, since a bath in
    # the garden is the pavilion the research does not find
    if "kitchen" in by_name:
        zones = [(z.x_ft, z.y_ft, z.x2, z.y2) for z in program.spine]
        host = by_name["kitchen"]
        others = [t for t in taken if t != (host.x_ft, host.y_ft, host.x2, host.y2)]
        if bath := _abut(env, host, BATH_W_FT, BATH_H_FT, others + zones):
            bx, by = bath
            taken.append((bx, by, bx + BATH_W_FT, by + BATH_H_FT))
            parts.append(rect(bx, by, BATH_W_FT, BATH_H_FT, KINDS["service"][0], KINDS["service"][1], 1.5, "", "bath"))
            caption("area", bx, by, BATH_W_FT, BATH_H_FT, "bath", 8, False, "#3A2E1C", "bath")
    # wells next: they take the middle of a face. A kitchen well may stand as far as 20 ft out - past the bath that
    # abuts the kitchen, serving both, as the Takayama residence's bath stood with its well and kitchen (research
    # buildings 320); the nearer seats are tried first
    for name in ("kitchen", "stables"):
        if name in by_name and (w := seat(by_name[name], 7.3, (0.5, 0.3, 0.7), (9.0, 12.0, 15.0, 20.0))):
            wells.append(w)
    for z in program.spine:
        if z.name == "garden":
            # the garden well stands at the garden's EAST end, where the bath stood before it joined the house: at the
            # west end it stood 8 ft from the kitchen well seated past the bath, and read as its duplicate
            wells.append((z.x2 - 5.0, z.y_ft + 5.0))
            taken.append((z.x2 - 8.65, z.y_ft + 1.35, z.x2 - 1.35, z.y_ft + 8.65))
    for name in ("barracks", "stables", "servants"):
        if name in by_name and (v := seat(by_name[name], 5.0, (0.85, 0.15, 0.5), (4.5, 7.0))):
            privies.append(v)
    # a door on each lodging block's face (DOOR_KINDS, `_door`), a part of its building: seated after the bath, the
    # wells and the privies and BEFORE the tubs, which have seats to spare - the kitchen's two tubs had taken every
    # run of its face a door could open on. The door and the ground before it are held clear of what follows.
    for p in result.placed:
        if p.spec.feature in DOOR_KINDS and (found := _door(env, p, [t for t in taken if t != (p.x_ft, p.y_ft, p.x2, p.y2)])):
            (dx, dy, dx2, dy2), approach = found
            taken += [(dx, dy, dx2, dy2), approach]
            parts.append(rect(dx, dy, dx2 - dx, dy2 - dy, "#4A3318", "none", 0, "", "door", p.spec.feature))
    for p in result.placed:
        if p.spec.kind == "kura":
            continue  # a plaster storehouse carries no tub (buildings.md, "Fire-water tubs")
        for _ in range(2 if p.spec.name.startswith("kitchen") else 1):
            # the ends of the face last (0.05, 0.95): where a roofed court covers the rest of it, the uncovered end
            if tub := seat(p, 2.6, (0.15, 0.85, 0.4, 0.6, 0.05, 0.95), (2.5,)):
                tubs.append(tub)
    _roji_parts(program, result, taken, rect, parts, ox, oy)
    for cx, cy in wells:
        parts.append(rect(cx - 3.65, cy - 3.65, 7.3, 7.3, "#9C8C70", "#5C4830", 1.2, "", "well"))
        caption("point", cx - 3.65, cy - 3.65, 7.3, 7.3, "well", 8, True, "#3A2E1C", "well")
    for cx, cy in privies:
        parts.append(rect(cx - 2.5, cy - 2.5, 5.0, 5.0, "#7E726A", "#4A3318", 0.8, "", "latrine"))
        caption("point", cx - 2.5, cy - 2.5, 5.0, 5.0, "latrine", 7, True, "#3A2E1C", "latrine")
    if tubs:
        parts.append('<g fill="#8FB0C6" stroke="#3A5060" stroke-width="1" data-kind="fire-water tubs">')
        parts += [f'<circle cx="{ox + cx * FTPX:.0f}" cy="{oy + cy * FTPX:.0f}" r="3.8"/>' for cx, cy in tubs]
        parts.append("</g>")
        for tx, ty in tubs:  # every tub is drawn - and so is an obstacle to every caption
            rect(tx - 1.27, ty - 1.27, 2.54, 2.54, "none", "none", 0)  # registers the tub; its drawn circle follows
        # the group's one caption goes on the tub with the most open ground around it: the first tub can stand hemmed
        # in (the residence's, between the wall, the kitchen and their corridor), and a caption pushed off it is
        # drawn far from any tub it names (pack audit `orphan_group_labels`)
        tx, ty = _roomiest(tubs, taken)
        caption("point", tx - 1.27, ty - 1.27, 2.54, 2.54, "fire-water tubs", 7, True, "#3A5060", "fire-water tubs")
    gl, _gr = _gate_interval(env)
    parts.append(rect(gl - 14.0, env.h_ft + 3.0, 6.0, 1.5, "#4A3318", "#2D2A24", 0.6, "", "notice board"))
    caption("point", gl - 14.0, env.h_ft + 3.0, 6.0, 1.5, "notice board", 7, True, "#3A2E1C", "notice board")
    return parts


def _roji_parts(program: CompoundProgram, result: PlaceResult, taken: list[Box], rect: Callable[..., str], parts: list[str], ox: float, oy: float) -> None:
    """The guest's way (R07's no-genkan form, research buildings 300): from the middle gate a stepping-stone path, the
    roji, straight to a shoe stone at the reception room's veranda - drawn where the program has a middle gate and a
    building with a `reception room` and an engawa. The stones are a part of the garden they cross (Hayakawa's form)."""
    env = program.envelope
    mid = _middle_gate(env, result.placed)
    host = next((p for p in result.placed if p.spec.engawa_ft and any(k == "reception room" for k, _w, _h in p.spec.rooms)), None)
    if mid is None or host is None:
        return
    rx = host.x_ft + sum(w for _k, w, _h in host.spec.rooms[: [k for k, _w, _h in host.spec.rooms].index("reception room")])
    rw = next(w for k, w, _h in host.spec.rooms if k == "reception room")
    _nx, ny, _fx, fy = _court_face(host, env)
    shoe = (rx + rw / 2 - 2.0, fy + (0.0 if ny > 0 else -1.67), 4.0, 1.67)
    gate = ((mid[0] + mid[1]) / 2, env.divider_ft + (-2.5 if host.spec.court == "inner" else 2.5))
    stones = _roji(gate, (rx + rw / 2, fy + 2.0 * ny), taken)
    parts.append('<g data-kind="garden"><g fill="#B8B0A0" stroke="#7A7060" stroke-width="0.5">')
    for x, y in stones:
        rect(x - 1.0, y - 0.67, 2.0, 1.33, "none", "none", 0)  # registers the stone with the captions; its ellipse follows
        parts.append(f'<ellipse cx="{ox + x * FTPX:.0f}" cy="{oy + y * FTPX:.0f}" rx="3" ry="2"/>')
    parts.append(rect(*shoe, "#9C9488", "#5C5448", 0.8))
    parts.append("</g></g>")
