"""The pieces every page of the record's site is made of (features 301, 303): the page shell, the trail of links at its
top, a listing of questions, the pager, and the navigation tree as data. `site.py` is the build that uses them.

The site's layout (spec 303 plan D6):

    index.html                     home: both halves, their sections nested as `contents.json` nests them; tags; sources
    findings/<section>.html        a section's page in the research half: its description, subsections and questions
    drawing/<section>.html         the same section in the half on how our maps draw it
    q/<heading id>.html            a question page of either half - flat, so a regrouping moves no URL (FR-004)
    tags/<facet>-<tag>.html        every question carrying one tag (FR-014)
    sources/<key>.html, sources/index.html     the registry
    all.html, nav.js, assets/
"""

from __future__ import annotations

import html
import json
from dataclasses import dataclass

from l7r.diagram.interactive.record import contents as ct
from l7r.diagram.interactive.record import questions as qs
from l7r.diagram.interactive.record import site_links as links
from l7r.diagram.interactive.sources import linkify

TITLE = "The research record"
#: The two halves of the record, in the order they are read. A section is shown in a half only when it, or one of its
#: subsections, holds a page of that half (spec 303 FR-012, FR-013).
HALVES = (("research", "The research"), ("drawing", "How our maps draw it"))
#: Where each half's section pages are in the site. Not `research/`: a path `research/<x>.html` is what the pointer check
#: refuses as a retired built page of the record (`scripts/gates/check-research-pointers.py`), and a site path must not read
#: as one.
HALF_DIR = links.SECTION_DIR
REGISTRY_GROUP = "Sources"
TAGS_GROUP = "Tags"
FACET_NAMES = {"subject": "Subject", "setting": "Setting", "level": "Level"}


@dataclass
class Item:
    """A question page or a registry entry: one small page."""

    id: str
    html: str
    title: str
    lead: str
    page: qs.Page | None = None


def root_of(here: str) -> str:
    """From a site file to the site root: `` for `index.html`, `../` for `q/x.html`."""
    return "../" * here.count("/")


def frame(title: str, here: str, open_keys: str, *, lazy_glossary: bool = False) -> tuple[str, str]:
    """The text a site page writes before its content and after it: the head, the navigation the script draws, and
    `<main>` around the content. `open_keys` names the sections of the navigation open on this page; `lazy_glossary`
    marks the single page, whose glossary hover `record.js` wraps a heading's run at a time as it nears the screen
    (feature 301 research R8).

    Research: page frame - NONE: process plumbing"""
    root = root_of(here)
    head = (
        "<!DOCTYPE html>\n<html lang=\"en\">\n<head>\n<meta charset=\"utf-8\">\n"
        '<meta name="viewport" content="width=device-width, initial-scale=1">\n'
        f"<title>{html.escape(title)}</title>\n"
        f'<link rel="stylesheet" href="{root}assets/record.css">\n<link rel="stylesheet" href="{root}assets/site.css">\n'
        f'<script src="{root}assets/theme.js"></script>\n'
        f'<script src="{root}assets/glossary.js" defer></script>\n'
        f'<script src="{root}nav.js" defer></script>\n<script src="{root}assets/site.js" defer></script>\n'
        f'<script src="{root}assets/record.js" defer></script>\n'
        "</head>\n"
        f'<body class="site" data-root="{root}" data-part="{html.escape(open_keys)}" data-page="{html.escape(here)}"{" data-lazy-glossary" if lazy_glossary else ""}>\n'
        '<div class="layout">\n<nav id="sidebar" aria-label="Contents">'
        f'<noscript><p><a href="{root}index.html">Contents</a> - <a href="{root}all.html">the whole record on one page</a></p></noscript></nav>\n'
        "<main>\n"
    )
    return head, "\n</main>\n</div>\n</body>\n</html>\n"


def shell(title: str, here: str, open_keys: str, body: str, *, lazy_glossary: bool = False) -> str:
    """A site page: its frame (`frame`) around its content, every bare URL in the content made a link."""
    head, tail = frame(title, here, open_keys, lazy_glossary=lazy_glossary)
    return head + linkify(body) + tail


def shell_utf8(title: str, here: str, open_keys: str, body: list[str], *, lazy_glossary: bool = False) -> bytes:
    """`shell` for a page given in PIECES, as its UTF-8 bytes - the single page's form; the list is CONSUMED.

    Feature 323: the single page (`all.html`, 42 MB as Python text) had been joined whole, linkified - which splits it whole
    into parts - and copied into the page, four to five copies at once; linking each piece in place and joining once took the
    build's peak 312 -> 236 MB, every file byte-identical (specs/323-site-build-peak/research.md R1, R2). A piece is a whole
    fragment, so linking each finds what linking the whole would. Feature 327: the site holds its pages as UTF-8, so each
    piece is linked AND encoded in place and the bytes joined - the 42 MB of text is never one string, and the page goes into
    the site as it will be written (specs/327-lean-site-fast-clip/research.md R2)."""
    head, tail = frame(title, here, open_keys, lazy_glossary=lazy_glossary)
    body.reverse()
    encoded = [head.encode("utf-8")]
    while body:  # each piece leaves the list as it is encoded, so its text is freed with it
        encoded.append(linkify(body.pop()).encode("utf-8"))
    encoded.append(tail.encode("utf-8"))
    return b"".join(encoded)


def half_title(half: str) -> str:
    return dict(HALVES)[half]


def section_file(half: str, section: ct.Section) -> str:
    return f"{HALF_DIR[half]}/{section.id}.html"


def tag_file(facet: str, tag: str) -> str:
    return f"tags/{facet}-{tag}.html"


def node_key(half: str, section: ct.Section) -> str:
    """A section's key in the navigation, which a page names to open it: its half's directory and its id."""
    return f"{HALF_DIR[half]}/{section.id}"


def open_keys(half: str, section: ct.Section | None) -> str:
    """The navigation nodes open on a page of this section: the section and its ancestors."""
    return " ".join(node_key(half, s) for s in section.path()) if section is not None else ""


def crumbs(here: str, trail: list[tuple[str, str]]) -> str:
    """The trail at the top of a page: the record's home, then each (title, site file) given."""
    root = root_of(here)
    links = [f'<a href="{root}index.html">{TITLE}</a>'] + [f'<a href="{root}{f}">{html.escape(t)}</a>' for t, f in trail]
    return '<p class="crumbs">' + " &rsaquo; ".join(links) + "</p>\n"


def section_trail(half: str, section: ct.Section) -> list[tuple[str, str]]:
    return [(s.title, section_file(half, s)) for s in section.path()]


def description(section: ct.Section, half: str) -> str:
    """What a section says of itself in one half."""
    return section.drawing_description if half == "drawing" else section.description


def listing(items: list[Item], here: str) -> str:
    """Questions as a list: each title linked to its page, its opening sentence beside it."""
    root = root_of(here)
    rows = []
    for item in items:
        lead = f' <span class="lead">{html.escape(item.lead)}</span>' if item.lead else ""
        rows.append(f'<li><a href="{root}q/{item.id}.html">{html.escape(item.title)}</a>{lead}</li>')
    return '<ul class="questions">\n' + "\n".join(rows) + "\n</ul>\n"


def pager(items: list[Item], at: int, here: str, folder: str) -> str:
    """Links to the previous and next pages of a run: a section's questions, or the registry's entries."""
    root = root_of(here)
    prev = f'<a rel="prev" href="{root}{folder}/{items[at - 1].id}.html">&lsaquo; {html.escape(items[at - 1].title)}</a>' if at > 0 else "<span></span>"
    nxt = f'<a rel="next" href="{root}{folder}/{items[at + 1].id}.html">{html.escape(items[at + 1].title)} &rsaquo;</a>' if at + 1 < len(items) else "<span></span>"
    return f'<nav class="pager">{prev}{nxt}</nav>\n'


def tags_line(tags: ct.Tags, vocab: ct.Vocabulary, here: str) -> str:
    """A question's tags, each linking its tag page (spec 303 FR-014)."""
    root = root_of(here)
    links = [f'<a href="{root}{tag_file(f, t)}">{html.escape(vocab.facet(f)[t].name)}</a>' for f, t in tags.all()]
    return '<p class="tags"><em>Tags:</em> ' + ", ".join(links) + "</p>\n"


def nav_tree(record: qs.Record, items: dict[str, Item], sources: list[dict]) -> dict:
    """The navigation as data: each half's sections nested with their questions, the tags, and the sources - their works
    sections straight under the Sources heading, each with its kinds and works beneath (feature 307)."""

    def node(half: str, section: ct.Section) -> dict:
        return {
            "key": node_key(half, section),
            "title": section.title,
            "href": section_file(half, section),
            "sections": [node(half, s) for s in section.sections if record.holds(s, half)],
            "items": [[items[p.file].title, f"q/{items[p.file].id}.html"] for p in record.in_section(section, half)],
        }

    groups = [{"label": label, "sections": [node(half, s) for s in record.sections if record.holds(s, half)]} for half, label in HALVES]
    tag_nodes = [
        {"key": f"tags/{facet}", "title": FACET_NAMES[facet], "href": "index.html#tags", "sections": [], "items": [[t.name, tag_file(facet, t.id)] for t in facet_tags(record.vocab, facet)]}
        for facet in ct.FACETS
    ]
    groups.append({"label": TAGS_GROUP, "sections": tag_nodes})
    groups.append({"label": REGISTRY_GROUP, "sections": sources})
    return {"title": TITLE, "home": "index.html", "all": "all.html", "groups": groups}


def facet_tags(vocab: ct.Vocabulary, facet: str) -> list[ct.Tag]:
    """A facet's tags in the vocabulary's order."""
    return vocab.level if facet == "level" else list(vocab.facet(facet).values())


def nav_js(tree: dict) -> str:
    """The navigation tree, once, as data, read by `assets/site.js` on every page (feature 301 research R3)."""
    return "// DERIVED FILE - written by `make record` from the record's fragments (features 301, 303). Never edit here.\nwindow.RECORD_NAV = " + json.dumps(tree, ensure_ascii=False) + ";\n"
