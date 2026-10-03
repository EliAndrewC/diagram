"""The placed houses' extents, indexed once (feature 276) - and the part boxes the fit rules read off a homestead's geometry.

Split out of `fit.py` at the 1,000-line bar (feature 315): `house_extent`, `houses_meeting`, `part_box`, `house_box`,
`recorded_box` and `drop_persimmon`, imported back by `fit` so every caller's name still resolves there.

Research: index plumbing - NONE: each rule that reads these boxes is claimed in `fit`
"""

import math
from typing import Any

from .._geom import PointGrid
from .._geom.indexes import indexed_grid

# ---- feature 276, FR-003: the placed houses, indexed ONCE and extended as each lands --------------------------------
#
# Every scan of the house records a candidate seat makes - the eave gap, the sun corridor both ways, the gardens' sun,
# the yard-sun conflict - walked EVERY record per candidate, so a seat cost more with each house standing: at constant
# density the placement primitive's per-house cost grew from 0.0009 s to 0.0017 s between 60 and 240 seeds on the
# nucleated path (specs/276 research R2). Each of those rules asks whether some part of a record lies within a reach box
# of the candidate, so a grid of each record's EXTENT - its house's circumscribed box and every part's box - asked for
# that reach box returns every record the rule could flag; the rule's own comparison then decides, unchanged. An
# `Indexed` house list carries its own version, so the grid is rebuilt on any change but an append, which extends it.
# THE ONE IN-PLACE MOVE of a record (`_solve_homestead`) bumps that version itself; a record's `geom` is complete when it
# is appended and never edited after.


def house_extent(rec: Any) -> tuple[float, float, float, float]:
    """The box holding everything of a house record the fit rules read: the house at any rake, and each part as drawn."""
    r = math.hypot(rec["w"], rec["h"]) / 2
    x0, y0, x1, y1 = rec["x"] - r, rec["y"] - r, rec["x"] + r, rec["y"] + r
    g = rec.get("geom") or {}
    for part in [part_box(g, key) for key in ("yard", "shed", "byre", "well")] + list(g.get("groves") or ()):
        if part is not None:
            x0, y0 = min(x0, part[0] - part[2] / 2), min(y0, part[1] - part[3] / 2)
            x1, y1 = max(x1, part[0] + part[2] / 2), max(y1, part[1] + part[3] / 2)
    for part in part_box(g, "gardens") or ():
        x0, y0 = min(x0, part[0] - part[2] / 2), min(y0, part[1] - part[3] / 2)
        x1, y1 = max(x1, part[0] + part[2] / 2), max(y1, part[1] + part[3] / 2)
    tree = (g.get("fixtures") or {}).get("persimmon")  # its crown, which may stand paces out (`_persimmon_sun_conflict` reads it)
    if tree is not None:
        x0, y0, x1, y1 = min(x0, tree[0] - tree[2] / 2), min(y0, tree[1] - tree[2] / 2), max(x1, tree[0] + tree[2] / 2), max(y1, tree[1] + tree[2] / 2)
    return x0 - 1.0, y0 - 1.0, x1 + 1.0, y1 + 1.0


def recorded_box(r: Any, turn: float) -> tuple[float, float, float, float]:
    """A laid fixture (x, y, w, h) as `grove_rules.fixtures_on_groves` reads its record: center and size rounded to 0.1 (the
    drawn record's own rounding, `farm_fixtures`), turned by `turn` degrees (already rounded) - its axis-aligned box."""
    x, y, w, h = round(float(r[0]), 1), round(float(r[1]), 1), round(float(r[2]), 1), round(float(r[3]), 1)
    th = math.radians(turn)
    return (x, y, abs(w * math.cos(th)) + abs(h * math.sin(th)), abs(w * math.sin(th)) + abs(h * math.cos(th)))


def part_box(geom: Any, key: str) -> Any:
    """A bundle part as the fit rules read it: its box AS DRAWN, turned with its house (`_bundle_geom`'s `boxes`, 269 B18);
    the part itself where the bundle carries no boxes (a grove arm, which is drawn unturned, or a hand-built geometry)."""
    boxes = geom.get("boxes") or {}
    return boxes[key] if key in boxes else geom.get(key)


def house_box(rec: Any) -> tuple[float, float, float, float]:
    """A placed farmhouse's box AS DRAWN, turned (269 B18) - its record's own rect where it carries no bundle."""
    box = part_box(rec.get("geom") or {}, "house")
    return tuple(box) if box is not None else (rec["x"], rec["y"], rec["w"], rec["h"])  # type: ignore[return-value]


def _extent_boxed(recs: Any) -> list[Any]:
    return [(rec, *house_extent(rec)) for rec in recs]


def drop_persimmon(geom: Any) -> None:
    """Take a household's persimmon out of its homestead, in place (feature 315): its fixture, its drawn box and its rolled size
    (the notes are copied first - a template's are shared)."""
    geom["fixtures"] = {k: v for k, v in (geom.get("fixtures") or {}).items() if k != "persimmon"}
    boxes = geom.get("boxes")
    if boxes and boxes.get("fixtures"):
        boxes["fixtures"] = {k: v for k, v in boxes["fixtures"].items() if k != "persimmon"}
    notes = geom.get("fixture_notes")
    if notes and (notes.get("ft") or {}).get("persimmon") is not None:
        geom["fixture_notes"] = {**notes, "ft": {k: v for k, v in notes["ft"].items() if k != "persimmon"}}


def houses_meeting(houses: Any, box: tuple[float, float, float, float]) -> list[Any]:
    """The records of `houses` whose extent meets `box`, each once, in list order (the order the linear scans read)."""

    def build(lst: Any) -> PointGrid:
        grid = PointGrid()
        grid.extend(_extent_boxed(lst))
        return grid

    def add(grid: PointGrid, tail: Any) -> None:
        grid.extend(_extent_boxed(tail))

    grid = indexed_grid(houses, "house_extents", build, add)
    x0, y0, x1, y1 = box
    seen: set[int] = set()
    out = []
    for it in grid.near((x0 + x1) / 2, (y0 + y1) / 2, max(x1 - x0, y1 - y0) / 2):
        rec, bx0, by0, bx1, by1 = it
        if id(rec) in seen or bx0 > x1 or bx1 < x0 or by0 > y1 or by1 < y0:
            continue
        seen.add(id(rec))
        out.append(rec)
    order = {id(rec): k for k, rec in enumerate(houses)} if len(out) > 1 else {}
    return sorted(out, key=lambda rec: order.get(id(rec), 0))
