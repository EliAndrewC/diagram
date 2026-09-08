"""The page's CONTENT lives in `assets/*.json`, and this is how a module reads it (feature 207, GM 2026-09-07).

WHY: prose a reader sees - the glossary, the sibling texts, the place card's wording, the page's fixed
phrases - used to be Python constants, which made every wording edit an ENGINE change: it re-keyed the
gate (a dict literal is executable code, so `gate-stamp`'s docstring-stripped AST moved), chilled the
roll cache (`page.py` imports these modules while writing a map's page, and `gencache` hashes every
imported module's top level), and cost the whole ten-minute suite. Feature 205 paid that for one
glossary term. A `.json` under `assets/` is an ASSET: outside the engine key, outside the roll-cache
key (`gencache.record` does not record a `.json` read), inside gate-stamp's `page` area and the render
fingerprint - so an edit owes `make page-check` and regenerates the pages on landing, exactly like the
stylesheet. The criterion for what moves is what a thing IS, never its size: content a reader sees
moves; data the engine executes on (`overlap/taxonomy.py`, the hit-region keys) stays code.

The loader is deliberately dumb: no schema, no caching beyond the module-level constants each consumer
builds once at import. A malformed file fails at import, loudly, which `make page-check` runs.
"""

from __future__ import annotations

import json
import os
from typing import Any

ASSETS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")


def content(name: str) -> Any:
    """The parsed JSON of `assets/<name>`."""
    with open(os.path.join(ASSETS, name), encoding="utf-8") as fh:
        return json.load(fh)
