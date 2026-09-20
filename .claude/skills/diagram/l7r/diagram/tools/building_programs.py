"""`make building-programs`: the required-items table of every declared Mode A type, rendered into
`buildings/programs.md` between markers (feature 254, plan D11).

WHY. The GM's rule for the second type was that a type is declared ONCE and the docs render from it.
The checks read `buildings/types.json`; the reviewers read `programs.md`. If the two are written
separately they drift - the tub check's fill list and its docstring did exactly that (2026-07-25) -
so the table the reviewer reads is DERIVED from the declaration, and `--check` fails the gate when
it is stale, the way `make glossary CHECK=1` holds the glossary asset to its source.

Each type's block sits between `<!-- types.json:<tier> -->` and `<!-- /types.json:<tier> -->`; the
prose around it (knobs, anchors, staffing, the composition rules) is hand-written and untouched.
"""

from __future__ import annotations

import argparse
import os
import re
import sys

from ..buildings.types import BuildingType, load_types

SKILL = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", ".."))
PROGRAMS = os.path.join(SKILL, "buildings", "programs.md")


def _band(item_band) -> str:
    if item_band.presence_only:
        return "presence"
    parts = []
    if item_band.w and item_band.h:
        parts.append(f"{item_band.w[0]:g}-{item_band.w[1]:g} by {item_band.h[0]:g}-{item_band.h[1]:g} ft")
    if item_band.area:
        parts.append(f"{item_band.area[0]:g}-{item_band.area[1]:g} sq ft")
    return "; ".join(parts)


def render(btype: BuildingType) -> str:
    """The Markdown table for one type: item, the label it is found by, its band, its class, its why."""
    lines = [
        "| item | found by the label (or declared by id) | band (feet; either orientation) | class | why |",
        "|---|---|---|---|---|",
    ]
    for it in btype.required:
        forms = "; ".join(f"under `{f}`: {'absent' if b is None else _band(b)}" for f, b in it.forms.items())
        band = _band(it.band) + (f" ({forms})" if forms else "") + (" - optional, a knob" if it.optional else "")
        if it.site:  # a SITE item (feature 257): drawn where the declared map shows its class, and only there
            band += f" - a site item: drawn where the sheet's declared map shows a {it.site.replace('_', ' ')} inside the frame"
        lines.append(f"| `{it.id}` | `/{it.label.pattern}/` | {band} | {it.cls} | {it.why} |")
    if btype.notes:
        lines += ["", btype.notes]
    return "\n".join(lines)


def _blocks(text: str) -> dict[str, tuple[int, int]]:
    out: dict[str, tuple[int, int]] = {}
    for m in re.finditer(r"<!-- types\.json:([a-z0-9-]+) -->\n(.*?)\n<!-- /types\.json:\1 -->", text, re.S):
        out[m.group(1)] = (m.start(2), m.end(2))
    return out


def apply(text: str, types: tuple[BuildingType, ...]) -> tuple[str, list[str]]:
    """`programs.md` with every marked block rewritten from its declaration; the tiers that have no block."""
    blocks = _blocks(text)
    missing = [t.tier for t in types if t.tier not in blocks]
    for t in sorted(types, key=lambda t: blocks.get(t.tier, (0, 0))[0], reverse=True):
        if t.tier in blocks:
            a, b = blocks[t.tier]
            text = text[:a] + render(t) + text[b:]
    return text, missing


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--check", action="store_true", help="exit 1 if the rendered blocks are stale or a declared type has no block")
    ap.add_argument("--path", default=PROGRAMS)
    args = ap.parse_args(argv)
    with open(args.path, encoding="utf-8") as fh:
        text = fh.read()
    new, missing = apply(text, load_types())
    if missing:
        print(f"building-programs: no `<!-- types.json:<tier> -->` block in {args.path} for: {', '.join(missing)}", file=sys.stderr)
        return 1
    if new == text:
        print(f"building-programs: {os.path.relpath(args.path)} is current")
        return 0
    if args.check:
        print(f"building-programs: {os.path.relpath(args.path)} is STALE - run `make building-programs`", file=sys.stderr)
        return 1
    with open(args.path, "w", encoding="utf-8") as fh:
        fh.write(new)
    print(f"building-programs: wrote {os.path.relpath(args.path)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
