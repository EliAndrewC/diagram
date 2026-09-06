"""The feature-class vocabulary of the interactive map - the package (feature 189).

Look here when: you are adding a KIND of feature (a class in the family module it belongs to), changing
what a modal SAYS (its docstring), or adding a sibling distinction (`siblings.py`). The mechanics - the
`FeatureClass` the page reads, the labels, the lead sentence, the docstring parser - are in `_base.py`.
Everything the old single module exported is exported from here unchanged.
"""

from __future__ import annotations

from . import dikepond, fields, greenery, homestead, water_and_ways  # noqa: F401 - imported for their classes, in the spec's FR-007 order
from ._base import (
    ANNOUNCED,
    CONVENTION_LEAD,
    NOT_HIGHLIGHTED,
    NOT_HIGHLIGHTED_OVERTURNED,
    NOT_HIGHLIGHTED_RULINGS,
    PLACE,
    FeatureClass,
    Kind,
    Label,
    install_siblings,
    label_phrase,
    lead_sentence,
    parse_explanation,
    slug,
)
from .siblings import _PAIRS

# THE ORDER IS THE FAMILIES', NOT THE IMPORT SORTER'S: ruff sorts the import above alphabetically, so
# `Kind.registry` fills dikepond-first; `_ORDER` restores the spec's FR-007 sequence explicitly, and the
# classes within a family keep their definition order. The noqa keeps an import that exists only for
# its side effect of defining the classes.
_ORDER = (homestead, greenery, fields, water_and_ways, dikepond)
_KINDS: list[type[Kind]] = [k for mod in _ORDER for k in Kind.registry if k.__module__ == mod.__name__]

#: Every feature class, by key. Insertion order is the spec's FR-007 order.
CLASSES: dict[str, FeatureClass] = install_siblings([k.feature() for k in _KINDS], _PAIRS)

__all__ = [
    "ANNOUNCED",
    "CLASSES",
    "CONVENTION_LEAD",
    "NOT_HIGHLIGHTED",
    "NOT_HIGHLIGHTED_OVERTURNED",
    "NOT_HIGHLIGHTED_RULINGS",
    "PLACE",
    "FeatureClass",
    "Kind",
    "Label",
    "label_phrase",
    "lead_sentence",
    "parse_explanation",
    "slug",
]
