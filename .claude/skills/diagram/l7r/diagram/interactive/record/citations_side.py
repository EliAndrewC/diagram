"""The citations page, and the one-time move of its notes beside their questions (feature 258, stage 3).

A citations page is assembled from four things, in this order:

    _citations-front.html   doctype through `<section class="works">` and its heading  - hand-authored
    the works block         DERIVED, between the two markers `citations.py` itself emits
    _citations-mid.html     `</section>`, the notes heading, `<section class="footnotes"><ol>`
    the notes               from each question's `.notes.html`, in the order the page cites them
    _citations-tail.html    `</ol></section>` and the closing tags                     - hand-authored

**`citations.py` is not taught about fragments** (spec FR-029, the plan review of 2026-09-20). The
assembly hands it an assembled PAGE, exactly as it reads a committed one: the page is written with the
works region as it stands, `derive()` reads it from disk, and the page is written again with the region
filled. The works depend on the notes and the notes on nothing, so two passes settle it.

**The works list moves with the notes, and that is declared** (spec SC-003). `cited_keys()` walks the
notes in page order, so reordering them reorders that list - the ORDER on 16 of 19 pages, the SET on
none. It is the same correction as the renumbering: the derivation's own contract says "in order of
first citation", which before this meant first in the notes' arbitrary order and after it means first
in the reader's page.
"""

from __future__ import annotations

import os
import re

from l7r.diagram.interactive.citations import WORKS_CLOSE, WORKS_OPEN
from l7r.diagram.interactive.record import fragments as frag
from l7r.diagram.interactive.record.notes import Placed, derive_key, render_note

#: A reference as the record carries it today, before the move: the two shapes it is written in
#: (with and without an `id`), and the hand-made `fnref-75b` that `water.html` uses where one note is
#: cited twice - the very case FR-021 replaces with an allocated `fnref-N-2`.
OLD_REFERENCE = re.compile(r'<sup class="fn"><a (?:id="fnref-\d+[a-z]?" )?href="[^"]*#fn-(\d+)">\d+</a></sup>')
#: A note as the record carries it today. Its back link is regenerated, so it is not part of the body.
OLD_NOTE = re.compile(r'<li id="fn-(\d+)">(.*?)</li>', re.S)
_BACK = re.compile(r'\s*<a class="fnback" href="[^"]*">back</a>\s*$', re.S)
#: The source key a note leads with, where it has one - 1,524 of 1,850 do (research R5).
_LEADING_KEY = re.compile(r'^\s*<a href="[^"]*"><code>([a-z0-9][a-z0-9-]*)</code></a>')
_EMPTY_WORKS = WORKS_OPEN + "\n" + WORKS_CLOSE


def citations_rel(page_rel: str) -> str:
    """`ways.html` -> `citations/ways.html`; `cities/fabric.html` -> `citations/cities/fabric.html`."""
    return f"citations/{page_rel}"


def citations_href(page_rel: str) -> str:
    """Where a research page's reference points: relative to the page's own depth, never stored."""
    return "../" * page_rel.count("/") + citations_rel(page_rel)


def page_href(page_rel: str) -> str:
    """Where a note's back link points, from the citations page back to the research page."""
    return "../" * (citations_rel(page_rel).count("/")) + page_rel


def old_notes(citations_html: str) -> dict[int, str]:
    """{number: body} from a citations page as it stands today, the back link stripped off."""
    return {int(n): _BACK.sub("", body) for n, body in OLD_NOTE.findall(citations_html)}


def leading_key(body: str) -> str | None:
    found = _LEADING_KEY.match(body)
    return found.group(1) if found else None


def keys_for(page_html: str, notes: dict[int, str], slug_of: dict[int, str]) -> dict[int, str]:
    """The key each numbered note takes, walking the references in the order a reader meets them.

    `slug_of` is the question slug each number is first referenced from, which is what names a note
    that leads with no source key (326 of them).
    """
    taken: set[str] = set()
    keys: dict[int, str] = {}
    for found in OLD_REFERENCE.finditer(page_html):
        number = int(found.group(1))
        if number in keys or number not in notes:
            continue
        key = derive_key(leading_key(notes[number]), slug_of.get(number, "note"), taken)
        taken.add(key)
        keys[number] = key
    return keys


def to_key_form(fragment_html: str, keys: dict[int, str]) -> str:
    """One question fragment, with every numbered reference replaced by its key."""

    def one(found: re.Match[str]) -> str:
        number = int(found.group(1))
        return f'<sup class="fn" data-note="{keys[number]}"></sup>' if number in keys else found.group(0)

    return OLD_REFERENCE.sub(one, fragment_html)


def split_regions(citations_html: str) -> tuple[str, str, str]:
    """(front, mid, tail) - everything of a citations page that is neither derived nor a note."""
    if WORKS_OPEN not in citations_html or WORKS_CLOSE not in citations_html:
        raise ValueError("this citations page carries no works markers - `make citations` writes them")
    front = citations_html[: citations_html.index(WORKS_OPEN)]
    after = citations_html[citations_html.index(WORKS_CLOSE) + len(WORKS_CLOSE) :]
    first_note = after.index("<li id=") if "<li id=" in after else len(after)
    mid = after[:first_note]
    tail = after[after.rindex("</li>") + len("</li>") :] if "</li>" in after else after[first_note:]
    return front, mid, tail


def assemble_citations(front: str, works: str, mid: str, placed: list[Placed], tail: str, back_to: str) -> str:
    """The citations page as a reader opens it, with the notes numbered and their back links written."""
    body = "".join(render_note(note, back_to) + "\n" for note in placed)
    return front + works + mid + body + tail.lstrip("\n")


def works_region(citations_html: str) -> str:
    """The derived block as it stands in a committed page, markers included - or empty markers."""
    if WORKS_OPEN in citations_html and WORKS_CLOSE in citations_html:
        start = citations_html.index(WORKS_OPEN)
        return citations_html[start : citations_html.index(WORKS_CLOSE) + len(WORKS_CLOSE)]
    return _EMPTY_WORKS


def notes_fragment(bodies: list[tuple[str, str]]) -> str:
    """A question's notes file: one `<li data-note=...>` per note, in the order the question cites them."""
    return "".join(f'<li data-note="{key}">{body}</li>\n' for key, body in bodies)


def question_slugs(record_dir: str, page_rel: str, names: list[str]) -> dict[str, str]:
    """{fragment file name: its heading id}, which is the slug a keyless note is named from."""
    return {name: frag.ordered([name])[0].split("-", 1)[1][: -len(".html")] for name in names if os.path.basename(name).split("-", 1)[0].isdigit()}
