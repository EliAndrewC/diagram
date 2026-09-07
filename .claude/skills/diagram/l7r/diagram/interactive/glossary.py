"""The glossary the map's explanations use (feature 134, GM 2026-08-28: "a glossary of terms defined so
that when we use those terms in our modals ... someone can hover their mouse over it to get an
explanation of the word ... 'bund' or 'coppiced', but also any Japanese words that are not so common
that we would expect everyone to know them").

Each entry: the term as it appears in the prose (matched whole-word, case-insensitive, with the
listed variants) and a one- or two-sentence definition. The page wraps every occurrence in the
explanation text in a hover tooltip. Definitions are written from the research entries the
explanations cite; a term here is a term the prose in `classes.py` actually uses.

THE ENTRIES ARE DATA - `assets/glossary.json` (feature 207): one object per term, `variants` and `def`.
Adding a term is a page-content edit that owes `make page-check`, not the gate (see `content.py`); the
record's derived `research/assets/glossary.js` is then rewritten by `make glossary` (feature 209).
"""

from __future__ import annotations

import json

from .content import content

#: term -> (variants matched in the prose, the definition)
GLOSSARY: dict[str, tuple[tuple[str, ...], str]] = {term: (tuple(entry["variants"]), entry["def"]) for term, entry in content("glossary.json").items()}


def record_glossary_js() -> str:
    """The research record's copy of this glossary, as the JavaScript asset `research/assets/glossary.js`
    (feature 209, GM 2026-09-07: *"apply the same kind of tooltip rules to our research sections that we have
    in our diagram HTML pages"*). ONE glossary serves both surfaces: the map inlines `glossary_for()` into each
    page at write time, and the record's hand-authored pages - static, no build step - load this DERIVED file,
    which `make glossary` writes from `assets/glossary.json` and `tests/interactive/test_record_format.py` proves is
    in sync. `record.js` wraps every occurrence of a term in a page's visible text the way `page.js` wraps a
    modal's. Variants longest first, as `glossary_for` orders them, so "head race" wins over "head"."""
    entries = [{"term": term, "variants": sorted(variants, key=len, reverse=True), "def": definition} for term, (variants, definition) in GLOSSARY.items()]
    return (
        "// DERIVED FILE - written by `make glossary` from l7r/diagram/interactive/assets/glossary.json (features 207 and 209). Never\n"
        "// edit here: add or change a term in glossary.json and run `make glossary`; the gate fails while the two differ.\n"
        "window.RECORD_GLOSSARY = " + json.dumps(entries, ensure_ascii=False, indent=1) + ";\n"
    )
