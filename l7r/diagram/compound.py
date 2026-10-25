#!/usr/bin/env python3
"""compound.py - a feet-first compound PROGRAM + a perimeter-first PLACER (feature 008).

Mode A compound plans are hand-authored, but their COMPOSITION (buildings ringing the
courts, the open court-spine held in the center) is easy to get wrong by hand. This module
lets a compound be declared as a feet-based program - the envelope, the reserved court-spine
(forecourt -> oshirasu -> garden, plus named yards like the practice ground), and a list of
buildings each sized IN FEET with a wall tag - and arranges them PERIMETER-FIRST into a
composed draft SVG the GM then refines.

Footage is the source unit; pixels are derived (FTPX) only at emit time. The placer is the
Mode A analog of the Mode B water-first generator: a fixed ordering (reserve the spine, then
hug the walls largest-first with fire-gaps) that cannot paint itself into a corner - the
opposite of worst-fit, which would scatter buildings into the center.

See docs/buildings.md "Composition: perimeter buildings + a named court-spine". The program's types and units live in
`compound_model.py`, what is seated around the placed masses (tubs, wells, doors, gates' posts, the roji) in
`compound_parts.py` (feature 267 split them out); the pool generators still import this module alone.

CLI:  python3 compound.py            # place the built-in county magistracy, write a draft SVG
"""

from __future__ import annotations

import math
import os
import sys
from collections.abc import Callable
from dataclasses import replace
from typing import Any

from .buildings.types import by_tier
from .compound_model import (
    COURT_FILL,
    DIVIDER_INK_FT,
    FIRE_GAP_FT,
    FTPX,
    GATE_POST_D_FT,
    GATE_POST_W_FT,
    KINDS,
    NAKAMON_POST_D_FT,
    OUTLINE_CLEAR_FT,
    ROOF_POST_FT,
    ROOFED_ZONES,
    WALL_FACE_CLEAR_FT,
    WALL_INK_FT,
    WALL_MARGIN_FT,
    BuildingSpec,
    CompoundProgram,
    CourtZone,
    Envelope,
    Placed,
    PlaceResult,
    _gate_interval,
    _kind_attr,
)
from .compound_parts import _clerk_seats, _court_side, _dais, _engawa, _gate_posts, _lattice, _mats, _middle_gate, _point_features, _rear_band, _roof_posts, _stable_parts, _wall_runs
from .compound_view import OneView, View, one_view
from .labels import Obstacle, ObstacleIndex, Placement, Subject
from .labels import place as place_caption
from .labels.standard import CHAR_W_EM, WEIGHT_OBSTACLE
from .labels.svg import caption_svg, leader_svg

# ---- placement (perimeter-first, 2-D collision) ------------------------------------------
#
# Buildings are placed in a single global priority order (rank 1 before rank 2, then highest
# `order`, then largest). Each building hugs its wall and slides ALONG that wall past every
# obstacle it overlaps - the spine courts, the south gate, AND every building already placed.
# So a contested corner goes to whichever building is placed first (highest order), and a
# short E/W building no longer blocks the whole corner it does not actually occupy: the crude
# per-court corner reservation the old placer used is gone, replaced by real rectangle overlap.
# A rank-2 building sits BEHIND the rank-1 row on its wall (a rear service strip / second rank) - the household's
# STORES behind the house, as the Higuchi house kept its storehouse beyond the ground behind the main house. Never its
# servants: a large household's servants lodge in a range on its street edge (feature 374 wave 124;
# research/questions/0115-servants-in-a-samurai-household-where-they-sleep-and-how-they-were-hired-hokonin.drawing.html).


def _court_yrange(env: Envelope, court: str) -> tuple[float, float]:
    return (0.0, env.divider_ft) if court == "inner" else (env.divider_ft, env.h_ft)


def _rank_depth(env: Envelope, already: list[Placed], spec: BuildingSpec) -> float:
    """How deep the rank-1 row on this building's wall reaches inward (0 if none placed yet)."""
    same = [p for p in already if p.spec.court == spec.court and p.spec.wall == spec.wall and p.spec.rank == 1]
    depths: list[float] = []
    for p in same:
        if spec.wall == "N":
            depths.append(p.y2)
        elif spec.wall == "S":
            depths.append(env.h_ft - p.y_ft)
        elif spec.wall == "W":
            depths.append(p.x2)
        else:  # "E"
            depths.append(env.w_ft - p.x_ft)
    return max(depths) if depths else 0.0


def _wall_clearance_ft(wall: str) -> float:
    """Ground a hugging building must leave for the wall: half the wall's thickness, because the wall is drawn centered on
    the boundary, then a foot or two clear of its face (WALL_FACE_CLEAR_FT, feature 374 wave 134; it was a hair, 0.5 ft).
    3 ft off a compound wall's centerline, 2.5 ft off a court divider's.

    Research:
        clear of the wall's face - research/questions/0092-compound-walls-neribei-and-tsuijibei.drawing.html: a building set a foot or two off the wall, its eaves nearly touching; the spacing the page's GUESS, 1.5 ft its middle"""
    return (DIVIDER_INK_FT if wall == "divider" else WALL_INK_FT) / 2 + WALL_FACE_CLEAR_FT


def _cross_coord(env: Envelope, spec: BuildingSpec, already: list[Placed]) -> float:
    """Fixed cross-axis top-left coord (y for N/S/divider, x for E/W). Rank 1 abuts the wall's
    inner face; rank 2 is offset inward past the rank-1 row already on that wall."""
    clear = _wall_clearance_ft(spec.wall)
    if spec.wall == "divider":  # backs the internal divider; no second rank
        return env.divider_ft + clear if spec.court == "outer" else env.divider_ft - spec.h_ft - clear
    # inward depth of this building's own face: the wall ink for rank 1, the rank-1 row + a
    # fire-gap for rank 2 (which already clears the ink, since that row sits beyond it)
    depth = ((_rank_depth(env, already, spec) + FIRE_GAP_FT) if spec.rank > 1 else clear) + spec.inset_ft
    if spec.wall == "N":
        return depth
    if spec.wall == "S":
        return env.h_ft - spec.h_ft - depth
    if spec.wall == "W":
        return depth
    return env.w_ft - spec.w_ft - depth  # "E"


def _rect_overlap(ax: float, ay: float, aw: float, ah: float, bx: float, by: float, bw: float, bh: float) -> bool:
    return ax < bx + bw and ax + aw > bx and ay < by + bh and ay + ah > by


def _obstacle_end(
    gate: tuple[float, float] | None,
    spine: tuple[CourtZone, ...],
    already: list[Placed],
    px: float,
    py: float,
    spec: BuildingSpec,
    horizontal: bool,
) -> float | None:
    """Along-axis end of the furthest obstacle (gate, spine court, or placed building) the
    candidate rectangle overlaps - or None if it overlaps nothing."""
    ends: list[float] = []
    if gate is not None and px < gate[1] and px + spec.w_ft > gate[0]:
        ends.append(gate[1])
    for z in spine:
        if _rect_overlap(px, py, spec.w_ft, spec.h_ft, z.x_ft, z.y_ft, z.w_ft, z.h_ft):
            ends.append(z.x2 if horizontal else z.y2)
    for p in already:
        # a building holds `tree_ft` more ground past its far end along its own wall (the compound shrine's tree)
        along = p.spec.wall in ("N", "S", "divider")
        w, h = (p.spec.w_ft + p.spec.tree_ft, p.spec.h_ft) if along else (p.spec.w_ft, p.spec.h_ft + p.spec.tree_ft)
        if _rect_overlap(px, py, spec.w_ft, spec.h_ft, p.x_ft, p.y_ft, w, h):
            ends.append(p.x_ft + w if horizontal else p.y_ft + h)
    return max(ends) if ends else None


def _place_one(env: Envelope, spec: BuildingSpec, spine: tuple[CourtZone, ...], already: list[Placed]) -> Placed | None:
    """Hug the wall and slide along it past every obstacle; None if it runs off the wall. A `beside_gate` building
    stands flush west of the main gate's west post instead, or nowhere if something already holds that ground."""
    horizontal = spec.wall in ("N", "S", "divider")
    cross = _cross_coord(env, spec, already)
    if spec.beside_gate:
        x = _gate_interval(env)[0] - GATE_POST_W_FT - OUTLINE_CLEAR_FT - spec.w_ft
        clash = _obstacle_end(None, spine, already, x, cross, spec, True)
        return Placed(spec, x, cross) if x >= WALL_MARGIN_FT and clash is None else None
    along_start, along_end = (0.0, env.w_ft) if horizontal else _court_yrange(env, spec.court)
    gate = _gate_interval(env) if spec.wall == "S" else None
    size = spec.w_ft if horizontal else spec.h_ft
    cursor = along_start + WALL_MARGIN_FT
    while True:
        px, py = (cursor, cross) if horizontal else (cross, cursor)
        end = _obstacle_end(gate, spine, already, px, py, spec, horizontal)
        if end is None:
            break
        cursor = end + (0.0 if any(_joined(spec, p.spec) and (p.x2 if horizontal else p.y2) == end for p in already) else FIRE_GAP_FT)
    if cursor + size > along_end - WALL_MARGIN_FT:
        return None
    px, py = (cursor, cross) if horizontal else (cross, cursor)
    return Placed(spec, px, py)


def _joined(a: BuildingSpec, b: BuildingSpec) -> bool:
    """One of the two is an ell of the other (`BuildingSpec.joins`): they abut, no fire-gap between."""
    return bool(a.joins and a.joins == b.feature) or bool(b.joins and b.joins == a.feature)


def _wall_tier(wall: str) -> int:
    """Placement tier: N/S rows first (own the corners), then E/W columns (flow below the
    N/S buildings), then the divider hall last (flows centered between the E/W columns)."""
    if wall in ("N", "S"):
        return 0
    return 1 if wall in ("E", "W") else 2


def place(program: CompoundProgram) -> PlaceResult:
    """Arrange the buildings perimeter-first with 2-D collision: reserve the spine, then place
    each building in priority order - rank 1 before rank 2, then N/S before E/W before divider,
    then highest `order`, then largest - hugging its wall and sliding past the gate, the courts,
    and every building already down. Corners go to the N/S rows; short E/W and divider buildings
    flow around them instead of blocking a whole corner they do not occupy.

    NO BUILDING IS LEFT IN OVERFLOW (feature 287, homes H29a): a building that runs off its wall grows the walled
    interior along that wall by its own length and a fire-gap, and the placement is run again - within the compound size
    the program states (`max_w_ft`, `max_h_ft`). A program asking for more than that much compound holds is refused here,
    naming the building (plan D7: the composer is seedless, so this is an impossible input refused before any sheet
    exists, never a sheet drawn with a building off its wall). The result carries the envelope it was placed in."""
    env = program.envelope
    grew: list[str] = []
    while True:
        result = PlaceResult(envelope=env)
        for spec in sorted(program.buildings, key=lambda s: (s.rank, _wall_tier(s.wall), -s.order, -(s.w_ft * s.h_ft))):
            placed = _place_one(env, spec, program.spine, result.placed)
            if placed is None:
                result.overflow.append(spec)
            else:
                result.placed.append(placed)
        if not result.overflow:
            # THE COMPOSITION IS IN ITS BANDS OR IT IS REFUSED (feature 287 wave 6, homes H29b; plan D7): coverage and
            # perimeter hugging are asked of the placed masses by the pack audit's own registered checks
            # (`composition_sitings`) - growing the envelope for an overflowing building adds unbuilt ground, and nothing
            # asked whether the coverage band survived it. The composer is seedless, so a composition out of its bands is
            # an impossible program, refused here naming what failed, never a sheet drawn out of band.
            if program.tier is not None and (found := composition_sitings(result, _declared_checks(program.tier))):
                why = f" (the compound was grown for {', '.join(repr(g) for g in grew)})" if grew else ""
                raise ValueError(f"{program.title}: the composition fails its bands{why}: " + "; ".join(found))
            return result
        grew.append(result.overflow[0].name)
        grown = _grown(env, result.overflow[0], program)
        if grown is None:
            spec = result.overflow[0]
            raise ValueError(
                f"{program.title}: {spec.name!r} ({spec.w_ft:g} x {spec.h_ft:g} ft, {spec.court} {spec.wall}) finds no seat on its wall inside the compound the program allows - "
                "shrink the building, move it, or state a larger compound (max_w_ft / max_h_ft)"
            )
        env = grown


DRAFT_MARGIN_FT = 7.0
"""The draft's parchment margin (`emit_svg`'s default): the checklist's ~15-25 px, 7 ft = 21 px.

Research: draft margin - CONVENTION: the parchment margin of a draft sheet is 7 ft, 21 px at 3 px to the foot, inside the checklist's 15-25 px border."""


def composition_plan(result: PlaceResult, margin_ft: float = DRAFT_MARGIN_FT) -> Any:
    """The composition as the pack audit reads a sheet (`tools/pack_audit/parse.ParsedPlan`): the precinct's two courts,
    every placed mass and the court divider, at the draft's own pixel frame and rounding (`emit_svg` writes each rect
    at `ox + x * FTPX` to the whole pixel), so the audit's grid measures - `coverage`, `perimeter_hugging_pct` - read the
    composition the way they read the drawn sheet. The point features the draft adds later (the bath and the
    privies) are not in it: they are seated around the masses and add built ground (measured on both generated drafts,
    2026-09-29: the drawn sheet's coverage 1.2 points over the masses' alone).

    Research:
        its drawn sizes - CONVENTION: sizes on the sheet, not in the world - 8 (title band above the precinct)
    """
    from .tools.pack_audit.parse import ParsedPlan, Rect

    assert result.envelope is not None, "place() records the envelope it placed in"
    env = result.envelope
    ox, oy = margin_ft * FTPX, (margin_ft + 8.0) * FTPX

    def rect(x: float, y: float, w: float, h: float) -> Rect:
        px0, py0, px1, py1 = _px_edges(ox, oy, x, y, w, h)
        return Rect(px0, py0, px1 - px0, py1 - py0)

    interior = (rect(0.0, 0.0, env.w_ft, env.divider_ft), rect(0.0, env.divider_ft, env.w_ft, env.h_ft - env.divider_ft))
    divider = Rect(round(ox), round(oy + env.divider_ft * FTPX), round(env.w_ft * FTPX), 2.0)  # the audit's thin rect of a divider line
    return ParsedPlan(interior, tuple(rect(p.x_ft, p.y_ft, p.spec.w_ft, p.spec.h_ft) for p in result.placed), (), (), (divider,))


def _px_edges(ox: float, oy: float, x: float, y: float, w: float, h: float) -> tuple[int, int, int, int]:
    """A box in feet as whole-pixel EDGES (x0, y0, x1, y1), each rounded half up on its own (feature 374 wave 134): rounding the
    origin and the size apart let two boxes flush in feet part by a pixel at a half-pixel origin - the clerks' seats, flush
    with the office hall's court face, stood a pixel past it once the hall stood 2.5 ft off the divider."""

    def r(v: float) -> int:
        return math.floor(v + 0.5)

    return r(ox + x * FTPX), r(oy + y * FTPX), r(ox + (x + w) * FTPX), r(oy + (y + h) * FTPX)


def _declared_checks(tier: str) -> tuple[str, ...]:
    """The checks the declaration lists for `tier` (none for a tier it does not declare)."""
    btype = by_tier(tier)
    return btype.checks if btype is not None else ()


def composition_sitings(result: PlaceResult, checks: tuple[str, ...] = ("coverage_band", "perimeter_hugging")) -> list[str]:
    """THE ONE PREDICATE of a generated sheet's coverage band and perimeter hugging (feature 287 wave 6, homes H29b): the
    pack audit's own registered checks (`shared.coverage_band`, `shared.perimeter_hugging`) asked of the composition
    (`composition_plan`), each only where `checks` (the type's declaration) lists it - each finding the audit would
    print, none where the composition is in its bands."""
    from .tools.pack_audit.shared import coverage_band, perimeter_hugging

    plan = composition_plan(result)
    return (coverage_band(plan) if "coverage_band" in checks else []) + (perimeter_hugging(plan) if "perimeter_hugging" in checks else [])


def _grown(env: Envelope, spec: BuildingSpec, program: CompoundProgram) -> Envelope | None:
    """The envelope grown along the overflowing building's wall by its own length and a fire-gap, or None past the
    compound size the program states (or where it states none, or where length cannot help: a building beside the gate)."""
    if spec.beside_gate:
        return None
    if spec.wall in ("N", "S", "divider"):
        w = env.w_ft + spec.w_ft + FIRE_GAP_FT
        return replace(env, w_ft=w) if program.max_w_ft is not None and w <= program.max_w_ft else None
    h = env.h_ft + spec.h_ft + FIRE_GAP_FT
    return replace(env, h_ft=h) if program.max_h_ft is not None and h <= program.max_h_ft else None


# ---- SVG emit (feet -> px at FTPX; a composed DRAFT the GM refines) -----------------------

#: The Mode A kind of each reserved court zone (feature 262) - what its ground lights as on the page.
ZONE_KINDS: dict[str, str] = {
    "forecourt": "outer court",
    "oshirasu": "hearing court",
    "garden": "garden",
    "yard": "outer court",
    "cart yard": "cart yard",
    "vegetable garden": "vegetable garden",
    "inner yard": "inner court",
    "practice ground": "practice ground",
    "rear yard": "rear yard",
    # the kitchen's working ground, named for what it is as Ochiba's sheet names its own (feature 374 wave 129)
    "service yard": "inner court",
}
#: Zones drawn as bare ground, with no edge: an outlined sub-rectangle of court reads as a FENCED court, and a fenced
#: forecourt is a GUESS the record does not support (research 0104; building-review round 3).
UNFENCED_ZONES: frozenset[str] = frozenset({"forecourt", "yard", "cart yard", "inner yard", "rear yard", "service yard"})
#: A zone's caption where its program name is not the reader's word: the hearing court is `oshirasu` in the program (and
#: in its fill pattern) but the sheets caption it in English (the other drafts and the hand sheets say `hearing court`).
#: A room's caption where its kind's name is not what the room is: the karo lodges in a BAY of the staff long-house
#: (research 0106), which the kind `karo's house` finds, but a bay is not a house (building-review round 6); the maids lodge in
#: a room of the house the kind `servants' quarters` finds (feature 374 batch 4, plan R4-1).
ROOM_CAPTIONS: dict[str, str] = {"karo's house": "karo's quarters", "servants' quarters": "maids' room"}
ZONE_CAPTIONS: dict[str, str] = {"oshirasu": "hearing court", "yard": "outer court", "inner yard": "inner court"}


_GROUND_KINDS = frozenset({*ZONE_KINDS.values(), "inner court", "outer court", "practice ground", "garden", "-"})
"""The kinds a draft draws as open ground - the courts and the zones - which are free space to a caption (feature 266,
FR-006: ground weighs 0). Everything else it draws is an obstacle."""


def stroke_band(a: tuple[float, float], b: tuple[float, float], half: float) -> list[tuple[float, float]]:
    """A stroked line's drawn band as a quad - a 9 px wall is 9 px wide to a caption, not a hairline."""
    dx, dy = b[0] - a[0], b[1] - a[1]
    n = (dx * dx + dy * dy) ** 0.5 or 1.0
    nx, ny = -dy / n * half, dx / n * half
    return [(a[0] + nx, a[1] + ny), (b[0] + nx, b[1] + ny), (b[0] - nx, b[1] - ny), (a[0] - nx, a[1] - ny)]


BOLD_CHAR_W_EM = 0.60
"""A bold mixed-case name's advance per character, in ems - the width the pack audit measured by rendering the pool's
bold building names (`tools/pack_audit/parse.py` CHAR_W_BOLD_MIXED, 2026-07-25).

Research: bold name width - NONE: a bold mixed-case name advances 0.60 em per character, a text-measuring figure taken by rendering the pool's names."""

CAPTION_ROOM = 40.0
"""How far below the drawn canvas a draft's caption may stand, in px (feature 266): room for one caption line beside
the notice board outside the gate. The canvas grows to hug whatever is placed there.

Research: caption room - CONVENTION: the canvas may grow 40 px below the drawing for one caption line beside the notice board, a sheet-layout allowance."""


CAPTION_GROWTHS = 3
"""How many `CAPTION_ROOM` steps the draft's foot may grow for a caption with no clean seat (feature 287, labels L15) -
past that the program itself is refused (plan D7).

Research: caption growths - NONE: the foot may grow by at most 3 CAPTION_ROOM steps before the program is refused, a loop count."""

CAPTION_REPAIR_EM = 2.0
"""How near a stranded caption's subject a seated caption must stand to be lifted for it, in ems of the stranded caption
plus that caption's own length - `labels.hand_sheet.REPAIR`, the hand sheets' repair, on the generated sheets.

Research: caption repair reach - CONVENTION: a seated caption within 2 ems of a stranded caption's subject (plus its length) is lifted to free a seat, a label-placement reach."""

Request = tuple[str, Subject, float, bool, str, str]


def _seat_captions(
    requests: list[Request],
    obstacles: list[Obstacle],
    frame: tuple[float, float, float, float],
    title: str = "",
    names: list[str] | None = None,
    one: OneView | None = None,
) -> tuple[list[str], float]:
    """Place every requested caption by the ONE placer (feature 266), in order, each an obstacle to the next, and write
    it - with its leader when the standard gives it one (FR-005). Returns the strings and the lowest point drawn. (The roofed
    court's floor joined the index only once its own captions were seated - feature 340 retired that: under the one view the
    hand-sheet placer's classification reads the court as built, as it reads a hand sheet's.)

    NO CAPTION LIES ON A FEATURE IT DOES NOT NAME (feature 287, labels L15; plan D7): each is placed STRICTLY - a free
    seat or none (`place(strict=True)`). A caption with none has one seated neighbor lifted and the pair re-seated
    (`_repair`, the hand sheets' repair), then the draft's foot is grown by `CAPTION_ROOM` and the whole set placed
    again; a program whose caption has no clean seat after that is refused at composition, naming the caption - the
    composer is seedless, so this is an impossible program, refused before any sheet exists."""
    stuck = 0
    for grow in range(CAPTION_GROWTHS + 1):
        seats, stuck_at = _seat_all(requests, obstacles, (frame[0], frame[1], frame[2], frame[3] + grow * CAPTION_ROOM), one)
        if stuck_at is None:
            break
        stuck = stuck_at
    else:
        raise ValueError(f"{title}: the caption {requests[stuck][0]!r} has no seat clear of every feature, even with a neighbor lifted and the sheet grown - change the program")
    out: list[str] = []
    foot = 0.0
    for i, ((_text, _subject, size, italic, fill, kind), p) in enumerate(zip(requests, seats, strict=True)):
        out.append(caption_svg(p, size, ' font-style="italic"' if italic else ' font-weight="bold"', fill, kind, names[i] if names else ""))
        if p.leader is not None:
            out.append(leader_svg(p, size, fill, kind))
        foot = max(foot, *(q[1] for q in p.block))
    return out, foot


def _caption_index(
    obstacles: list[Obstacle],
    seats: list[Placement],
    lifted: int | None = None,
    subject: Subject | None = None,
    view: View | None = None,
    caption: int = 0,
) -> ObstacleIndex:
    """The index a caption is placed against: the drawn features and every caption seated (but a `lifted` one). For an AREA caption the features holding its area are waived - a room's name lies in
    its building by necessity, as the hand sheets waive the building holding a named room (feature 267). Given the one
    `view` (feature 340), the drawn features are the hand-sheet placer's classification of the sheet for this subject and
    kind - its every weighted obstacle a block, inner ink included, but never a shape the caption declares (plan D4) - and the
    composer's own list is not read; the seated captions are added as before."""
    if view is not None and subject is not None:
        index = view(caption, subject).copy()
        for k, p in enumerate(seats):
            if k != lifted:
                index.add(Obstacle(p.block, WEIGHT_OBSTACLE))
        return index
    index = ObstacleIndex([o for o in obstacles if subject is None or subject.kind != "area" or not _holds(o.poly, subject.poly)])
    for k, p in enumerate(seats):
        if k != lifted:
            index.add(Obstacle(p.block, WEIGHT_OBSTACLE))
    return index


def _holds(outer: tuple[tuple[float, float], ...], inner: tuple[tuple[float, float], ...]) -> bool:
    """Does `outer`'s box hold `inner`'s, and more than it (1 px of slack)?"""
    a, b = _box(outer), _box(inner)
    return a[0] <= b[0] + 1 and a[1] <= b[1] + 1 and a[2] >= b[2] - 1 and a[3] >= b[3] - 1 and (a[2] - a[0]) * (a[3] - a[1]) > (b[2] - b[0]) * (b[3] - b[1]) + 1


def _seat_all(requests: list[Request], obstacles: list[Obstacle], frame: tuple[float, float, float, float], one: OneView | None = None) -> tuple[list[Placement], int | None]:
    """Every caption placed strictly in order, repaired where stranded; the placements, and the first caption no repair
    frees (None when all are seated). Under the one view (feature 340) a caption's subjects are tried in order, inside then
    beside, the first with a free seat winning, as the hand-sheet placer tries them - and only when none has one is a
    neighbor lifted for it."""
    seats: list[Placement] = []
    for i, (text, subject, size, *_style) in enumerate(requests):
        subs = one.subjects[i] if one else [subject]
        p = None
        for sub in subs:
            p = place_caption(text, size, sub, _view_index(obstacles, seats, sub, one, i), frame, strict=True, char_w=_width(one, i))
            if p is not None:
                break
        for sub in subs:
            if p is not None:
                break
            p = _repair(i, requests, obstacles, seats, frame, one, sub)
        if p is None:
            return seats, i
        seats.append(p)
    return seats, None


def _view_index(obstacles: list[Obstacle], seats: list[Placement], subject: Subject, one: OneView | None, caption: int, lifted: int | None = None) -> ObstacleIndex:
    """`_caption_index` for caption `caption` under the one view when there is one, else the composer's own."""
    return _caption_index(obstacles, seats, lifted=lifted, subject=subject, view=one.view if one else None, caption=caption)


def _width(one: OneView | None, i: int) -> float:
    """Caption `i`'s character width: the hand-sheet placer's measure of its face under the one view, else the standard's."""
    return one.widths[i] if one else CHAR_W_EM


def _repair(
    i: int,
    requests: list[Request],
    obstacles: list[Obstacle],
    seats: list[Placement],
    frame: tuple[float, float, float, float],
    one: OneView | None = None,
    sub: Subject | None = None,
) -> Placement | None:
    """Caption `i`, stranded, seated with one neighbor lifted and the neighbor re-seated after it - both on free seats, or
    neither moves (feature 286's repair, `labels.hand_sheet.repair`, on the generated sheets). The neighbors tried are
    the seated captions standing within `CAPTION_REPAIR_EM` ems plus their own length of the stranded caption's subject."""
    text, subject, size, *_style = requests[i]
    subject = sub or subject
    sx0, sy0, sx1, sy1 = _box(subject.poly)
    for j, done in enumerate(seats):
        bx0, by0, bx1, by1 = _box(done.block)
        reach = CAPTION_REPAIR_EM * size + max(bx1 - bx0, by1 - by0)
        if max(bx0 - sx1, sx0 - bx1, by0 - sy1, sy0 - by1, 0.0) > reach:
            continue
        pi = place_caption(text, size, subject, _view_index(obstacles, seats, subject, one, i, lifted=j), frame, strict=True, char_w=_width(one, i))
        if pi is None:
            continue
        jt, js, jsize, *_jstyle = requests[j]
        js = one.subjects[j][0] if one else js
        index = _view_index(obstacles, seats, js, one, j, lifted=j)
        index.add(Obstacle(pi.block, WEIGHT_OBSTACLE))
        pj = place_caption(jt, jsize, js, index, frame, strict=True, char_w=_width(one, j))
        if pj is not None:
            seats[j] = pj
            return pi
    return None


def _box(poly: tuple[tuple[float, float], ...]) -> tuple[float, float, float, float]:
    return min(q[0] for q in poly), min(q[1] for q in poly), max(q[0] for q in poly), max(q[1] for q in poly)


_DEFS = (
    '<defs>'
    '<pattern id="court-earth" patternUnits="userSpaceOnUse" width="16" height="16">'
    '<rect width="16" height="16" fill="#D9C28E"/><circle cx="4" cy="6" r="0.6" fill="#A88E58"/>'
    '<circle cx="12" cy="2" r="0.6" fill="#A88E58"/></pattern>'
    '<pattern id="oshirasu-sand" patternUnits="userSpaceOnUse" width="12" height="12">'
    '<rect width="12" height="12" fill="#F2EAD0"/><circle cx="3" cy="4" r="0.5" fill="#C9B884"/>'
    '<circle cx="8" cy="2" r="0.5" fill="#C9B884"/></pattern>'
    # a worked bed's furrows (feature 283, a map drawing convention: a vegetable bed reads apart from the ornamental garden)
    '<pattern id="vegetable-rows" patternUnits="userSpaceOnUse" width="8" height="8">'
    '<rect width="8" height="8" fill="#CDBF95"/><rect y="2.5" width="8" height="3" fill="#8FA36A"/></pattern>'
    '<pattern id="garden-stipple" patternUnits="userSpaceOnUse" width="14" height="14">'
    '<rect width="14" height="14" fill="#BFCFA0"/><circle cx="3" cy="3" r="0.8" fill="#7A8C5C"/>'
    '<circle cx="10" cy="9" r="0.8" fill="#7A8C5C"/></pattern>'
    # a takakura's timber walls, the hand sheets' slats (feature 374 wave 128: 0098's raised timber storehouse)
    '<pattern id="granary-slats" patternUnits="userSpaceOnUse" width="14" height="6">'
    '<rect width="14" height="6" fill="#D9B47A"/><line x1="0" y1="0" x2="14" y2="0" stroke="#7A5430" stroke-width="0.8"/>'
    '<line x1="0" y1="3" x2="14" y2="3" stroke="#A88454" stroke-width="0.5"/></pattern>'
    '<pattern id="keiko-earth" patternUnits="userSpaceOnUse" width="16" height="16">'
    '<rect width="16" height="16" fill="#E2CE9E"/><line x1="0" y1="5" x2="16" y2="5" stroke="#C2A46C" stroke-width="0.5"/>'
    '<line x1="0" y1="13" x2="16" y2="13" stroke="#C2A46C" stroke-width="0.5"/></pattern></defs>'
)


def emit_svg(program: CompoundProgram, result: PlaceResult, margin_ft: float = DRAFT_MARGIN_FT) -> str:
    """Build a composed draft SVG (feet -> px). Not a final map - the GM refines it.

    The parchment margin is the checklist's ~15-25 px (7 ft = 21 px; `viewbox_cropped` holds every
    sheet to it, the drafts included since feature 254); the top adds the title band and the scale bar. The compound is
    drawn at the envelope its buildings were placed in (`PlaceResult.envelope`, feature 287 H29a).

    Research:
        its drawn sizes - CONVENTION: sizes on the sheet, not in the world - 8 (posts caption font); 20 (title font; title 9 ft above the precinct); 11 (zone caption font); 9 (title font; title 9 ft above the precinct); 12 (scale bar 12 ft above the precinct); 0.8 (rack stroke); 0.6 (mat stroke); 5 (scale bar mid tick, end ticks); 45 (scale note label); 16 (scale bar label); 27 (scale note label); 6 (scale bar's obstacle box); 92 (scale bar's obstacle box); 30 (scale bar's obstacle box); 1.4 (post marker's obstacle box (0165: "a small marker")); 0.7 (post marker's obstacle box (0165: "a small marker"))
        its salts, guards and sentinels - NONE: they decide nothing about the place - 11.4 (caption box round both posts (their places ±0.7)); 14.4 (caption box round both posts (their places ±0.7)); 5.7 (caption box round both posts (their places ±0.7)); 13.3 (caption box round both posts (their places ±0.7)); 0.25 (text box descent/ascent per font size)
        its figures of ours - GUESS: searched, the record silent (feature 417 T38, 2026-10-25) - 14 (posts' places on the ground (±5 ft across, 14 and 27 ft in))
        its weapon rack - research/questions/0165-martial-training-grounds-and-dojo.drawing.html: 8 (rack 8 ft long); 2 (rack 2 ft deep), centered on the practice ground's south edge
        its striking posts - GUESS research/questions/0165-martial-training-grounds-and-dojo.drawing.html: 2 (two striking posts)
    """
    if result.envelope is not None and result.envelope != program.envelope:
        program = replace(program, envelope=result.envelope)
    env = program.envelope
    ox = margin_ft * FTPX
    oy = (margin_ft + 8.0) * FTPX
    iw, ih = env.w_ft * FTPX, env.h_ft * FTPX
    cw, ch = iw + 2 * ox, ih + oy + margin_ft * FTPX

    # EVERY CAPTION IS SEATED BY THE ONE PLACER (feature 266), after everything it could land on is drawn: `rect` records
    # each drawn feature as an obstacle (the courts are free ground), `caption` records a request by SUBJECT, and the
    # requests are placed and written last, in order, each an obstacle to the next.
    obstacles: list[Obstacle] = []
    requests: list[tuple[str, Subject, float, bool, str, str]] = []
    # THE DECLARATIONS (feature 340, plan D1): every visible rect carries a `data-id`, and each caption's `data-names` lists
    # the drawn shapes it names, the hand sheets' form - so `labels.hand_sheet` reads the draft as it reads a hand sheet.
    # Additive: the composer still seats each caption by its own subject.
    drawn: list[tuple[tuple[float, float, float, float], str]] = []
    declared: list[str] = []

    def px(x: float, y: float) -> tuple[float, float]:
        return ox + x * FTPX, oy + y * FTPX

    def box(x: float, y: float, w: float, h: float) -> tuple[tuple[float, float], ...]:
        (x0, y0), (x1, y1) = px(x, y), px(x + w, y + h)
        return ((x0, y0), (x1, y0), (x1, y1), (x0, y1))

    def rect(x: float, y: float, w: float, h: float, fill: str, stroke: str, sw: float, ident: str = "", kind: str = "", part_of: str = "") -> str:
        tag = f' id="{ident}"' if ident else ""
        if kind not in _GROUND_KINDS:
            obstacles.append(Obstacle(box(x, y, w, h), WEIGHT_OBSTACLE))
        whole = f' data-part-of="{part_of}"' if part_of else ""
        sid = ""
        if fill != "none" or stroke != "none":  # a visible rect: a shape a caption may name (an invisible stand-in never is)
            sid = f' data-id="d{len(drawn)}"'
            drawn.append(((round(x, 3), round(y, 3), round(w, 3), round(h, 3)), f"d{len(drawn)}"))
        px0, py0, px1, py1 = _px_edges(ox, oy, x, y, w, h)
        return f'<rect x="{px0}" y="{py0}" width="{px1 - px0}" height="{py1 - py0}" fill="{fill}"{tag} stroke="{stroke}" stroke-width="{sw}"{_kind_attr(kind)}{whole}{sid}/>'

    def caption(
        where: str,
        x: float,
        y: float,
        w: float,
        h: float,
        s: str,
        size: int,
        italic: bool,
        fill: str,
        kind: str = "",
        names: tuple[str, ...] | None = None,
        of: tuple[float, float, float, float] | None = None,
    ) -> str:
        """Ask the placer for a caption naming the feature at (x, y, w, h) in feet - `where` "area" (the name lies
        inside it) or "point" (the name stands beside it). Drawn at the end; returns nothing to splice now. Its declaration
        (feature 340): `names` when given, else every drawn rect at `of` (the subject's own box when `of` is None)."""
        requests.append((s, Subject(where, box(x, y, w, h)), float(size), italic, fill, kind))
        at = tuple(round(v, 3) for v in (of or (x, y, w, h)))
        declared.append(" ".join(names if names is not None else [sid for b, sid in drawn if b == at]))
        return ""

    def plain(cx: float, cy: float, s: str, size: int, italic: bool, fill: str) -> str:
        """The title and the draft note: no feature to name, so not captions (FR-001) - written where they stand,
        and obstacles to every caption."""
        st = ' font-style="italic"' if italic else ' font-weight="bold"'
        hw = len(s) * size * CHAR_W_EM / 2
        x, y = px(cx, cy)
        obstacles.append(Obstacle(((x - hw, y - size * 0.8), (x + hw, y - size * 0.8), (x + hw, y + size * 0.25), (x - hw, y + size * 0.25)), WEIGHT_OBSTACLE))
        return f'<text x="{x:.0f}" y="{y:.0f}" text-anchor="middle" font-size="{size}"{st} fill="{fill}" data-kind="-">{s}</text>'

    for p in result.placed:
        if not p.spec.feature:
            raise ValueError(f"{p.spec.name}: a building declares its Mode A kind (`feature=`) so the draft's page can say what it is (feature 262)")

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {cw:.0f} {ch:.0f}" font-family="Georgia, \'Times New Roman\', serif">',
        _DEFS,
        f'<rect x="0" y="0" width="{cw:.0f}" height="{ch:.0f}" fill="#EFE3C2" data-kind="-"/>',
        # the declared precinct (feature 254), one rect per court so the page can light each court's ground
        # (feature 262); both keep the id, and they abut at the divider - which renders as the one rect did
        rect(0, 0, env.w_ft, env.divider_ft, "url(#court-earth)", "none", 0, "precinct", "inner court"),
        rect(0, env.divider_ft, env.w_ft, env.h_ft - env.divider_ft, "url(#court-earth)", "none", 0, "precinct", "outer court"),
        plain(env.w_ft / 2, -9, program.title, 20, False, "#3A2E1C"),
        plain(env.w_ft / 2, -3, "(perimeter-first composed draft - refine by hand)", 10, True, "#6B4F2A"),
    ]
    for z in program.spine:  # reserved open courts, drawn + named
        zk = ZONE_KINDS.get(z.name, "outer court" if z.y_ft >= env.divider_ft else "inner court")
        zstroke, zsw = ("none", 0.0) if z.name in UNFENCED_ZONES else ROOFED_ZONES.get(z.name, ("#9C7A40", 0.8))
        parts.append(rect(z.x_ft, z.y_ft, z.w_ft, z.h_ft, COURT_FILL.get(z.name, "url(#court-earth)"), zstroke, zsw, "", zk))
        caption("area", z.x_ft, z.y_ft, z.w_ft, z.h_ft, ZONE_CAPTIONS.get(z.name, z.name), 11, True, "#5C4318", zk)
        if z.name in ROOFED_ZONES:
            # the straw mats the parties knelt on (`_mats`), a part of the court, then their caption - the one other
            # caption under the roof; the court's floor joins the obstacles once both are seated
            parts.append(f'<g{_kind_attr("kneeling positions")}><g fill="#C8B078" stroke="#7A5430" stroke-width="0.6">')
            mats = _mats(z)
            first = len(drawn)
            parts += [rect(mx, my, mx2 - mx, my2 - my, "#C8B078", "#7A5430", 0.6) for mx, my, mx2, my2 in mats]
            parts.append("</g></g>")
            ax, ay, ax2, ay2 = mats[-1]
            # it names EVERY mat, as a hand sheet's caption names its group (plan review round 1); the composer seats it by the last
            caption("point", ax, ay, ax2 - ax, ay2 - ay, "straw mats", 8, True, "#7A5C30", "kneeling positions", names=tuple(sid for _b, sid in drawn[first:]))
            # the posts carrying the roof along the open (south) side, the court's own ink (ROOFED_ZONES)
            # its solid outline is a building's edge, so no caption crosses it (the ground inside stays free)
            corners = [px(z.x_ft, z.y_ft), px(z.x2, z.y_ft), px(z.x2, z.y2), px(z.x_ft, z.y2)]
            obstacles.extend(Obstacle(tuple(stroke_band(corners[i], corners[(i + 1) % 4], zsw / 2 + 1)), WEIGHT_OBSTACLE) for i in range(4))
            parts.append(f'<g fill="{zstroke}"{_kind_attr(zk)}>')
            for pxf, pyf in _roof_posts(z):
                obstacles.append(Obstacle(box(pxf, pyf, ROOF_POST_FT, ROOF_POST_FT), WEIGHT_OBSTACLE))
                parts.append(f'<rect x="{ox + pxf * FTPX:.0f}" y="{oy + pyf * FTPX:.0f}" width="{ROOF_POST_FT * FTPX:.0f}" height="{ROOF_POST_FT * FTPX:.0f}"/>')
            parts.append("</g>")
        if z.name == "practice ground":
            # The program item's durable equipment (docs/buildings.md "Practice ground"): a weapon
            # rack on the zone's south edge (the hand-refined map moves it flush to the
            # adjacent lodging's wall) and two tategi striking posts as r2 location markers. Each is a
            # PART of the ground (feature 264): its own kind, inside a group of the ground's, so it lights
            # as itself and with the ground.
            parts.append(f"<g{_kind_attr(zk)}>")
            parts.append(rect(z.x_ft + z.w_ft / 2 - 4, z.y2 - 2, 8, 2, "#8C6F3E", "#4A3318", 0.8, "", "weapon rack"))
            caption("point", z.x_ft + z.w_ft / 2 - 5.7, z.y_ft + 13.3, 11.4, 14.4, "striking posts", 8, True, "#5C4830", "striking posts", names=("post-0", "post-1"))
            for k, (dx_ft, dy_ft) in enumerate(((-5.0, 14.0), (5.0, 27.0))):
                cx, cy = z.x_ft + z.w_ft / 2 + dx_ft, z.y_ft + dy_ft
                obstacles.append(Obstacle(box(cx - 0.7, cy - 0.7, 1.4, 1.4), WEIGHT_OBSTACLE))
                parts.append(f'<circle cx="{ox + cx * FTPX:.0f}" cy="{oy + cy * FTPX:.0f}" r="2" fill="#7A5430" stroke="#4A3318" stroke-width="0.8"{_kind_attr("striking posts")} data-id="post-{k}"/>')
            parts.append("</g>")
    _draw_buildings(result, rect, caption, px, parts)
    parts += _point_features(program, result, rect, caption, ox, oy)
    # the scale bar every Mode A sheet carries (docs/buildings.md "Scale"; the registered check `scale_bar_present`)
    sx, sy = ox, oy - 12 * FTPX
    parts.append(
        f'<g stroke="#3A2E1C" data-kind="-"><line x1="{sx:.0f}" y1="{sy:.0f}" x2="{sx + 90:.0f}" y2="{sy:.0f}" stroke-width="2"/><line x1="{sx:.0f}" y1="{sy - 5:.0f}" x2="{sx:.0f}" y2="{sy + 5:.0f}" stroke-width="2"/><line x1="{sx + 90:.0f}" y1="{sy - 5:.0f}" x2="{sx + 90:.0f}" y2="{sy + 5:.0f}" stroke-width="2"/><line x1="{sx + 45:.0f}" y1="{sy - 3:.0f}" x2="{sx + 45:.0f}" y2="{sy + 3:.0f}" stroke-width="1"/></g>'
    )
    parts.append(f'<text x="{sx + 45:.0f}" y="{sy + 16:.0f}" text-anchor="middle" font-size="10" fill="#3A2E1C" data-kind="-">30 ft</text>')
    parts.append(f'<text x="{sx + 45:.0f}" y="{sy + 27:.0f}" text-anchor="middle" font-size="8" font-style="italic" fill="#5C4830" data-kind="-">(3 px = 1 ft)</text>')
    obstacles.append(Obstacle(((sx - 2, sy - 6), (sx + 92, sy - 6), (sx + 92, sy + 30), (sx - 2, sy + 30)), WEIGHT_OBSTACLE))  # the scale bar
    _draw_walls_and_gates(env, result, ox, oy, px, box, obstacles, parts)
    # A CAPTION MAY HOLD THE SHEET'S EDGE (the review checklist: every edge "held by real content"): the notice board
    # stands outside the gate, 21 px from the canvas's foot, where no caption fits beside it - the old draft's caption
    # hung past the edge and was clipped. So the placer is given room below, and the canvas then grows to hug what it
    # placed there.
    seated, foot = _seat_captions(requests, obstacles, (0.0, 0.0, cw, ch + CAPTION_ROOM), program.title, declared, one_view("\n".join([*parts, "</svg>"]), requests, declared))
    parts += seated
    if foot + margin_ft * FTPX > ch:
        grown = foot + margin_ft * FTPX
        parts[0] = parts[0].replace(f'viewBox="0 0 {cw:.0f} {ch:.0f}"', f'viewBox="0 0 {cw:.0f} {grown:.0f}"')
        parts[2] = parts[2].replace(f'height="{ch:.0f}"', f'height="{grown:.0f}"')
    parts.append("</svg>")
    return "\n".join(parts)


def _draw_buildings(result: PlaceResult, rect: Callable[..., str], caption: Callable[..., str], px: Callable[[float, float], tuple[float, float]], parts: list[str]) -> None:
    """Draw every placed building - its fill, its rooms, veranda and dais, its outline and its name - into `parts`, through
    `emit_svg`'s own `rect` and `caption` (lifted out of it by feature 370, the 100-statement cap; the same order, so the
    same SVG and the same caption requests).

    Research:
        its drawn sizes - CONVENTION: sizes on the sheet, not in the world - 8 (dais caption font); 5 (name goes in a rear alley at least 5 ft wide); 6 (name fit margin, smaller font); 1.2 (veranda stroke); 7 (clerk caption font); 0.9 ("every room named" test for where the name goes); 0.25 (stable passage fill inset); 0.8 (stall stroke)
    """
    ox, oy = px(0.0, 0.0)
    for p in result.placed:  # buildings
        fill, stroke = KINDS.get(p.spec.kind, KINDS["service"])
        # a name that runs wider than its building at 10 px is written at 8 (the gatehouse's overran its 54 px box), measured
        # at BOLD_CHAR_W_EM - a building's name is bold, and bold mixed case runs wider than the standard's em (pass 6: the
        # retainers' 26-letter name, judged to fit, ran over the wall's ink)
        size = 10 if len(p.spec.name) * 10 * BOLD_CHAR_W_EM <= p.spec.w_ft * FTPX - 6 else 8
        if p.spec.kind == "cell":
            # a cell reads by its lattice front: short bars across its court face, clear of its name (the two end lines
            # it had bracketed the caption)
            parts += [f"<g{_kind_attr(p.spec.feature)}>", rect(p.x_ft, p.y_ft, p.spec.w_ft, p.spec.h_ft, fill, stroke, 2)]
            parts += [f'<line x1="{ox + a * FTPX:.0f}" y1="{oy + b * FTPX:.0f}" x2="{ox + c * FTPX:.0f}" y2="{oy + d * FTPX:.0f}" stroke="#3A2010" stroke-width="0.8"/>' for a, b, c, d in _lattice(p)]
            parts.append("</g>")
            caption("area", p.x_ft, p.y_ft, p.spec.w_ft, p.spec.h_ft, p.spec.name, size, False, "#3A2E1C", p.spec.feature)
            continue
        if p.spec.kind == "takakura":
            # 0098's raised timber storehouse on its posts, as the hand sheets draw one: the slatted body and a post at each
            # corner, the posts their own kind (feature 374 wave 128)
            parts += [f"<g{_kind_attr(p.spec.feature)}>", rect(p.x_ft, p.y_ft, p.spec.w_ft, p.spec.h_ft, fill, stroke, 2)]
            parts += ["<g" + _kind_attr("granary stilts") + ">", *(rect(x, y, STILT_FT, STILT_FT, "#4A3318", "none", 0) for x, y in _stilts(p)), "</g>", "</g>"]
            caption("area", p.x_ft, p.y_ft, p.spec.w_ft, p.spec.h_ft, p.spec.name, size, False, "#3A2E1C", p.spec.feature)
            continue
        if p.spec.feature == "stables":
            # the stable as every sheet draws it (feature 374 wave 126, 0108): the earth passage, the grooms' room, the stalls
            (ax, ay, ax2, ay2), walls = _stable_parts(p)
            parts += [f"<g{_kind_attr(p.spec.feature)}>", rect(p.x_ft, p.y_ft, p.spec.w_ft, p.spec.h_ft, fill, stroke, 2)]
            parts.append(rect(ax + 0.25, ay + 0.25, ax2 - ax - 0.5, ay2 - ay - 0.5, "#B8A07A", "none", 0))
            parts += [
                f'<line x1="{ox + a * FTPX:.0f}" y1="{oy + b * FTPX:.0f}" x2="{ox + c * FTPX:.0f}" y2="{oy + d * FTPX:.0f}" stroke="{stroke}" stroke-width="{0.8 if dash else 1}"{' stroke-dasharray="3 2"' if dash else ""}/>'
                for a, b, c, d, dash in walls
            ]
            parts.append("</g>")
            caption("area", p.x_ft, p.y_ft, p.spec.w_ft, p.spec.h_ft, p.spec.name, size, False, "#3A2E1C", p.spec.feature)
            continue
        if not (p.spec.rooms or p.spec.engawa_ft or p.spec.dais[0]):
            walls = _bay_walls(p, px, stroke)  # inside a group of the building's kind, so the page tags its walls
            parts += [f"<g{_kind_attr(p.spec.feature)}>"] if walls else []
            parts.append(rect(p.x_ft, p.y_ft, p.spec.w_ft, p.spec.h_ft, fill, stroke, 2, "", p.spec.feature))
            parts += [*walls, "</g>"] if walls else []
            caption("area", p.x_ft, p.y_ft, p.spec.w_ft, p.spec.h_ft, p.spec.name, size, False, "#3A2E1C", p.spec.feature)
            continue
        # a building with parts (rooms, a veranda, a dais): its fill, a same-color floor per room, partitions, the
        # outline on top - all inside a group of the building's kind, the hand sheets' form (feature 264)
        parts.append(f"<g{_kind_attr(p.spec.feature)}>")
        parts.append(rect(p.x_ft, p.y_ft, p.spec.w_ft, p.spec.h_ft, fill, "none", 0, "", p.spec.feature))
        for rkind, rx, ry, rw, rh in p.spec.rooms:
            parts.append(rect(p.x_ft + rx, p.y_ft + ry, rw, rh, fill, "none", 0, "", rkind))
            caption("area", p.x_ft + rx, p.y_ft + ry, rw, rh, ROOM_CAPTIONS.get(rkind, rkind), 8, False, "#3A2E1C", rkind)
            (x0, y0), (x1, y1) = px(p.x_ft + rx, p.y_ft + ry), px(p.x_ft + rx + rw, p.y_ft + ry + rh)
            parts.append(f'<rect x="{x0:.0f}" y="{y0:.0f}" width="{x1 - x0:.0f}" height="{y1 - y0:.0f}" fill="none" stroke="{stroke}" stroke-width="0.8" stroke-dasharray="4 3"/>')
        if p.spec.engawa_ft:  # the veranda, a lighter strip along the court face under the building's outline (R01)
            ex, ey, ex2, ey2 = _engawa(p)
            parts.append(rect(ex, ey, ex2 - ex, ey2 - ey, KINDS["plain"][0], stroke, 1.2, "", "engawa"))
        if p.spec.dais[0]:  # the magistrate's dais, dark tatami on the court face (docs/buildings.md "Office hall")
            dx, dy, dx2, dy2 = _dais(p)
            parts.append(rect(dx, dy, dx2 - dx, dy2 - dy, "#8C6F3E", "#4A3318", 1, "", "magistrate's dais"))
            caption("area", dx, dy, dx2 - dx, dy2 - dy, "magistrate's dais", 8, False, "#FFFAE6", "magistrate's dais")
        parts += _bay_walls(p, px, stroke)
        parts.append(rect(p.x_ft, p.y_ft, p.spec.w_ft, p.spec.h_ft, "none", stroke, 2))
        if p.spec.dais[0]:  # the clerks' positions flanking the dais, drawn over the outline so it buries neither
            dx, dy, dx2, dy2 = _dais(p)
            parts.append("<g" + _kind_attr("clerks' seats") + ">")
            for sx0, sy0, sx1, sy1 in _clerk_seats((dx, dy, dx2, dy2), _court_side(p)):
                parts.append(rect(sx0, sy0, sx1 - sx0, sy1 - sy0, "#B89868", "#5C4830", 0.5))
                caption("area", sx0, sy0, sx1 - sx0, sy1 - sy0, "clerk", 7, False, "#3A2E1C", "clerks' seats")
            parts.append("</g>")
        parts.append("</g>")
        # the block's own name after its rooms', and BESIDE the block where every room is named: inside, it sat within
        # one room beside that room's name and read as a room (the residence's, building-review round 3)
        # - in its rear alley where it stands off its wall (`inset_ft`), which reads as the block's own ground
        full = sum(r[3] * r[4] for r in p.spec.rooms) >= 0.9 * p.spec.w_ft * (p.spec.h_ft - p.spec.engawa_ft)
        if full and p.spec.inset_ft >= 5.0:
            ax, ay, aw, ah = _rear_band(p)
            caption("area", ax, ay, aw, ah, p.spec.name, size, False, "#3A2E1C", p.spec.feature, of=(p.x_ft, p.y_ft, p.spec.w_ft, p.spec.h_ft))  # declared: the block
        else:
            caption("point" if full else "area", p.x_ft, p.y_ft, p.spec.w_ft, p.spec.h_ft, p.spec.name, size, False, "#3A2E1C", p.spec.feature)


STILT_FT = 8.0 / 3.0  # a takakura's corner post, the hand sheets' 8 px square: a MAP DRAWING CONVENTION (a real post ~1 ft)


def _stilts(p: Placed) -> list[tuple[float, float]]:
    """The four corner posts of a raised storehouse, each STILT_FT square inside its corners."""
    return [(x, y) for x in (p.x_ft, p.x2 - STILT_FT) for y in (p.y_ft, p.y2 - STILT_FT)]


def _bay_walls(p: Placed, px: Callable[[float, float], tuple[float, float]], stroke: str) -> list[str]:
    """The walls between a rowhouse's dwellings (`BuildingSpec.bays`), solid across its depth at each offset along its
    long side."""
    out: list[str] = []
    for off in p.spec.bays:
        a, b = ((p.x_ft + off, p.y_ft), (p.x_ft + off, p.y2)) if p.spec.w_ft >= p.spec.h_ft else ((p.x_ft, p.y_ft + off), (p.x2, p.y_ft + off))
        (x1, y1), (x2, y2) = px(*a), px(*b)
        out.append(f'<line x1="{x1:.0f}" y1="{y1:.0f}" x2="{x2:.0f}" y2="{y2:.0f}" stroke="{stroke}" stroke-width="1"/>')
    return out


def _draw_walls_and_gates(
    env: Envelope,
    result: PlaceResult,
    ox: float,
    oy: float,
    px: Callable[[float, float], tuple[float, float]],
    box: Callable[[float, float, float, float], tuple[tuple[float, float], ...]],
    obstacles: list[Obstacle],
    parts: list[str],
) -> None:
    """Draw the compound wall, the court divider and every gate's posts into `parts`, each an obstacle to the captions
    (lifted out of `emit_svg` by feature 370, the 100-statement cap; the same order, so the same SVG).

    Research:
        its drawn sizes - CONVENTION: sizes on the sheet, not in the world - 4.5 (half the 9 px wall stroke (WALL_INK_FT, 0092))
        its wall widths - research/questions/0090-magistrates-compounds-jinya-and-yamen.drawing.html: 9 (compound wall drawn 3 ft)
        its figures against 0090 - research/questions/0090-magistrates-compounds-jinya-and-yamen.drawing.html: 6 (the wall between the two courts drawn 2 ft, where the page's walls are 3 ft thick) - a departure the code keeps until feature 417 T33
    """
    # compound wall (4 segments; S wall broken by the gate) + divider - each in a `<g stroke=...>` group,
    # the authoring form the audit's gate-opening and divider readers parse (feature 254: the drafts are
    # swept by the gate like the hand-drawn sheets, so they are drawn the way the checks read)
    # the compound wall, broken where the main gate and the postern pass through it (`_wall_runs`), and the divider
    # broken at the middle gate - each in a `<g stroke=...>` group, the authoring form the audit's gate-opening and
    # divider readers parse (feature 254: the drafts are swept by the gate like the hand-drawn sheets, so they are
    # drawn the way the checks read). The gates' posts follow, each gate a group of its kind (feature 267).
    parts.append('<g stroke="#2D2A24" stroke-width="9" data-kind="compound wall">')
    for _side, x1, y1, x2, y2 in _wall_runs(env):
        lx1, ly1, lx2, ly2 = _px_edges(ox, oy, x1, y1, x2 - x1, y2 - y1)  # half up, as every box's edge (wave 132: a 7 ft gate lost a pixel)
        parts.append(f'<line x1="{lx1}" y1="{ly1}" x2="{lx2}" y2="{ly2}"/>')
        obstacles.append(Obstacle(tuple(stroke_band(px(x1, y1), px(x2, y2), 4.5)), WEIGHT_OBSTACLE))  # the wall, 9 px drawn
    parts.append("</g>")
    gates = [("main gate", "S", *_gate_interval(env), env.h_ft, GATE_POST_D_FT, "#2D2A24", "")]
    for side, at, w in env.posterns:
        gates.append(("side gate", side, at - w / 2, at + w / 2, {"N": 0.0, "W": 0.0, "E": env.w_ft}.get(side, env.h_ft), GATE_POST_D_FT, "#2D2A24", ""))
    mid = _middle_gate(env, result.placed)
    runs = [(0.0, env.w_ft)] if mid is None else [(0.0, mid[0]), (mid[1], env.w_ft)]
    if mid is not None:
        gates.append(("nakamon", "divider", mid[0], mid[1], env.divider_ft, NAKAMON_POST_D_FT, "#3F3A30", ' data-part-of="court divider"'))
    parts.append('<g stroke="#3F3A30" stroke-width="6" data-kind="court divider">')
    for a, b in runs:
        dx1, dy1, dx2, _dy2 = _px_edges(ox, oy, a, env.divider_ft, b - a, 0.0)
        parts.append(f'<line x1="{dx1}" y1="{dy1}" x2="{dx2}" y2="{dy1}"/>')
        obstacles.append(Obstacle(tuple(stroke_band(px(a, env.divider_ft), px(b, env.divider_ft), 3.0)), WEIGHT_OBSTACLE))
    parts.append("</g>")
    for gkind, side, lo, hi, line, deep, ink, whole in gates:
        parts.append(f'<g fill="{ink}"{_kind_attr(gkind)}{whole}>')
        for bx, by, bx2, by2 in _gate_posts(side, lo, hi, line, GATE_POST_W_FT, deep):
            obstacles.append(Obstacle(box(bx, by, bx2 - bx, by2 - by), WEIGHT_OBSTACLE))
            gx0, gy0, gx1, gy1 = _px_edges(ox, oy, bx, by, bx2 - bx, by2 - by)
            parts.append(f'<rect x="{gx0}" y="{gy0}" width="{gx1 - gx0}" height="{gy1 - gy0}"/>')
        parts.append("</g>")


# ---- a built-in county-magistracy program: `compound_example.py` (feature 374 wave 125) ---------------
from .compound_example import _EXAMPLE_TIER, county_magistracy_program  # noqa: E402,F401 - re-exported: the pool generator and the tests call `compound.county_magistracy_program`


def main(argv: list[str] | None = None) -> int:
    args = sys.argv[1:] if argv is None else argv
    out = args[0] if args else os.path.join("pool", _EXAMPLE_TIER, "county-magistracy-example", "county-magistracy-example.svg")
    program = county_magistracy_program()
    result = place(program)
    svg = emit_svg(program, result)  # composed BEFORE the file is opened: a refused program leaves no emptied draft behind
    with open(out, "w", encoding="utf-8") as fh:
        fh.write(svg)
    print(f"wrote {out}: {len(result.placed)} buildings placed")  # `place` refuses a program that overflows (feature 287)
    return 0


if __name__ == "__main__":
    from l7r.diagram._invocation import guard

    # REFUSE unless invoked through this project's make (feature 127). At the TOP of the
    # entry point, never in a loop - the determination reads /proc and is cached per process.
    guard("l7r.diagram.compound")
    raise SystemExit(main())
