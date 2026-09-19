"""Labels paired with the footprints they name (feature 254, D7) - the ONE pairing the size table and the
band check share.

`scripts/_size_table.py` labeled every rect with its nearest `<text>` by center distance, and printed
the distance so a far label reads as the guess it is. The band check needs the pairing the other way
round - each required item's label, and the structure it stands on - and it must not grow its own
version of the rule, which is how a documented intent and an implementation drift apart (the tub
check's fill list, 2026-07-25). So both come here.
"""

from __future__ import annotations

import math
from collections.abc import Sequence

from ...buildings.types import BuildingType, RequiredItem
from .grids import FTPX
from .parse import Label, ParsedPlan, Rect

PAIR_MAX_FT: float = 30.0  # a label farther than this from every structure names ground, not a building


def nearest_label(cx: float, cy: float, labels: Sequence[tuple[float, float, str]]) -> tuple[str, float] | None:
    """The label nearest a point, with the distance in px: `(text, px)`, or None when there are none."""
    if not labels:
        return None
    lx, ly, text = min(labels, key=lambda lab: math.hypot(lab[0] - cx, lab[1] - cy))
    return text, math.hypot(lx - cx, ly - cy)


def structure_for(label: Label, structures: Sequence[Rect], max_ft: float = PAIR_MAX_FT) -> Rect | None:
    """The built footprint a label names: the structure its center stands ON, else the nearest one
    within `max_ft` of it, else None (a zone label - RESIDENCE, HEARING COURT - names ground)."""
    cx, cy = label.cx, label.cy
    on = [r for r in structures if r.x <= cx <= r.x2 and r.y <= cy <= r.y2]
    if on:
        return min(on, key=lambda r: r.area_px)  # the smallest containing footprint is the one labeled
    best = None
    best_d = max_ft * FTPX
    for r in structures:
        dx = max(r.x - cx, 0.0, cx - r.x2)
        dy = max(r.y - cy, 0.0, cy - r.y2)
        d = math.hypot(dx, dy)
        if d < best_d:
            best, best_d = r, d
    return best


def matches(item: RequiredItem, labels: Sequence[Label]) -> list[Label]:
    """The sheet's labels that name `item` (its `label` regex, case-insensitive, over the whole text)."""
    return [lb for lb in labels if item.label.search(" ".join(lb.text.split()))]


def check_program(plan: ParsedPlan, btype: BuildingType, form: str | None) -> list[str]:
    """Every required item of the type's program is on the sheet by label; an item a knob or the declared
    form makes absent is not asked for."""
    out: list[str] = []
    for item in btype.required:
        if item.optional or item.band_for(form) is None:
            continue
        if not matches(item, plan.labels):
            out.append(f"no `{item.id}` on the sheet (a label matching /{item.label.pattern}/)")
    return out


def check_bands(plan: ParsedPlan, btype: BuildingType, form: str | None) -> list[str]:
    """Every labeled required item's footprint lies in its declared band (feet, either orientation)."""
    out: list[str] = []
    for item in btype.required:
        band = item.band_for(form)
        if band is None or band.presence_only:
            continue
        for lb in matches(item, plan.labels):
            r = structure_for(lb, plan.structures)
            if r is None:
                continue  # a label on open ground: the program check's business, not a size's
            w_ft, h_ft = r.w / FTPX, r.h / FTPX
            if not band.holds(w_ft, h_ft):
                a, bw, bh = band.area, band.w, band.h
                if a is not None and not (a[0] <= w_ft * h_ft <= a[1]):
                    want = f"area {a[0]:.0f}-{a[1]:.0f} sq ft"
                else:
                    assert bw is not None and bh is not None  # `holds` passes anything without both, so this is the w-by-h case
                    want = f"w {bw[0]:.0f}-{bw[1]:.0f} by h {bh[0]:.0f}-{bh[1]:.0f} ft"
                out.append(f"`{item.id}` ({lb.text!r}) is {w_ft:.0f} x {h_ft:.0f} ft ({w_ft * h_ft:.0f} sq ft) at svg({r.x:.0f},{r.y:.0f}) - the band is {want} ({item.cls}: {item.why})")
            break  # one footprint per item: the first label that stands on a structure
    return out
