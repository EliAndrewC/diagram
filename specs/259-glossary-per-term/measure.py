#!/usr/bin/env python3
"""The measurements behind this spec - one subcommand each, re-runnable.

    python3 specs/259-glossary-per-term/measure.py R1

R1 what the glossary weighs, and what a membership test actually needs of it
R2 the variants two terms both claim, which is what makes term ORDER load-bearing
R3 the filename hazards: a term a filename cannot carry, and the ones that need no slug
"""

from __future__ import annotations

import collections
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SKILL = os.path.normpath(os.path.join(HERE, "..", "..", ".claude", "skills", "diagram"))
SOURCE = os.path.join(SKILL, "l7r", "diagram", "interactive", "assets", "glossary.json")
DERIVED = os.path.join(SKILL, "research", "assets", "glossary.js")


def glossary() -> dict[str, dict]:
    with open(SOURCE, encoding="utf-8") as fh:
        return json.load(fh)


def size(text: str) -> int:
    """BYTES, not characters - the glossary carries macrons and kanji."""
    return len(text.encode("utf-8"))


def r1() -> None:
    """What a check reads today, against what the question it is asking needs."""
    g = glossary()
    names = sum(size(k) for k in g)
    variants = sum(size(json.dumps(v.get("variants", []), ensure_ascii=False)) for v in g.values())
    defs = sum(size(json.dumps(v, ensure_ascii=False)) for v in g.values())
    listing = size("\n".join(sorted(f"{i * 10:04d}-{k.replace('/', '%2F')}.json" for i, k in enumerate(g, 1))) + "\n")
    print(f"  source   {os.path.relpath(SOURCE, SKILL)}: {os.path.getsize(SOURCE):,} bytes, {len(g)} terms")
    print(f"  derived  {os.path.relpath(DERIVED, SKILL)}: {os.path.getsize(DERIVED):,} bytes  <- what a check reads today")
    print(f"\n  term NAMES alone            {names:>9,}")
    print(f"  names + variants            {names + variants:>9,}")
    print(f"  the definitions             {defs:>9,}")
    print(f"\n  a directory listing of one file per term: {listing:,} bytes")
    sizes = sorted(size(json.dumps(v, ensure_ascii=False)) for v in g.values())
    print(f"  one term's file: median {sizes[len(sizes) // 2]} bytes, min {sizes[0]}, max {sizes[-1]}")


def r2() -> None:
    """Which variants two terms both claim - the reason term ORDER decides what a reader sees."""
    g = glossary()
    claimed: dict[str, list[str]] = collections.defaultdict(list)
    for term, entry in g.items():
        for variant in entry["variants"]:
            claimed[variant.lower()].append(term)
    clash = {v: ts for v, ts in claimed.items() if len(ts) > 1}
    order = list(g)
    print(f"  variants claimed by more than one term: {len(clash)}")
    for variant, terms in clash.items():
        winner = max(terms, key=order.index)          # record.js: defs[v] = def, in file order
        print(f"    {variant!r:<22} claimed by {terms} - the page shows {winner!r}, because it is later in the file")


def r3() -> None:
    """The filename hazards, counted rather than assumed."""
    g = glossary()
    illegal = [k for k in g if "/" in k or "\0" in k]
    non_ascii = [k for k in g if not k.isascii()]
    slugged = collections.Counter(k.replace("/", "%2F") for k in g)
    print(f"  terms a filename cannot carry as they stand: {len(illegal)} -> {illegal}")
    print(f"  terms with non-ASCII characters (a filename CAN carry these): {len(non_ascii)} -> {non_ascii}")
    print(f"  collisions after percent-encoding: {[k for k, n in slugged.items() if n > 1]}")
    print(f"  terms whose name is already a plain filename: {len(g) - len(illegal)}")


def main(argv: list[str]) -> int:
    which = {"R1": r1, "R2": r2, "R3": r3}
    if len(argv) != 2 or argv[1].upper() not in which:
        print(f"usage: {os.path.basename(__file__)} R1|R2|R3", file=sys.stderr)
        return 2
    which[argv[1].upper()]()
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
