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


@dataclass(frozen=True)
class Split:
    """One element, two classes: `fill` for its filled body, `stroke` for its outline."""

    fill: str
    stroke: str


Parts = tuple[tuple[str | None, str], ...]
ClsTag = str | Split | Parts | None
