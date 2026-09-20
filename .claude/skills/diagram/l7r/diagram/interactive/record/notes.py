"""Footnotes that carry a name instead of a number (feature 258, stage 3).

A note is written beside the question that references it, in `NNN-<slug>.notes.html`, and both sides
name it by a KEY:

    in the question:  <sup class="fn" data-note="bearing-length"></sup>
    in its notes:     <li data-note="bearing-length">... the quoted passage and the gloss ...</li>

Every number on both pages is allocated HERE, at assembly, in the order the references appear in the
assembled research page. Nothing in a fragment carries one.

WHY, measured (research R4, R5): 16 of the record's 19 pages carry their references out of document
order, because a note added mid-page either renumbers everything after it by hand or is appended out
of order, and 1,860 references is far too many to renumber by hand. Two defects fall out of allocating
instead of typing: 4 references carry no `id` at all, so no back link can return to them, and 2 pages
carry a duplicated reference id, which is invalid HTML and a back link that can only resolve to one of
the two. Both disappear here rather than being separately fixed.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

#: A reference in a question fragment. It carries a key and no number.
#: The key is matched LOOSELY and validated after, so a malformed one is refused rather than passed
#: over: a pattern that only matches well formed keys drops a mistyped one silently, and a dropped
#: reference is an assertion that loses its footnote with nothing said.
REFERENCE = re.compile(r'<sup class="fn" data-note="([^"]*)"></sup>')
#: A note in a notes fragment. Same: a key, no number, and no back link - the assembly writes that.
NOTE = re.compile(r'<li data-note="([^"]*)">(.*?)</li>', re.S)
_KEY = re.compile(r"^[a-z0-9][a-z0-9-]*$")


class NoteError(Exception):
    """A refusal about notes. Its message names the key and the file."""


@dataclass(frozen=True)
class Placed:
    """One note, after allocation: its key, its number, its body, and every reference to it."""

    key: str
    number: int
    body: str
    references: int


def allocate(page_html: str, keys_defined: dict[str, str], where: str = "") -> tuple[str, list[Placed]]:
    """Number the references in `page_html` in the order they appear, and place their notes.

    Returns the page with each reference rewritten to the numbered anchor the record carries, and the
    notes in number order. `keys_defined` is {key: body} gathered from the page's notes fragments.
    """
    order: list[str] = []
    seen: dict[str, int] = {}
    counts: dict[str, int] = {}
    for found in REFERENCE.finditer(page_html):
        key = found.group(1)
        if not _KEY.match(key):
            raise NoteError(f"{where}: `{key}` is not a note key - lower case, digits and hyphens")
        if key not in keys_defined:
            raise NoteError(f"{where}: a reference names `{key}`, which no note on this page defines")
        if key not in seen:
            order.append(key)
            seen[key] = len(order)
        counts[key] = counts.get(key, 0) + 1
    unused = [k for k in keys_defined if k not in seen]
    if unused:
        raise NoteError(
            f"{where}: {', '.join(sorted(unused))} - defined as a note, referenced nowhere. "
            f"A note nothing cites is either a reference that was deleted or a note that was "
            f"never wired up; the assembly will not quietly drop it"
        )
    placed = [Placed(key=k, number=seen[k], body=keys_defined[k], references=counts[k]) for k in order]
    return REFERENCE.sub(lambda m: "", page_html), placed


def number_references(page_html: str, placed: list[Placed], citations_href: str) -> str:
    """Rewrite every reference into the numbered anchor a reader's page carries.

    A key referenced more than once gets a document-unique id per reference - `fnref-N`, `fnref-N-2` -
    so that every `id` on the page is unique and every reference can be returned to. The note's back
    link points at the first (`render_note`).
    """
    numbers = {p.key: p.number for p in placed}
    used: dict[str, int] = {}

    def one(found: re.Match[str]) -> str:
        key = found.group(1)
        n = numbers[key]
        used[key] = used.get(key, 0) + 1
        ref_id = f"fnref-{n}" if used[key] == 1 else f"fnref-{n}-{used[key]}"
        return f'<sup class="fn"><a id="{ref_id}" href="{citations_href}#fn-{n}">{n}</a></sup>'

    return REFERENCE.sub(one, page_html)


def render_note(placed: Placed, page_href: str) -> str:
    """One `<li>` of a citations page: the number, the body as written, and the back link."""
    return f'<li id="fn-{placed.number}">{placed.body} <a class="fnback" href="{page_href}#fnref-{placed.number}">back</a></li>'


def notes_of(fragment: str, where: str = "") -> dict[str, str]:
    """{key: body} from one notes fragment, refusing what the contract refuses."""
    out: dict[str, str] = {}
    for found in NOTE.finditer(fragment):
        key, body = found.group(1), found.group(2)
        if not _KEY.match(key):
            raise NoteError(f"{where}: `{key}` is not a note key - lower case, digits and hyphens")
        if key in out:
            raise NoteError(f"{where}: `{key}` is defined twice in one file")
        out[key] = body
    return out


def merge(per_question: list[tuple[str, dict[str, str]]]) -> dict[str, str]:
    """Every note of a page, from its questions' notes fragments, refusing a key defined twice."""
    out: dict[str, str] = {}
    seen: dict[str, str] = {}
    for where, notes in per_question:
        for key, body in notes.items():
            if key in out:
                raise NoteError(f"`{key}` is defined in {seen[key]} and again in {where} - a note key is unique within its page, because the reference names it and nothing else")
            out[key], seen[key] = body, where
    return out


def derive_key(source_key: str | None, question_slug: str, taken: set[str]) -> str:
    """The key the SPLITTER gives a note that has only ever had a number.

    From the note's own leading source key where it has one - 1,524 of 1,850 do (R5) - with an ordinal
    where a page cites the same work more than once, which 635 notes do. A note that leads with no
    source key takes its question's slug and an ordinal: an absence note, a note reasoning from several
    works, a note quoting the GM.
    """
    stem = source_key or question_slug
    if stem not in taken:
        return stem
    n = 2
    while f"{stem}-{n}" in taken:
        n += 1
    return f"{stem}-{n}"
