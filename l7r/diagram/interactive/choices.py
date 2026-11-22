"""The title card's choices (feature 319, plan D10, FR-009): what was chosen for this settlement, each value a modal.

The GM, 2026-10-03, on Inashiro: the per-settlement differences belong on the title card, where each choice opens its own
modal, so every feature modal can be the same on every map. `assets/choices.json` is the table - every knob of the populated
registry and every declared choice, in the order the card lists them, each value's label - and each value's modal is a file
`assets/modals/choice/<key>--<value>.md` (a degree along a continuum, marked `degree`, one file `<key>.md`), read by the same
parser as a feature modal and keyed `choice:<key>=<value>` (or `choice:<key>`) in the page's data."""

from __future__ import annotations

import json
import os
from functools import cache
from typing import Any

from . import conditions
from .classes._base import MODALS_DIR, FeatureClass, _about_feature, parse_explanation

TABLE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "choices.json")
"""Research: choice plumbing - NONE"""
CHOICE_DIR = os.path.join(MODALS_DIR, "choice")
"""Research: choice plumbing - NONE"""


@cache
def not_choices() -> dict[str, str]:
    """Per-settlement rolls that are not choices of form - geometry, a degree, a count - each with why (the plan review of
    D10: every roll is a choice on the card or accounted for here).
    Research: choice plumbing - NONE"""
    with open(TABLE, encoding="utf-8") as fh:
        return dict(json.load(fh).get("not_choices", {}))


@cache
def table() -> list[dict[str, Any]]:
    """The choices in card order.
    Research: choice plumbing - NONE"""
    with open(TABLE, encoding="utf-8") as fh:
        return list(json.load(fh)["choices"])


def modal_key(entry: dict[str, Any], value: str) -> str:
    """The page-data key of a value's modal.
    Research: choice plumbing - NONE"""
    return f"choice:{entry['key']}" if entry.get("degree") else f"choice:{entry['key']}={value}"


def modal_file(entry: dict[str, Any], value: str) -> str:
    """The file a value's modal is written in.
    Research: choice plumbing - NONE"""
    name = entry["key"] if entry.get("degree") else f"{entry['key']}--{value}"
    return os.path.join(CHOICE_DIR, f"{name}.md")


def modal(entry: dict[str, Any], value: str) -> FeatureClass | None:
    """A value's modal, or None while its file is not written.
    Research: choice plumbing - NONE"""
    path = modal_file(entry, value)
    if not os.path.isfile(path):
        return None
    with open(path, encoding="utf-8") as fh:
        parts = parse_explanation(fh.read(), os.path.basename(path))
    return _about_feature(os.path.basename(path), modal_key(entry, value), parts)


def made(meta: dict[str, Any]) -> list[dict[str, str]]:
    """This map's choices, in card order: each recorded choice's name, its value's label and its modal's key (empty while
    the modal is not written). A recorded value the table does not know is listed by its raw value, so a gap shows.
    Research: choice plumbing - NONE"""
    out = []
    for entry in table():
        if entry["key"] not in meta or meta[entry["key"]] is None or not applies(entry, meta):
            continue
        value = str(meta[entry["key"]])
        label = entry["values"].get(value, value)
        if entry.get("degree"):
            label = entry["values"].get(value, f"{value} degrees")
        out.append({"name": entry["name"], "value": label, "k": modal_key(entry, value) if modal(entry, value) else ""})
    return out


def applies(entry: dict[str, Any], meta: dict[str, Any]) -> bool:
    """Does this choice belong to this settlement? An entry's `when` - in the modal conditions' form, `[settlement_form=linear]`
    - names the settlement it is a choice of: a row village's row, a scattered farm's water. A map records some of them
    whatever its form, and the card does not list a choice its settlement did not make (the plan review of D10).
    Research: choice plumbing - NONE"""
    conds, _ = conditions.split(entry.get("when", ""))
    return conditions.holds(conds, meta)


def registry_for(meta: dict[str, Any]) -> dict[str, FeatureClass]:
    """The modals of this map's choices, by page-data key.
    Research: choice plumbing - NONE"""
    out: dict[str, FeatureClass] = {}
    for entry in table():
        if entry["key"] in meta and meta[entry["key"]] is not None and applies(entry, meta):
            fc = modal(entry, str(meta[entry["key"]]))
            if fc is not None:
                out[fc.key] = fc
    return out
