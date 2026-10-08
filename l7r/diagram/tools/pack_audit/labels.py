"""A program item paired with the footprint that draws it (feature 254, D7) - the pairing the band check makes, by the
sheet's own tags.

BY THE TAGS, NEVER BY WHERE A CAPTION STANDS (feature 286). The band check paired each item's label with the structure
the label stood on, or the nearest one within 30 ft. Since feature 286 a hand sheet's captions are placed by the one
placer in the render pipeline: the tracked sheet declares what a caption names and never where it stands, so a
caption's position is the placer's output, not evidence of which footprint the drawing means (the GM: "There is no point
in having an automated check run against an automated process"). The sheet tags every drawn element with its kind
(feature 262), and that is what is read - the same tags `scripts/reviews/size_table.py` names each rect by, so the size
table and the band check cannot drift apart.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence

from ...buildings.types import BuildingType, RequiredItem, classification
from .grids import FTPX
from .parse import Label, ParsedPlan, Rect


def footprint(plan: ParsedPlan, kind: str) -> Rect | None:
    """The footprint the sheet draws under `kind`: the largest structure tagged with it, None when no structure is.

    The LARGEST, because a building's parts drawn inside its group - an engawa strip, a porch, a room drawn in the
    building's own fill - carry its tag too and are smaller than it, and a stepped building is measured on its main
    block. A kind whose tagged elements are all ground (a court, a garden) has no footprint: its size is not a band's."""
    own = [r for r in plan.structures if plan.label_kinds.get(r.pos) == kind]
    return max(own, key=lambda r: r.area_px) if own else None


def matches(item: RequiredItem, labels: Sequence[Label]) -> list[Label]:
    """The sheet's labels a LABELED item's regex finds, case-insensitive, over the whole text (a kind item, feature
    262, is found by its tag and never by a label)."""
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


def kinds_of(item: RequiredItem, plan: ParsedPlan) -> list[str]:
    """The kinds the sheet draws `item` under, in document order: a kind item's own; a labeled item's, the kinds its
    matching labels are tagged with (an untagged label names nothing the check can measure)."""
    if item.kind is not None:
        return [item.kind]
    out: list[str] = []
    for lb in matches(item, plan.labels):
        kind = plan.label_kinds.get(lb.pos)
        if kind is not None and kind not in out:
            out.append(kind)
    return out


def check_bands(plan: ParsedPlan, btype: BuildingType, form: str | None) -> list[str]:
    """Every required item's footprint lies in its declared band (feet, either orientation)."""
    out: list[str] = []
    for item in btype.required:
        band = item.band_for(form)
        if band is None or band.presence_only:
            continue
        for kind in kinds_of(item, plan):
            r = footprint(plan, kind)
            if r is None:
                continue  # drawn as ground or not at all: the program check's business, not a size's
            w_ft, h_ft = r.w / FTPX, r.h / FTPX
            if not band.holds(w_ft, h_ft):
                a, bw, bh = band.area, band.w, band.h
                if a is not None and not (a[0] <= w_ft * h_ft <= a[1]):
                    want = f"area {a[0]:.0f}-{a[1]:.0f} sq ft"
                else:
                    assert bw is not None and bh is not None  # `holds` passes anything without both, so this is the w-by-h case
                    want = f"w {bw[0]:.0f}-{bw[1]:.0f} by h {bh[0]:.0f}-{bh[1]:.0f} ft"
                cls, why = classification(item)
                out.append(f"`{item.id}` ({kind}) is {w_ft:.0f} x {h_ft:.0f} ft ({w_ft * h_ft:.0f} sq ft) at svg({r.x:.0f},{r.y:.0f}) - the band is {want} ({cls}: {why})")
            break  # one footprint per item: the first kind the sheet draws one under
    return out
