"""The works a question's notes cite, and what kind of note each is (features 211, 235, 303).

The GM, feature 211 (2026-09-07): the notes are written once and loaded by every page that shows them, and a work's
write-up - its citation line, what it is, why it applies and its limits - is written once, in its registry entry
(*"we do not want to have multiple different write ups of a single paper"*). What is DERIVED from those two stores is
the WORKS block at the foot of a question's page in the record's site: for each work the page's notes cite, in order of
first citation, its citation line and the two write-ups (`works_html`, called by `record/site.py`).

Feature 211's per-page citations pages went with the page directories (feature 303): a question's notes are in its own
notes file and shown at the foot of its own page, and the single page carries every note.

Nothing is typed twice: the notes live beside their questions, the write-ups in the registry, and everything else is
a derivation.
"""

from __future__ import annotations

import re

from l7r.diagram.interactive.record import absence
from l7r.diagram.interactive.sources import WHAT_LABEL, WHY_LABEL, link_target

_KEY_LINK = re.compile(r'<a href="[^"]*"><code>([a-z0-9][a-z0-9-]*)</code></a>')
_BACK = re.compile(r'\s*<a class="fnback" href="[^"]*">back</a>')
#: The markers the works section is derived between. Everything between them is `make citations`' output;
#: the test fails while it differs, and the message says which page.
WORKS_OPEN = "<!-- works-cited: DERIVED by `make citations` from SOURCES.html - change a work's write-up in its registry entry, never here -->"
WORKS_CLOSE = "<!-- /works-cited -->"


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
