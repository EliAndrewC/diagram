"""Cross-links between a research section and the rendering section about it (feature 292).

The GM, 2026-09-29: how the maps draw a thing belongs in *"a separate collection of files that have to do with our
rendering decisions"*, and the two *"should definitely link to each other. And I think that linking should be automated
rather than something that we write ... the make target that assembles this research page should drop all of that into
place automatically."*

So a link is never typed. A rendering section declares, once, the research section it is about - a comment on the
line after its heading, `<!-- about: homesteads.html#groves-of-trees-around-farmhouses-yashikirin -->` - and the
assembly writes a small link under BOTH headings: on the research section to the rendering one, on the rendering
section back. Two-way by construction: there is one declaration and no second place to forget.

These are the second bytes the assembly writes rather than copies (the first are footnote numbers, `notes.py`): a
link at the start of the `<h2>`, marked `class="xref"` so the stylesheet can float it small at the right of the heading's
line and so every reader of a heading's text can drop it. A declaration naming a section that does not exist is a
refusal, not a silently missing link.
"""

from __future__ import annotations

import os
import re
from dataclasses import dataclass

from l7r.diagram.interactive.record import fragments as frag

#: The rendering collection (`sources.COLLECTIONS`), whose sections carry the declarations.
RENDERING = "rendering"
ABOUT = re.compile(r"<!-- about: ((?:[a-z-]+/)?[a-z-]+\.html)#([^\s]+) -->")
TO_RENDERING = "How it's drawn"
TO_RESEARCH = "The history behind it"


@dataclass(frozen=True)
class Pair:
    """One rendering section and the research section it is about."""

    rendering_page: str  # `rendering/homesteads.html`
    rendering_id: str
    research_page: str  # `homesteads.html`
    research_id: str


def _heading_id(text: str) -> str:
    m = re.match(r'\s*<h[23] id="([^"]+)"', text)
    return m.group(1) if m else ""


def pairs(record_dir: str) -> list[Pair]:
    """Every declaration in the rendering collection, in page and prefix order."""
    root = os.path.join(record_dir, RENDERING)
    out: list[Pair] = []
    if not os.path.isdir(root):
        return out
    for page in sorted(d for d in os.listdir(root) if os.path.isdir(os.path.join(root, d))):
        where = os.path.join(root, page)
        for name in frag.ordered(os.listdir(where)):
            with open(os.path.join(where, name), encoding="utf-8") as fh:
                text = fh.read()
            for m in ABOUT.finditer(text):
                out.append(Pair(f"{RENDERING}/{page}.html", _heading_id(text), m.group(1), m.group(2)))
    return out


def _href(from_page: str, to_page: str, anchor: str) -> str:
    return os.path.relpath(to_page, os.path.dirname(from_page) or ".").replace(os.sep, "/") + "#" + anchor


def _links_for(page_rel: str, all_pairs: list[Pair]) -> dict[str, list[str]]:
    """{section id: [link html]} for the sections of this page that a declaration joins."""
    links: dict[str, list[str]] = {}
    for p in all_pairs:
        if p.research_page == page_rel:
            links.setdefault(p.research_id, []).append(f'<a href="{_href(page_rel, p.rendering_page, p.rendering_id)}">{TO_RENDERING}</a>')
        if p.rendering_page == page_rel:
            links.setdefault(p.rendering_id, []).append(f'<a href="{_href(page_rel, p.research_page, p.research_id)}">{TO_RESEARCH}</a>')
    return links


def link(page_html: str, page_rel: str, all_pairs: list[Pair]) -> str:
    """The assembled page with a `<span class="xref">` written at the start of each joined section's heading, which the
    stylesheet floats to the right of the heading's own line (GM 2026-09-29: *"should be floated to the right-hand side
    of the same row"*). It is inside the heading, and every reader of a heading's text drops it (`sources.page_text`)."""
    for section_id, anchors in _links_for(page_rel, all_pairs).items():
        m = re.search(rf'<h[23] id="{re.escape(section_id)}">', page_html)
        if m is None:
            continue  # the target side is checked by `unresolved`, which names the declaration
        page_html = page_html[: m.end()] + f'<span class="xref">{" - ".join(anchors)}</span>' + page_html[m.end() :]
    return page_html


def unresolved(all_pairs: list[Pair], record_dir: str) -> list[str]:
    """Each declaration whose research section, or whose own rendering section, is not on its page - a message per
    pair, naming the declaration, for `make record` to refuse on."""
    bad = []
    for p in all_pairs:
        for page, anchor in ((p.research_page, p.research_id), (p.rendering_page, p.rendering_id)):
            where = os.path.join(record_dir, frag.page_dir(page))
            ids = set()
            if os.path.isdir(where):
                for name in frag.ordered(os.listdir(where)):
                    with open(os.path.join(where, name), encoding="utf-8") as fh:
                        ids.add(_heading_id(fh.read()))
            if anchor not in ids:
                bad.append(f"{p.rendering_page}: `about: {p.research_page}#{p.research_id}` - no section `{anchor}` on {page}")
    return bad
