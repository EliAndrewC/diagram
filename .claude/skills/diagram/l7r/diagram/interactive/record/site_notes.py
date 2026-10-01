"""Footnotes in the record's site (feature 301).

The GM, 2026-10-01: *"for the small individual page versions, we do just start the footnotes counting at one every time.
And then ... we can include the footnotes and reference sources at the bottom of each individual page by including only
the ones that are relevant there"*; on the single page, *"one footnote count for everything"*.

A note is written beside the question that FIRST cites it, by key (`notes.py`), and a later question of the same page
may cite it again - so a small page's notes are looked up in its page's merged notes, never in its own notes file
alone (research R4). Numbers are allocated here and typed nowhere, exactly as for the pages they replace.

In a note, a source key links the work's entry - the hover rule of feature 292 (GM 2026-09-29: the tooltip's link
*"should instead take us to ... #work-kashima-kainyo-1987 which itself opens with a `kashima-kainyo-1987` link to the
actual source"*): on a small page the entry is at the page's own foot, on the single page it is in the Sources part.
"""

from __future__ import annotations

import re

from l7r.diagram.interactive.record.notes import REFERENCE, NoteError, Placed, allocate, number_references, render_note

#: A source key as a note carries it - linked to the document, or to the registry where it was not read.
KEY_LINK = re.compile(r'<a href="[^"]*"><code>([a-z0-9][a-z0-9-]*)</code></a>')


def keyed_to(body: str, prefix: str) -> str:
    """A note with each source key linking `<prefix><key>` - `#work-` on a small page, `#` on the single page."""
    return KEY_LINK.sub(lambda m: f'<a href="{prefix}{m.group(1)}"><code>{m.group(1)}</code></a>', body)


def small_page(question: str, page_notes: dict[str, str], where: str) -> tuple[str, list[Placed]]:
    """A question with its references numbered from 1, and its notes in number order.

    Only the notes this question cites are placed: `allocate` refuses a note nothing references, and on a small page
    every other note of the page is referenced elsewhere, by another question."""
    cited = {key: page_notes[key] for key in dict.fromkeys(REFERENCE.findall(question)) if key in page_notes}
    _stripped, placed = allocate(question, cited, where)
    return number_references(question, placed, ""), placed


def foot(placed: list[Placed], works: str) -> str:
    """The foot of a small page: its notes, numbered, each with its way back; then the works they cite."""
    if not placed:
        return ""
    notes = "".join(render_note(Placed(p.key, p.number, keyed_to(p.body, "#work-"), p.references), "") + "\n" for p in placed)
    return (
        '\n<section class="footnotes"><h2 id="page-notes">Notes</h2>\n<ol>\n' + notes + '</ol></section>\n<section class="works"><h2 id="page-works">Works cited here</h2>\n' + works + "\n</section>\n"
    )


class Numbering:
    """One count through the whole single page. A note's key is unique within its page, not across the record, so
    each is qualified by its page; and a note cited twice gets a fresh reference id each time, `fnref-N-2`, so every
    id on the single page is unique and every reference can be returned to."""

    def __init__(self) -> None:
        self.placed: list[tuple[str, Placed]] = []  # (page_rel, the note)
        self._numbers: dict[tuple[str, str], int] = {}
        self._used: dict[int, int] = {}

    def number(self, question: str, page_rel: str, page_notes: dict[str, str], where: str) -> str:
        """`question` with every reference numbered in the single page's count, placing each note the first time."""

        def one(found: re.Match[str]) -> str:
            key = found.group(1)
            if key not in page_notes:
                raise NoteError(f"{where}: a reference names `{key}`, which no note on {page_rel} defines")
            n = self._numbers.get((page_rel, key))
            if n is None:
                n = len(self.placed) + 1
                self._numbers[(page_rel, key)] = n
                self.placed.append((page_rel, Placed(key=key, number=n, body=page_notes[key], references=0)))
            self._used[n] = self._used.get(n, 0) + 1
            ref_id = f"fnref-{n}" if self._used[n] == 1 else f"fnref-{n}-{self._used[n]}"
            return f'<sup class="fn"><a id="{ref_id}" href="#fn-{n}">{n}</a></sup>'

        return REFERENCE.sub(one, question)
