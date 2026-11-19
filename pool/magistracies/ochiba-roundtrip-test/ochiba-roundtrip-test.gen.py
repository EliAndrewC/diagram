#!/usr/bin/env python3
"""ochiba-roundtrip-test.gen.py - round-trip TEST of the perimeter-first placer (feature 008).

Encode the EXISTING hand-authored Ochiba magistracy (pool/magistracies/ochiba-magistracy/ochiba-magistracy.svg) as a feet-first
compound program - its real envelope, its real court-spine, and its real building masses measured off the finished SVG at 3 px = 1 ft -
then compose it with the compound generator, to see whether the generator, given Ochiba's ACTUAL program, composes it the way the GM
hand-composed it, and to surface exactly where the two diverge (that divergence is the finding of the test).

The program is data since feature 449 T152: `ochiba-roundtrip-test.compound.json` beside this file (it was `ochiba_program()` here),
with the research claims its docstring carried. Garden pavilions and point features (bath, wells, latrines, fire-tubs, the notice board)
are NOT massed perimeter buildings - the generator seats them against the masses (feature 254: a draft in the pool is swept by the gate
with the whole program, so it carries the whole program).

DRAWN BY THE MODE A ENGINE (feature 449 T152): `l7r-mode-a compound <spec>` composes the sheet, places its captions, writes the svg,
renders the png unless `DIAGRAM_SKIP_RENDER=1`, writes the page and judges the census (`rust/mode_a/src/compound/`, rebuilt from its
derivation, `specs/449-rust-codebase/derivations/T208-compound.md`).

Run:  make map GEN=pool/magistracies/ochiba-roundtrip-test/ochiba-roundtrip-test.gen.py
"""

from __future__ import annotations

import os
import sys

sys.path.insert(
    0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
)  # <tree>/<tier>/<map>/ - one level deeper since feature 161 gave every map its own folder

from l7r.diagram.interactive.sheet import draw_compound_sheet  # noqa: E402

SPEC = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ochiba-roundtrip-test.compound.json")


def main() -> int:
    # the sheet drawn whole - composed, captions placed, picture, page and census - and the generator's exit the engine's (feature 449 T152)
    return draw_compound_sheet(SPEC)


if __name__ == "__main__":
    raise SystemExit(main())
