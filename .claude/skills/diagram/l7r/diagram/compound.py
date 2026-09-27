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

See buildings.md "Composition: perimeter buildings + a named court-spine". The program's types and units live in
`compound_model.py`, what is seated around the placed masses (tubs, wells, doors, gates' posts, the roji) in
`compound_parts.py` (feature 267 split them out); the pool generators still import this module alone.

CLI:  python3 compound.py            # place the built-in county magistracy, write a draft SVG
"""

from __future__ import annotations

import os
import sys

from .buildings.types import load_types
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
from .compound_parts import _clerk_seats, _court_side, _dais, _engawa, _gate_posts, _lattice, _mats, _middle_gate, _point_features, _rear_band, _roof_posts, _wall_runs
from .labels import Obstacle, ObstacleIndex, Subject
from .labels import place as place_caption
from .labels.standard import CHAR_W_EM, WEIGHT_OBSTACLE
from .labels.svg import caption_svg, leader_svg

# The built-in example's pool tier: the type that declares the example as its generated exception
# (feature 254) - the folder is the declaration's to name, not this module's.
_EXAMPLE_TIER: str = next(t.tier for t in load_types() if "county-magistracy-example" in t.generated_exceptions)

# ---- placement (perimeter-first, 2-D collision) ------------------------------------------
#
# Buildings are placed in a single global priority order (rank 1 before rank 2, then highest
# `order`, then largest). Each building hugs its wall and slides ALONG that wall past every
# obstacle it overlaps - the spine courts, the south gate, AND every building already placed.
# So a contested corner goes to whichever building is placed first (highest order), and a
# short E/W building no longer blocks the whole corner it does not actually occupy: the crude
# per-court corner reservation the old placer used is gone, replaced by real rectangle overlap.
# A rank-2 building sits BEHIND the rank-1 row on its wall (a rear service strip / second rank),
# which is how real residences ranked servants behind the family wing.


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
    """Ground a hugging building must leave for the wall's own INK: half the wall's thickness,
    because the wall is drawn centered on the boundary, plus a hair for its own outline (see
    WALL_INK_FT / OUTLINE_CLEAR_FT). 2 ft off a compound wall, 1.5 ft off a court divider."""
    return (DIVIDER_INK_FT if wall == "divider" else WALL_INK_FT) / 2 + OUTLINE_CLEAR_FT


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
        if _rect_overlap(px, py, spec.w_ft, spec.h_ft, p.x_ft, p.y_ft, p.spec.w_ft, p.spec.h_ft):
            ends.append(p.x2 if horizontal else p.y2)
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
        cursor = end + FIRE_GAP_FT
    if cursor + size > along_end - WALL_MARGIN_FT:
        return None
    px, py = (cursor, cross) if horizontal else (cross, cursor)
    return Placed(spec, px, py)


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
    flow around them instead of blocking a whole corner they do not occupy."""
    result = PlaceResult()
    env = program.envelope
    for spec in sorted(program.buildings, key=lambda s: (s.rank, _wall_tier(s.wall), -s.order, -(s.w_ft * s.h_ft))):
        placed = _place_one(env, spec, program.spine, result.placed)
        if placed is None:
            result.overflow.append(spec)
        else:
            result.placed.append(placed)
    return result


# ---- SVG emit (feet -> px at FTPX; a composed DRAFT the GM refines) -----------------------

#: The Mode A kind of each reserved court zone (feature 262) - what its ground lights as on the page.
ZONE_KINDS: dict[str, str] = {
    "forecourt": "outer court",
    "oshirasu": "hearing court",
    "garden": "garden",
    "yard": "outer court",
    "cart yard": "cart yard",
    "practice ground": "practice ground",
}
#: Zones drawn as bare ground, with no edge: an outlined sub-rectangle of court reads as a FENCED court, and a fenced
#: forecourt is a GUESS the record does not support (research buildings 300; building-review round 3).
UNFENCED_ZONES: frozenset[str] = frozenset({"forecourt", "yard", "cart yard"})
#: A zone's caption where its program name is not the reader's word: the hearing court is `oshirasu` in the program (and
#: in its fill pattern) but the sheets caption it in English (the other drafts and the hand sheets say `hearing court`).
ZONE_CAPTIONS: dict[str, str] = {"oshirasu": "hearing court", "yard": "outer court"}


_GROUND_KINDS = frozenset({*ZONE_KINDS.values(), "inner court", "outer court", "practice ground", "garden", "-"})
"""The kinds a draft draws as open ground - the courts and the zones - which are free space to a caption (feature 266,
FR-006: ground weighs 0). Everything else it draws is an obstacle."""


def stroke_band(a: tuple[float, float], b: tuple[float, float], half: float) -> list[tuple[float, float]]:
    """A stroked line's drawn band as a quad - a 9 px wall is 9 px wide to a caption, not a hairline."""
    dx, dy = b[0] - a[0], b[1] - a[1]
    n = (dx * dx + dy * dy) ** 0.5 or 1.0
    nx, ny = -dy / n * half, dx / n * half
    return [(a[0] + nx, a[1] + ny), (b[0] + nx, b[1] + ny), (b[0] - nx, b[1] - ny), (a[0] - nx, a[1] - ny)]


CAPTION_ROOM = 40.0
"""How far below the drawn canvas a draft's caption may stand, in px (feature 266): room for one caption line beside
the notice board outside the gate. The canvas grows to hug whatever is placed there."""


def _seat_captions(
    requests: list[tuple[str, Subject, float, bool, str, str]], obstacles: list[Obstacle], frame: tuple[float, float, float, float], late: dict[int, list[Obstacle]] | None = None
) -> tuple[list[str], float]:
    """Place every requested caption by the ONE placer (feature 266), in order, each an obstacle to the next, and write
    it - with its leader when the standard gives it one (FR-005). `late[i]` are obstacles that join the index once
    caption i is seated: ground only that caption may stand on (a roofed court's floor is its own caption's, and no
    other caption stands under its roof). Returns the strings and the lowest point drawn."""
    index = ObstacleIndex(obstacles)
    out: list[str] = []
    foot = 0.0
    for i, (text, subject, size, italic, fill, kind) in enumerate(requests):
        p = place_caption(text, size, subject, index, frame)
        out.append(caption_svg(p, size, ' font-style="italic"' if italic else ' font-weight="bold"', fill, kind))
        if p.leader is not None:
            out.append(leader_svg(p, size, fill, kind))
        index.add(Obstacle(p.block, WEIGHT_OBSTACLE))
        for ob in (late or {}).get(i, []):
            index.add(ob)
        foot = max(foot, *(q[1] for q in p.block))
    return out, foot


_DEFS = (
    '<defs>'
    '<pattern id="court-earth" patternUnits="userSpaceOnUse" width="16" height="16">'
    '<rect width="16" height="16" fill="#D9C28E"/><circle cx="4" cy="6" r="0.6" fill="#A88E58"/>'
    '<circle cx="12" cy="2" r="0.6" fill="#A88E58"/></pattern>'
    '<pattern id="oshirasu-sand" patternUnits="userSpaceOnUse" width="12" height="12">'
    '<rect width="12" height="12" fill="#F2EAD0"/><circle cx="3" cy="4" r="0.5" fill="#C9B884"/>'
    '<circle cx="8" cy="2" r="0.5" fill="#C9B884"/></pattern>'
    '<pattern id="garden-stipple" patternUnits="userSpaceOnUse" width="14" height="14">'
    '<rect width="14" height="14" fill="#BFCFA0"/><circle cx="3" cy="3" r="0.8" fill="#7A8C5C"/>'
    '<circle cx="10" cy="9" r="0.8" fill="#7A8C5C"/></pattern>'
    '<pattern id="keiko-earth" patternUnits="userSpaceOnUse" width="16" height="16">'
    '<rect width="16" height="16" fill="#E2CE9E"/><line x1="0" y1="5" x2="16" y2="5" stroke="#C2A46C" stroke-width="0.5"/>'
    '<line x1="0" y1="13" x2="16" y2="13" stroke="#C2A46C" stroke-width="0.5"/></pattern></defs>'
)


def emit_svg(program: CompoundProgram, result: PlaceResult, margin_ft: float = 7.0) -> str:
    """Build a composed draft SVG (feet -> px). Not a final map - the GM refines it.

    The parchment margin is the checklist's ~15-25 px (7 ft = 21 px; `viewbox_cropped` holds every
    sheet to it, the drafts included since feature 254); the top adds the title band and the scale bar."""
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
    late: dict[int, list[Obstacle]] = {}

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
        return (
            f'<rect x="{ox + x * FTPX:.0f}" y="{oy + y * FTPX:.0f}" width="{w * FTPX:.0f}" height="{h * FTPX:.0f}" fill="{fill}"{tag} stroke="{stroke}" stroke-width="{sw}"{_kind_attr(kind)}{whole}/>'
        )

    def caption(where: str, x: float, y: float, w: float, h: float, s: str, size: int, italic: bool, fill: str, kind: str = "") -> str:
        """Ask the placer for a caption naming the feature at (x, y, w, h) in feet - `where` "area" (the name lies
        inside it) or "point" (the name stands beside it). Drawn at the end; returns nothing to splice now."""
        requests.append((s, Subject(where, box(x, y, w, h)), float(size), italic, fill, kind))
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
            parts += [rect(mx, my, mx2 - mx, my2 - my, "#C8B078", "#7A5430", 0.6) for mx, my, mx2, my2 in mats]
            parts.append("</g></g>")
            ax, ay, ax2, ay2 = mats[-1]
            caption("point", ax, ay, ax2 - ax, ay2 - ay, "straw mats", 8, True, "#7A5C30", "kneeling positions")
            late[len(requests) - 1] = [Obstacle(box(z.x_ft, z.y_ft, z.w_ft, z.h_ft), WEIGHT_OBSTACLE)]
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
            # The program item's durable equipment (buildings.md "Practice ground"): a weapon
            # rack on the zone's south edge (the hand-refined map moves it flush to the
            # adjacent lodging's wall) and two tategi striking posts as r2 location markers. Each is a
            # PART of the ground (feature 264): its own kind, inside a group of the ground's, so it lights
            # as itself and with the ground.
            parts.append(f"<g{_kind_attr(zk)}>")
            parts.append(rect(z.x_ft + z.w_ft / 2 - 4, z.y2 - 2, 8, 2, "#8C6F3E", "#4A3318", 0.8, "", "weapon rack"))
            caption("point", z.x_ft + z.w_ft / 2 - 5.7, z.y_ft + 13.3, 11.4, 14.4, "striking posts", 8, True, "#5C4830", "striking posts")
            for dx_ft, dy_ft in ((-5.0, 14.0), (5.0, 27.0)):
                cx, cy = z.x_ft + z.w_ft / 2 + dx_ft, z.y_ft + dy_ft
                obstacles.append(Obstacle(box(cx - 0.7, cy - 0.7, 1.4, 1.4), WEIGHT_OBSTACLE))
                parts.append(f'<circle cx="{ox + cx * FTPX:.0f}" cy="{oy + cy * FTPX:.0f}" r="2" fill="#7A5430" stroke="#4A3318" stroke-width="0.8"{_kind_attr("striking posts")}/>')
            parts.append("</g>")
    for p in result.placed:  # buildings
        fill, stroke = KINDS.get(p.spec.kind, KINDS["service"])
        # a name that runs wider than its building at 10 px is written at 8 (the gatehouse's overran its 54 px box)
        size = 10 if len(p.spec.name) * 10 * CHAR_W_EM <= p.spec.w_ft * FTPX - 6 else 8
        if p.spec.kind == "cell":
            # a cell reads by its lattice front: short bars across its court face, clear of its name (the two end lines
            # it had bracketed the caption)
            parts += [f"<g{_kind_attr(p.spec.feature)}>", rect(p.x_ft, p.y_ft, p.spec.w_ft, p.spec.h_ft, fill, stroke, 2)]
            parts += [f'<line x1="{ox + a * FTPX:.0f}" y1="{oy + b * FTPX:.0f}" x2="{ox + c * FTPX:.0f}" y2="{oy + d * FTPX:.0f}" stroke="#3A2010" stroke-width="0.8"/>' for a, b, c, d in _lattice(p)]
            parts.append("</g>")
            caption("area", p.x_ft, p.y_ft, p.spec.w_ft, p.spec.h_ft, p.spec.name, size, False, "#3A2E1C", p.spec.feature)
            continue
        if not (p.spec.rooms or p.spec.engawa_ft or p.spec.dais[0]):
            parts.append(rect(p.x_ft, p.y_ft, p.spec.w_ft, p.spec.h_ft, fill, stroke, 2, "", p.spec.feature))
            caption("area", p.x_ft, p.y_ft, p.spec.w_ft, p.spec.h_ft, p.spec.name, size, False, "#3A2E1C", p.spec.feature)
            continue
        # a building with parts (rooms, a veranda, a dais): its fill, a same-color floor per room, partitions, the
        # outline on top - all inside a group of the building's kind, the hand sheets' form (feature 264)
        parts.append(f"<g{_kind_attr(p.spec.feature)}>")
        parts.append(rect(p.x_ft, p.y_ft, p.spec.w_ft, p.spec.h_ft, fill, "none", 0, "", p.spec.feature))
        for rkind, rx, ry, rw, rh in p.spec.rooms:
            parts.append(rect(p.x_ft + rx, p.y_ft + ry, rw, rh, fill, "none", 0, "", rkind))
            caption("area", p.x_ft + rx, p.y_ft + ry, rw, rh, rkind, 8, False, "#3A2E1C", rkind)
            (x0, y0), (x1, y1) = px(p.x_ft + rx, p.y_ft + ry), px(p.x_ft + rx + rw, p.y_ft + ry + rh)
            parts.append(f'<rect x="{x0:.0f}" y="{y0:.0f}" width="{x1 - x0:.0f}" height="{y1 - y0:.0f}" fill="none" stroke="{stroke}" stroke-width="0.8" stroke-dasharray="4 3"/>')
        if p.spec.engawa_ft:  # the veranda, a lighter strip along the court face under the building's outline (R01)
            ex, ey, ex2, ey2 = _engawa(p)
            parts.append(rect(ex, ey, ex2 - ex, ey2 - ey, KINDS["plain"][0], stroke, 1.2, "", "engawa"))
        if p.spec.dais[0]:  # the magistrate's dais, dark tatami on the court face (buildings.md "Office hall")
            dx, dy, dx2, dy2 = _dais(p)
            parts.append(rect(dx, dy, dx2 - dx, dy2 - dy, "#8C6F3E", "#4A3318", 1, "", "magistrate's dais"))
            caption("area", dx, dy, dx2 - dx, dy2 - dy, "magistrate's dais", 8, False, "#FFFAE6", "magistrate's dais")
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
            caption("area", ax, ay, aw, ah, p.spec.name, size, False, "#3A2E1C", p.spec.feature)
        else:
            caption("point" if full else "area", p.x_ft, p.y_ft, p.spec.w_ft, p.spec.h_ft, p.spec.name, size, False, "#3A2E1C", p.spec.feature)
    parts += _point_features(program, result, rect, caption, ox, oy)
    # the scale bar every Mode A sheet carries (buildings.md "Scale"; the registered check `scale_bar_present`)
    sx, sy = ox, oy - 12 * FTPX
    parts.append(
        f'<g stroke="#3A2E1C" data-kind="-"><line x1="{sx:.0f}" y1="{sy:.0f}" x2="{sx + 90:.0f}" y2="{sy:.0f}" stroke-width="2"/><line x1="{sx:.0f}" y1="{sy - 5:.0f}" x2="{sx:.0f}" y2="{sy + 5:.0f}" stroke-width="2"/><line x1="{sx + 90:.0f}" y1="{sy - 5:.0f}" x2="{sx + 90:.0f}" y2="{sy + 5:.0f}" stroke-width="2"/><line x1="{sx + 45:.0f}" y1="{sy - 3:.0f}" x2="{sx + 45:.0f}" y2="{sy + 3:.0f}" stroke-width="1"/></g>'
    )
    parts.append(f'<text x="{sx + 45:.0f}" y="{sy + 16:.0f}" text-anchor="middle" font-size="10" fill="#3A2E1C" data-kind="-">30 ft</text>')
    parts.append(f'<text x="{sx + 45:.0f}" y="{sy + 27:.0f}" text-anchor="middle" font-size="8" font-style="italic" fill="#5C4830" data-kind="-">(3 px = 1 ft)</text>')
    obstacles.append(Obstacle(((sx - 2, sy - 6), (sx + 92, sy - 6), (sx + 92, sy + 30), (sx - 2, sy + 30)), WEIGHT_OBSTACLE))  # the scale bar
    # compound wall (4 segments; S wall broken by the gate) + divider - each in a `<g stroke=...>` group,
    # the authoring form the audit's gate-opening and divider readers parse (feature 254: the drafts are
    # swept by the gate like the hand-drawn sheets, so they are drawn the way the checks read)
    # the compound wall, broken where the main gate and the postern pass through it (`_wall_runs`), and the divider
    # broken at the middle gate - each in a `<g stroke=...>` group, the authoring form the audit's gate-opening and
    # divider readers parse (feature 254: the drafts are swept by the gate like the hand-drawn sheets, so they are
    # drawn the way the checks read). The gates' posts follow, each gate a group of its kind (feature 267).
    parts.append('<g stroke="#2D2A24" stroke-width="9" data-kind="compound wall">')
    for _side, x1, y1, x2, y2 in _wall_runs(env):
        parts.append(f'<line x1="{ox + x1 * FTPX:.0f}" y1="{oy + y1 * FTPX:.0f}" x2="{ox + x2 * FTPX:.0f}" y2="{oy + y2 * FTPX:.0f}"/>')
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
        parts.append(f'<line x1="{ox + a * FTPX:.0f}" y1="{oy + env.divider_ft * FTPX:.0f}" x2="{ox + b * FTPX:.0f}" y2="{oy + env.divider_ft * FTPX:.0f}"/>')
        obstacles.append(Obstacle(tuple(stroke_band(px(a, env.divider_ft), px(b, env.divider_ft), 3.0)), WEIGHT_OBSTACLE))
    parts.append("</g>")
    for gkind, side, lo, hi, line, deep, ink, whole in gates:
        parts.append(f'<g fill="{ink}"{_kind_attr(gkind)}{whole}>')
        for bx, by, bx2, by2 in _gate_posts(side, lo, hi, line, GATE_POST_W_FT, deep):
            obstacles.append(Obstacle(box(bx, by, bx2 - bx, by2 - by), WEIGHT_OBSTACLE))
            parts.append(f'<rect x="{ox + bx * FTPX:.0f}" y="{oy + by * FTPX:.0f}" width="{(bx2 - bx) * FTPX:.0f}" height="{(by2 - by) * FTPX:.0f}"/>')
        parts.append("</g>")
    # A CAPTION MAY HOLD THE SHEET'S EDGE (the review checklist: every edge "held by real content"): the notice board
    # stands outside the gate, 21 px from the canvas's foot, where no caption fits beside it - the old draft's caption
    # hung past the edge and was clipped. So the placer is given room below, and the canvas then grows to hug what it
    # placed there.
    seated, foot = _seat_captions(requests, obstacles, (0.0, 0.0, cw, ch + CAPTION_ROOM), late)
    parts += seated
    if foot + margin_ft * FTPX > ch:
        grown = foot + margin_ft * FTPX
        parts[0] = parts[0].replace(f'viewBox="0 0 {cw:.0f} {ch:.0f}"', f'viewBox="0 0 {cw:.0f} {grown:.0f}"')
        parts[2] = parts[2].replace(f'height="{ch:.0f}"', f'height="{grown:.0f}"')
    parts.append("</svg>")
    return "\n".join(parts)


# ---- a built-in county-magistracy program ------------------------------------------------


def county_magistracy_program() -> CompoundProgram:
    """A generic county magistracy declared entirely in feet (the placer composes it).

    Building masses are sized to land in the ~37-42% jin'ya coverage band (real jin'ya
    consolidate into a few large masses); the spine (garden -> oshirasu -> forecourt, plus
    the practice ground beside the barracks) sits clear of the wall rows so the placer never
    has to overlap it.
    """
    # The main gate is a one-bay yakuimon with an 8 ft passage - R26's knob, the one-bay form (6-8.5 ft, research
    # buildings 480); it was a 13 ft opening, the carriage gate the vocabulary once drew. The postern in the west wall,
    # centered 50 ft down it, opens on the kitchen yard between the bath and the karo's house (buildings/programs.md:
    # the kitchen postern keeps deliveries and night-soil off the hearing court); its 6 ft passage is a GUESS. The
    # middle gate keeps the Envelope's 6 ft (narrower than the main gate). The outer court's SERVICE GATE (pass 4,
    # building-review round 3; buildings/programs.md "Walled enclosure": a busy outer court warrants a small service
    # gate so muck, night-soil and prisoner transfers skip the formal gate) stands in the south wall by the cell, at
    # the head of the cart yard; its 6 ft passage is a GUESS, narrower than the main gate.
    env = Envelope(w_ft=270.0, h_ft=200.0, divider_ft=90.0, gate_w_ft=8.0, posterns=(("W", 50.0, 6.0), ("S", 244.0, 6.0)))
    spine = (
        # THE GARDEN LIES BEFORE THE HOUSE (feature 267 pass 3, building-review: only 23 ft of the residence's 92 ft
        # south face looked onto it while the kitchen, bath, well and karo's house took the rest; research buildings
        # 230 'The shady rear is the service strip' - the garden faces the reception rooms). It starts at the
        # residence's west end (x 50: the kitchen takes the corner, so the residence lands at 50-142) and runs to the
        # guest house (x ~233) less its tub; it abuts the residence's south face (y 46, the house standing 8 ft off the
        # north wall since pass 4) and runs 36 ft deep to y 82, into the void that stood below it, leaving an 8 ft walk
        # along the divider to the middle gate. Its size is a GUESS.
        CourtZone("garden", 34.0, 40.0, 188.0, 42.0),
        # The hearing court is centered on the office hall (x 43-156 as placed: the tax archive's 34 ft and a
        # fire-gap west of it) and no longer than it - R22, research buildings 450: under the office hall's roof or its
        # own, before the dais. 80 ft leaves each end of the hall's south face out from under the roof, where its tub
        # stands; 32 ft deep (36 until pass 5) keeps the cart slot to the stables and room for the stable well before
        # them (buildings.md "Hearing court"). It was 132 x 39 ft, longer than the hall and 34 ft off its center. Its
        # size is a GUESS - no roofed court's size was found.
        CourtZone("oshirasu", 59.5, 126.0, 80.0, 32.0),
        # just inside the main gate (131-139), east of the gatehouse that stands beside it, and 55 ft wide (it was 36)
        # to take the ground east of the gate the hearing court gave up when it shrank to the hall's length; a
        # marshalling apron's width is a GUESS
        CourtZone("forecourt", 130.0, 166.0, 55.0, 31.0),
        # Practice ground beside where the watch lodges (the E-wall barracks, 45 ft long since pass 5, lands at x 223,
        # y 128 under the current masses): 33 x 42 ft = 1,386 sqft, inside the 1,200-2,000
        # sqft full-platoon band at ~90-135 sqft per drilling samurai (buildings.md
        # "Practice ground" + the dojo-is-a-city-institution grounding), west of the E column,
        # whose barracks abuts the swept patch at x 223 - which is what "beside the watch's
        # lodging" means - so the wall rows still flow past it without overflow. Pass 4 widened it to 45 ft; pass 5
        # gave the 12 ft back to the barracks.
        CourtZone("practice ground", 190.0, 126.0, 33.0, 42.0),
        # The outer court's open ground between the hearing court and the practice ground (pass 4, building-review round
        # 3: ~50 x 40 ft unnamed): the way from the forecourt to the middle gate and the hall's east door, named, not
        # fenced (UNFENCED_ZONES). Its bounds are a drawing convention.
        CourtZone("yard", 141.0, 126.0, 47.0, 38.0),
        # The cart yard before the service gate (pass 4: the ~71 x 30 ft of bare ground in the SE outer court) - the
        # carts, the stable muck and the prisoners' way out; the kind the hand sheets draw (a DEVIATION from canon on
        # H and U, forms.md). Its size is a GUESS.
        CourtZone("cart yard", 188.0, 172.0, 62.0, 25.0),  # its north edge 172 (pass 5) leaves the garrison privy its seat by the barracks
    )
    b = BuildingSpec
    buildings = (
        # inner (residence) court - buildings ring N/E/W walls + back the divider
        # The residence: one block under one roof (R02's ordinary form, research buildings 250), MASSED IN TWO ROWS front
        # and back (pass 4, building-review round 3: the one-room-deep bar; forms.md R02, as pass 2 re-massed Ochiba's; the
        # Kuchiba house's rooms "stand in two rows, front and back", research buildings 260). Its rooms take the palace
        # order's lesser form - the reception at the east END nearest the middle gate, the full depth; the master's rooms
        # beside it on the garden row; the family's beyond, on the garden row by the kitchen and the inner rooms behind
        # (R03, research buildings 260: the reception at one end, the master's rooms adjoining it and the family's). The
        # veranda runs along the garden face alone, 5 ft (R01's first form, research buildings 240: 3-6 ft). The room
        # sizes are GUESSES. Its inner entrance opens on its west face, onto the slot below the kitchen's corridor
        # (research buildings 370), its family privy attached there. It stands 8 ft off the north wall: the rear band
        # narrowed to a cart/servant alley, one of research buildings 230's two forms (the other a service strip).
        # 92 x 36 ft (3,312 sq ft with its veranda) is ABOVE the houses research buildings 380 measures (49 tsubo, ~1,740
        # sq ft, at middle rank; 67 tsubo, ~2,380 sq ft, for a 500-1,000 koku retainer) - that entry governs a house's
        # size, and this one is a GUESS a size above it for a county magistrate's household; the "about 180 to 200 ft"
        # in the residence's kind entry is the length of the hand sheets' two-block wings, not a house.
        b(
            "residence",
            "lord",
            66.0,
            30.0,
            "inner",
            "N",
            order=10,
            feature="residence",
            rooms=(
                ("inner rooms", 0.0, 0.0, 44.0, 12.5),
                ("family quarters", 0.0, 12.5, 22.0, 12.5),
                ("lord's quarters", 22.0, 12.5, 22.0, 12.5),
                ("reception room", 44.0, 0.0, 22.0, 25.0),
            ),
            engawa_ft=5.0,
            door_face="W",
            inset_ft=8.0,
        ),
        # 72 x 18 ft (it was 66 x 15): a nagaya two rooms deep less its eaves, for the ~10 household servants; pass 5 gave the
        # compound's mass back to its lodgings when the house came down to research buildings 380's size. A GUESS.
        b("servants' quarters", "service", 72.0, 18.0, "inner", "N", order=2, feature="servants' quarters"),
        # The kitchen takes the NW corner on the north wall (order above the residence's), joined to the residence's
        # west end by the short corridor across the fire-gap (research buildings 360/370), so the residence's whole
        # south face is left to the garden and the kitchen's own south face - the bath, the well, its door - opens on
        # a service yard of its own with the postern. It was 44 x 36 ft on the west wall, about 31% of the house; 40 x
        # 30 ft is the reviewer's figure for a house of this size, a GUESS inside the kitchen band (20-52 x 16-46).
        b("kitchen", "service", 24.0, 20.0, "inner", "N", order=11, feature="kitchen"),
        # A MODEST shrine, 18 x 14 ft (pass 4, building-review round 3: it was 36 x 30 ft, the hall-shrine ceiling, which
        # is Ochiba's particular - buildings/programs.md: the shrine is universal equipment, its scale the per-manor
        # particular; buildings.md "Modest shrine"). The size is a GUESS inside the shrine band (40-1,150 sq ft).
        b("shrine", "shrine", 18.0, 14.0, "inner", "E", order=4, feature="compound shrine"),
        # A detached guest house is a GUESS (R10, research buildings 330: guests were received in the main house, and a
        # guest house apart at a samurai house was not found); kept as the example's draft of the item.
        b("guest house", "lord", 33.0, 30.0, "inner", "E", order=3, feature="guest quarters"),
        # A karo's house of its own inside the compound is a GUESS (R11, research buildings 340: the intendancy's staff
        # lived in small houses or long-house bays inside it; a chief retainer's own house there was not found).
        b("karo's house", "lord", 37.0, 26.0, "inner", "divider", order=3, feature="karo's house"),
        # outer (administrative) court - office hall backs the divider (oshirasu in front)
        # The clerks' room is a ROOM of the office hall, at its west end on the rear (divider) side, 30 x 20 ft - the
        # footprint the freestanding clerks' building had (feature 267 R20, research buildings 430: the clerks worked in
        # rooms of the office; no page gives them a workroom building). Its size is a guess.
        # Its DAIS BAND (pass 4, building-review round 3): the magistrate's dais, 30 x 10 ft centered on its south face over
        # the hearing court (buildings.md "Office hall (with dais band)", the size Ochiba draws; a GUESS). Its door opens
        # on its east face, by the middle gate - the south face is the court's.
        b(
            "office hall",
            "lord",
            113.0,
            34.0,
            "outer",
            "divider",
            order=10,
            feature="office hall",
            rooms=(("clerks' room", 0.0, 0.0, 30.0, 20.0), ("day office", 30.0, 0.0, 42.0, 20.0), ("official study", 72.0, 0.0, 41.0, 20.0)),
            dais=(30.0, 10.0),
            door_face="E",
        ),
        b("tax archive", "kura", 34.0, 30.0, "outer", "W", order=6, feature="tax archive"),
        # 50 ft long (it was 60): the hearing court, now centered on the hall, starts at x 59.5, and the retainers'
        # east face must keep a 7 ft run in front of it for its tub and door
        # 24 ft deep (it was 18): two rooms deep for the senior retainers' households - pass 5, the mass the house gave
        # up; a GUESS
        b("senior retainers' quarters", "service", 50.0, 24.0, "outer", "W", order=4, feature="retainers' quarters"),
        # 60 x 30 ft (it was 52 x 28), the top of the granary band (30-60 x 14-36): pass 5 returned the ~2,000 sq ft the
        # house gave up (research buildings 380) to the compound's working stores and lodgings, holding coverage in the
        # jin'ya band (33-42%) without shrinking the envelope (buildings.md). A GUESS in the band.
        b("granary", "kura", 60.0, 30.0, "outer", "E", order=6, feature="granary"),
        # 45 ft long (it was 33): the platoon lodged on the grounds (staff housing option (a)) is ~10-20 men, and the
        # watch's range should out-foot the stable by a margin (buildings.md "Barracks": ~27-53 ft); pass 5. A GUESS.
        b("barracks", "service", 45.0, 34.0, "outer", "E", order=4, feature="barracks"),
        # 12 x 10 ft: the small end of the single cells read (Osaka's 6 mats, ~12 x 9 ft, to Tenmacho's 18); a county
        # remand cell belongs there, its size a guess in the span (feature 267 R24, research buildings 460). It was
        # 18 x 16 ft.
        b("cell", "cell", 12.0, 10.0, "outer", "E", order=1, feature="cell"),
        # The gatehouse stands BESIDE the gate, a building of its own (R19's Takayama form, research buildings 420),
        # 18 x 12 ft - the one measured freestanding guardroom (Kita-in's 3 x 2 ken). It was 42 x 15 ft in the SW
        # corner, 83 ft from the gate; ~40 ft is the gate range's scale.
        # Its door opens on the gate passage (east), where the gatekeepers watch - not on the court.
        b("gatehouse", "dark", 18.0, 12.0, "outer", "S", order=8, feature="gatehouse", beside_gate=True, door_face="E"),
        # 36 x 24 ft (it was 33 x 23; pass 5, the same return of mass), still under the barracks as buildings.md asks
        b("stables", "service", 36.0, 24.0, "outer", "S", order=5, feature="stables"),
        # The grooms' and bearers' row (pass 5, building-review round 4: the bare SW ground by the stables while the
        # grooms lodged in the inner court): a servants' nagaya in the SW corner beside the stables it serves
        # (research: the domestic servants - cooks, grooms, cleaners - lived in a nagaya; a second row by the stables is
        # a GUESS), 44 x 16 ft. It takes the corner (order above the stables') so the stables' privy keeps its end face.
        b("grooms' row", "service", 44.0, 16.0, "outer", "S", order=6, feature="servants' quarters"),
    )
    return CompoundProgram("County Magistracy (example)", env, spine, buildings)


def main(argv: list[str] | None = None) -> int:
    args = sys.argv[1:] if argv is None else argv
    out = args[0] if args else os.path.join("pool", _EXAMPLE_TIER, "county-magistracy-example", "county-magistracy-example.svg")
    program = county_magistracy_program()
    result = place(program)
    with open(out, "w", encoding="utf-8") as fh:
        fh.write(emit_svg(program, result))
    print(f"wrote {out}: {len(result.placed)} buildings placed, {len(result.overflow)} overflow")
    for spec in result.overflow:
        print(f"  OVERFLOW (did not fit its wall): {spec.name} ({spec.w_ft:.0f}x{spec.h_ft:.0f} ft, {spec.court} {spec.wall})")
    return 0


if __name__ == "__main__":
    from l7r.diagram._invocation import guard

    # REFUSE unless invoked through this project's make (feature 127). At the TOP of the
    # entry point, never in a loop - the determination reads /proc and is cached per process.
    guard("l7r.diagram.compound")
    raise SystemExit(main())
