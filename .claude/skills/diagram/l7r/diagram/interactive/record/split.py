"""Taking a page apart: the inverse of the assembly (feature 258).

The splitter exists twice over. Once, to perform the migration; and thereafter as the assembler's
inverse, which is what lets `tests/interactive/test_record_assembly.py` assert
`assemble(split(page)) == page` over the REAL record on every run rather than over a fixture that
would drift away from it.

WHERE IT CUTS, and why the rule is not "at every `<h2>`" (spec FR-008a, research R1). `SOURCES.html`
carries an 8,042-byte HTML comment holding two whole `<h2>` groups - the old citing rules and the
re-sourcing queue - so a plain count reports five sections where a reader sees three. A heading inside a
comment is not a section. A heading is also recognized wherever it stands on its line: the only two in
the record that do not begin their line are both inside that same comment, so that half of the rule
guards a case the record does not carry today, and is written down so no cut is ever anchored to the
line start - which would pass on today's record and fail on the first page that indents a heading.

Byte-identity would NOT have caught either mistake: splitting and rejoining is lossless wherever you
cut, so a splitter that cut a comment in half still assembles back byte for byte while writing
fragments no reader's page has. That is why the tests assert the section count and the heading ids too.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

_COMMENT = re.compile(r"<!--.*?-->", re.S)
_ID = re.compile(r'id="([^"]*)"')
#: What closes a page: the pointer to its citations page where there is one, then the closing tags.
#: Every one of the record's 38 pages ends in exactly this (research R1's companion check, 2026-09-20).
_TAIL = re.compile(r'(?:\n<section class="citations">.*?</section>)?\n</main>\n</body>\n</html>\n?$', re.S)


@dataclass(frozen=True)
class Entry:
    """One entry inside a section - a registry source. `text` is its heading and its body, verbatim."""

    id: str
    text: str


@dataclass(frozen=True)
class Section:
    """One section of a page - a question, or a group of the registry.

    `text` is its heading and everything to the next section, EXCEPT what its entries hold: where a
    section has entries, `text` stops at the first of them, so that assembly is `text` then the
    entries in order, with nothing counted twice.
    """

    id: str
    text: str
    entries: tuple[Entry, ...] = ()


@dataclass(frozen=True)
class Page:
    """A page taken apart. Assembly is `front`, the sections in order, `tail` - and nothing else."""

    front: str
    sections: tuple[Section, ...]
    tail: str


def comments(html: str) -> list[tuple[int, int]]:
    """The [start, end) of every HTML comment."""
    return [(m.start(), m.end()) for m in _COMMENT.finditer(html)]


def headings(html: str, level: int) -> list[re.Match[str]]:
    """Every `<hN` that opens a real section: not one inside a comment, wherever it sits on its line."""
    hidden = comments(html)
    return [m for m in re.finditer(rf"<h{level}\b", html)
            if not any(start <= m.start() < end for start, end in hidden)]


def heading_id(html: str, at: int) -> str:
    """The id of the heading opening at `at`. The record's anchors are these ids, so a heading without
    one is refused rather than given a made-up name."""
    tag_end = html.index(">", at)
    found = _ID.search(html[at:tag_end])
    if not found:
        raise ValueError(f"a heading with no id at offset {at}: {html[at:tag_end + 1]!r} - "
                         f"the record's anchors are heading ids, and a fragment is named for one")
    return found.group(1)


def sections_of(html: str, level: int = 2) -> tuple[Section, ...]:
    """The sections of a page, in order, with no entries read - what a reader's table of contents is."""
    return split(html, entry_level=None, level=level).sections


def split(html: str, entry_level: int | None = None, level: int = 2) -> Page:
    """Take a page apart into front, sections and tail.

    `entry_level` is the heading level whose occurrences inside a section are ENTRIES of their own -
    3 for the registry, whose works roster holds 920 of them. It is passed rather than guessed: a
    research page may one day carry an `<h3>` inside a question, and a splitter that helpfully turned
    it into a separate entry would quietly change what a fragment is.
    """
    tail_at = _tail_start(html)
    opens = [m.start() for m in headings(html, level) if m.start() < tail_at]
    if not opens:
        return Page(front=html[:tail_at], sections=(), tail=html[tail_at:])
    bounds = list(zip(opens, opens[1:] + [tail_at]))
    return Page(
        front=html[: opens[0]],
        sections=tuple(_section(html, start, stop, entry_level) for start, stop in bounds),
        tail=html[tail_at:],
    )


def _section(html: str, start: int, stop: int, entry_level: int | None) -> Section:
    body = html[start:stop]
    if entry_level is None:
        return Section(id=heading_id(html, start), text=body)
    opens = [m.start() for m in headings(body, entry_level)]
    if not opens:
        return Section(id=heading_id(html, start), text=body)
    bounds = list(zip(opens, opens[1:] + [len(body)]))
    return Section(
        id=heading_id(html, start),
        text=body[: opens[0]],
        entries=tuple(Entry(id=heading_id(body, at), text=body[at:end]) for at, end in bounds),
    )


def _tail_start(html: str) -> int:
    """Where the closing run begins. Refused rather than guessed: a page that does not end the way
    every page of the record ends is a page this splitter has not been shown."""
    found = _TAIL.search(html)
    if not found:
        raise ValueError("this page does not end with `</main></body></html>` and its optional "
                         "citations pointer - the splitter has not been shown its shape")
    return found.start()
