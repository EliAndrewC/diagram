"""Three marks a hand sheet draws by a rule the record or the doc settles (feature 335): the landing steps cut into the
revetment, a door set inside the wall it opens through, and a torii drawn in plan.

Each is a geometry question a Mode A sheet answers with no placer behind it, so each is a check (`registry.CHECKS`) with
a red fixture cut from a sheet as it stood before feature 335 redrew it.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

from .grids import FTPX
from .parse import ParsedPlan, Rect

_ATTR = re.compile(r'([\w:-]+)="([^"]*)"')
_RECT = re.compile(r"<rect\b([^>]*)/?>")
_STEPS = re.compile(r'<g\b[^>]*data-id="landing-steps"[^>]*>(.*?)</g>', re.S)
_TORII = re.compile(r'<g\b[^>]*data-kind="torii"[^>]*>(.*?)</g>', re.S)

# A door's edge within this of its building's wall is ON the wall (the stroke's half-width, as `floating_doors` allows)
DOOR_WALL_TOL_PX = 1.5
"""Research: door on wall tolerance - NONE: a door's edge within 1.5 px of its building's wall is on the wall, the stroke's half-width."""


def _box(attrs: str) -> tuple[float, float, float, float] | None:
    a = dict(_ATTR.findall(attrs))
    try:
        x, y, w, h = (float(a.get(k, "0")) for k in ("x", "y", "width", "height"))
    except ValueError:
        return None
    return (x, y, x + w, y + h)


def _tagged_rect(text: str, kind: str) -> tuple[float, float, float, float] | None:
    """The first `<rect>` carrying `data-kind="<kind>"` itself, or the first rect inside a group so tagged."""
    for m in _RECT.finditer(text):
        if f'data-kind="{kind}"' in m.group(1):
            return _box(m.group(1))
    g = re.search(rf'<g\b[^>]*data-kind="{re.escape(kind)}"[^>]*>(.*?)</g>', text, re.S)
    if g:
        r = _RECT.search(g.group(1))
        if r:
            return _box(r.group(1))
    return None


@dataclass(frozen=True)
class StepsPast:
    """A flight of landing steps reaching past the revetment's water-side face."""

    x: float
    y: float
    past_ft: float


def steps_past_revetment(text: str) -> list[StepsPast]:
    """Research 0176: the steps of a stepped landing are CUT INTO the revetment, so no part of the flight declared
    `data-id="landing-steps"` may stand past the revetment's water-side face - the side facing the sheet's `river`."""
    m = _STEPS.search(text)
    rev = _tagged_rect(text, "revetment")
    river = _tagged_rect(text, "river")
    if not (m and rev and river):
        return []
    r = _RECT.search(m.group(1))
    steps = _box(r.group(1)) if r else None
    if steps is None:
        return []
    east = (river[0] + river[2]) / 2 > (rev[0] + rev[2]) / 2
    past = steps[2] - rev[2] if east else rev[0] - steps[0]
    if past <= 0:
        return []
    return [StepsPast((steps[0] + steps[2]) / 2, (steps[1] + steps[3]) / 2, past / FTPX)]


@dataclass(frozen=True)
class DoorOffWall:
    """A door rect that is not set inside a building flush to its wall."""

    x: float
    y: float
    how: str  # "outside" | "floating"


def _inside(d: Rect, b: Rect) -> bool:
    return d.x >= b.x - DOOR_WALL_TOL_PX and d.y >= b.y - DOOR_WALL_TOL_PX and d.x2 <= b.x2 + DOOR_WALL_TOL_PX and d.y2 <= b.y2 + DOOR_WALL_TOL_PX


def _on_its_wall(d: Rect, b: Rect) -> bool:
    return min(abs(d.x - b.x), abs(b.x2 - d.x2), abs(d.y - b.y), abs(b.y2 - d.y2)) <= DOOR_WALL_TOL_PX


def doors_off_their_walls(plan: ParsedPlan) -> list[DoorOffWall]:
    """The one door convention (feature 335, research 0117's drawing page, docs/buildings.md): every `data-kind="door"`
    rect is set WHOLLY INSIDE a building, its outer edge on the wall it opens through - never a slab outside the wall,
    never across the wall line, never floating just inside it. Read by TAG, whatever the fill: a light-filled door is a
    door (the older `floating_doors` reads the dark fills only)."""
    doors = [r for r in plan.fills if plan.label_kinds.get(r.pos) == "door"]
    held = {d.pos for d in doors}
    hosts = [s for s in plan.structures if s.pos not in held]
    out: list[DoorOffWall] = []
    for d in doors:
        around = [b for b in hosts if _inside(d, b) and b.area_px > d.area_px]
        if not around:
            out.append(DoorOffWall(d.x + d.w / 2, d.y + d.h / 2, "outside"))
        elif not any(_on_its_wall(d, b) for b in around):
            out.append(DoorOffWall(d.x + d.w / 2, d.y + d.h / 2, "floating"))
    return out


def arches_not_in_plan(text: str) -> list[int]:
    """docs/buildings.md "Arch (torii) and approach" (feature 268): a Mode A arch is drawn IN PLAN, and its group declares
    the invisible `id="arch"` bounding rect the checks read. The 1-based line of every `data-kind="torii"` group that
    declares none (an elevation silhouette)."""
    return [text.count("\n", 0, m.start()) + 1 for m in _TORII.finditer(text) if 'id="arch"' not in m.group(1)]
