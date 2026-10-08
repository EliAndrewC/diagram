"""The sized marks a rect table misses (feature 294, plan B15c; the audit's Z5 row): every circle, ellipse, path, line,
polyline and polygon of a Mode A sheet, in feet, named by its `data-kind` tag - and the kinds no row names.

WHY. `make size-table` (`scripts/reviews/size_table.py`) hands `size-audit` every drawn RECT in feet, and the audit's first
method was to enumerate every sized feature from that table. A tree crown, a tub, a road, an arch, a stepping stone is
drawn as a circle or a stroke, so it was not in the table, and the agent measured it by hand or not at all. This lists
them from the same tags (`interactive.sheet.element_kinds`, read through `tagged.marks`), and `untabled_kinds` names a
tagged kind that neither a rect nor a mark row carries - a kind drawn only as a caption, or in an element no row reads.
"""

from __future__ import annotations

import math
from dataclasses import dataclass

from .grids import FTPX
from .tagged import Mark, marks

#: The element tags a mark row lists (a rect is the rect table's).
MARK_TAGS: frozenset[str] = frozenset({"circle", "ellipse", "path", "line", "polyline", "polygon"})
NOT_HIGHLIGHTED = "-"  # the not-highlighted ruling (`interactive.classes.NOT_HIGHLIGHTED`): ink no table row is owed


@dataclass(frozen=True)
class MarkRow:
    """One sized mark: its tag, kind, box (ft), its line length (ft, a stroke's run; 0 for a closed shape) and stroke (ft)."""

    tag: str
    kind: str
    x_px: float
    y_px: float
    w_ft: float
    h_ft: float
    length_ft: float
    stroke_ft: float


def _length(pts: tuple[tuple[float, float], ...]) -> float:
    return sum(math.hypot(b[0] - a[0], b[1] - a[1]) for a, b in zip(pts, pts[1:], strict=False))


def mark_rows(svg: str) -> list[MarkRow]:
    """Every tagged circle, ellipse, path, line, polyline and polygon, in feet, largest first."""
    out: list[MarkRow] = []
    for m in marks(svg):
        if m.tag not in MARK_TAGS or m.kind in (None, NOT_HIGHLIGHTED):
            continue
        assert m.kind is not None
        out.append(MarkRow(m.tag, m.kind, round(m.x, 1), round(m.y, 1), round(m.w / FTPX, 1), round(m.h / FTPX, 1), round(_length(m.pts) / FTPX, 1), round(m.stroke_width / FTPX, 1)))
    out.sort(key=lambda r: -(r.w_ft * r.h_ft + r.length_ft))
    return out


def _sized(m: Mark) -> bool:
    """A row of either table: a rect with an area, or a mark of `MARK_TAGS`."""
    return (m.tag == "rect" and m.w > 0 and m.h > 0) or m.tag in MARK_TAGS


def untabled_kinds(svg: str) -> list[str]:
    """The tagged kinds that no rect row and no mark row carries, as its own kind or as a kind it is a part of - sized
    nowhere a size audit reads. A group kind whose parts carry kinds of their own (a river landing of revetment, steps
    and a barge) is listed by its parts' rows. A kind tagged on nothing but captions (a room's alcove named in its caption)
    has no drawn extent to size, so it owes no row (feature 294: the rule holds a DRAWN feature to the table)."""
    ms = marks(svg)
    listed = {k for m in ms if _sized(m) for k in (m.kind, *m.lineage)}
    tagged = {m.kind for m in ms if m.kind is not None and m.tag != "text"}
    return sorted(k for k in tagged - listed if k != NOT_HIGHLIGHTED)


def render(rows: list[MarkRow]) -> str:
    """The mark rows as the size table's second section."""
    lines = [f"marks (circles, ellipses, paths, lines, polygons): {len(rows)}", f"{'w ft':>7}{'h ft':>7}{'run ft':>8}{'ink ft':>8}  {'tag':<9}{'at px':<14}kind (data-kind)"]
    lines += [f"{r.w_ft:>7}{r.h_ft:>7}{r.length_ft:>8}{r.stroke_ft:>8}  {r.tag:<9}{f'{r.x_px:g},{r.y_px:g}':<14}{r.kind}" for r in rows]
    return "\n".join(lines)


__all__ = ["Mark", "MarkRow", "mark_rows", "render", "untabled_kinds"]
