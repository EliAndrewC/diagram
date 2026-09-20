"""Where a fragment lives, and what its name means (feature 258).

A page is a directory of fragments; a fragment is one entry of the record. The name carries two things
and nothing else: the ORDER (a gapped numeric prefix) and what the entry IS (the heading's own id, or a
source's key). Nothing else may be inferred from a name - the record's anchors are the heading ids
inside the fragments, so renaming a file changes nothing a reader can see.

The prefixes are GAPPED, counting by ten, on the GM's decision of 2026-09-20: *"Gapped (`010-`, `020-`)
so inserting a question doesn't renumber the directory"*. Three digits for a page's questions (39 is the
most any page has), four for the registry's 920 entries.
"""

from __future__ import annotations

import os
import re

#: The fragments that are not entries. They sort first and last by name, not by prefix.
FRONT = "_front.html"
TAIL = "_tail.html"
CITATIONS_FRONT = "_citations-front.html"
CITATIONS_WORKS = "_citations-works.html"
CITATIONS_TAIL = "_citations-tail.html"
#: A question's notes live beside it: `010-how-deep.html` -> `010-how-deep.notes.html`.
NOTES_SUFFIX = ".notes.html"

GAP = 10
SECTION_DIGITS = 3
ENTRY_DIGITS = 4
#: A registry entry's heading id is its key with this in front: `<h3 id="work-fei-1939">`.
WORK_PREFIX = "work-"

_PREFIXED = re.compile(r"^(\d+)-(.+)\.html$")


def page_dir(page_rel: str) -> str:
    """The directory a page's fragments live in.

    `ways.html` -> `ways`, `cities/defenses.html` -> `cities/defenses`, and the registry
    `SOURCES.html` -> `sources`, which is the one page whose directory is not simply its own name:
    `sources/` says what is in it to a reader who has never seen this scheme.
    """
    if page_rel == "SOURCES.html":
        return "sources"
    return page_rel[: -len(".html")] if page_rel.endswith(".html") else page_rel


def prefix(position: int, digits: int = SECTION_DIGITS) -> str:
    """The gapped prefix of the fragment at `position`, counting from 1: 1 -> `010`, 2 -> `020`."""
    return str(position * GAP).zfill(digits)


def section_file(position: int, heading_id: str) -> str:
    """`010-how-far-past-the-bank-does-a-bridge-land.html`."""
    return f"{prefix(position)}-{heading_id}.html"


def entry_file(position: int, heading_id: str) -> str:
    """`0010-fei-1939.html` - the source's KEY, not the `work-` id, so one glob on the key finds it."""
    return f"{prefix(position, ENTRY_DIGITS)}-{key_of(heading_id)}.html"


def notes_file(section_file_name: str) -> str:
    """The notes beside a question fragment."""
    return section_file_name[: -len(".html")] + NOTES_SUFFIX


def key_of(heading_id: str) -> str:
    """A registry entry's source key: `work-fei-1939` -> `fei-1939`."""
    return heading_id[len(WORK_PREFIX):] if heading_id.startswith(WORK_PREFIX) else heading_id


def ordered(names: list[str]) -> list[str]:
    """The entry fragments of a directory, in prefix order. Names that carry no prefix are not
    entries and are left to the caller - `_front.html` and the rest are placed by the assembly, never
    by sorting, so that a rename cannot silently reorder a page."""
    return sorted((n for n in names if _PREFIXED.match(n) and not n.endswith(NOTES_SUFFIX)),
                  key=lambda n: (int(_PREFIXED.match(n).group(1)), n))  # type: ignore[union-attr]


def position_of(name: str) -> int:
    """The prefix a fragment's name carries, as a number."""
    found = _PREFIXED.match(name)
    if not found:
        raise ValueError(f"{name}: a fragment of an ordered kind must be named <prefix>-<id>.html")
    return int(found.group(1))


def free_prefix(before: int, after: int, digits: int = SECTION_DIGITS) -> str:
    """A prefix strictly between two neighbors, for inserting an entry without renaming anything.

    Raises when the gap is exhausted, rather than pick a number that collides: the directory is then
    re-spaced deliberately, as one commit that changes no assembled byte.
    """
    if after - before < 2:
        raise ValueError(f"no free prefix between {before} and {after} - re-space the directory")
    return str((before + after) // 2).zfill(digits)


def page_of(fragment_path: str) -> str:
    """The page a fragment belongs to, from its path - the inverse of `page_dir` for error messages."""
    return os.path.dirname(fragment_path)
