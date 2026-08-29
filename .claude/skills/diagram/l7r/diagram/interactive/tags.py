"""The class TAG a record-stream entry carries - the side-list value beside each `add()` string.

Feature 134: the SVG text never changes (FR-010 - the PNG is byte-identical by construction), so the
class of a primitive rides in a parallel list, one tag per `add()`. Three shapes, because three
things happen at an emit site:

- a `str` - the whole string is one class (the common case; `"-"` is the not-highlighted ruling);
- `Parts` - one string joined from pieces of MORE than one class (a farmhouse and its attached shed
  are one `<g transform>` in `house()`), each piece tagged, the join byte-identical to before;
- `Split` - ONE element whose FILL is one class and whose STROKE is another (a comb paddy: the fill
  is the flooded plot, the stroke is the bund). The SVG keeps the one polygon; the HTML target emits
  a fill-only copy and a stroke-only copy so the two highlight apart (spec US3).

`None` is "nobody ruled on this" - what the FR-009 census reports.
"""

from __future__ import annotations

from dataclasses import dataclass


class Planted(str):
    """A class key, marking a string as the PLANTING on that feature rather than the feature itself.

    Feature 153 (GM 2026-08-29: *"when the Mulberry dikes are highlighted ... we can no longer see the
    greenery along them ... it will be clear that there is cultivated plant life growing on top of the
    thing"*). The crop dike's coppiced crowns are already tagged with the dike's own key - one `add()`
    for the band, another for the planting - so both light together, which is what the GM asked for. What
    was missing is that the highlight sets ONE fill across the group, so the bushes vanish into the bank.

    A `str` SUBCLASS on purpose: every consumer that asks `isinstance(tag, str)` - the census, the present
    set, the hit-copy lookup - keeps treating it as the key it is, and only the page's group opener
    notices the difference and adds a marker the stylesheet can reach. Nothing about the drawn record
    changes; the SVG and PNG stay byte-identical (feature 134 FR-010)."""

    __slots__ = ()


@dataclass(frozen=True)
class Split:
    """One element, two classes: `fill` for its filled body, `stroke` for its outline."""

    fill: str
    stroke: str


Parts = tuple[tuple[str | None, str], ...]
ClsTag = str | Planted | Split | Parts | None
