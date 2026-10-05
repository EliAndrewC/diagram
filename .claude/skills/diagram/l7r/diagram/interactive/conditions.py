"""Items of a modal that depend on the settlement's knobs (feature 319, FR-015, plan D14).

The GM, 2026-10-05, of the windbreak's guess that a clustered village sheltered behind one shared wood, shown on every map:
*"Could we make that kind of item still automatic but dependent on the "knobs" for a settlement in cases where that is
relevant?"* So a guess bullet, a paragraph of About or Depiction, or an `Entry:` path may carry a condition -
`[settlement_form=nucleated]`, or several values `[settlement_form=nucleated|linear]`, or several conditions that must all
hold `[settlement_form=nucleated][lane_web=alleys]` - opening the item (a path: following it), and the page shows the item only
on a map whose manifest records, for every condition, a value among them. A condition may name a declared choice of the title
card's table (`choices.json`, e.g. `harvest_weather`) as well as a registered knob (writer F's grave and lane modals, 2026-10-05). A map that records no
value for the knob shows none of its conditional items: nothing says they hold there. The condition never reaches the reader.

The knob and its values are checked against the POPULATED knob registry when a page is written (`check`), because the knobs
are registered from modules across the engine, and the vocabulary is parsed at import, before the engine is loaded."""

from __future__ import annotations

import importlib
import pathlib
import re
from collections.abc import Iterable, Mapping
from functools import cache
from typing import Any

#: `[knob=value]` or `[knob=value|value]`, at the start of an item
LEAD = re.compile(r"^\[([a-z_]+)=([a-z_0-9-]+(?:\|[a-z_0-9-]+)*)\]\s*")
"""Research: modal condition plumbing - NONE"""

#: the same condition after an `Entry:` path, up to the next comma
AFTER_PATH = re.compile(r"(\S+\.html)((?:\s*\[[a-z_]+=[a-z_0-9-]+(?:\|[a-z_0-9-]+)*\])+)")
"""Research: modal condition plumbing - NONE"""

#: anything bracketed that looks meant as a condition but is not one: the error says the form
LOOSE = re.compile(r"^\[[^\]]*=[^\]]*\]")
"""Research: modal condition plumbing - NONE"""


Cond = tuple[tuple[str, tuple[str, ...]], ...]


def split(item: str) -> tuple[Cond | None, str]:
    """The item's conditions ((knob, values), ...) and its text; (None, item) for an item with none. A bracket at the start
    that is not a well-formed condition is refused, so a typo is not shown to a reader as text.
    Research: modal condition plumbing - NONE"""
    conds: list[tuple[str, tuple[str, ...]]] = []
    rest = item
    while True:
        hit = LEAD.match(rest)
        if not hit:
            break
        conds.append((hit.group(1), tuple(hit.group(2).split("|"))))
        rest = rest[hit.end() :]
    if LOOSE.match(rest):
        raise ValueError(f"a modal condition is written [knob=value] or [knob=value|value], lower case: {item[:60]!r} (dev/modals.md M22)")
    return (tuple(conds) if conds else None), rest


def entry_conditions(entry: str) -> dict[str, Cond]:
    """The `Entry:` paths that carry conditions, each with them.
    Research: modal condition plumbing - NONE"""
    out: dict[str, Cond] = {}
    for m in AFTER_PATH.finditer(entry):
        conds, _ = split(m.group(2).replace(" ", ""))
        if conds:
            out[m.group(1)] = conds
    return out


def strip_entry(entry: str) -> str:
    """The `Entry:` line with its conditions removed - what every reader of the paths sees.
    Research: modal condition plumbing - NONE"""
    return AFTER_PATH.sub(r"\1", entry)


def holds(conds: Cond | None, meta: Mapping[str, Any]) -> bool:
    """Does the map meet every condition? An item with none always does; a map recording no value for a knob never does.
    Research: modal condition plumbing - NONE"""
    return conds is None or all(str(meta.get(knob, "")) in values for knob, values in conds)


def shown(items: Iterable[str], meta: Mapping[str, Any]) -> list[str]:
    """The items this map shows, conditions removed.
    Research: modal condition plumbing - NONE"""
    out = []
    for item in items:
        cond, text = split(item)
        if holds(cond, meta):
            out.append(text)
    return out


def shown_entry(entry: str, meta: Mapping[str, Any]) -> str:
    """The `Entry:` line this map lists: a path whose condition fails is dropped, so a question resting only on a hidden
    item is not linked (FR-015, the GM: "simply not link to things which are not covered").
    Research: modal condition plumbing - NONE"""
    conds = entry_conditions(entry)
    kept = [p for p in re.split(r"[,;]\s*", strip_entry(entry)) if p.strip() and holds(conds.get(p.strip()), meta)]
    return ", ".join(p.strip() for p in kept)


@cache
def knobs() -> dict[str, tuple[str, ...]]:
    """Every registered knob and its forms, the registry POPULATED: each module that calls `register_knob(` is imported,
    found by reading the source tree, so a knob registered in a new module is known without a list to update.
    Research: modal condition plumbing - NONE"""
    root = pathlib.Path(__file__).resolve().parents[1]
    for path in sorted(root.rglob("*.py")):
        if "register_knob(" in path.read_text(encoding="utf-8") and path.name != "_knobs.py":
            importlib.import_module("l7r.diagram." + ".".join(path.relative_to(root).with_suffix("").parts))
    from l7r.diagram.settlement._knobs import KNOBS  # noqa: PLC0415

    from .choices import table  # noqa: PLC0415

    out = {name: tuple(str(v) for v in k.value_space) for name, k in KNOBS.items()}
    for entry in table():  # the title card's declared choices, and the values a manifest records beyond a knob's registry
        out[entry["key"]] = tuple(dict.fromkeys([*out.get(entry["key"], ()), *entry["values"]]))
    return out


def check(name: str, conds: Iterable[Cond | None]) -> None:
    """Refuse a condition naming a knob or a value the registry and the choices table do not know, with the knob's forms in
    the message.
    Research: modal condition plumbing - NONE"""
    known = knobs()
    for knob, values in (c for group in conds if group for c in group):
        if knob not in known:
            raise ValueError(f"{name}: [{knob}=...] names no registered knob - one of {sorted(known)} (dev/modals.md M22)")
        bad = [v for v in values if v not in known[knob]]
        if bad:
            raise ValueError(f"{name}: [{knob}={'|'.join(values)}]: {bad} not among {knob}'s forms {list(known[knob])} (dev/modals.md M22)")


def label(conds: Cond) -> str:
    """How a check's bundle shows conditions: "(only where settlement_form is nucleated or linear)".
    Research: modal condition plumbing - NONE"""
    return "(only where " + " and ".join(f"{knob} is {' or '.join(values)}" for knob, values in conds) + ")"
