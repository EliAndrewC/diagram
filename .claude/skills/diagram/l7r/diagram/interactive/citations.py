"""The record's CITATIONS PAGES (feature 211, GM 2026-09-07) - what is derived from them, and how.

Every research page `research/<name>.html` has a citations page `research/citations/<name>.html`
(`citations/cities/<name>.html` for a `cities/` page) holding its footnotes - the hand-authored store of every
note's key link, quoted passage and gloss. The GM: *"All of the citations at the end of a research file can be moved
into the citations document. We should be careful to avoid duplicating content because currently the tooltips ...
display the actual content ... we probably need to do something like move our citations into a third location that
can be loaded by both of the different pages."* What is DERIVED from that one store:

- **the works section** of the citations page - for each work the page's footnotes cite, in order of first citation:
  its citation line, and the two write-ups its registry entry carries (what it is; why it applies, and its limits).
  Written once per work in `SOURCES.html` (spec D2: *"we do not want to have multiple different write ups of a single
  paper"*), derived here between two markers.

Since feature 301 the citations page is assembled IN MEMORY (`record/store.assemble_pages`, through `fill_works`) and
never written: the record's reader opens the site `make record` builds (`record/site.py`), where each small page
carries its own notes and the works they cite at its foot, and the single page carries every note. The derived hover
script `citations/<name>.js` of feature 211 is retired with the pages it served - a note on a small page is IN the
page, which is where `record.js` looks first.

Nothing is typed twice: the notes live beside their questions, the write-ups in the registry, and everything else is
a derivation.
"""

from __future__ import annotations

import os
import re

from l7r.diagram.interactive.record import absence
from l7r.diagram.interactive.sources import RESEARCH_DIR, WHAT_LABEL, WHY_LABEL, collection_pages, is_page_dir, link_target, page_rel_of, registry_entries

#: A note on a citations page: its number and its inner HTML.
NOTE = re.compile(r'<li id="fn-(\d+)">(.*?)</li>', re.S)
_KEY_LINK = re.compile(r'<a href="[^"]*"><code>([a-z0-9][a-z0-9-]*)</code></a>')
_BACK = re.compile(r'\s*<a class="fnback" href="[^"]*">back</a>')
#: The markers the works section is derived between. Everything between them is `make citations`' output;
#: the test fails while it differs, and the message says which page.
WORKS_OPEN = "<!-- works-cited: DERIVED by `make citations` from SOURCES.html - change a work's write-up in its registry entry, never here -->"
WORKS_CLOSE = "<!-- /works-cited -->"
_WORKS = re.compile(re.escape(WORKS_OPEN) + r".*?" + re.escape(WORKS_CLOSE), re.S)


def research_pages(research_dir: str = RESEARCH_DIR) -> list[str]:
    """The research pages, as paths relative to `research/` - `homesteads.html`, `cities/fabric.html` - in sorted
    order. The registry and the citations pages are not research pages."""
    top = sorted(page_rel_of(d) for d in os.listdir(research_dir) if d != "sources" and is_page_dir(os.path.join(research_dir, d)))
    return top + collection_pages(research_dir)


def citations_page(page_rel: str) -> str:
    """`homesteads.html` -> `citations/homesteads.html`; `cities/fabric.html` -> `citations/cities/fabric.html`."""
    return f"citations/{page_rel}"


def rel_to_research(citations_rel: str) -> str:
    """The prefix that reaches `research/` from a citations page: `../` for `citations/x.html`, `../../` for
    `citations/cities/x.html`."""
    return "../" * citations_rel.count("/")


def notes(citations_html: str) -> list[tuple[str, str]]:
    """(number, inner HTML) for every `<li id="fn-n">` on a citations page, in page order."""
    return [(m.group(1), m.group(2).strip()) for m in NOTE.finditer(citations_html)]


def cited_keys(page_notes: list[tuple[str, str]]) -> list[str]:
    """The registry keys the notes cite, in order of first citation, once each - the order the works section lists
    them (spec D7: the reader arrives from a footnote, so the list follows the page's own order)."""
    keys: list[str] = []
    for _n, body in page_notes:
        for k in _KEY_LINK.findall(body):
            if k not in keys:
                keys.append(k)
    return keys


def works_html(keys: list[str], entries: dict[str, dict[str, str]], rel: str) -> tuple[str, list[str]]:
    """The works section's derived block for `keys`, and the keys whose entry lacks a write-up (a gate failure - a
    new source cannot be cited without one, spec FR-003). Each work: its key linked as feature 190 links it (the
    document when read, the registry entry when not), its citation line, and the two write-ups."""
    parts = [WORKS_OPEN]
    missing: list[str] = []
    for key in keys:
        e = entries.get(key)
        if e is None or not e["what"] or not e["why"]:
            missing.append(key)
            continue
        parts.append(f'<h3 id="work-{key}"><a href="{link_target(key, e["line"], rel)}"><code>{key}</code></a></h3>')
        parts.append(f"<p>{e['cite']}</p>")
        parts.append(f"<p><em>{WHAT_LABEL}</em> {e['what']}</p>")
        parts.append(f"<p><em>{WHY_LABEL}</em> {e['why']}</p>")
    parts.append(WORKS_CLOSE)
    return "\n".join(parts), missing


def with_works(citations_html: str, block: str) -> str:
    """The citations page with its works region replaced by `block`. A page without the two markers is not a
    citations page in the record's form and is refused rather than guessed at."""
    if not _WORKS.search(citations_html):
        raise ValueError("no works-cited markers - a citations page carries WORKS_OPEN and WORKS_CLOSE")
    return _WORKS.sub(lambda _m: block, citations_html, count=1)


def fill_works(page_rel: str, citations_html: str, research_dir: str = RESEARCH_DIR) -> tuple[str, list[str]]:
    """For one research page: (its citations page with the works section derived, the keys with no write-up). Reads
    the registry through the record's in-memory assembly; reads and writes no file of its own (feature 301 - the
    citations page is assembled in memory and never committed)."""
    block, missing = works_html(cited_keys(notes(citations_html)), registry_entries(research_dir), rel_to_research(citations_page(page_rel)))
    return with_works(citations_html, block), missing


# ---------------------------------------------------------------------------------------------
# WHAT KIND OF NOTE IS THIS? (feature 195, GM 2026-09-06; the third form feature 235, GM 2026-09-12)
#
# One classifier, in the engine, because three readers ask the question and none of them may answer it
# differently: the gate's `tests/interactive/test_footnotes.py`, the `footnote-census` tool, and any later
# reader of the record. It lived in the test file until feature 235, which is where the census had to import
# it from - a dependency the wrong way round (`tests/` is invisible to the generation cache and is not a
# place engine code may import from).
# ---------------------------------------------------------------------------------------------

#: An ABSENCE note: no key, no link, what was searched and when. THE BACKLOG - the only kind that owes work.
#: Since feature 292 the search may be an HTML comment after the marker - the reader is not shown what was searched or
#: when (`record/absence.py`) - and a rendered page is read through `absence.unrender`.
ABSENCE = re.compile(r"^no publicly readable source\s*(?:\(searched \d{4}-\d{2}-\d{2}:|<!--\s*searched \d{4}-\d{2}-\d{2}:)")
#: An absence searched to exhaustion by two dated passes carries the marker beside its search (feature 235 FR-004).
SETTLED = re.compile(r"settled \d{4}-\d{2}-\d{2}")
#: THE SIX REASONS A GROUNDS NOTE MAY NAME (feature 235, GM 2026-09-12: *"if we're counting things that are not
#: actually problems in a category that is meant to denote problems, then we're just gonna keep getting
#: confused"*). Closed on purpose: free text would make the new kind a place to put anything inconvenient, which
#: is how a category meant to denote problems stops denoting them. Adding a seventh is a change to the spec, not
#: a judgment at writing time.
GROUNDS_REASONS = (
    "measured on our own maps",
    "the record's own silence",
    "follows from the definitions",
    "physical necessity",
    "a drawing convention",
    "this project's decision",
)
#: The reason is captured with `*` rather than `+` so that a grounds note with NO reason is a grounds note
#: with a defect the classifier can name, rather than an unrecognized note the reader has to work out.
GROUNDS = re.compile(r"^no source is owed:\s*(.*?)\s*(?:<!--|$)", re.S)
_HREF_OF_KEY = re.compile(r'<a href="([^"]*)"><code>[a-z0-9][a-z0-9-]*</code></a>')


def grounds_reasons(body: str) -> list[str]:
    """The reasons a grounds note names, in order. A note may name several where a sentence rests on several."""
    m = GROUNDS.match(_BACK.sub("", body).strip())
    if not m:
        return []
    split = r";|,(?=\s*(?:{}))".format("|".join(map(re.escape, GROUNDS_REASONS)))
    return [r.strip() for r in re.split(split, m.group(1)) if r.strip()]


def is_settled(body: str) -> bool:
    """An absence note that two dated passes have searched to exhaustion (feature 235 FR-004)."""
    return bool(SETTLED.search(body))


def footnote_form(body: str, canon: set[str]) -> str | None:
    """'citation', 'absence', 'grounds', or the defect (feature 195 FR-002; feature 235 added the third form).
    A citation links its key to an http(s) page - the registry is not a page where a quote can be read - unless the
    key is canon; an absence note carries no key link and no URL at all (its only anchor is the back link, which
    since feature 211 names the research page); a GROUNDS note reads `no source is owed: <reason>` and says there is
    nothing to find, so like an absence note it owes no key, no link and no quotation."""
    body = _BACK.sub("", body)
    if GROUNDS.match(body.strip()):
        if "<code>" in body or 'href="' in body:
            return "a grounds note carries no key and no link"
        named = grounds_reasons(body)
        unknown = [r for r in named if r not in GROUNDS_REASONS]
        if unknown:
            return f"names a reason that is not one of the six: {unknown!r}"
        if not named:
            return "a grounds note names at least one of the six reasons"
        return "grounds"
    if ABSENCE.match(absence.unrender(body).lstrip()):
        if "<code>" in body or 'href="' in body:
            return "an absence note carries no key and no link"
        return "absence"
    key = _KEY_LINK.search(body)
    href = _HREF_OF_KEY.search(body)
    if not key or not href:
        return None
    target = href.group(1)
    if target.startswith(("http://", "https://")):
        return "citation"
    if "SOURCES.html#" in target and key.group(1) in canon:
        return "citation"
    return f"links the key to {target!r}, which is not a page on the public internet where the quote can be read"
