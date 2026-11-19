#!/usr/bin/env python3
"""ochiba-magistracy.gen.py - rasterize the hand-authored manor plan.

Mode A magistracy plans are hand-authored svg SOURCE (tracked in git); only the png is
derived. This gen is the pool wiring that keeps the gitignored png fresh in main:
render-sync regenerates every `pool/*/*.gen.py` from its own directory, and a render
with no gen wrapper is a one-off hand render that silently goes stale (the
county-magistracy-example png did exactly that; caught 2026-07-24). This gen writes the png
and, since feature 262, the interactive page beside it (`<map>.html`, from the sheet's own `data-kind`
tags) - the tracked svg is never touched; the captions are placed in the pipeline (feature 286).

DRAWN BY THE MODE A ENGINE (feature 449 T202): the captions placed by the placer rebuilt from its derivation, the png rendered
unless `DIAGRAM_SKIP_RENDER=1`, the page written and the census judged, all by `l7r-mode-a hand-sheet` (`rust/mode_a/src/sheet/hand.rs`),
as the country shrine's generator since T151; this file stays the pool's wiring and the generation cache's entry.

Run:  python3 pool/magistracies/ochiba-magistracy/ochiba-magistracy.gen.py   (from anywhere)
"""

from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))  # <skill>/pool/<tier>/<map>/

from l7r.diagram.interactive.sheet import draw_hand_sheet  # noqa: E402

SVG = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ochiba-magistracy.svg")


def main() -> int:
    # the sheet drawn whole - captions, picture, page and census - and the generator's exit the engine's (feature 449 T151, T202)
    return draw_hand_sheet(SVG)


if __name__ == "__main__":
    raise SystemExit(main())
