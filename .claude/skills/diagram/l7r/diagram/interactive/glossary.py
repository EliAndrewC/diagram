"""The glossary the map's explanations use (feature 134, GM 2026-08-28: "a glossary of terms defined so
that when we use those terms in our modals ... someone can hover their mouse over it to get an
explanation of the word ... 'bund' or 'coppiced', but also any Japanese words that are not so common
that we would expect everyone to know them").

Each entry: the term as it appears in the prose (matched whole-word, case-insensitive, with the
listed variants) and a one- or two-sentence definition. The page wraps every occurrence in the
explanation text in a hover tooltip. Definitions are written from the research entries the
explanations cite; a term here is a term the prose in `classes.py` actually uses.

THE ENTRIES ARE DATA - `assets/glossary.json` (feature 207): one object per term, `variants` and `def`.
Adding a term is a page-content edit that owes `make page-check`, not the gate (see `content.py`).
"""

from __future__ import annotations

from .content import content

#: term -> (variants matched in the prose, the definition)
GLOSSARY: dict[str, tuple[tuple[str, ...], str]] = {term: (tuple(entry["variants"]), entry["def"]) for term, entry in content("glossary.json").items()}
