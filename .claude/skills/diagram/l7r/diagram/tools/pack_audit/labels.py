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
from collections.abc import Mapping, Sequence

from ...buildings.types import BuildingType, RequiredItem, classification
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


def matches(item: RequiredItem, labels: Sequence[Label], label_kinds: Mapping[int, str] | None = None) -> list[Label]:
    """The sheet's labels that name `item`: for a KIND item (feature 262), the labels the sheet itself tags with that
    kind (`label_kinds`, the parser's offset -> kind map); otherwise those its `label` regex finds, case-insensitive,
    over the whole text."""
    if item.kind is not None:
        return [lb for lb in labels if (label_kinds or {}).get(lb.pos) == item.kind]
    assert item.label is not None  # a declaration item is labeled or kinded (types.py `_item` refuses anything else)
    return [lb for lb in labels if item.label.search(" ".join(lb.text.split()))]


def _present(item: RequiredItem, plan: ParsedPlan) -> bool:
    """Whether the sheet draws `item`: a kind item by any element tagged with its kind, a labeled one by a label its
    regex finds - and either by an element DECLARED with its id (an arch, an approach, a well, a fence group need no
    caption saying what they plainly are - the no-obvious-labels rule; the id is what the checks read)."""
    if item.id in plan.ids:
        return True
    if item.kind is not None:
        return item.kind in plan.kinds
    return bool(matches(item, plan.labels))


def _how_found(item: RequiredItem) -> str:
    """How the sheet shows an item, in the words a missing-item finding uses."""
    if item.kind is not None:
        return f'an element tagged data-kind="{item.kind}"'
    assert item.label is not None
    return f"a label matching /{item.label.pattern}/"


def check_program(plan: ParsedPlan, btype: BuildingType, form: str | None, site: Mapping[str, bool] | None = None) -> list[str]:
    """Every required item of the type's program is on the sheet by label; an item a knob or the declared
    form makes absent is not asked for, and a SITE item (feature 257) only where `site` - the classes the
    declared map shows inside the sheet's frame - says the map has its class there (None: no declaration,
    every site item is asked for)."""
    out: list[str] = []
    for item in btype.required:
        if item.optional or item.band_for(form) is None:
            continue
        if item.site is not None and site is not None and not site.get(item.site, False):
            continue  # the map shows none of that class at the subject: the sheet draws none (the GM, 2026-09-20)
        if not _present(item, plan):
            out.append(f"no `{item.id}` on the sheet ({_how_found(item)}, or an element marked id=\"{item.id}\")")
    return out


def _of_its_kind(label: Label, plan: ParsedPlan) -> Sequence[Rect]:
    """The structures a label may name: those tagged with the label's own kind where it carries one and any are drawn,
    else all of them. A caption seated beside its building by the standard (feature 267) can stand nearer another one -
    Ubame's INARI SHRINE, set left of the shrine, stood nearest a 6 x 5 ft privy and was measured as the shrine."""
    kind = plan.label_kinds.get(label.pos)
    own = [r for r in plan.structures if kind and plan.label_kinds.get(r.pos) == kind]
    return own or plan.structures


def check_bands(plan: ParsedPlan, btype: BuildingType, form: str | None) -> list[str]:
    """Every labeled required item's footprint lies in its declared band (feet, either orientation)."""
    out: list[str] = []
    for item in btype.required:
        band = item.band_for(form)
        if band is None or band.presence_only:
            continue
        for lb in matches(item, plan.labels, plan.label_kinds):
            r = structure_for(lb, _of_its_kind(lb, plan))
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
                cls, why = classification(item)
                out.append(f"`{item.id}` ({lb.text!r}) is {w_ft:.0f} x {h_ft:.0f} ft ({w_ft * h_ft:.0f} sq ft) at svg({r.x:.0f},{r.y:.0f}) - the band is {want} ({cls}: {why})")
            break  # one footprint per item: the first label that stands on a structure
    return out
