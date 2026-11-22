"""Cross-links between a research page and the drawing page about it (features 292, 303).

The GM, 2026-09-29: how the maps draw a thing belongs in *"a separate collection of files that have to do with our
rendering decisions"*, and the two *"should definitely link to each other. And I think that linking should be automated
rather than something that we write ... the make target that assembles this research page should drop all of that into
place automatically."*

So a link is never typed. Since feature 303 the pairing is the STEM: a question's research page and its drawing page
are `NNNN-<slug>.html` and `NNNN-<slug>.drawing.html`. A second drawing page of a question is its own stem and names
the question it draws once, `<!-- about: NNNN-<slug> -->` (`questions.py` checks it). Either way the build writes a small
link under BOTH headings: on the research page to the drawing page, on the drawing page back. Two-way by construction.

These are bytes the assembly writes rather than copies (the others are footnote numbers, `notes.py`): a link at the
start of the `<h2>`, marked `class="xref"` so the stylesheet can float it small at the right of the heading's line and
so every reader of a heading's text can drop it.

Research: plumbing - NONE
"""

from __future__ import annotations

import re
from dataclasses import dataclass

from l7r.diagram.interactive.record import questions as qs

TO_RENDERING = "How it's drawn"
TO_RESEARCH = "The history behind it"


@dataclass(frozen=True)
class Pair:
    """A drawing page and the research page it is about, by file name."""

    drawing: str
    research: str


def pairs(record: qs.Record) -> list[Pair]:
    """Every drawing page with the research page it is about, in number order."""
    out: list[Pair] = []
    for q in record.questions:
        if q.drawing is None:
            continue
        about = q if q.research is not None else (record.by_stem.get(q.about) if q.about else None)
        if about is not None and about.research is not None:
            out.append(Pair(q.drawing.file, about.research.file))
    return out


def link(page_html: str, page: qs.Page, all_pairs: list[Pair]) -> str:
    """The page with a `<span class="xref">` written at the start of its heading, linking each page it is paired with
    (GM 2026-09-29: *"should be floated to the right-hand side of the same row"*). It is inside the heading, and every
    reader of a heading's text drops it (`sources.page_text`)."""
    anchors = [f'<a href="{p.drawing}">{TO_RENDERING}</a>' for p in all_pairs if p.research == page.file]
    anchors += [f'<a href="{p.research}">{TO_RESEARCH}</a>' for p in all_pairs if p.drawing == page.file]
    if not anchors:
        return page_html
    m = re.search(rf'<h[23] id="{re.escape(page.heading_id)}">', page_html)
    assert m is not None, page.file  # every page's heading was read from this text by `questions.load`
    return page_html[: m.end()] + f'<span class="xref">{" - ".join(anchors)}</span>' + page_html[m.end() :]
