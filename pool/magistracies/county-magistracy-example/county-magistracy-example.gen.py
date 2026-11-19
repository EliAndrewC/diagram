#!/usr/bin/env python3
"""county-magistracy-example.gen.py - the generic county magistracy, drawn by the compound generator.

The program is data: `county-magistracy-example.compound.json` beside this file, a generic county magistracy declared in feet from
docs/building-programs.md's county magistrate's manor program and its knobs (feature 449 T152, which rebuilt the generator in Rust
from its derivation, `specs/449-rust-codebase/derivations/T208-compound.md`, and moved the program out of the old Python builder). This
gen is the pool wiring for it: render-sync regenerates every `pool/*/*.gen.py` from its own directory, so wrapping the program in a gen
keeps the gitignored svg, png and page fresh in main. Before this gen existed the png was a one-off hand render and silently went stale
(caught 2026-07-24).

DRAWN BY THE MODE A ENGINE (feature 449 T152): `l7r-mode-a compound <spec>` composes the sheet, places its captions, writes the svg,
renders the png unless `DIAGRAM_SKIP_RENDER=1`, writes the page and judges the census (`rust/mode_a/src/compound/`).

Run:  make map GEN=pool/magistracies/county-magistracy-example/county-magistracy-example.gen.py
"""

from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))  # <tree>/<tier>/<map>/ - one level deeper since feature 161 gave every map its own folder

from l7r.diagram.interactive.sheet import draw_compound_sheet  # noqa: E402

SPEC = os.path.join(os.path.dirname(os.path.abspath(__file__)), "county-magistracy-example.compound.json")


def main() -> int:
    # the sheet drawn whole - composed, captions placed, picture, page and census - and the generator's exit the engine's (feature 449 T152)
    return draw_compound_sheet(SPEC)


if __name__ == "__main__":
    raise SystemExit(main())
