"""Where a fragment of the REGISTRY lives, and what its name means (features 258, 303).

Since feature 303 the questions are one flat directory of stems (`questions.py`) and the registry is the one page left
as a directory of fragments: `sources/`, its front matter and closing, a group per `<prefix>-<heading id>.html` and the
group's entries in the directory beside it, `<prefix>-<key>.html`. The name carries two things and nothing else: the
ORDER (a gapped numeric prefix) and what the entry IS (the heading's own id, or a source's key).

The prefixes are GAPPED, counting by ten, on the GM's decision of 2026-09-20: *"Gapped (`010-`, `020-`) so inserting a
question doesn't renumber the directory"* - four digits for the registry's entries.
"""

from __future__ import annotations

import re

#: The fragments that are not entries. They sort first and last by name, not by prefix.
FRONT = "_front.html"
TAIL = "_tail.html"

SECTION_DIGITS = 3
#: A registry entry's heading id is its key with this in front: `<h3 id="work-fei-1939">`.
WORK_PREFIX = "work-"

_PREFIXED = re.compile(r"^(\d+)-(.+)\.html$")


def page_dir(page_rel: str) -> str:
    """The directory a page's fragments live in.

    The registry `SOURCES.html` -> `sources`, the one page whose directory is not simply its own name (`sources/` says
    what is in it to a reader who has never seen this scheme); any other page is its own name (`ways.html` -> `ways`).
    """
    if page_rel == "SOURCES.html":
        return "sources"
    return page_rel[: -len(".html")] if page_rel.endswith(".html") else page_rel


def key_of(heading_id: str) -> str:
    """A registry entry's source key: `work-fei-1939` -> `fei-1939`."""
    return heading_id[len(WORK_PREFIX) :] if heading_id.startswith(WORK_PREFIX) else heading_id


def ordered(names: list[str]) -> list[str]:
    """The entry fragments of a directory, in prefix order. Names that carry no prefix are not
    entries and are left to the caller - `_front.html` and the rest are placed by the assembly, never
    by sorting, so that a rename cannot silently reorder a page."""
    return sorted((n for n in names if _PREFIXED.match(n)), key=lambda n: (int(_PREFIXED.match(n).group(1)), n))  # type: ignore[union-attr]


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
