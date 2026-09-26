"""The Mode A kinds - what each kind of thing on a compound plan IS, for the interactive page (feature 262).

The GM, 2026-09-26: *"see write-ups of what these things were and the extent to which this is indeed based on
real historical research or is a thing specific to this fictional setting"*. This package is the hamlet
vocabulary's twin (`../classes/`): the same `Kind` base, the same docstring form (`What:` / `Why:` / `Note:` /
optional `Caveat:`, then `Name:` / `Covers:` / `Label:` / `Sources:` / `Entry:`), parsed at import into the
`FeatureClass` the page reads. A sheet says WHERE a thing is and what KIND it is with `data-kind` on the drawn
element (`../sheet.py`); this says what that kind of thing is, ONCE, for every magistracy that draws one.

A SEPARATE REGISTRY, not rows added to `CLASSES`, because a compound's well and a hamlet's well are written
about different places: the key may coincide and each page reads its own vocabulary (`render_page(registry=)`).
The hamlet registry is untouched (spec FR-011).

EVERY WRITE-UP IS WRITTEN FROM THE EXISTING RECORD (spec FR-005, the GM: *"for now, I only want to tie into
existing research findings that already exist"*). A kind keeps the classification an existing finding already
gave it - a research section, or the `buildings/types.json` program item folded into it (FR-003a: the item's
class and why are stated here, once, and the audit and `programs.md` read them back from here). A kind no
research section covers names no question in its `Entry:`, so the page's missing references show the gap. The
measurement behind every label is `specs/262-interactive-magistracy-pages/coverage.md`.

Look here when: a magistracy modal says something wrong (the kind's docstring), a new kind of thing is drawn
on a sheet (a class in the family it belongs to, and its tag on the sheet), or the program audit reports a
class or why (they come from here).
"""

from __future__ import annotations

from ..classes import FeatureClass, Kind, install_siblings
from . import grounds, household, office, particulars
from .siblings import PAIRS

#: The families in the order their kinds are listed; within a family, definition order.
_ORDER = (grounds, office, household, particulars)
_KINDS: list[type[Kind]] = [k for mod in _ORDER for k in Kind.registry if k.__module__ == mod.__name__]

#: Every Mode A kind, by key - the vocabulary a magistracy page is written with.
COMPOUND_CLASSES: dict[str, FeatureClass] = install_siblings([k.feature() for k in _KINDS], PAIRS)

__all__ = ["COMPOUND_CLASSES"]
