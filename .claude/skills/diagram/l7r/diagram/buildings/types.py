"""The declaration's reader (feature 254, D1). The data is `types.json` beside this file - a JSON
asset outside the engine key, like feature 207's page content - and this module only reads, shapes
and validates it. A malformed file fails at first use, loudly, naming the field.

WHY DATA. The GM asked, with the second Mode A type, how the checks would be structured so that
"some of those automated checks will likely just be the same for all types of buildings ... and some
of them may be specific to individual building types". A type declared as data is what lets a shared
check stay ignorant of types and a per-type check declare the tiers it applies to; and it is what
makes adding a third type a data change and a folder rather than five edits in five files (the
classifier's closed gen list, the index's tier set, the ignore file's per-file lines, the size
table's usage text, the sweep) - which is what a grep for `magistracies` found on 2026-09-19.
"""

from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass, field
from functools import cache
from typing import Any

CLASSES = ("accurate", "deviation", "convention", "guess")
_TIER = re.compile(r"^[a-z][a-z0-9-]*$")
_DECLARATION = os.path.join(os.path.dirname(os.path.abspath(__file__)), "types.json")


@dataclass(frozen=True)
class Band:
    """A footprint band in feet: `w` and `h` ranges, or an `area` range in sq ft; empty = presence only."""

    w: tuple[float, float] | None = None
    h: tuple[float, float] | None = None
    area: tuple[float, float] | None = None

    @property
    def presence_only(self) -> bool:
        return self.w is None and self.h is None and self.area is None

    def holds(self, w_ft: float, h_ft: float) -> bool:
        """Whether a `w_ft` by `h_ft` footprint lies in the band (either orientation for w/h)."""
        if self.area is not None and not (self.area[0] <= w_ft * h_ft <= self.area[1]):
            return False
        if self.w is None or self.h is None:
            return True
        upright = self.w[0] <= w_ft <= self.w[1] and self.h[0] <= h_ft <= self.h[1]
        turned = self.w[0] <= h_ft <= self.w[1] and self.h[0] <= w_ft <= self.h[1]
        return upright or turned


@dataclass(frozen=True)
class RequiredItem:
    """One item of a type's program: found on a sheet by `label`, held to `band`."""

    id: str
    label: re.Pattern[str]
    band: Band
    cls: str
    why: str
    optional: bool = False
    forms: dict[str, Band | None] = field(default_factory=dict)  # a form's own band, or None = absent under that form

    def band_for(self, form: str | None) -> Band | None:
        """The band under `form` (a notes file's `**Form**:` value): the form's own, None if the item
        is absent under it, else the default band."""
        if form is not None and form in self.forms:
            return self.forms[form]
        return self.band


@dataclass(frozen=True)
class BuildingType:
    tier: str
    title: str
    program: str
    hand_drawn: bool
    required: tuple[RequiredItem, ...]
    checks: tuple[str, ...]
    generated_exceptions: tuple[str, ...] = ()
    notes: str = ""


def _range(value: Any, where: str) -> tuple[float, float]:
    if not (isinstance(value, list) and len(value) == 2 and all(isinstance(v, (int, float)) for v in value)) or value[0] > value[1]:
        raise ValueError(f"{where}: a band range is [min, max] with min <= max, not {value!r}")
    return float(value[0]), float(value[1])


def _band(raw: Any, where: str) -> Band:
    if not isinstance(raw, dict) or set(raw) - {"w", "h", "area"}:
        raise ValueError(f"{where}: band_ft carries only w, h and area, not {raw!r}")
    return Band(
        w=_range(raw["w"], where) if "w" in raw else None,
        h=_range(raw["h"], where) if "h" in raw else None,
        area=_range(raw["area"], where) if "area" in raw else None,
    )


def _item(raw: Any, where: str) -> RequiredItem:
    keys = {"id", "label", "band_ft", "class", "why", "optional", "forms"}
    if not isinstance(raw, dict) or not {"id", "label", "band_ft", "class", "why"} <= set(raw) or set(raw) - keys:
        raise ValueError(f"{where}: a required item carries id, label, band_ft, class, why (and optional, forms), not {sorted(raw) if isinstance(raw, dict) else raw!r}")
    if raw["class"] not in CLASSES:
        raise ValueError(f"{where}/{raw['id']}: class must be one of {CLASSES}, not {raw['class']!r}")
    forms: dict[str, Band | None] = {}
    for form, spec in (raw.get("forms") or {}).items():
        forms[form] = None if spec is None else _band(spec, f"{where}/{raw['id']}/forms/{form}")
    return RequiredItem(
        id=str(raw["id"]),
        label=re.compile(str(raw["label"]), re.IGNORECASE),
        band=_band(raw["band_ft"], f"{where}/{raw['id']}"),
        cls=str(raw["class"]),
        why=str(raw["why"]),
        optional=bool(raw.get("optional", False)),
        forms=forms,
    )


def parse_types(data: Any) -> tuple[BuildingType, ...]:
    """The declaration's objects as `BuildingType`s, refusing a malformed one by name."""
    if not isinstance(data, list) or not data:
        raise ValueError("types.json is a non-empty list of type objects")
    out: list[BuildingType] = []
    for raw in data:
        need = {"tier", "title", "program", "hand_drawn", "required", "checks"}
        if not isinstance(raw, dict) or not need <= set(raw) or set(raw) - (need | {"generated_exceptions", "notes"}):
            raise ValueError(f"a type object carries {sorted(need)} (and generated_exceptions, notes), not {sorted(raw) if isinstance(raw, dict) else raw!r}")
        tier = str(raw["tier"])
        if not _TIER.match(tier):
            raise ValueError(f"tier {tier!r} is not lower-case kebab")
        items = tuple(_item(r, tier) for r in raw["required"])
        ids = [i.id for i in items]
        if len(set(ids)) != len(ids):
            raise ValueError(f"{tier}: required item ids repeat")
        out.append(
            BuildingType(
                tier=tier,
                title=str(raw["title"]),
                program=str(raw["program"]),
                hand_drawn=bool(raw["hand_drawn"]),
                required=items,
                checks=tuple(str(c) for c in raw["checks"]),
                generated_exceptions=tuple(str(s) for s in raw.get("generated_exceptions", ())),
                notes=str(raw.get("notes", "")),
            )
        )
    tiers_seen = [t.tier for t in out]
    if len(set(tiers_seen)) != len(tiers_seen):
        raise ValueError("a tier is declared twice")
    return tuple(out)


@cache
def load_types(path: str = _DECLARATION) -> tuple[BuildingType, ...]:
    """The declaration, parsed once per path."""
    with open(path, encoding="utf-8") as fh:
        return parse_types(json.load(fh))


def tiers(path: str = _DECLARATION) -> frozenset[str]:
    return frozenset(t.tier for t in load_types(path))


def by_tier(tier: str, path: str = _DECLARATION) -> BuildingType | None:
    return next((t for t in load_types(path) if t.tier == tier), None)


def hand_drawn_tiers(path: str = _DECLARATION) -> frozenset[str]:
    return frozenset(t.tier for t in load_types(path) if t.hand_drawn)
