"""Mode A building TYPES, declared once in `types.json` beside this file (feature 254, GM 2026-09-19).

The declaration's reader is Rust since feature 449 T168 (`rust/mode_a/src/types.rs`), which the audit, `make building-programs`
and the pool sweep read. What stays here is the least the Python pipeline still asks of it - each declared type's pool tier and
title, for `pipeline/poolmaps.py`'s classifier and `pipeline/pool_index.py`'s sections - read straight from the JSON (feature 449
T212 deleted `types.py`, its full reader, with the Python audit that was its last other importer). T157 rebuilds the pipeline in
Rust and drops this module with it.
"""

from __future__ import annotations

import json
import os
from functools import cache
from typing import NamedTuple

_DECLARATION = os.path.join(os.path.dirname(os.path.abspath(__file__)), "types.json")


class BuildingType(NamedTuple):
    """A declared type as the pipeline reads it: its pool tier and its title on the pool index."""

    tier: str
    title: str


@cache
def load_types(path: str = _DECLARATION) -> tuple[BuildingType, ...]:
    """The declared types in their order; the Rust reader (`l7r-mode-a`) is the one that validates the declaration."""
    with open(path, encoding="utf-8") as fh:
        return tuple(BuildingType(str(t["tier"]), str(t["title"])) for t in json.load(fh))


def tiers(path: str = _DECLARATION) -> frozenset[str]:
    """Every declared type's pool tier."""
    return frozenset(t.tier for t in load_types(path))


__all__ = ["BuildingType", "load_types", "tiers"]
