"""The map-notes block: facts a settlement's `.notes.md` hands to its interactive page (feature 154).

The GM, 2026-08-29: *"the notes that exist for a particular settlement should be formatted in such a
way that the scripted process, which generates the HTML map, is able to pull these details"* - and,
in the same breath, the property that shapes every line below: *"we should not presume that such
sections exist and our code that parses the notes file to find these special notes should be
resilient against that formatting not being present, and should default to simply not pulling
anything in if the parsing fails."*

So this module is deliberately the most forgiving code in the package. There is no error path and no
warning: a missing file, a missing section, a bullet with no colon, a truncated last line, a nested
list, an HTML comment, a key nobody recognizes - each contributes nothing and the page is written
without it. `read_map_notes()` cannot raise.

THE CONVENTION (documented for authors in `interactive/CLAUDE.md`):

    ## Map notes

    ### Place

    - **district**: Hoshigaoka
    - **district direction**: east
    - **imperial road**: directly south

    ### Features

    - **village lane**: The connector track runs south to the Imperial road; the district's
      main village, Hoshigaoka, lies east along it.

`### Place` feeds the place card (`place.py`, which looks for the keys it knows and ignores the
rest). `### Features` is keyed by CLASS KEY from `classes.py`, so ANY feature on the map can carry a
sentence true of that map only - the general capability the GM asked for, not a list of blessed
features: *"This is, in general, the kind of thing that we want to be able to do for any kind of map
feature."*

Everything else in a `.notes.md` is prose for human readers and is never parsed. The block may sit
anywhere in the file.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

#: A heading line: the hashes give the level, the rest is the title.
_HEADING = re.compile(r"^(#{1,6})[ \t]+(.*?)[ \t]*$")

#: A top-level entry. The bullet must sit at column 0 - an INDENTED bullet is a nested list, which
#: the convention does not use and which must not be mistaken for an entry or for a continuation.
_BULLET = re.compile(r"^-[ \t]+\*\*(.+?)\*\*[ \t]*:[ \t]*(.*?)[ \t]*$")


@dataclass(frozen=True)
class MapNotes:
    """What one map's notes file offers its page. Both halves are optional and usually absent."""

    place: dict[str, str] = field(default_factory=dict)
    features: dict[str, str] = field(default_factory=dict)

    def __bool__(self) -> bool:
        return bool(self.place or self.features)


#: The result of every failure, and of a file that simply has no block. Shared, and frozen.
EMPTY = MapNotes()


def normalize_key(raw: str) -> str:
    """A key as it is looked up: lower-cased, whitespace collapsed, surrounding punctuation gone.
    So `**District Direction**` and `**district  direction**` are the same key, and a class key with
    a space in it (`village lane`, `pond sluice`) survives unchanged."""
    return re.sub(r"\s+", " ", raw.strip().strip("`*_")).strip().lower()


def section(text: str, heading: str) -> str:
    """The body under the FIRST heading whose title is `heading` (case-insensitively, punctuation
    and emphasis ignored), running to the next heading of the same or higher level. Empty string
    when there is no such heading - which is the normal case for most of the pool."""
    want = normalize_key(heading)
    lines = text.splitlines()
    level = 0
    body: list[str] = []
    for line in lines:
        m = _HEADING.match(line)
        if m is None:
            if level:
                body.append(line)
            continue
        depth, title = len(m.group(1)), normalize_key(m.group(2))
        if level:
            if depth <= level:  # a sibling or an uncle closes the section
                break
            body.append(line)  # a deeper heading is part of the body
        elif title == want:
            level = depth
    return "\n".join(body)


def bullets(block: str) -> dict[str, str]:
    """The `- **key**: value` entries of one section, in order, first occurrence winning.

    A value may WRAP: an indented line that is not itself a bullet, a heading or an HTML comment
    continues the entry above it, so a long annotation reads normally in the markdown. Anything else
    in the block - prose, blank lines, comments, nested lists, a bullet with no colon, a truncated
    final line - is skipped in silence, and an entry whose value is empty is dropped."""
    out: dict[str, str] = {}
    key = ""
    parts: list[str] = []

    def close() -> None:
        value = re.sub(r"\s+", " ", " ".join(parts)).strip()
        if key and value and key not in out:
            out[key] = value

    for line in block.splitlines():
        m = _BULLET.match(line)
        if m is not None:
            close()
            key, parts = normalize_key(m.group(1)), [m.group(2)]
            continue
        stripped = line.strip()
        wrapped = bool(key) and line[:1].isspace() and bool(stripped) and not stripped.startswith(("-", "*", "#", "<!--", "|"))
        if wrapped:
            parts.append(stripped)
        elif stripped or _HEADING.match(line):
            close()  # anything else ends the entry above it; the entry keeps what it had
            key, parts = "", []
    close()
    return out


def parse_map_notes(text: str) -> MapNotes:
    """The block's two halves, from the text of a `.notes.md`. No block, no halves, nothing at all -
    every one of those is `EMPTY`, never an error."""
    block = section(text, "map notes")
    if not block:
        return EMPTY
    place, features = bullets(section(block, "place")), bullets(section(block, "features"))
    return MapNotes(place, features) if (place or features) else EMPTY


def read_map_notes(path: str) -> MapNotes:
    """`<base>.notes.md` beside a map's output, parsed. Missing, unreadable or undecodable - all
    `EMPTY`. This function does not raise; that is the GM's requirement, not an implementation
    convenience, so the `except` is deliberately broad and is the one place breadth is correct."""
    try:
        with open(path, encoding="utf-8", errors="replace") as fh:
            return parse_map_notes(fh.read())
    except OSError:
        return EMPTY
