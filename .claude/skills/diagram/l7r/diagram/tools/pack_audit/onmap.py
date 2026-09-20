"""The map declaration (feature 257, spec FR-003): a sheet whose subject already stands on a settlement map
says so in its notes, and the map check holds the sheet to that map.

    **On map**: <manifest path from the skill root> - <manifest key> at (<x>, <y>) = <sheet id>

The manifest is the map's RECORDED output (the JSON beside every pool map), never a generator re-run;
the key is the top-level list the subject is recorded in (`religious`, `houses`); (x, y) the subject's
center in the map's own px; the sheet id names the rect that IS the subject on the sheet, whose center
is the transform's origin. A sheet with no such line is on no map, and the check says so.
"""

from __future__ import annotations

import os
import re
from dataclasses import dataclass

_ON_MAP_LINE_RE = re.compile(r"^\*\*On map\*\*:\s*(?P<rest>[^\n]*?)\s*$", re.M)
_ON_MAP_RE = re.compile(r"^(?P<manifest>\S+)\s+-\s+(?P<key>[A-Za-z_][\w]*)\s+at\s+\(\s*(?P<x>-?\d+(?:\.\d+)?)\s*,\s*(?P<y>-?\d+(?:\.\d+)?)\s*\)\s*=\s*`?(?P<sheet_id>[A-Za-z_][\w-]*)`?$")
GRAMMAR = "**On map**: <manifest path from the skill root> - <manifest key> at (<x>, <y>) = <sheet id>"


@dataclass(frozen=True)
class OnMap:
    manifest: str  # the map's recorded manifest, a path from the skill root (or absolute)
    key: str  # the manifest list the subject is recorded in
    x: float  # the subject's center, map px
    y: float
    sheet_id: str  # the `id` of the sheet rect that is the subject


def parse_on_map(notes: str) -> OnMap | None:
    """The declaration in a notes file's text, None when there is none; a line that starts the declaration
    and does not follow the grammar is refused by name."""
    m = _ON_MAP_LINE_RE.search(notes)
    if not m:
        return None
    g = _ON_MAP_RE.match(m.group("rest").replace("`", ""))
    if not g:
        raise ValueError(f"the notes' `**On map**:` line does not follow the grammar `{GRAMMAR}`: {m.group(0)!r}")
    return OnMap(g.group("manifest"), g.group("key"), float(g.group("x")), float(g.group("y")), g.group("sheet_id"))


def read_on_map(svg_path: str) -> OnMap | None:
    """The declaration of the sheet's notes file (`<stem>.notes.md` beside it), or None."""
    notes = svg_path[: -len(".svg")] + ".notes.md" if svg_path.endswith(".svg") else ""
    if not notes or not os.path.isfile(notes):
        return None
    with open(notes, encoding="utf-8") as fh:
        return parse_on_map(fh.read())
